"""Evaluate full-finetune checkpoints on a set of math benchmarks.

Eval outputs are written inside each step/checkpoint dir under
`eval_realistic_benchmarks_results/` (alongside the model weights).

For each step, the Hugging Face model dir is resolved as:
  - OPSD: <ckpt-base>/<run-name>/step_N/policy/weights/model/consolidated/
  - SFT:  <ckpt-base>/<run-name>/checkpoint-N/                      (already a HF dir)

Usage:
    python eval_realistic_benchmarks.py \
        --ckpt-base /path/to/checkpoints \
        --run-name <subdir-under-ckpt-base> \
        --step 500
    python eval_realistic_benchmarks.py ... --step all
    python eval_realistic_benchmarks.py ... --list-steps
    python eval_realistic_benchmarks.py ... --datasets aime2024 math500
"""

import argparse
import json
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, PROJECT_DIR)

from mixsd.eval.checkpoint_eval import run_checkpoint_eval

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


def _done_datasets(eval_dir: str) -> set:
    """Datasets already present in <eval_dir>/summary.json (empty set if none)."""
    summary_path = os.path.join(eval_dir, "summary.json")
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


def _resolve_hf_model_path(step_dir: str) -> str:
    """Return a ready-to-load HF model dir for this checkpoint."""
    consolidated = os.path.join(step_dir, "policy", "weights", "model", "consolidated")
    if os.path.exists(os.path.join(consolidated, "config.json")):
        return consolidated
    if os.path.exists(os.path.join(step_dir, "config.json")):
        return step_dir
    raise FileNotFoundError(
        f"No HF model found under {step_dir} or {consolidated}/"
    )


def _step_dir_for(checkpoint_root: str, step: int) -> str | None:
    """Return the concrete dir name for this step, either step_N/ (OPSD) or checkpoint-N/ (SFT)."""
    for candidate in (f"step_{step}", f"checkpoint-{step}"):
        p = os.path.join(checkpoint_root, candidate)
        if os.path.exists(p):
            return p
    return None


def get_available_steps(checkpoint_root: str):
    steps = []
    if os.path.exists(checkpoint_root):
        for d in os.listdir(checkpoint_root):
            if d.startswith("step_"):
                steps.append(int(d.split("_")[1]))
            elif d.startswith("checkpoint-"):
                steps.append(int(d.split("-")[1]))
    return sorted(steps)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ckpt-base", required=True,
        help="Directory containing <run-name>/step_*/ or <run-name>/checkpoint-*/ dirs.",
    )
    parser.add_argument(
        "--run-name", required=True,
        help="Subdir under --ckpt-base that holds step_* or checkpoint-* folders.",
    )
    parser.add_argument("--step", type=str, required=False)
    parser.add_argument("--tp", type=int, default=1)
    parser.add_argument(
        "--datasets", nargs="+", default=ALL_DATASETS,
        help="Datasets to evaluate on. Default: all.",
    )
    parser.add_argument(
        "--list-steps", action="store_true",
        help="Print available step numbers (one per line) and exit.",
    )
    parser.add_argument(
        "--list-incomplete-steps", action="store_true",
        help="Print available steps that still have at least one requested dataset missing.",
    )
    parser.add_argument(
        "--list-plan", action="store_true",
        help="Print 'step\\tmissing,datasets' for every incomplete step, then exit.",
    )
    args = parser.parse_args()

    checkpoint_root = os.path.join(args.ckpt_base, args.run_name)

    available = get_available_steps(checkpoint_root)

    if args.list_steps:
        for s in available:
            print(s)
        return

    if args.list_incomplete_steps or args.list_plan:
        for s in available:
            step_dir = _step_dir_for(checkpoint_root, s)
            if step_dir is None:
                continue
            eval_dir = os.path.join(step_dir, "eval_realistic_benchmarks_results")
            done = _done_datasets(eval_dir)
            missing = [d for d in args.datasets if d not in done]
            if not missing:
                continue
            if args.list_plan:
                print(f"{s}\t{','.join(missing)}")
            else:
                print(s)
        return

    if args.step is None:
        parser.error("--step is required unless --list-steps / --list-incomplete-steps / --list-plan is set")

    print(f"Checkpoint root: {checkpoint_root}")
    print(f"Available checkpoints: {available}")
    steps = available if args.step == "all" else [int(args.step)]

    for step in steps:
        step_dir = _step_dir_for(checkpoint_root, step)
        if step_dir is None:
            print(f"step {step} not found, skipping")
            continue

        step_output_dir = os.path.join(step_dir, "eval_realistic_benchmarks_results")
        done = _done_datasets(step_output_dir)
        missing = [d for d in args.datasets if d not in done]
        print(f"[step {step}] already done : {sorted(done)}")
        print(f"[step {step}] will evaluate: {missing}")
        if not missing:
            print(f"[step {step}] nothing to do, skipping")
            continue

        model_path = _resolve_hf_model_path(step_dir)

        temperature = 0.0 if _is_llama_model(model_path) else 1.0
        print(f"[step {step}] temperature={temperature} (llama detected: {temperature == 0.0})")

        run_checkpoint_eval(
            checkpoint_path=model_path,
            output_dir=step_output_dir,
            datasets=missing,
            num_tests_per_prompt={"aime2024": 16, "aime2025": 16},
            temperature=temperature,
            tensor_parallel_size=args.tp,
        )


if __name__ == "__main__":
    main()
