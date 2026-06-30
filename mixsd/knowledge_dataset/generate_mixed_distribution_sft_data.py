"""Mixture-Distribution Sampling SFT data generation — knowledge variant.

Thin wrapper that wires the knowledge OPSD ``knowledge_base_answer`` GT-guidance
prompt into the shared ``mixsd.mix_distribution_sampling`` core. The
guidance block matches what
``sbatch_opsd_knowledge_forward_kl_gt_d5_e10_20260422.sh`` injects into the
teacher's user turn.

Usage example (defaults: lambda=0.5, T=0, n=1, topk=64, max_retries=100,
extract_mode=boxed):
    python generate_mixed_distribution_sft_data.py \\
        --model Qwen/Qwen3-4B-Instruct-2507 \\
        --tensor_parallel_size 1
"""

from __future__ import annotations

import os
import sys

# Make the project root importable so this file works under either
# `python generate_mixed_distribution_sft_data.py` or
# `python -m mixsd.knowledge_dataset.generate_mixed_distribution_sft_data`.
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mixsd.mix_distribution_sampling import (  # noqa: E402
    build_arg_parser,
    run_generation,
)


# OPSD knowledge_base_answer prompt variant — matches
# mixsd/train/knowledge_opsd/run_opsd.py defaults.
GT_PREFIX = (
    "\nThis question is from a new knowledge base. "
    "Here is the answer to this question:\n"
)
GT_TRANSITION = "\nNow answer the question within \\boxed{}"


_DEFAULT_INPUT = (
    "/path/to/mixsd_data/mixsd/data/"
    "knowledge_d5_e10/atomic_sft/train_messages.jsonl"
)
_DEFAULT_OUTPUT_DIR = (
    "/path/to/mixsd_data/mixsd/data/"
    "knowledge_d5_e10/atomic_sft"
)


def main() -> None:
    ap = build_arg_parser(
        default_input=_DEFAULT_INPUT,
        default_output_dir=_DEFAULT_OUTPUT_DIR,
        default_extract_mode="boxed",
    )
    args = ap.parse_args()
    run_generation(args, GT_PREFIX, GT_TRANSITION)


if __name__ == "__main__":
    main()
