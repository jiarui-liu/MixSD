#!/usr/bin/env python3
"""SFT entry point for the simpleqa_opsd dataset using nemo-rl's built-in SFT.

Pure SFT on the dataset's ground-truth assistant turn — no rollout, no teacher
generation, no top-k. Trains the student via NLL on the GT label that's already
in train_messages.jsonl.

Apples-to-apples counterpart to
  scripts/sbatch_offpsd_simpleqa_nll_gt_qwen3_*_n1_t0_*.sh
which does NLL on a base-model+GT-context greedy rollout. Same nemo-rl
framework, same model / optimizer / scheduler / batch / seq length — only the
supervision source changes (dataset GT vs base-model greedy rollout).

Usage:
    python run_sft.py --config sft_config.yaml [overrides...]
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from _opsd_sft_runner import run
from register_dataset import register_opsd_datasets


if __name__ == "__main__":
    run(register_opsd_datasets)
