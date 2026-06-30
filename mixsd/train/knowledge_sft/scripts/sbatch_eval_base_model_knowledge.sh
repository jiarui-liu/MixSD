#!/bin/bash
# Evaluate a Hugging Face base model (no fine-tune) on the 5 knowledge_d5_e10
# test sets used by the OPSD/SFT pipeline.
#
# Test sets (same as sbatch_eval_knowledge_d5_e10_opsd_and_sft_20260416.sh):
#   - Atomic in-distribution                    (atomic_sft/test_subset_of_train)
#   - Atomic paraphrased                        (atomic_sft/val_paraphrased)
#   - Compositional 2-step                      (compositional_2step_sft/test_alpaca)
#   - Atomic with-context CoT                   (atomic_with_context_cot/test_alpaca)
#   - Compositional 2-step with-context CoT     (compositional_2step_with_context_cot/test_alpaca)
#
# Outputs go to ${OUTPUT_DIR}/<subdir>/<stem>_results.jsonl, mirroring the
# layout of <step_dir>/eval_results/ for trained checkpoints.
#
# Usage:
#   sbatch sbatch_eval_base_model_knowledge.sh
#   BASE_MODEL=/path/to/HF/model sbatch sbatch_eval_base_model_knowledge.sh
#   BASE_MODEL=meta-llama/Llama-3.2-1B-Instruct sbatch sbatch_eval_base_model_knowledge.sh
#   OUTPUT_DIR=/custom/dir sbatch sbatch_eval_base_model_knowledge.sh

#SBATCH --job-name=eval-base-knowledge
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=80G
#SBATCH --time=4:00:00
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
DATA_ROOT="${DATA_ROOT:-${BASE_DATA_DIR}/data/knowledge_d5_e10}"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_TOKEN="${HF_TOKEN:-}"
export TMPDIR="/path/to/tmp"
mkdir -p "$TMPDIR"

# ---- Inputs (overridable via env) ----
BASE_MODEL="${BASE_MODEL:-/path/to/data/models/Qwen/Qwen3-4B-Instruct-2507}"
OUTPUT_DIR="${OUTPUT_DIR:-${BASE_DATA_DIR}/eval_results/base_model/$(basename "$BASE_MODEL")}"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_sft.py"

echo "=========================================="
echo "Eval: knowledge tests (base model)"
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
    "${DATA_ROOT}/atomic_sft/test_subset_of_train_inference.jsonl" 512 512
# 2. Atomic val_paraphrased (paraphrased robustness)
run_eval_one_test atomic \
    "${DATA_ROOT}/atomic_sft/val_paraphrased_inference.jsonl" 512 512
# 3. Compositional 2-step test (OOD generalization)
run_eval_one_test compositional_2step \
    "${DATA_ROOT}/compositional_2step_sft/test_alpaca.jsonl" 4096 1024
# 4. Atomic with-context CoT test (retrieval-from-context)
run_eval_one_test atomic_with_context_cot \
    "${DATA_ROOT}/atomic_with_context_cot/test_alpaca.jsonl" 512 1024
# 5. Compositional 2-step with-context CoT test (multi-hop retrieval+reasoning)
run_eval_one_test compositional_2step_with_context_cot \
    "${DATA_ROOT}/compositional_2step_with_context_cot/test_alpaca.jsonl" 4096 2048

echo "Evaluation complete."
