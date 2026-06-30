#!/usr/bin/env python3
"""OPSD entry point for math operations.

On-Policy Self-Distillation:
  - Single frozen teacher = same model as the student (separate copy).
  - The teacher receives the ground-truth solution + final answer in its user
    turn as guidance; the student generates on-policy.
  - KL loss direction comes from ``loss_fn.kl_type`` in the YAML config
    (default: reverse).

Shared helpers (GT-text builder factory, smart 60/40 teacher-input builder,
the training driver) live in ``opsd_common.py`` and are reused by the sibling
``knowledge_opsd`` variant — this entry point only wires the math-ops
prompt and dataset registration.

Usage:
    python run_opsd.py --config opsd_distillation_config.yaml [hydra overrides]
"""

import os

# Register custom datasets before nemo-rl internals touch the registry.
from register_dataset import register_opsd_datasets

from opsd_common import make_build_cot_gt_texts, run_opsd_training


# ------------------------------------------------------------------ #
#  Math-ops GT-guidance prompt                                         #
# ------------------------------------------------------------------ #

_PREFIX = (
    "\nHere is a reference solution to this problem, "
    "including the correct final answer:\n"
)
_TRANSITION = (
    "\nAfter understanding the reference solution, "
    "please attempt to answer the question again:\n"
    "Please reason step by step, and put your final answer within \\boxed{{}}"
)

_build_cot_gt_texts_math_ops = make_build_cot_gt_texts(_PREFIX, _TRANSITION)


def main() -> None:
    run_opsd_training(
        default_config_path=os.path.join(
            os.path.dirname(__file__), "opsd_distillation_config.yaml"
        ),
        register_datasets_fn=register_opsd_datasets,
        build_cot_gt_texts_fn=_build_cot_gt_texts_math_ops,
        variant_name="math-ops",
    )


if __name__ == "__main__":
    main()
