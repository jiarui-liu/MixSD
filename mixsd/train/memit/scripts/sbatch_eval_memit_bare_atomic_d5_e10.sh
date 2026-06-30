#!/bin/bash
# Dedicated eval for MEMIT "bare-prompt" checkpoints.
#
# Test set: `{prompt, ground_truth_answer}` JSONL where
#   - prompt  = bare question identical to what MEMIT was trained on
#               (no CoT instruction, chat-template applied by the inference
#               script at runtime)
#   - target  = raw entity string (no "The answer is..." wrapper, no \boxed{})
#   - scoring = strict (normalized exact match, no substring fallback)
#
# Two modes (like sbatch_eval_knowledge_d5_e10_opsd_and_sft_20260416.sh):
#   (A) Dispatcher (default): discover the six bare-prompt memit checkpoint
#       dirs and submit one SLURM job each.
#   (B) Worker (EVAL_TARGET set): evaluate a single checkpoint and exit.

#SBATCH --job-name=eval-memit-bare-d5e10
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=80G
#SBATCH --time=2:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_%x_%j.err

set -euxo pipefail

PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
DATA_ROOT="${BASE_DATA_DIR}/data/knowledge_d5_e10"
CKPT_ROOT="${BASE_DATA_DIR}/checkpoints/knowledge"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_sft.py"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

SELF="$(readlink -f "$0")"

# The two memit-bare tests. Keep in sync between dispatcher skip-check
# and worker run loop below.
EXPECTED_OUTPUTS=(
    "atomic_memit_bare/test_subset_of_train_memit_bare_results.jsonl"
    "atomic_memit_bare/val_paraphrased_memit_bare_results.jsonl"
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

# The six bare-prompt memit checkpoint output dirs.
MEMIT_BARE_CKPTS=(
    "memit_atomic_d5_e10_bare_layers4to14_wiki100k_qwen3_4b_instruct"
    "memit_atomic_d5_e10_bare_layers4to14_wiki100k_qwen3_8b"
    "memit_atomic_d5_e10_bare_layers3to11_wiki100k_qwen3_0_6b"
    "memit_atomic_d5_e10_bare_layers3to11_wiki100k_qwen3_1_7b"
    "memit_atomic_d5_e10_bare_layers2to8_wiki100k_llama3_2_1b"
    "memit_atomic_d5_e10_bare_layers3to11_wiki100k_llama3_2_3b"
)

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

    EVAL_DIR="${EVAL_TARGET}/eval_results"
    mkdir -p "${EVAL_DIR}/atomic_memit_bare"

    run_one() {
        local TEST_DATA="$1"
        local STEM
        STEM="$(basename "$TEST_DATA" .jsonl)"
        local OUT_JSONL="${EVAL_DIR}/atomic_memit_bare/${STEM}_results.jsonl"
        if [ -f "$OUT_JSONL" ]; then
            echo "[skip] ${STEM} already evaluated"
            return 0
        fi
        python "$EVAL_SCRIPT" \
            --merged_model_dir "$EVAL_TARGET" \
            --test_data "$TEST_DATA" \
            --output_dir "${EVAL_DIR}/atomic_memit_bare" \
            --skip_merge \
            --max_new_tokens 128 \
            --max_input_sequence_length 256 \
            --temperature 0.0 \
            --score_mode strict
    }

    echo "##### memit-bare eval on $(basename "$EVAL_TARGET") #####"
    run_one "${DATA_ROOT}/atomic_sft/test_subset_of_train_memit_bare.jsonl"
    run_one "${DATA_ROOT}/atomic_sft/val_paraphrased_memit_bare.jsonl"
    echo "DONE: $(basename "$EVAL_TARGET")"
    exit 0
fi

############################################################
# Dispatcher mode
############################################################
SUBMITTED=0
for name in "${MEMIT_BARE_CKPTS[@]}"; do
    TARGET="${CKPT_ROOT}/${name}"
    if [ ! -d "$TARGET" ]; then
        echo "[skip] missing dir: $TARGET"
        continue
    fi
    EVAL_DIR="${TARGET}/eval_results"
    mapfile -t MISSING < <(missing_tests_for "$EVAL_DIR")
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo "[plan] ${name}: both tests done — skip"
        continue
    fi
    echo "[plan] ${name}: missing ${#MISSING[@]}/${#EXPECTED_OUTPUTS[@]} → ${MISSING[*]}"
    JOB_NAME="eval-memit-bare-${name}"
    sbatch \
        --job-name="$JOB_NAME" \
        --export=ALL,EVAL_TARGET="$TARGET" \
        "$SELF"
    SUBMITTED=$((SUBMITTED + 1))
done
echo "[dispatch] Submitted ${SUBMITTED} job(s)."
