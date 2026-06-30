#!/usr/bin/env python3
"""Evaluate an SFT or OPSD checkpoint on a math-operations test set.

Three steps:
  1. (Optional) Merge a LoRA adapter into the base model — only when
     ``--checkpoint_dir`` points at an adapter; pass ``--skip_merge`` for
     pre-merged or full-finetune checkpoints.
  2. Run inference via the shared run_batch_inference.py.
  3. Score predictions and save results (overall + per-operation breakdown).

The test JSONL may be in any of three formats; the converter is auto-selected:
  - ``messages``  → {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
  - alpaca       → {"instruction": ..., "input": ..., "output": ...}
  - inference    → {"prompt": ..., "ground_truth_answer": ...}

Usage
-----
# Pre-merged / consolidated OPSD or SFT checkpoint:
python eval_sft.py \\
    --merged_model_dir /path/to/consolidated_or_full_sft \\
    --test_data        /path/to/test_messages.jsonl \\
    --skip_merge

# LoRA checkpoint (merge first):
python eval_sft.py \\
    --checkpoint_dir /path/to/lora_ckpt \\
    --test_data      /path/to/test_messages.jsonl
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional

import torch

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
INFERENCE_SCRIPT = PROJECT_ROOT / "mixsd" / "test" / "sglang" / "run_batch_inference.py"
sys.path.insert(0, str(PROJECT_ROOT))

from mixsd.eval.eval_output import (  # noqa: E402
    compare_answers,
    evaluate_output_file,
    extract_answer_from_text,
    extract_answer_tags,
    extract_boxed_answer,
    save_result_to_csv,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_base_model_from_adapter(checkpoint_dir: str) -> Optional[str]:
    """Read base_model_name_or_path from a PEFT adapter_config.json."""
    cfg = Path(checkpoint_dir) / "adapter_config.json"
    if cfg.exists():
        with open(cfg) as f:
            data = json.load(f)
        return data.get("base_model_name_or_path")
    return None


def _extract_op_label(text: str) -> Optional[str]:
    """Extract operation label from a prompt (A-K uppercase or a-t lowercase)."""
    m = re.search(r"\bfunction\s+([A-Za-z]+)\.", text)
    if m:
        return m.group(1)
    m = re.search(r"\b([A-Za-z]+)\(\d+\)", text)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Format conversion: → {"prompt", "ground_truth_answer", "instruction"}
# ---------------------------------------------------------------------------

def _ground_truth_from_text(text: str) -> str:
    """Extract a ground-truth answer string from a free-form output / assistant turn."""
    gt = extract_boxed_answer(text)
    if gt is None:
        gt = extract_answer_tags(text)
    if gt is None:
        gt = extract_answer_from_text(text)
    return str(gt) if gt is not None else str(text)


def _detect_format(first_record: dict) -> str:
    if "messages" in first_record:
        return "messages"
    if "prompt" in first_record:
        return "inference"
    if "instruction" in first_record:
        return "alpaca"
    raise ValueError(
        f"Unknown test-data record format (keys: {list(first_record)}). "
        "Expected one of: 'messages', 'prompt', 'instruction'."
    )


def convert_to_inference_format(src_path: str, dst_path: str, fmt: str) -> str:
    """Rewrite *src_path* into {prompt, ground_truth_answer, instruction} JSONL."""
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    with open(src_path) as fin, open(dst_path, "w") as fout:
        for line in fin:
            if not line.strip():
                continue
            item = json.loads(line)

            if fmt == "messages":
                msgs = item["messages"]
                user = next((m["content"] for m in msgs if m["role"] == "user"), "")
                assistant = next(
                    (m["content"] for m in msgs if m["role"] == "assistant"), ""
                )
                prompt = user
                gt = _ground_truth_from_text(assistant)
            elif fmt == "alpaca":
                prompt = item.get("instruction", "")
                inp = item.get("input", "")
                if inp:
                    prompt = f"{prompt}\n{inp}"
                gt = _ground_truth_from_text(item.get("output", ""))
            else:
                raise AssertionError(f"convert called for already-converted fmt: {fmt}")

            fout.write(
                json.dumps(
                    {
                        "prompt": prompt,
                        "ground_truth_answer": gt,
                        "instruction": prompt,
                    }
                )
                + "\n"
            )
    return dst_path


# ---------------------------------------------------------------------------
# Step 1: Merge LoRA
# ---------------------------------------------------------------------------

def merge_lora(base_model_path: str, lora_path: str, output_path: str) -> str:
    """Merge a LoRA adapter into the base model and save."""
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    logger.info("Loading base model: %s", base_model_path)
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )

    logger.info("Loading LoRA adapter: %s", lora_path)
    model = PeftModel.from_pretrained(model, lora_path)

    logger.info("Merging LoRA weights ...")
    model = model.merge_and_unload()

    logger.info("Saving merged model to: %s", output_path)
    Path(output_path).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    del model
    torch.cuda.empty_cache()
    return output_path


# ---------------------------------------------------------------------------
# Step 2: Inference via run_batch_inference.py
# ---------------------------------------------------------------------------

def run_inference(
    model_path: str,
    input_path: str,
    output_path: str,
    max_new_tokens: int,
    max_input_sequence_length: int,
    temperature: float,
) -> str:
    """Call run_batch_inference.py as a subprocess."""
    cmd = [
        sys.executable, str(INFERENCE_SCRIPT),
        "-i", input_path,
        "-o", output_path,
        "-m", model_path,
        "--temperature", str(temperature),
        "--top_p", "1.0",
        "--top_k", "-1",
        "--tp_size", "1",
        "--dp_size", "1",
        "--max_input_sequence_length", str(max_input_sequence_length),
        "--max_running_requests", "64",
        "--max_new_tokens", str(max_new_tokens),
        "--max_sequence_length", str(max_input_sequence_length + max_new_tokens),
        "--apply_chat_template",
        "--prompt_key", "prompt",
        "--post_cleanup",
        "--print_metrics",
        "--no-resume",
    ]
    logger.info("Running inference: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return output_path


# ---------------------------------------------------------------------------
# Step 3: Score
# ---------------------------------------------------------------------------

def score_results(output_path: str) -> Dict[str, Any]:
    """Score an inference-output JSONL. Returns overall + per-operation metrics."""
    overall = evaluate_output_file(output_path)

    per_op: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"total": 0, "correct": 0, "format": 0}
    )
    with open(output_path) as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            prompt = item.get("instruction", item.get("prompt", ""))
            op = _extract_op_label(prompt) or "unknown"

            gt = item.get("ground_truth_answer", "")
            output = item.get("output", {})
            text = output.get("text", "") if isinstance(output, dict) else str(output or "")

            per_op[op]["total"] += 1
            extracted = extract_answer_from_text(text)
            if extract_boxed_answer(text) is not None or extract_answer_tags(text) is not None:
                per_op[op]["format"] += 1
            if extracted is not None and compare_answers(extracted, gt):
                per_op[op]["correct"] += 1

    per_op_summary = {}
    for op in sorted(per_op):
        d = per_op[op]
        per_op_summary[op] = {
            "total": d["total"],
            "correct": d["correct"],
            "accuracy": round(d["correct"] / d["total"] * 100, 2) if d["total"] else 0.0,
            "format_found": d["format"],
        }

    return {
        "overall": {
            "total": overall["total_lines"],
            "correct": overall["correct_lines"],
            "accuracy": round(overall["accuracy"], 2),
            "format_found": overall["format_found"],
            "format_accuracy": round(overall["format_accuracy"], 2),
        },
        "per_operation": per_op_summary,
        "errors": overall["errors"],
    }


# ---------------------------------------------------------------------------
# Display / save
# ---------------------------------------------------------------------------

def print_results(results: Dict[str, Any], elapsed: float):
    o = results["overall"]
    print()
    print("=" * 64)
    print(
        f"  Overall  —  {o['correct']}/{o['total']}  accuracy {o['accuracy']:.2f}%"
        f"  format {o['format_accuracy']:.2f}%  ({elapsed:.1f}s)"
    )
    print("=" * 64)

    per_op = results["per_operation"]
    if len(per_op) > 1 or "unknown" not in per_op:
        print(f"  {'Op':<6} {'Correct':>8} {'Total':>6} {'Acc':>8}")
        print(f"  {'-'*6} {'-'*8} {'-'*6} {'-'*8}")
        for op, d in sorted(per_op.items()):
            print(f"  {op:<6} {d['correct']:>8} {d['total']:>6} {d['accuracy']:>7.2f}%")
        print()

    errors = results["errors"]
    if errors:
        n = min(10, len(errors))
        print(f"  First {n} errors:")
        for e in errors[:n]:
            print(f"    Line {e['line']}: {e['error']}")
            if "ground_truth" in e:
                print(f"      gt:   {e['ground_truth']}")
            if "extracted" in e:
                print(f"      pred: {e['extracted']}")
        print()


def save_results(results: Dict[str, Any], output_dir: str, output_jsonl: str):
    """Save / merge eval_summary.json (keyed by test stem) and append a CSV row."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    summary_path = out / "eval_summary.json"
    entry = {k: v for k, v in results.items() if k != "errors"}
    entry["n_errors"] = len(results["errors"])
    entry["results_file"] = str(output_jsonl)
    test_key = Path(output_jsonl).stem

    existing: Dict[str, Any] = {}
    if summary_path.exists():
        try:
            with open(summary_path) as f:
                loaded = json.load(f)
            if isinstance(loaded, dict) and "overall" in loaded:
                legacy_key = Path(loaded.get("results_file", "legacy")).stem or "legacy"
                existing = {legacy_key: loaded}
            elif isinstance(loaded, dict):
                existing = loaded
        except Exception:
            existing = {}

    existing[test_key] = entry
    with open(summary_path, "w") as f:
        json.dump(existing, f, indent=2)
    logger.info("Summary → %s (key=%s, %d test sets)", summary_path, test_key, len(existing))

    csv_path = out / "eval_results.csv"
    save_result_to_csv(
        output_jsonl,
        {
            "total_lines": results["overall"]["total"],
            "correct_lines": results["overall"]["correct"],
            "accuracy": results["overall"]["accuracy"],
            "format_found": results["overall"]["format_found"],
            "format_accuracy": results["overall"]["format_accuracy"],
            "errors": results["errors"],
        },
        str(csv_path),
    )
    logger.info("CSV   → %s", csv_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Evaluate an SFT/OPSD checkpoint on a math-ops test set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--checkpoint_dir", default=None,
                   help="LoRA adapter directory (has adapter_model.safetensors)")
    p.add_argument("--test_data", required=True,
                   help="Test JSONL — messages / alpaca / inference format auto-detected")
    p.add_argument("--base_model", default=None,
                   help="Base model path (default: auto-detect from adapter_config.json)")
    p.add_argument("--merged_model_dir", default=None,
                   help="Where to save/load the merged or full-SFT model "
                        "(default: {checkpoint_dir}/merged)")
    p.add_argument("--output_dir", default=None,
                   help="Where to save results "
                        "(default: {checkpoint_dir}/eval_results or "
                        "{merged_model_dir}/eval_results)")
    p.add_argument("--skip_merge", action="store_true",
                   help="Skip LoRA merge (use existing merged or full-SFT model)")
    p.add_argument("--max_new_tokens", type=int, default=4096)
    p.add_argument("--max_input_sequence_length", type=int, default=2048)
    p.add_argument("--temperature", type=float, default=0.0)
    args = p.parse_args()

    if args.checkpoint_dir and not Path(args.checkpoint_dir).exists():
        logger.error("Checkpoint not found: %s", args.checkpoint_dir)
        sys.exit(1)
    if not Path(args.test_data).exists():
        logger.error("Test data not found: %s", args.test_data)
        sys.exit(1)
    if not INFERENCE_SCRIPT.exists():
        logger.error("Inference script not found: %s", INFERENCE_SCRIPT)
        sys.exit(1)

    ckpt = Path(args.checkpoint_dir) if args.checkpoint_dir else None

    if args.base_model is None and ckpt:
        args.base_model = read_base_model_from_adapter(str(ckpt))
        if args.base_model:
            logger.info("Auto-detected base model from adapter_config.json: %s", args.base_model)

    if args.merged_model_dir is None:
        if ckpt:
            args.merged_model_dir = str(ckpt / "merged")
        else:
            logger.error("--merged_model_dir is required when --checkpoint_dir is not set")
            sys.exit(1)

    if args.output_dir is None:
        args.output_dir = str(
            (ckpt if ckpt else Path(args.merged_model_dir)) / "eval_results"
        )

    # Use `<parent_dir>_<filename_stem>` so different test files that share a
    # base name (e.g. `test_messages.jsonl` in both `primitive_atomic_balanced_sft_50k`
    # and `primitive_atomic_balanced_new_operations`) don't overwrite each other.
    _test_path = Path(args.test_data)
    test_stem = f"{_test_path.parent.name}_{_test_path.stem}"
    output_jsonl = str(Path(args.output_dir) / f"{test_stem}_results.jsonl")

    logger.info("Checkpoint:   %s", args.checkpoint_dir)
    logger.info("Test data:    %s", args.test_data)
    logger.info("Base model:   %s", args.base_model)
    logger.info("Merged dir:   %s", args.merged_model_dir)
    logger.info("Output dir:   %s", args.output_dir)
    logger.info("Output file:  %s", output_jsonl)

    if Path(output_jsonl).exists():
        logger.info("[skip] %s already exists; re-scoring only.", output_jsonl)
        results = score_results(output_jsonl)
        print_results(results, 0.0)
        save_results(results, args.output_dir, output_jsonl)
        return

    # ── Step 1: Merge LoRA (or use existing merged/full-SFT dir) ───────
    if args.skip_merge:
        if not Path(args.merged_model_dir).exists():
            logger.error("--skip_merge but merged model not found: %s", args.merged_model_dir)
            sys.exit(1)
        logger.info("Skipping merge — reusing: %s", args.merged_model_dir)
        merged = args.merged_model_dir
    else:
        if not args.base_model:
            logger.error("Cannot merge: base model unknown. Pass --base_model.")
            sys.exit(1)
        merged = merge_lora(args.base_model, str(ckpt), args.merged_model_dir)

    # ── Step 2: Convert test data → inference format if needed ─────────
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    with open(args.test_data) as f:
        first = json.loads(f.readline())
    fmt = _detect_format(first)
    if fmt == "inference":
        inference_input = args.test_data
    else:
        converted_path = str(Path(args.output_dir) / f"{test_stem}_converted.jsonl")
        logger.info("Converting %s → inference format: %s", fmt, converted_path)
        convert_to_inference_format(args.test_data, converted_path, fmt=fmt)
        inference_input = converted_path

    # ── Step 3: Inference ──────────────────────────────────────────────
    t0 = time.time()
    run_inference(
        model_path=merged,
        input_path=inference_input,
        output_path=output_jsonl,
        max_new_tokens=args.max_new_tokens,
        max_input_sequence_length=args.max_input_sequence_length,
        temperature=args.temperature,
    )
    elapsed = time.time() - t0

    # ── Step 4: Score ──────────────────────────────────────────────────
    results = score_results(output_jsonl)
    print_results(results, elapsed)
    save_results(results, args.output_dir, output_jsonl)
    print(f"Results saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
