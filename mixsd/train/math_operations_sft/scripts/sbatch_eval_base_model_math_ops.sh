#!/bin/bash
# Evaluate a Hugging Face base model (no fine-tune) on the 11 math-operations
# test sets (same set as sbatch_eval_math_ops_opsd_and_sft_20260426.sh):
#
#   - primitive_atomic_balanced_sft_50k/test_messages.jsonl                 (175)
#   - primitive_compositional_sft_n_steps_2/op_{B..H}_test_messages.jsonl   (200×7)
#   - primitive_atomic_balanced_new_operations/test_messages.jsonl          (500)
#   - compositional_sft_n_steps_2/test_messages.jsonl                       (200)
# (op A is excluded from the 7-op default; see math_operation_dataset/generate_datasets.py)
#
# Outputs land at ${OUTPUT_DIR}/<subdir>/<test_stem>_results.jsonl, mirroring
# the layout of <step_dir>/eval_results/ for trained checkpoints.
#
# Usage:
#   sbatch sbatch_eval_base_model_math_ops.sh
#   BASE_MODEL=Qwen/Qwen3-1.7B sbatch sbatch_eval_base_model_math_ops.sh
#   BASE_MODEL=Qwen/Qwen3-8B   sbatch sbatch_eval_base_model_math_ops.sh
#   OUTPUT_DIR=/custom/dir BASE_MODEL=... sbatch sbatch_eval_base_model_math_ops.sh

#SBATCH --job-name=eval-base-math-ops
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=80G
#SBATCH --time=8:00:00
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
DATA_ROOT="${DATA_ROOT:-${BASE_DATA_DIR}/data/math_operations}"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"
MODEL_DIR="${ROOT_DIR}/beyond_pattern_matching_data/models"

export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_TOKEN="${HF_TOKEN:-}"
export TMPDIR="/path/to/tmp"
mkdir -p "$TMPDIR"

# ---- Inputs (overridable via env) ----
BASE_MODEL="${BASE_MODEL:-${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507}"
# Resolve a HF repo id (e.g. "Qwen/Qwen3-1.7B") to a local snapshot if available.
if [ ! -d "$BASE_MODEL" ] && [ -d "${MODEL_DIR}/${BASE_MODEL}" ]; then
    BASE_MODEL="${MODEL_DIR}/${BASE_MODEL}"
fi
OUTPUT_DIR="${OUTPUT_DIR:-${BASE_DATA_DIR}/eval_results/base_model/$(basename "$BASE_MODEL")/math_operations}"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/math_operations_sft/scripts/eval_sft.py"

echo "=========================================="
echo "Eval: math-ops tests (base model)"
echo "Model:  ${BASE_MODEL}"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"

run_eval_one_test() {
    local SUBDIR="$1"
    local TEST_DATA="$2"
    local MAX_NEW="$3"
    local MAX_IN="$4"

    local TEST_PATH
    TEST_PATH="$(basename "$(dirname "$TEST_DATA")")_$(basename "$TEST_DATA" .jsonl)"
    local OUT_JSONL="${OUTPUT_DIR}/${SUBDIR}/${TEST_PATH}_results.jsonl"
    if [ -f "$OUT_JSONL" ]; then
        echo "[skip] ${SUBDIR}/${TEST_PATH} already evaluated → ${OUT_JSONL}"
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

# 1. Balanced primitive atomic test
run_eval_one_test primitive_atomic_balanced_sft_50k \
    "${DATA_ROOT}/primitive_atomic_balanced_sft_50k/test_messages.jsonl" 4096 1024
# 2. Primitive compositional per-op (A-H)
for OP in B C D E F G H; do
    run_eval_one_test primitive_compositional_sft_n_steps_2 \
        "${DATA_ROOT}/primitive_compositional_sft_n_steps_2/op_${OP}_test_messages.jsonl" 4096 4096
done
# 3. New operations atomic
run_eval_one_test primitive_atomic_balanced_new_operations \
    "${DATA_ROOT}/primitive_atomic_balanced_new_operations/test_messages.jsonl" 4096 1024
# 4. Compositional 2-step (mixed ops)
run_eval_one_test compositional_sft_n_steps_2 \
    "${DATA_ROOT}/compositional_sft_n_steps_2/test_messages.jsonl" 4096 4096

echo "Evaluation complete."
