"""Mixture-Distribution Sampling SFT data generation — math-operations variant.

Thin wrapper that wires the math_operations OPSD GT-guidance prompt into the
shared ``mixsd.mix_distribution_sampling`` core. The guidance block
matches what ``mixsd/train/math_operations_opsd/run_opsd.py`` injects
into the teacher's user turn (used by all
``sbatch_opsd_math_ops_forward_kl_gt_*.sh`` jobs).

Defaults: lambda=0.5, T=0, n=1, topk=64, max_retries=100,
extract_mode=boxed_or_last_number (the model is trained to wrap the answer in
``\\boxed{}`` but we also accept the trailing integer if it forgets).

Usage example:
    python generate_mixed_distribution_sft_data.py \\
        --model Qwen/Qwen3-4B-Instruct-2507 \\
        --tensor_parallel_size 1 \\
        --limit 1000
"""

from __future__ import annotations

import os
import sys

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mixsd.mix_distribution_sampling import (  # noqa: E402
    build_arg_parser,
    run_generation,
)


# Math-ops GT-guidance prompt — matches
# mixsd/train/math_operations_opsd/run_opsd.py.
GT_PREFIX = (
    "\nHere is a reference solution to this problem, "
    "including the correct final answer:\n"
)
GT_TRANSITION = (
    "\nAfter understanding the reference solution, "
    "please attempt to answer the question again:\n"
    "Please reason step by step, and put your final answer within \\boxed{}"
)


_DEFAULT_INPUT = (
    "/path/to/mixsd_data/mixsd/data/"
    "math_operations/primitive_atomic_balanced_sft_50k/train_messages.jsonl"
)
_DEFAULT_OUTPUT_DIR = (
    "/path/to/mixsd_data/mixsd/data/"
    "math_operations/primitive_atomic_balanced_sft_50k"
)


def main() -> None:
    ap = build_arg_parser(
        default_input=_DEFAULT_INPUT,
        default_output_dir=_DEFAULT_OUTPUT_DIR,
        # Math answers are integers; fall back to the last numeric token if
        # the model forgets to wrap the answer in \\boxed{}.
        default_extract_mode="boxed_or_last_number",
    )
    args = ap.parse_args()
    run_generation(args, GT_PREFIX, GT_TRANSITION)


if __name__ == "__main__":
    main()
