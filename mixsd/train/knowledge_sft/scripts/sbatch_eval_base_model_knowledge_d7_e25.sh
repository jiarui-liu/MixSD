#!/bin/bash
# Evaluate a Hugging Face base model (no fine-tune) on the 5 knowledge_d7_e25
# test sets. Counterpart to sbatch_eval_base_model_knowledge.sh (d5_e10).
#
# Test sets (same five subdirs/file stems as d5_e10, but the d7_e25 splits
# are larger — ~520 items per test):
#   - Atomic in-distribution                    (atomic_sft/test_subset_of_train)
#   - Atomic paraphrased                        (atomic_sft/val_paraphrased)
#   - Compositional 2-step                      (compositional_2step_sft/test_alpaca)
#   - Atomic with-context CoT                   (atomic_with_context_cot/test_alpaca)
#   - Compositional 2-step with-context CoT     (compositional_2step_with_context_cot/test_alpaca)
#
# Per-test (max_new_tokens, max_input_sequence_length) match the dispatcher
# `sbatch_eval_knowledge_d5_e10_opsd_and_sft_20260416.sh` (which is reused by
# the d7_e25 fine-tuned-checkpoint eval orchestrator), so base-model numbers
# are apples-to-apples with the fine-tuned d7_e25 numbers.
#
# Outputs go to ${OUTPUT_DIR}/<subdir>/<stem>_results.jsonl, mirroring the
# layout used for trained checkpoints' eval_results/ dir. The default
# OUTPUT_DIR is the new top-level folder eval_knowledge_d7_e25_results/, kept
# separate from eval_results/ (which holds the d5_e10 base-model results).
#
# Usage:
#   sbatch sbatch_eval_base_model_knowledge_d7_e25.sh
#   BASE_MODEL=/path/to/HF/model sbatch sbatch_eval_base_model_knowledge_d7_e25.sh
#   BASE_MODEL=meta-llama/Llama-3.2-1B-Instruct sbatch sbatch_eval_base_model_knowledge_d7_e25.sh
#   OUTPUT_DIR=/custom/dir sbatch sbatch_eval_base_model_knowledge_d7_e25.sh

#SBATCH --job-name=eval-base-knowledge-d7e25
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=80G
#SBATCH --time=12:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_%x_%j.err

set -euxo pipefail

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
source "$CONDA_SH"
conda activate opsd

# --- Project paths ---
PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
DATA_ROOT="${DATA_ROOT:-${BASE_DATA_DIR}/data/knowledge_d7_e25}"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_TOKEN="${HF_TOKEN:-}"
export TMPDIR="/path/to/tmp"
mkdir -p "$TMPDIR"

# ---- Inputs (overridable via env) ----
BASE_MODEL="${BASE_MODEL:-/path/to/data/models/Qwen/Qwen3-4B-Instruct-2507}"
OUTPUT_DIR="${OUTPUT_DIR:-${BASE_DATA_DIR}/eval_knowledge_d7_e25_results/base_model/$(basename "$BASE_MODEL")}"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_sft.py"

echo "=========================================="
echo "Eval: knowledge tests (base model, d7_e25)"
echo "Model:  ${BASE_MODEL}"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"

run_eval_one_test() {
    local SUBDIR="$1"
    local TEST_DATA="$2"
    local MAX_NEW="$3"
    local MAX_IN="$4"

    local STEM
    STEM="$(basename "$TEST_DATA" .jsonl)"
    local OUT_JSONL="${OUTPUT_DIR}/${SUBDIR}/${STEM}_results.jsonl"
    if [ -f "$OUT_JSONL" ]; then
        echo "[skip] ${SUBDIR}/${STEM} already evaluated → ${OUT_JSONL}"
        return 0
    fi

    mkdir -p "${OUTPUT_DIR}/${SUBDIR}"
    python "$EVAL_SCRIPT" \
        --merged_model_dir "$BASE_MODEL" \
        --base_model "$BASE_MODEL" \
        --test_data "$TEST_DATA" \
        --output_dir "${OUTPUT_DIR}/${SUBDIR}" \
        --skip_merge \
        --max_new_tokens "$MAX_NEW" \
        --max_input_sequence_length "$MAX_IN" \
        --temperature 0.0
}

# 1. Atomic test_subset_of_train (in-distribution memorization)
run_eval_one_test atomic \
    "${DATA_ROOT}/atomic_sft/test_subset_of_train_inference.jsonl" 4096 512
# 2. Atomic val_paraphrased (paraphrased robustness)
run_eval_one_test atomic \
    "${DATA_ROOT}/atomic_sft/val_paraphrased_inference.jsonl" 4096 512
# 3. Compositional 2-step test (OOD generalization)
run_eval_one_test compositional_2step \
    "${DATA_ROOT}/compositional_2step_sft/test_alpaca.jsonl" 4096 1024
# 4. Atomic with-context CoT test (retrieval-from-context)
run_eval_one_test atomic_with_context_cot \
    "${DATA_ROOT}/atomic_with_context_cot/test_alpaca.jsonl" 4096 1024
# 5. Compositional 2-step with-context CoT test (multi-hop retrieval+reasoning)
run_eval_one_test compositional_2step_with_context_cot \
    "${DATA_ROOT}/compositional_2step_with_context_cot/test_alpaca.jsonl" 4096 2048

echo "Evaluation complete."
