#!/bin/bash
# Generate the knowledge_d5_e10 SFT datasets + all evaluation test sets in a
# single pass. The "_d5_e10" suffix is auto-appended to --output_dir when
# --num_domains / --num_entities are set.
#
# Output structure under ${OUTPUT_DIR}_d5_e10/:
#   atomic_sft/
#     train_messages.jsonl
#     test_subset_of_train_inference.jsonl
#     val_paraphrased_messages.jsonl
#     val_paraphrased_inference.jsonl
#   compositional_2step_sft/
#     test_alpaca.jsonl            (all compositional trajectories; no train/val)
#   atomic_with_context_cot/
#     test_alpaca.jsonl
#   compositional_2step_with_context_cot/
#     test_alpaca.jsonl

BASE_DIR="/path/to/MixSD"
OUTPUT_DIR="/path/to/mixsd_data/mixsd/data/knowledge"

# Fix Python's randomized string hashing so set/dict iteration order is
# reproducible across runs (must be set BEFORE python starts).
export PYTHONHASHSEED=0

cd "$BASE_DIR"

# python -m mixsd.knowledge_dataset.generate_sft_data \
#     --output_dir "$OUTPUT_DIR" \
#     --seed 42 \
#     --num_domains 5 \
#     --num_entities 10 \
#     --num_compositional 6000 \
#     --num_compositional_test 10000 \
#     --atomic_context_size 50 \
#     --compositional_context_per_step 50


python -m mixsd.knowledge_dataset.generate_sft_data \
    --output_dir "$OUTPUT_DIR" \
    --seed 42 \
    --num_domains 7 \
    --num_entities 25 \
    --num_compositional 50000 \
    --num_compositional_test 10000 \
    --atomic_context_size 50 \
    --compositional_context_per_step 50