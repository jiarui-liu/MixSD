#!/bin/bash
# Combined eval for math-operations OPSD/SFT/OffPSD checkpoints.
#
# Two modes:
#   (A) Dispatcher (default)  — discover every OPSD step_* and every SFT
#       checkpoint dir, then submit ONE independent SLURM job per checkpoint
#       so they can run in parallel. Invoke as:
#           bash sbatch_eval_math_ops_opsd_and_sft_20260426.sh
#   (B) Worker (EVAL_TARGET set) — evaluate a single checkpoint. Invoked
#       automatically by the dispatcher via:
#           sbatch --export=ALL,EVAL_TARGET=<dir>,EVAL_KIND=<opsd|sft> <self>
#
# Test sets evaluated per checkpoint (10 total, all messages format):
#   - primitive_atomic_balanced_sft_50k/test_messages.jsonl                 (175)
#   - primitive_compositional_sft_n_steps_2/op_{B..H}_test_messages.jsonl   (200×7)
#   - primitive_atomic_balanced_new_operations/test_messages.jsonl          (500)
#   - compositional_sft_n_steps_2/test_messages.jsonl                       (200)
# (op A is excluded from the 7-op default; see math_operation_dataset/generate_datasets.py)
#
# Env-var overrides (dispatcher mode):
#   OPSD_RUN_DIR    — absolute path to a single run_YYYYMMDD.HHMMSS dir.
#   OPSD_CKPT_BASE  — a training variant root (.../<variant>/); latest run_*
#                     is used. Defaults to forward_kl_gt_qwen3_4b 20260426.
#   SFT_CKPT_ROOT   — SFT output_dir containing checkpoint-* subdirs (or the
#                     dir itself if it already holds the model files).
#   SKIP_OPSD=1     — skip submitting OPSD jobs.
#   SKIP_SFT=1      — skip submitting SFT jobs.

#SBATCH --job-name=eval-math-ops
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

# --- Project paths ---
PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
DATA_ROOT="${DATA_ROOT:-${BASE_DATA_DIR}/data/math_operations}"
MODEL_DIR="${ROOT_DIR}/beyond_pattern_matching_data/models"
BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/math_operations_sft/scripts/eval_sft.py"
CONSOLIDATION_TOOL="${PROJECT_DIR}/mixsd/train/nemo-rl/3rdparty/Automodel-workspace/Automodel/tools/offline_hf_consolidation.py"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

SELF="$(readlink -f "$0")"

# Canonical (subdir, jsonl-stem) pairs for the 11 test outputs (relative to a
# checkpoint's eval_results/ dir). Stem names use parent_dir prefix to keep
# `test_messages.jsonl` from different sources distinct.
EXPECTED_OUTPUTS=(
    "primitive_atomic_balanced_sft_50k/primitive_atomic_balanced_sft_50k_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_B_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_C_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_D_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_E_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_F_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_G_test_messages_results.jsonl"
    "primitive_compositional_sft_n_steps_2/primitive_compositional_sft_n_steps_2_op_H_test_messages_results.jsonl"
    "primitive_atomic_balanced_new_operations/primitive_atomic_balanced_new_operations_test_messages_results.jsonl"
    "compositional_sft_n_steps_2/compositional_sft_n_steps_2_test_messages_results.jsonl"
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
# Worker mode: evaluate one checkpoint and exit.
############################################################
if [ -n "${EVAL_TARGET:-}" ]; then
    EVAL_KIND="${EVAL_KIND:-sft}"

    CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
    source "$CONDA_SH"
    conda activate opsd

    export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
    export PYTHONUNBUFFERED=1
    export TMPDIR="/path/to/tmp"
    mkdir -p "$TMPDIR"

    # --- Auto-detect BASE_MODEL per target ---
    detect_base_model() {
        local TARGET="$1"
        local KIND="$2"
        local name=""

        if [ "$KIND" = "opsd" ]; then
            local cfg="${TARGET}/config.yaml"
            if [ -f "$cfg" ]; then
                name=$(python3 - "$cfg" <<'PY' || true
import sys, yaml
try:
    d = yaml.safe_load(open(sys.argv[1])) or {}
    print((d.get("policy") or {}).get("model_name") or "", end="")
except Exception:
    pass
PY
                )
            fi
        else
            case "$TARGET" in
                *_qwen3_1_7b*)              name="Qwen/Qwen3-1.7B" ;;
                *_qwen3_4b*|*qwen3-4b*)     name="Qwen/Qwen3-4B-Instruct-2507" ;;
                *_qwen3_8b*)                name="Qwen/Qwen3-8B" ;;
                *_llama3_2_1b*)             name="meta-llama/Llama-3.2-1B-Instruct" ;;
                *_llama3_2_3b*)             name="meta-llama/Llama-3.2-3B-Instruct" ;;
            esac
        fi

        if [ -n "$name" ]; then
            if [ -d "${MODEL_DIR}/${name}" ]; then
                echo "${MODEL_DIR}/${name}"
            else
                echo "$name"
            fi
        fi
    }

    DETECTED=$(detect_base_model "$EVAL_TARGET" "$EVAL_KIND")
    if [ -n "$DETECTED" ]; then
        echo "[base-model] auto-detected for ${EVAL_KIND}: ${DETECTED} (was default: ${BASE_MODEL})"
        BASE_MODEL="$DETECTED"
    else
        echo "[base-model] auto-detect failed; using default: ${BASE_MODEL}"
    fi

    # Run a single test set; skips if its output already exists.
    run_eval_one_test() {
        local CKPT="$1"
        local EVAL_DIR="$2"
        local SUBDIR="$3"
        local TEST_DATA="$4"
        local MAX_NEW="$5"
        local MAX_IN="$6"

        local TEST_PATH
        TEST_PATH="$(basename "$(dirname "$TEST_DATA")")_$(basename "$TEST_DATA" .jsonl)"
        local OUT_JSONL="${EVAL_DIR}/${SUBDIR}/${TEST_PATH}_results.jsonl"
        if [ -f "$OUT_JSONL" ]; then
            echo "[skip] ${SUBDIR}/${TEST_PATH} already evaluated → ${OUT_JSONL}"
            return 0
        fi

        mkdir -p "${EVAL_DIR}/${SUBDIR}"
        python "$EVAL_SCRIPT" \
            --merged_model_dir "$CKPT" \
            --base_model "$BASE_MODEL" \
            --test_data "$TEST_DATA" \
            --output_dir "${EVAL_DIR}/${SUBDIR}" \
            --skip_merge \
            --max_new_tokens "$MAX_NEW" \
            --max_input_sequence_length "$MAX_IN" \
            --temperature 0.0
    }

    run_eval_all_test_sets() {
        local CKPT="$1"
        local EVAL_DIR="$2"
        mkdir -p "$EVAL_DIR"

        echo "[eval] CKPT=${CKPT}"
        echo "[eval] OUT=${EVAL_DIR}"

        # 1. Balanced primitive atomic test (in-distribution)
        run_eval_one_test "$CKPT" "$EVAL_DIR" primitive_atomic_balanced_sft_50k \
            "${DATA_ROOT}/primitive_atomic_balanced_sft_50k/test_messages.jsonl" 4096 1024
        # 2. Primitive compositional per-op (A-H, OOD on same op repeated)
        for OP in B C D E F G H; do
            run_eval_one_test "$CKPT" "$EVAL_DIR" primitive_compositional_sft_n_steps_2 \
                "${DATA_ROOT}/primitive_compositional_sft_n_steps_2/op_${OP}_test_messages.jsonl" 4096 4096
        done
        # 3. New operations atomic (held-out ops, OOD generalization)
        run_eval_one_test "$CKPT" "$EVAL_DIR" primitive_atomic_balanced_new_operations \
            "${DATA_ROOT}/primitive_atomic_balanced_new_operations/test_messages.jsonl" 4096 1024
        # 4. Compositional 2-step (mixed ops, OOD compositional generalization)
        run_eval_one_test "$CKPT" "$EVAL_DIR" compositional_sft_n_steps_2 \
            "${DATA_ROOT}/compositional_sft_n_steps_2/test_messages.jsonl" 4096 4096
    }

    case "$EVAL_KIND" in
        opsd)
            STEP_DIR="$EVAL_TARGET"
            SHARDED_DIR="${STEP_DIR}/policy/weights/model"
            TOKENIZER_DIR="${STEP_DIR}/policy/tokenizer"
            CONSOLIDATED_DIR="${STEP_DIR}/policy/weights/model/consolidated"
            EVAL_DIR="${STEP_DIR}/eval_results"

            echo "##### OPSD $(basename "$STEP_DIR") #####"

            if [ -f "${CONSOLIDATED_DIR}/model.safetensors" ] || \
               ls "${CONSOLIDATED_DIR}"/*.safetensors 1>/dev/null 2>&1; then
                echo "[consolidate] already exists, skipping."
            else
                echo "[consolidate] running..."
                python "$CONSOLIDATION_TOOL" \
                    --model-name "$BASE_MODEL" \
                    --input-dir "$SHARDED_DIR" \
                    --output-dir "$CONSOLIDATED_DIR" \
                    --backend gloo
            fi

            for f in "$TOKENIZER_DIR"/*; do
                fname=$(basename "$f")
                if [ ! -f "${CONSOLIDATED_DIR}/${fname}" ]; then
                    cp "$f" "${CONSOLIDATED_DIR}/${fname}"
                fi
            done
            if [ ! -f "${CONSOLIDATED_DIR}/config.json" ] && [ -f "${BASE_MODEL}/config.json" ]; then
                cp "${BASE_MODEL}/config.json" "${CONSOLIDATED_DIR}/config.json"
            fi

            run_eval_all_test_sets "$CONSOLIDATED_DIR" "$EVAL_DIR"
            ;;
        sft)
            echo "##### SFT $(basename "$EVAL_TARGET") #####"
            run_eval_all_test_sets "$EVAL_TARGET" "${EVAL_TARGET}/eval_results"
            ;;
        *)
            echo "ERROR: unknown EVAL_KIND=${EVAL_KIND} (expected 'opsd' or 'sft')"
            exit 1
            ;;
    esac

    echo "DONE: ${EVAL_KIND} ${EVAL_TARGET}"
    exit 0
fi

############################################################
# Dispatcher mode: enumerate checkpoints and submit one sbatch per.
############################################################

OPSD_CKPT_BASE="${OPSD_CKPT_BASE:-${BASE_DATA_DIR}/checkpoints/math_operations/opsd_forward_kl_gt_qwen3_4b_20260426}"
SFT_CKPT_ROOT="${SFT_CKPT_ROOT:-}"
SKIP_OPSD="${SKIP_OPSD:-0}"
SKIP_SFT="${SKIP_SFT:-1}"  # default-skip until an SFT ckpt root is provided

submit_one() {
    local KIND="$1"
    local TARGET="$2"
    local TAG="$3"
    local JOB_NAME="eval-math-${KIND}-${TAG}"
    echo "[dispatch] sbatch ${JOB_NAME}  (${TARGET})"
    sbatch \
        --job-name="$JOB_NAME" \
        --export=ALL,EVAL_TARGET="$TARGET",EVAL_KIND="$KIND" \
        "$SELF"
}

maybe_submit() {
    local KIND="$1"
    local TARGET="$2"
    local EVAL_DIR="${TARGET}/eval_results"
    if [ "$KIND" = "opsd" ]; then
        EVAL_DIR="${TARGET}/eval_results"
    fi

    mapfile -t MISSING < <(missing_tests_for "$EVAL_DIR")
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo "[plan] ${KIND} $(basename "$TARGET"): all ${#EXPECTED_OUTPUTS[@]} tests done — skip"
        return 1
    fi
    echo "[plan] ${KIND} $(basename "$TARGET"): missing ${#MISSING[@]}/${#EXPECTED_OUTPUTS[@]}"
    submit_one "$KIND" "$TARGET" "$(basename "$TARGET")"
    return 0
}

SUBMITTED=0

# --- OPSD: submit one job per step_* ---
if [ "$SKIP_OPSD" = "0" ]; then
    if [ -n "${OPSD_RUN_DIR:-}" ]; then
        LATEST_RUN="$OPSD_RUN_DIR"
    else
        LATEST_RUN=$(ls -d "${OPSD_CKPT_BASE}"/run_* 2>/dev/null | sort | tail -1)
    fi
    if [ -z "${LATEST_RUN:-}" ] || [ ! -d "${LATEST_RUN}" ]; then
        echo "[OPSD] ERROR: no valid run directory (OPSD_CKPT_BASE=${OPSD_CKPT_BASE})"
        exit 1
    fi
    echo "[OPSD] run directory: ${LATEST_RUN}"

    mapfile -t STEP_DIRS < <(ls -d "${LATEST_RUN}"/step_* 2>/dev/null | sort -t_ -k2 -n)
    if [ ${#STEP_DIRS[@]} -eq 0 ]; then
        echo "[OPSD] ERROR: no step_* directories under ${LATEST_RUN}"
        exit 1
    fi
    echo "[OPSD] Found ${#STEP_DIRS[@]} step checkpoint(s); filtering by completion status."
    for STEP_DIR in "${STEP_DIRS[@]}"; do
        if maybe_submit opsd "$STEP_DIR"; then
            SUBMITTED=$((SUBMITTED + 1))
        fi
    done
else
    echo "[OPSD] skipped (SKIP_OPSD=1)"
fi

# --- SFT: submit one job per checkpoint-* (if a root is provided) ---
if [ "$SKIP_SFT" = "0" ]; then
    if [ -z "$SFT_CKPT_ROOT" ] || [ ! -d "$SFT_CKPT_ROOT" ]; then
        echo "[SFT] ERROR: SFT_CKPT_ROOT not set or not a directory: ${SFT_CKPT_ROOT}"
        exit 1
    fi
    echo "[SFT] checkpoint root: ${SFT_CKPT_ROOT}"

    mapfile -t SFT_CKPT_DIRS < <(ls -d "${SFT_CKPT_ROOT}"/checkpoint-* 2>/dev/null | sort -t- -k2 -n)
    if [ ${#SFT_CKPT_DIRS[@]} -eq 0 ]; then
        echo "[SFT] No checkpoint-* dirs found; treating root dir as the single target."
        SFT_CKPT_DIRS=("$SFT_CKPT_ROOT")
    fi
    echo "[SFT] Found ${#SFT_CKPT_DIRS[@]} checkpoint(s); filtering by completion status."
    for CKPT in "${SFT_CKPT_DIRS[@]}"; do
        if maybe_submit sft "$CKPT"; then
            SUBMITTED=$((SUBMITTED + 1))
        fi
    done
else
    echo "[SFT] skipped (SKIP_SFT=1; pass SFT_CKPT_ROOT and SKIP_SFT=0 to enable)"
fi

echo "[dispatch] Submitted ${SUBMITTED} job(s)."
