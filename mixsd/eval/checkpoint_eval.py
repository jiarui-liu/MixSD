"""Evaluate full-finetune OPSD / SFT checkpoints on math benchmarks.

Workflow:
1. Load a ready Hugging Face checkpoint with vLLM and generate responses
2. Evaluate with math verification
3. Save predictions and metrics

Caller is responsible for giving a checkpoint dir that already has
config.json + model*.safetensors + tokenizer files (for OPSD runs, that is
step_N/policy/weights/model/consolidated/ produced by offline_hf_consolidation.py;
for SFT, it is the checkpoint-N/ dir itself).
"""

import json
import os
import time
from pathlib import Path

from mixsd.eval.humaneval import (
    build_humaneval_prompt as _build_humaneval_prompt,
    check_humaneval_answer as _check_humaneval_answer,
)
from mixsd.eval.mmlu import (
    build_mmlu_prompt as _build_mmlu_prompt,
    check_mmlu_answer as _check_mmlu_answer,
)


def run_checkpoint_eval(
    checkpoint_path: str,
    output_dir: str,
    datasets: list[str] = None,
    num_tests_per_prompt: "int | dict[str, int]" = 1,
    max_new_tokens: int = 16384,
    temperature: float = 0.0,
    top_p: float = 1.0,
    top_k: int = -1,
    min_p: float = 0.0,
    gpu_memory_utilization: float = 0.9,
    tensor_parallel_size: int = 1,
    max_model_len: int = 16384,
) -> dict:
    """Evaluate a Hugging Face checkpoint on math benchmarks.

    Parameters
    ----------
    checkpoint_path : str
        Path to a ready HF model dir (config.json + weights + tokenizer).
    output_dir : str
        Directory to save results.
    datasets : list[str]
        Dataset names: 'aime2024', 'aime2025', 'math500', 'minerva_math',
        'olympiadbench', 'livecodebench_v6', 'deepmath15k_test', 'deepmath15k_val'.
    """
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer

    if datasets is None:
        datasets = ["aime2024", "deepmath15k_test"]

    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'=' * 70}")
    print(f"  CHECKPOINT EVALUATION")
    print(f"{'=' * 70}")
    print(f"  Checkpoint:    {checkpoint_path}")
    print(f"  Datasets:      {datasets}")
    print(f"  Sampling:      temp={temperature}, top_p={top_p}, top_k={top_k}, min_p={min_p}")
    print(f"{'=' * 70}\n", flush=True)

    print("Loading vLLM engine...", flush=True)
    # Defensive fix: axolotl writes tokenizer_config.json's `extra_special_tokens`
    # as a list, but transformers' loader does .keys() on it (expects a dict).
    # Drop the field if it's a list so AutoTokenizer doesn't crash.
    _tok_cfg = Path(checkpoint_path) / "tokenizer_config.json"
    if _tok_cfg.exists():
        try:
            _tc = json.loads(_tok_cfg.read_text())
            _changed = False
            if isinstance(_tc.get("extra_special_tokens"), list):
                del _tc["extra_special_tokens"]
                _changed = True
            if _tc.get("tokenizer_class") == "TokenizersBackend":
                del _tc["tokenizer_class"]
                _changed = True
            if _changed:
                _tok_cfg.write_text(json.dumps(_tc, indent=2))
        except Exception:
            pass
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    llm = LLM(
        model=checkpoint_path,
        gpu_memory_utilization=gpu_memory_utilization,
        tensor_parallel_size=tensor_parallel_size,
        max_model_len=max_model_len,
        trust_remote_code=True,
        seed=42,
    )

    # Per-dataset max_tokens: MMLU is a classification-style eval where the
    # answer is one letter in `\boxed{}`; capping generation avoids hours of
    # unused CoT rambling on 14k questions.
    per_dataset_max_tokens = {
        "mmlu": 1024,
    }
    def _make_sampling(dataset_name: str):
        return SamplingParams(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            min_p=min_p,
            max_tokens=per_dataset_max_tokens.get(dataset_name, max_new_tokens),
        )

    # Start from any existing summary so datasets we don't re-run are preserved.
    summary_path = os.path.join(output_dir, "summary.json")
    if os.path.exists(summary_path):
        try:
            with open(summary_path) as f:
                all_summary = json.load(f)
            if not isinstance(all_summary, dict):
                all_summary = {}
        except Exception:
            all_summary = {}
    else:
        all_summary = {}

    for dataset_name in datasets:
        if isinstance(num_tests_per_prompt, dict):
            k = num_tests_per_prompt.get(dataset_name, 1)
        else:
            k = num_tests_per_prompt

        print(f"\n{'─' * 50}")
        print(f"  Evaluating on: {dataset_name} (n={k})")
        print(f"{'─' * 50}", flush=True)

        # Load dataset
        examples = _load_dataset(dataset_name)
        print(f"  Loaded {len(examples)} examples", flush=True)

        # Determine eval type (code vs math)
        eval_type = examples[0].get("eval_type", "math") if examples else "math"

        # Build prompts (with enable_thinking=False for Qwen3)
        if eval_type == "code":
            prompts = [_build_code_prompt(ex, tokenizer) for ex in examples]
        elif eval_type == "humaneval":
            prompts = [_build_humaneval_prompt(ex, tokenizer) for ex in examples]
        elif eval_type == "mmlu":
            prompts = [_build_mmlu_prompt(ex, tokenizer) for ex in examples]
        else:
            prompts = [_build_prompt(ex["problem"], tokenizer) for ex in examples]

        # Replicate for multiple samples
        if k > 1:
            prompts = [p for p in prompts for _ in range(k)]
            examples_expanded = [e for e in examples for _ in range(k)]
        else:
            examples_expanded = examples

        # Generate (dataset-specific max_tokens)
        sp = _make_sampling(dataset_name)
        start_time = time.time()
        outputs = llm.generate(prompts, sp)
        elapsed = time.time() - start_time

        # Evaluate
        results = []
        for ex, output in zip(examples_expanded, outputs):
            response = output.outputs[0].text
            if eval_type == "code":
                correct = _check_code_answer(
                    response, ex["answer"], ex.get("starter_code", ""),
                )
            elif eval_type == "humaneval":
                correct = _check_humaneval_answer(response, ex["answer"])
            elif eval_type == "mmlu":
                correct = _check_mmlu_answer(response, ex["answer"])
            elif eval_type == "olympiad":
                correct = _check_olympiad_answer(response, ex["answer"])
            else:
                correct = _check_answer(response, ex["answer"])
            display_answer = ex["answer"]
            if eval_type == "code":
                display_answer = "(test cases)"
            elif eval_type == "humaneval":
                display_answer = f"(check({ex['answer']['entry_point']}))"
            elif eval_type == "olympiad":
                display_answer = ", ".join(ex["answer"])
            results.append({
                "problem": ex["problem"],
                "answer": display_answer,
                "source": ex.get("source", dataset_name),
                "response": response,
                "correct": correct,
            })

        # Metrics
        total = len(results)
        n_correct = sum(r["correct"] for r in results)
        accuracy = n_correct / total if total > 0 else 0.0

        print(f"  Accuracy: {accuracy:.4f} ({n_correct}/{total})")
        print(f"  Time: {elapsed:.1f}s", flush=True)

        # Save predictions
        pred_file = os.path.join(output_dir, f"predictions_{dataset_name}.jsonl")
        with open(pred_file, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
        print(f"  Saved to {pred_file}", flush=True)

        all_summary[dataset_name] = {
            "accuracy": accuracy,
            "correct": n_correct,
            "total": total,
            "num_tests_per_prompt": k,
        }

    # Save merged summary (existing entries for datasets we didn't re-run are kept).
    with open(summary_path, "w") as f:
        json.dump(all_summary, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  EVALUATION SUMMARY")
    print(f"{'=' * 70}")
    for ds, m in all_summary.items():
        print(f"  {ds}: {m['accuracy']:.4f} ({m['correct']}/{m['total']})")
    print(f"  Saved to: {summary_path}")
    print(f"{'=' * 70}\n", flush=True)

    return all_summary




# ------------------------------------------------------------------ #
#  Dataset loading                                                     #
# ------------------------------------------------------------------ #

def _load_dataset(name: str) -> list[dict]:
    """Load a test dataset. Returns list of {problem, answer, source, ...}.

    Math datasets return {problem, answer, source}.
    Code datasets additionally return {eval_type: "code", starter_code, ...}.
    """
    if name == "aime2024":
        from datasets import load_dataset
        ds = load_dataset("HuggingFaceH4/aime_2024", split="train")
        return [{"problem": r["problem"], "answer": str(r["answer"]), "source": "AIME2024"} for r in ds]
    elif name == "aime2025":
        return _load_aime2025()
    elif name == "math500":
        return _load_math500()
    elif name == "minerva_math":
        return _load_minerva_math()
    elif name == "olympiadbench":
        return _load_olympiadbench()
    elif name == "livecodebench_v6":
        return _load_livecodebench_v6()
    elif name == "deepmath15k_test":
        return _load_deepmath("test")
    elif name == "deepmath15k_val":
        return _load_deepmath("val")
    elif name == "deepmath15k_train":
        return _load_deepmath("train")
    elif name == "gsm8k_test":
        return _load_gsm8k()
    elif name == "humaneval":
        from mixsd.eval.humaneval import load_humaneval
        return load_humaneval()
    elif name == "mmlu":
        from mixsd.eval.mmlu import load_mmlu
        return load_mmlu()
    else:
        raise ValueError(
            f"Unknown dataset: {name}. Supported: aime2024, aime2025, math500, "
            f"minerva_math, olympiadbench, livecodebench_v6, deepmath15k_test, "
            f"deepmath15k_val, deepmath15k_train, gsm8k_test, humaneval, mmlu"
        )


def _load_deepmath(split: str) -> list[dict]:
    data_dir = Path(os.environ.get(
        "DEEPMATH_15K_DIR",
        "/path/to/data"
        "/datasets/deepmath_103k/dm_15k",
    ))
    jsonl_path = data_dir / f"{split}.jsonl"
    examples = []
    with open(jsonl_path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("final_answer"):
                examples.append({
                    "problem": d["question"],
                    "answer": str(d["final_answer"]),
                    "source": f"DeepMath15K_{split}",
                })
    return examples


def _load_gsm8k() -> list[dict]:
    """GSM8K test split (1319 grade-school math word problems).

    Source dataset and gold-answer extraction follow huggingface/Math-Verify's
    gsm8k task config: `openai/gsm8k` (subset `main`, split `test`), with the
    gold answer parsed from the `#### <number>` suffix of the `answer` field.
    """
    from datasets import load_dataset
    ds = load_dataset("openai/gsm8k", "main", split="test")
    examples = []
    for r in ds:
        if not r["question"].strip():
            continue
        gold = r["answer"].split("####")[-1].strip()
        examples.append({
            "problem": r["question"],
            "answer": gold,
            "source": "GSM8K",
        })
    return examples


def _load_aime2025() -> list[dict]:
    """AIME 2025 (30 problems: AIME I + II)."""
    from datasets import concatenate_datasets, load_dataset
    ds0 = load_dataset("opencompass/AIME2025", "AIME2025-I", split="test")
    ds1 = load_dataset("opencompass/AIME2025", "AIME2025-II", split="test")
    ds = concatenate_datasets([ds0, ds1])
    return [{"problem": r["question"], "answer": str(r["answer"]), "source": "AIME2025"} for r in ds]


def _load_math500() -> list[dict]:
    """MATH-500 (500-problem subset of MATH benchmark)."""
    from datasets import load_dataset
    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    return [{"problem": r["problem"], "answer": str(r["answer"]), "source": "MATH-500"} for r in ds]


def _load_minerva_math() -> list[dict]:
    """Minerva Math (272 problems from Lewkowycz et al., 2022)."""
    from datasets import load_dataset
    ds = load_dataset("math-ai/minervamath", split="test")
    return [{"problem": r["question"], "answer": str(r["answer"]), "source": "MinervaMath"} for r in ds]


def _load_olympiadbench() -> list[dict]:
    """OlympiadBench text-only (674 olympiad-level math/physics problems)."""
    from datasets import load_dataset
    ds = load_dataset("math-ai/olympiadbench", split="test")
    examples = []
    for r in ds:
        fa = r["final_answer"]
        # Keep answer as list for proper multi-answer evaluation
        if isinstance(fa, list):
            answer_list = [str(a) for a in fa]
        else:
            answer_list = [str(fa)]
        examples.append({
            "problem": r["question"],
            "answer": answer_list,
            "source": "OlympiadBench",
            "eval_type": "olympiad",
        })
    return examples


def _load_livecodebench_v6() -> list[dict]:
    """LiveCodeBench v6 code generation (lite version with pruned test cases)."""
    from datasets import load_dataset
    ds = load_dataset(
        "json",
        data_files="hf://datasets/livecodebench/code_generation_lite/test6.jsonl",
        split="train",
    )
    examples = []
    for r in ds:
        examples.append({
            "problem": r["question_content"],
            "answer": r.get("private_test_cases") or r.get("public_test_cases", "[]"),
            "source": "LiveCodeBench_v6",
            "eval_type": "code",
            "starter_code": r.get("starter_code") or "",
        })
    return examples


# ------------------------------------------------------------------ #
#  Prompt building and answer checking                                 #
# ------------------------------------------------------------------ #

PROMPT_TEMPLATE = (
    "Think step-by-step to solve the following problem. "
    "Output your answer inside of \\boxed{{}} tags.:\n"
    "{problem}\n\n"
    "Let's think step-by-step"
)


def _build_prompt(problem: str, tokenizer) -> str:
    messages = [{
        "role": "user",
        "content": PROMPT_TEMPLATE.format(problem=problem),
    }]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False,
    )


CODE_PROMPT_TEMPLATE = (
    "{problem}\n\n"
    "{starter_code_section}"
    "Please write a complete Python solution. Read input from stdin and "
    "write output to stdout. Wrap your final code in ```python ... ``` blocks."
)


def _build_code_prompt(example: dict, tokenizer) -> str:
    starter = example.get("starter_code", "")
    starter_section = f"Starter code:\n```python\n{starter}\n```\n\n" if starter else ""
    content = CODE_PROMPT_TEMPLATE.format(
        problem=example["problem"],
        starter_code_section=starter_section,
    )
    messages = [{"role": "user", "content": content}]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False,
    )


def _extract_code(response: str) -> str:
    """Extract Python code from markdown code blocks.

    Uses the same approach as VERL's LiveCodeBench evaluation:
    split on ```python, take the last block, split on ```.
    """
    # Strip thinking tags if present (Qwen3 thinking mode)
    if "</think>" in response:
        response = response.split("</think>", 1)[1]
    # Match VERL's extraction: last ```python ... ``` block
    if "```python" in response:
        return response.split("```python")[-1].split("```")[0].strip()
    # Fallback: last ``` block
    if "```" in response:
        parts = response.split("```")
        if len(parts) >= 3:
            return parts[-2].strip()
    return ""


def _check_code_answer(
    response: str, test_cases_raw: str, starter_code: str = "",
) -> bool:
    """Check code correctness using multiprocessing sandbox.

    Follows the same evaluation approach as VERL/LiveCodeBench:
    1. Extract code from ```python blocks
    2. Parse test cases (JSON or compressed pickle)
    3. Run in a separate process with timeout via run_test
    4. All test cases must pass for True

    The test case format is {"inputs": [...], "outputs": [...], "fn_name": ...}
    matching the LiveCodeBench/APPS standard.
    """
    import base64
    import multiprocessing
    import pickle
    import zlib

    code = _extract_code(response)
    if not code:
        return False

    # Parse test cases -- may be JSON or compressed pickle (LiveCodeBench format)
    try:
        in_outs = json.loads(test_cases_raw)
    except (json.JSONDecodeError, TypeError):
        try:
            in_outs = json.loads(
                pickle.loads(zlib.decompress(base64.b64decode(test_cases_raw.encode("utf-8"))))
            )
        except Exception:
            return False

    # LiveCodeBench lite format: [{"input": ..., "output": ..., "testtype": ...}, ...]
    # Convert to VERL/APPS format: {"inputs": [...], "outputs": [...], "fn_name": None}
    if isinstance(in_outs, list):
        in_outs = {
            "inputs": [tc["input"] for tc in in_outs],
            "outputs": [tc["output"] for tc in in_outs],
            "fn_name": None,
        }

    if not in_outs or "inputs" not in in_outs:
        return False

    # Basic subprocess execution for stdin/stdout problems.
    return _check_code_answer_basic(code, in_outs)


def _check_code_answer_basic(code: str, in_outs: dict) -> bool:
    """Fallback code checker using subprocess when VERL is not available.

    Handles only stdin/stdout problems (not call-based/fn_name problems).
    """
    import subprocess
    import tempfile
    from decimal import Decimal, InvalidOperation

    if in_outs.get("fn_name") is not None:
        # Call-based problems require the full testing_util; cannot handle here
        return False

    inputs = in_outs.get("inputs", [])
    outputs = in_outs.get("outputs", [])
    if not inputs or len(inputs) != len(outputs):
        return False

    # Clean if __name__ == '__main__' blocks (same as testing_util)
    import re
    code = re.sub(
        r'if\s+__name__\s*==\s*["\']__main__["\']\s*:', "if True:", code
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        code_path = f.name

    try:
        for tc_input, tc_expected in zip(inputs, outputs):
            try:
                result = subprocess.run(
                    ["python3", code_path],
                    input=str(tc_input),
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                pred_lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
                exp_lines = [l.strip() for l in str(tc_expected).strip().split("\n") if l.strip()]
                if len(pred_lines) != len(exp_lines):
                    return False
                for pred_line, exp_line in zip(pred_lines, exp_lines):
                    if pred_line == exp_line:
                        continue
                    # Decimal comparison for floating-point tolerance
                    try:
                        if Decimal(pred_line) == Decimal(exp_line):
                            continue
                    except InvalidOperation:
                        pass
                    return False
            except (subprocess.TimeoutExpired, Exception):
                return False
    finally:
        os.unlink(code_path)

    return True


def _check_olympiad_answer(response: str, answer_list: list[str]) -> bool:
    """Check OlympiadBench answers using the official OBJudge evaluation.

    OlympiadBench problems may have multiple answer components (e.g., x=3, y=5).
    The official evaluation checks each component with numerical tolerance and
    symbolic equivalence via SymPy.
    """
    import re

    # Extract the answer portion (after thinking, from boxed)
    resp = response
    if "</think>" in resp:
        resp = resp.split("</think>", 1)[1]

    # Try using the OBJudge from numinamath (official OlympiadBench evaluation)
    try:
        from mixsd.eval.numinamath_eval import OBJudge
        scorer = OBJudge()
        gt_str = ", ".join(answer_list)
        if scorer.judge(gt_str, resp, 1e-2):
            return True
    except (ImportError, Exception):
        print("Failed to import numinamath_eval")
        pass

    # Fallback: try math_verify on each answer component
    try:
        from math_verify import verify, parse
    except ImportError:
        print("Failed to import math_verify")
        return False

    # Extract boxed answers from response
    boxed = re.findall(r"\\boxed\{([^}]*)\}", resp)
    if not boxed:
        # Try math_verify on the full response against joined ground truth
        try:
            gt_boxed = "\\boxed{" + ", ".join(answer_list) + "}"
            return float(verify(parse(resp), parse(gt_boxed)))
        except Exception:
            return False

    # Single answer: compare last boxed with joined ground truth
    if len(answer_list) == 1:
        try:
            gt_boxed = "\\boxed{" + answer_list[0] + "}"
            return float(verify(parse(resp), parse(gt_boxed)))
        except Exception:
            return boxed[-1].strip() == answer_list[0].strip()

    # Multi-answer: match each ground truth element to a boxed element
    if len(boxed) < len(answer_list):
        return False
    # Take the last N boxed values to match N ground truth elements
    pred_answers = boxed[-len(answer_list):]
    for pred, gt in zip(pred_answers, answer_list):
        try:
            gt_boxed = "\\boxed{" + gt + "}"
            pred_boxed = "\\boxed{" + pred + "}"
            if not float(verify(parse(pred_boxed), parse(gt_boxed))):
                return False
        except Exception:
            if pred.strip() != gt.strip():
                return False
    return True


def _check_answer(response: str, ground_truth: str) -> bool:
    """Check answer using math_metric (same as nemo-rl MathEnvironment / OPSD).

    Delegates to the shared verify_math_answer in utils.math_verify.
    """
    from mixsd.eval.math_verify import verify_math_answer
    return verify_math_answer(response, ground_truth)
