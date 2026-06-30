#!/usr/bin/env python3
"""OPSD entry point for SimpleQA.

On-Policy Self-Distillation:
  - Single frozen teacher = same model as the student (separate copy).
  - The teacher receives the ground-truth answer in its user turn as guidance;
    the student generates on-policy.
  - KL loss direction comes from ``loss_fn.kl_type`` in the YAML config
    (default: reverse).

Shared helpers (GT-text builder factory, smart 60/40 teacher-input builder,
the training driver) live in ``math_operations_opsd.opsd_common`` and are
reused here — this entry point only wires the simpleqa prompt and dataset
registration.

Usage:
    python run_opsd.py --config opsd_distillation_config.yaml [hydra overrides]
"""

import os
import sys

# Register custom datasets before nemo-rl internals touch the registry.
# Import this BEFORE adding math_operations_opsd to sys.path — both directories
# define a `register_dataset.py` module, so prepending math_operations_opsd
# would shadow the simpleqa-specific one (silent bug: registers `math_ops_opsd`
# instead of `simpleqa_opsd`).
from register_dataset import register_opsd_datasets

# Reuse the shared OPSD training driver and helpers from math_operations_opsd.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "math_operations_opsd")
    ),
)

from opsd_common import make_build_cot_gt_texts, run_opsd_training


# ------------------------------------------------------------------ #
#  SimpleQA GT-guidance prompt                                        #
# ------------------------------------------------------------------ #

_PREFIX = (
    "\nHere is a reference solution to this problem, "
    "including the correct final answer:\n"
)
_TRANSITION = (
    "\nAfter understanding the reference solution, "
    "please attempt to answer the question again:\n"
    "Please reason step by step, and put your final answer within \\boxed{}"
)

_build_cot_gt_texts_simpleqa = make_build_cot_gt_texts(_PREFIX, _TRANSITION)


def main() -> None:
    run_opsd_training(
        default_config_path=os.path.join(
            os.path.dirname(__file__), "opsd_distillation_config.yaml"
        ),
        register_datasets_fn=register_opsd_datasets,
        build_cot_gt_texts_fn=_build_cot_gt_texts_simpleqa,
        variant_name="simpleqa",
    )


if __name__ == "__main__":
    main()
