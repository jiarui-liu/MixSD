#!/bin/bash
# Generate all math-operation datasets in knowledge_dataset format.
#
# Op A (`digit_sum_max_product`) is excluded by default — the strong base
# models reliably infer it from few-shot, so it isn't a useful test of the
# OPSD pipeline. Datasets use 7 ops (B–H).
#
# Output layout under ${OUTPUT_DIR}:
#   primitive_atomic_balanced_sft_50k/
#     train_messages.jsonl   (43750 records)
#     test_messages.jsonl    (175 records)
#   primitive_compositional_sft_n_steps_2/
#     op_{B..H}_test_messages.jsonl
#   primitive_atomic_balanced_new_operations/
#     test_messages.jsonl
#   compositional_sft_n_steps_2/
#     test_messages.jsonl

set -euo pipefail

BASE_DIR="/path/to/MixSD"
OUTPUT_DIR="/path/to/mixsd_data/mixsd/data/math_operations"

# Reproducible iteration order for any set/dict-driven sampling.
export PYTHONHASHSEED=0

cd "$BASE_DIR"

python -m mixsd.math_operation_dataset.generate_datasets \
    --output_dir "$OUTPUT_DIR" \
    "$@"
