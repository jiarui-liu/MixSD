#!/bin/bash
# Knowledge eval for MEMIT MQuAKE checkpoints (easyedit, chat-prompt variant).
# Worker mode: EVAL_TARGET=<checkpoint_dir> → evaluate that single checkpoint.
# Dispatcher mode (default): submit one job per MEMIT MQuAKE checkpoint.

#SBATCH --job-name=eval-memit-mquake-know
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

PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
DATA_ROOT="${BASE_DATA_DIR}/data/knowledge_d5_e10_mquake"
CKPT_ROOT="${BASE_DATA_DIR}/checkpoints/knowledge"
MODEL_DIR="${ROOT_DIR}/beyond_pattern_matching_data/models"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_sft.py"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

SELF="$(readlink -f "$0")"

MEMIT_MQUAKE_CKPTS=(
    "memit_mquake_easyedit_layers3to11_wiki100k_qwen3_1_7b"
    "memit_mquake_easyedit_layers4to14_wiki100k_qwen3_4b_instruct"
    "memit_mquake_easyedit_layers4to14_wiki100k_qwen3_8b"
)

# MQuAKE has 4 tests (no compositional_2step_with_context_cot).
EXPECTED_OUTPUTS=(
    "atomic/test_subset_of_train_inference_results.jsonl"
    "atomic/val_paraphrased_inference_results.jsonl"
    "compositional_2step/test_alpaca_results.jsonl"
    "atomic_with_context_cot/test_alpaca_results.jsonl"
)

missing_tests_for() {
    local EVAL_DIR="$1"
    local rel
    for rel in "${EXPECTED_OUTPUTS[@]}"; do
        if [ ! -f "${EVAL_DIR}/${rel}" ]; then
            echo "$rel"
        fi
    done
}

############################################################
# Worker mode
############################################################
if [ -n "${EVAL_TARGET:-}" ]; then
    CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
    source "$CONDA_SH"
    conda activate opsd

    export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
    export PYTHONUNBUFFERED=1
    export TMPDIR="/path/to/tmp"
    mkdir -p "$TMPDIR"

    # Auto-detect base model from checkpoint dir name
    case "$EVAL_TARGET" in
        *_qwen3_1_7b*) BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-1.7B" ;;
        *_qwen3_4b*)   BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507" ;;
        *_qwen3_8b*)   BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-8B" ;;
        *)             BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507" ;;
    esac
    echo "[base-model] ${BASE_MODEL}"

    EVAL_DIR="${EVAL_TARGET}/eval_results"
    mkdir -p "$EVAL_DIR"

    run_one() {
        local SUBDIR="$1"
        local TEST_DATA="$2"
        local MAX_NEW="$3"
        local MAX_IN="$4"

        local STEM
        STEM="$(basename "$TEST_DATA" .jsonl)"
        local OUT_JSONL="${EVAL_DIR}/${SUBDIR}/${STEM}_results.jsonl"
        if [ -f "$OUT_JSONL" ]; then
            echo "[skip] ${SUBDIR}/${STEM} already evaluated"
            return 0
        fi
        mkdir -p "${EVAL_DIR}/${SUBDIR}"
        python "$EVAL_SCRIPT" \
            --merged_model_dir "$EVAL_TARGET" \
            --base_model "$BASE_MODEL" \
            --test_data "$TEST_DATA" \
            --output_dir "${EVAL_DIR}/${SUBDIR}" \
            --skip_merge \
            --max_new_tokens "$MAX_NEW" \
            --max_input_sequence_length "$MAX_IN" \
            --temperature 0.0
    }

    echo "##### MEMIT MQuAKE knowledge eval: $(basename "$EVAL_TARGET") #####"

    # 1. Atomic test_subset_of_train
    run_one atomic \
        "${DATA_ROOT}/atomic_sft/test_subset_of_train_inference.jsonl" 4096 512
    # 2. Atomic val_paraphrased
    run_one atomic \
        "${DATA_ROOT}/atomic_sft/val_paraphrased_inference.jsonl" 4096 512
    # 3. Compositional 2-step
    run_one compositional_2step \
        "${DATA_ROOT}/compositional_2step_sft/test_alpaca.jsonl" 4096 1024
    # 4. Atomic with-context CoT
    run_one atomic_with_context_cot \
        "${DATA_ROOT}/atomic_with_context_cot/test_alpaca.jsonl" 4096 1024

    echo "DONE: $(basename "$EVAL_TARGET")"
    exit 0
fi

############################################################
# Dispatcher mode
############################################################
SUBMITTED=0
for name in "${MEMIT_MQUAKE_CKPTS[@]}"; do
    TARGET="${CKPT_ROOT}/${name}"
    if [ ! -d "$TARGET" ]; then
        echo "[skip] missing dir: $TARGET"
        continue
    fi
    EVAL_DIR="${TARGET}/eval_results"
    mapfile -t MISSING < <(missing_tests_for "$EVAL_DIR")
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo "[plan] ${name}: all tests done — skip"
        continue
    fi
    echo "[plan] ${name}: missing ${#MISSING[@]}/${#EXPECTED_OUTPUTS[@]} → ${MISSING[*]}"
    JOB_NAME="eval-memit-mquake-know-${name##memit_mquake_easyedit_}"
    sbatch \
        --job-name="$JOB_NAME" \
        --export=ALL,EVAL_TARGET="$TARGET" \
        "$SELF"
    SUBMITTED=$((SUBMITTED + 1))
done
echo "[dispatch] Submitted ${SUBMITTED} knowledge-eval job(s)."
