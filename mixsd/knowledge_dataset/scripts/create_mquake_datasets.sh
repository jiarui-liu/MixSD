#!/bin/bash
# Generate MQuAKE SFT datasets in the same layout as the synthetic knowledge
# dataset. Output files are unprefixed and land in their own data root
# (…/knowledge_d${NUM_DOMAINS}_e${NUM_ENTITIES}_mquake/).
#
# Layout (see generate_from_mquake.py):
#   atomic_sft/
#     train_messages.jsonl              — SFT/OPSD training targets
#     val_paraphrased_messages.jsonl / val_paraphrased_inference.jsonl
#     test_subset_of_train_inference.jsonl  — memorisation eval on train facts
#   atomic_with_context_cot/
#     test_alpaca.jsonl                 — HELD-OUT facts (disjoint from train)
#                                          with held-out-only distractor context
#   compositional_{2,3,4}step_sft/
#     test_alpaca.jsonl / test_messages.jsonl
#
# Unused alpaca variants (atomic train_alpaca / test_subset_of_train_alpaca) are
# no longer written.

BASE_DIR="/path/to/MixSD"
OUTPUT_DIR="/path/to/mixsd_data/mixsd/data/knowledge"

# Must match the values used in create_sft_datasets.sh so the suffix aligns.
NUM_DOMAINS=5
NUM_ENTITIES=10

# Scale: cap total unique atomic facts injected.
# Cases are selected greedily (most fact-reuse first) so 2/3/4-step files
# always share the same fact pool.  Leave empty to use all ~8594 facts.
# Example: MAX_FACTS="--max_facts 100"
MAX_FACTS="--max_facts 100"

# Held-out fact budget for atomic_with_context_cot (disjoint from train).
# Set EVAL_MAX_FACTS="--eval_max_facts 0" to skip building the held-out set.
EVAL_MAX_FACTS="--eval_max_facts 100"

export PYTHONHASHSEED=0

cd "$BASE_DIR"

DATA_ROOT="${OUTPUT_DIR}_d${NUM_DOMAINS}_e${NUM_ENTITIES}_mquake"

python -m mixsd.knowledge_dataset.mquake_same_format.generate_from_mquake \
    --data_root "$DATA_ROOT" \
    --seed 42 \
    ${MAX_FACTS} \
    ${EVAL_MAX_FACTS}
