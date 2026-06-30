#!/bin/bash
# Combined eval for the knowledge_d5_e10 (20260416) comparison.
#
# This script has two modes:
#   (A) Dispatcher (default)  — discover every OPSD step_* and every SFT
#       checkpoint-* dir, then submit ONE independent SLURM job per
#       checkpoint so they can run in parallel. Invoke as:
#           bash sbatch_eval_knowledge_d5_e10_opsd_and_sft_20260416.sh
#   (B) Worker (EVAL_TARGET set) — evaluate a single checkpoint. Invoked
#       automatically by the dispatcher via:
#           sbatch --export=ALL,EVAL_TARGET=<dir>,EVAL_KIND=<opsd|sft> <self>
#
# Test sets (shared, per checkpoint):
#   - Atomic in-distribution                    (atomic_sft/test_subset_of_train)
#   - Atomic paraphrased                        (atomic_sft/val_paraphrased)
#   - Compositional 2-step                      (compositional_2step_sft/test_alpaca)
#   - Atomic with-context CoT                   (atomic_with_context_cot/test_alpaca)
#   - Compositional 2-step with-context CoT     (compositional_2step_with_context_cot/test_alpaca)
#
# Env-var overrides (dispatcher mode):
#   OPSD_RUN_DIR   — absolute path to a single run_YYYYMMDD.HHMMSS dir.
#   OPSD_CKPT_BASE — a training variant's root (…/opsd_<variant>/); latest
#                    run_* is used. Defaults to the d5_e10 20260416 variant.
#   SFT_CKPT_ROOT  — SFT output_dir containing checkpoint-* subdirs.
#                    Defaults to atomic_full_sft_d5_e10_10ep_t20260416.
#   SKIP_OPSD=1    — skip submitting OPSD jobs.
#   SKIP_SFT=1     — skip submitting SFT jobs.

#SBATCH --job-name=eval-know-d5e10
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

# --- Project paths ---
PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
DATA_ROOT="${DATA_ROOT:-${BASE_DATA_DIR}/data/knowledge_d5_e10}"
MODEL_DIR="${ROOT_DIR}/beyond_pattern_matching_data/models"
BASE_MODEL="${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_sft.py"
CONSOLIDATION_TOOL="${PROJECT_DIR}/mixsd/train/nemo-rl/3rdparty/Automodel-workspace/Automodel/tools/offline_hf_consolidation.py"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

SELF="$(readlink -f "$0")"

# Canonical expected-output paths for the 5 test sets (relative to a checkpoint's
# eval_results/ dir). Keep these in sync with run_eval_sft_py above.
EXPECTED_OUTPUTS=(
    "atomic/test_subset_of_train_inference_results.jsonl"
    "atomic/val_paraphrased_inference_results.jsonl"
    "compositional_2step/test_alpaca_results.jsonl"
    "atomic_with_context_cot/test_alpaca_results.jsonl"
    "compositional_2step_with_context_cot/test_alpaca_results.jsonl"
)
# When SKIP_TEST_5=1, drop the 5th test (compositional_2step_with_context_cot);
# used for datasets like mquake that don't provide that subset.
if [ "${SKIP_TEST_5:-0}" = "1" ]; then
    unset 'EXPECTED_OUTPUTS[4]'
fi

# Prints the relative paths that are still missing under $1 (an eval_results dir).
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

    # --- Conda + env (worker only) ---
    CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
    source "$CONDA_SH"
    conda activate opsd

    export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
    export PYTHONUNBUFFERED=1
    export TMPDIR="/path/to/tmp"
    mkdir -p "$TMPDIR"

    # --- Auto-detect BASE_MODEL per target ---
    # OPSD: parse nemo-rl's saved step_*/config.yaml for policy.model_name.
    # SFT:  infer from the checkpoint dir name (axolotl doesn't persist
    #       base_model_name_or_path in trainer_state / config.json).
    # Falls back to the shared BASE_MODEL default if detection fails.
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
                *_llama3_2_1b*)  name="meta-llama/Llama-3.2-1B-Instruct" ;;
                *_llama3_2_3b*)  name="meta-llama/Llama-3.2-3B-Instruct" ;;
                *_qwen3_0_6b*)   name="Qwen/Qwen3-0.6B" ;;
                *_qwen3_1_7b*)   name="Qwen/Qwen3-1.7B" ;;
                *_qwen3_8b*)     name="Qwen/Qwen3-8B" ;;
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

    # The 5 (subdir, test_data, max_new_tokens, max_input_len) triples shared
    # between the worker (to run) and the dispatcher (to decide what's missing).
    # Keep this in sync with TEST_SPECS below.
    run_eval_one_test() {
        local CKPT="$1"
        local EVAL_DIR="$2"
        local SUBDIR="$3"
        local TEST_DATA="$4"
        local MAX_NEW="$5"
        local MAX_IN="$6"

        local STEM
        STEM="$(basename "$TEST_DATA" .jsonl)"
        local OUT_JSONL="${EVAL_DIR}/${SUBDIR}/${STEM}_results.jsonl"
        if [ -f "$OUT_JSONL" ]; then
            echo "[skip] ${SUBDIR}/${STEM} already evaluated → ${OUT_JSONL}"
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

    run_eval_sft_py() {
        local CKPT="$1"
        local EVAL_DIR="$2"
        mkdir -p "$EVAL_DIR"

        echo "[eval] CKPT=${CKPT}"
        echo "[eval] OUT=${EVAL_DIR}"

        # 1. Atomic test_subset_of_train (in-distribution memorization)
        run_eval_one_test "$CKPT" "$EVAL_DIR" atomic \
            "${DATA_ROOT}/atomic_sft/test_subset_of_train_inference.jsonl" 4096 512
        # 2. Atomic val_paraphrased (paraphrased robustness)
        run_eval_one_test "$CKPT" "$EVAL_DIR" atomic \
            "${DATA_ROOT}/atomic_sft/val_paraphrased_inference.jsonl" 4096 512
        # 3. Compositional 2-step test (OOD generalization)
        run_eval_one_test "$CKPT" "$EVAL_DIR" compositional_2step \
            "${DATA_ROOT}/compositional_2step_sft/test_alpaca.jsonl" 4096 1024
        # 4. Atomic with-context CoT test (retrieval-from-context)
        run_eval_one_test "$CKPT" "$EVAL_DIR" atomic_with_context_cot \
            "${DATA_ROOT}/atomic_with_context_cot/test_alpaca.jsonl" 4096 1024
        # 5. Compositional 2-step with-context CoT test (multi-hop retrieval+reasoning)
        if [ "${SKIP_TEST_5:-0}" = "1" ]; then
            echo "[skip] compositional_2step_with_context_cot (SKIP_TEST_5=1)"
        else
            run_eval_one_test "$CKPT" "$EVAL_DIR" compositional_2step_with_context_cot \
                "${DATA_ROOT}/compositional_2step_with_context_cot/test_alpaca.jsonl" 4096 2048
        fi
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
            # The consolidation tool doesn't write config.json; sglang's
            # model loader needs it (otherwise hf_config.architectures is
            # None → TypeError). Copy from BASE_MODEL.
            if [ ! -f "${CONSOLIDATED_DIR}/config.json" ] && [ -f "${BASE_MODEL}/config.json" ]; then
                cp "${BASE_MODEL}/config.json" "${CONSOLIDATED_DIR}/config.json"
            fi

            run_eval_sft_py "$CONSOLIDATED_DIR" "$EVAL_DIR"
            ;;
        sft)
            echo "##### SFT $(basename "$EVAL_TARGET") #####"
            run_eval_sft_py "$EVAL_TARGET" "${EVAL_TARGET}/eval_results"
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

OPSD_CKPT_BASE="${OPSD_CKPT_BASE:-${BASE_DATA_DIR}/checkpoints/knowledge/opsd_forward_kl_gt_d5_e10_20260416}"
SFT_CKPT_ROOT="${SFT_CKPT_ROOT:-${BASE_DATA_DIR}/checkpoints/knowledge/atomic_full_sft_d5_e10_10ep_t20260416}"
SKIP_OPSD="${SKIP_OPSD:-0}"
SKIP_SFT="${SKIP_SFT:-0}"

submit_one() {
    local KIND="$1"
    local TARGET="$2"
    local TAG="$3"
    local JOB_NAME="eval-know-d5e10-${KIND}-${TAG}"
    echo "[dispatch] sbatch ${JOB_NAME}  (${TARGET})"
    sbatch \
        --job-name="$JOB_NAME" \
        --export=ALL,EVAL_TARGET="$TARGET",EVAL_KIND="$KIND" \
        "$SELF"
}

# Decides whether to submit a job for a given target; prints a plan line either way.
# Returns 0 if anything is missing (→ submit), 1 otherwise.
maybe_submit() {
    local KIND="$1"
    local TARGET="$2"
    local EVAL_DIR="${TARGET}/eval_results"

    mapfile -t MISSING < <(missing_tests_for "$EVAL_DIR")
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo "[plan] ${KIND} $(basename "$TARGET"): all 5 tests done — skip"
        return 1
    fi
    echo "[plan] ${KIND} $(basename "$TARGET"): missing ${#MISSING[@]}/5 → ${MISSING[*]}"
    submit_one "$KIND" "$TARGET" "$(basename "$TARGET")"
    return 0
}

SUBMITTED=0

# --- OPSD: submit one job per step_* that still has missing tests ---
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

# --- SFT: submit one job per checkpoint-* that still has missing tests ---
if [ "$SKIP_SFT" = "0" ]; then
    if [ ! -d "$SFT_CKPT_ROOT" ]; then
        echo "[SFT] ERROR: not a directory: ${SFT_CKPT_ROOT}"
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
    echo "[SFT] skipped (SKIP_SFT=1)"
fi

echo "[dispatch] Submitted ${SUBMITTED} job(s)."
