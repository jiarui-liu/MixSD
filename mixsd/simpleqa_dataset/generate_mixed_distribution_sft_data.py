"""Mixture-Distribution Sampling SFT data generation — SimpleQA variant.

Thin wrapper that wires the SimpleQA GT-context prompt into the shared
``mixsd.mix_distribution_sampling`` core (same code path as the
knowledge / math_operations wrappers; only the
``(PREFIX, TRANSITION)`` block injected into the teacher's user turn changes).

GT block format (appended to each training sample's user turn during teacher
rollout):

    <user question>
    This is a factual short-answer question. Here is the correct answer:
    <answer>
    Now, answer the question concisely within \\boxed{}

Usage example (defaults: lambda=0.5, T=0, n=1, topk=64, max_retries=10,
extract_mode=boxed):
    python generate_mixed_distribution_sft_data.py \\
        --model Qwen/Qwen3-4B-Instruct-2507 \\
        --tensor_parallel_size 4
"""

from __future__ import annotations

import os
import sys

# Make the project root importable so this file works under either
# `python generate_mixed_distribution_sft_data.py` or
# `python -m mixsd.simpleqa_dataset.generate_mixed_distribution_sft_data`.
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mixsd.mix_distribution_sampling import (  # noqa: E402
    build_arg_parser,
    run_generation,
)


# SimpleQA GT-context prompt — wraps the dataset's gold answer in a frame that
# tells the teacher this is a factual short-answer item, then asks for a
# concise boxed answer. Mirrors the (PREFIX, TRANSITION) split used by the
# knowledge / math_operations wrappers so the shared core stays uniform.
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
    "simpleqa/atomic_sft/train_messages.jsonl"
)
_DEFAULT_OUTPUT_DIR = (
    "/path/to/mixsd_data/mixsd/data/"
    "simpleqa/atomic_sft"
)


def main() -> None:
    ap = build_arg_parser(
        default_input=_DEFAULT_INPUT,
        default_output_dir=_DEFAULT_OUTPUT_DIR,
        default_extract_mode="boxed",
        default_max_retries=10,
    )
    args = ap.parse_args()
    run_generation(args, GT_PREFIX, GT_TRANSITION)


if __name__ == "__main__":
    main()
