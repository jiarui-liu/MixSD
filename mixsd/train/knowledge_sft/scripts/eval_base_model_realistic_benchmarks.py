"""Evaluate a Hugging Face base model on the realistic-benchmark suite.

Thin wrapper around ``mixsd.eval.checkpoint_eval.run_checkpoint_eval``
(which accepts any HF model dir, not just trained checkpoints). See
sbatch_eval_base_model_realistic_benchmarks.sh for the canonical setup.

Usage:
    python eval_base_model_realistic_benchmarks.py \
        --model /path/to/hf_model_dir \
        --output-dir /path/to/eval_output \
        [--datasets aime2024 math500 ...] \
        [--tp 1]
"""

import argparse
import json
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, PROJECT_DIR)

from mixsd.eval.checkpoint_eval import run_checkpoint_eval


def _done_datasets(output_dir: str) -> set:
    """Datasets already present in <output_dir>/summary.json (empty set if none)."""
    summary_path = os.path.join(output_dir, "summary.json")
    if not os.path.exists(summary_path):
        return set()
    try:
        with open(summary_path) as f:
            data = json.load(f)
        return set(data) if isinstance(data, dict) else set()
    except Exception:
        return set()


def _is_llama_model(model_dir: str) -> bool:
    """True if the HF model dir reports a Llama-family architecture (Meta-style evals use greedy)."""
    cfg_path = os.path.join(model_dir, "config.json")
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except Exception:
        return False
    if cfg.get("model_type") == "llama":
        return True
    archs = cfg.get("architectures") or []
    return any("llama" in a.lower() for a in archs)

ALL_DATASETS = [
    "aime2024",
    # "aime2025",
    "math500",
    # "minerva_math",
    # "olympiadbench",
    # "livecodebench_v6",
    # "deepmath15k_test",
    "gsm8k_test",
    "humaneval",
    "mmlu",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True,
        help="Path to a Hugging Face model dir (config.json + weights + tokenizer).",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Where to write per-dataset predictions and summary.json.",
    )
    parser.add_argument("--tp", type=int, default=1)
    parser.add_argument(
        "--datasets", nargs="+", default=ALL_DATASETS,
        help="Datasets to evaluate on. Default: all uncommented in ALL_DATASETS.",
    )
    args = parser.parse_args()

    done = _done_datasets(args.output_dir)
    missing = [d for d in args.datasets if d not in done]
    print(f"[filter] output_dir = {args.output_dir}")
    print(f"[filter] already done : {sorted(done)}")
    print(f"[filter] will evaluate: {missing}")
    if not missing:
        print("[filter] nothing to do, exiting")
        return

    temperature = 0.0 if _is_llama_model(args.model) else 1.0
    print(f"[temperature] {temperature} (llama detected: {temperature == 0.0})")

    run_checkpoint_eval(
        checkpoint_path=args.model,
        output_dir=args.output_dir,
        datasets=missing,
        num_tests_per_prompt={"aime2024": 16, "aime2025": 16},
        temperature=temperature,
        tensor_parallel_size=args.tp,
    )


if __name__ == "__main__":
    main()
