#!/bin/bash
# Evaluate math-ops OPSD / SFT / OffPSD checkpoints on realistic benchmarks
# (aime2024, math500, gsm8k_test, humaneval, mmlu — controlled by ALL_DATASETS
# in eval_realistic_benchmarks.py; override via --datasets).
#
# Eval outputs land inside each step dir under
# `eval_realistic_benchmarks_results/`. For OPSD step dirs, if the consolidated
# HF model isn't already present at <step>/policy/weights/model/consolidated/,
# it is produced by offline_hf_consolidation.py before eval runs.
#
# Usage:
#   bash   sbatch_eval_realistic_benchmarks.sh                # dispatch one sbatch per available step
#   sbatch sbatch_eval_realistic_benchmarks.sh 100            # evaluate step 100 only
#   RUN=sft_math_ops bash sbatch_eval_realistic_benchmarks.sh # different run shorthand
#   CKPT_BASE=/path RUN_NAME=some/run sbatch sbatch_eval_realistic_benchmarks.sh 100

#SBATCH --job-name=eval-math-ops-realistic
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=18:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.err

set -euxo pipefail

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
source "$CONDA_SH"
conda activate opsd

PROJECT_DIR="/path/to/MixSD"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"
CONSOLIDATION_TOOL="${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel/tools/offline_hf_consolidation.py"
export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_TOKEN="${HF_TOKEN:-}"
export NEMO_RL_PY_EXECUTABLES_SYSTEM=1
# Required for `evaluate.load("code_eval")` to actually execute HumanEval tests.
export HF_ALLOW_CODE_EVAL=1

# ---- Absolute paths (overridable via env) ----
CKPT_BASE="${CKPT_BASE:-/path/to/mixsd_data/mixsd/checkpoints/math_operations}"

# Base model (default): used by the consolidation tool. Auto-detected per
# step in worker mode based on RUN_NAME / saved config.yaml.
BASE_MODEL="${BASE_MODEL:-/path/to/data/models/Qwen/Qwen3-4B-Instruct-2507}"
MODEL_DIR="/path/to/data/models"

# Convenience shorthands. Any RUN whose name starts with `opsd_`/`offpsd_`/
# `sft_`/`grpo_` is accepted; pass RUN_NAME explicitly for those.
RUN="${RUN:-opsd_math_ops}"
case "$RUN" in
    opsd_math_ops)
        DEFAULT_RUN="opsd_forward_kl_gt_qwen3_4b_20260426/run_20260426.180551"
        ;;
    sft_math_ops)
        DEFAULT_RUN="sft_gt_qwen3_4b_20260426"
        ;;
    opsd_*|offpsd_*|sft_*|grpo_*)
        DEFAULT_RUN=""
        ;;
    *)
        echo "Unknown RUN=${RUN}. Must be opsd_*, offpsd_*, sft_*, or grpo_*."
        exit 1
        ;;
esac

RUN_NAME="${RUN_NAME:-$DEFAULT_RUN}"
if [ -z "$RUN_NAME" ]; then
    echo "RUN_NAME is empty for RUN=${RUN}; set RUN_NAME=<subdir under CKPT_BASE>."
    exit 1
fi
STEP="${1:-all}"

detect_base_model_for_run() {
    local name=""
    case "$RUN_NAME" in
        *_qwen3_1_7b*)              name="Qwen/Qwen3-1.7B" ;;
        *_qwen3_4b*|*qwen3-4b*)     name="Qwen/Qwen3-4B-Instruct-2507" ;;
        *_qwen3_8b*)                name="Qwen/Qwen3-8B" ;;
        *_llama3_2_1b*)             name="meta-llama/Llama-3.2-1B-Instruct" ;;
        *_llama3_2_3b*)             name="meta-llama/Llama-3.2-3B-Instruct" ;;
    esac
    local cfg="${CKPT_BASE}/${RUN_NAME}/step_${STEP}/config.yaml"
    if [ -z "$name" ] && [ -f "$cfg" ]; then
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
    if [ -n "$name" ]; then
        if [ -d "${MODEL_DIR}/${name}" ]; then
            echo "${MODEL_DIR}/${name}"
        else
            echo "$name"
        fi
    fi
}

if [ "$STEP" != "all" ]; then
    DETECTED=$(detect_base_model_for_run)
    if [ -n "$DETECTED" ]; then
        echo "[base-model] auto-detected: ${DETECTED} (was default: ${BASE_MODEL})"
        BASE_MODEL="$DETECTED"
    else
        echo "[base-model] auto-detect failed; using default: ${BASE_MODEL}"
    fi
fi

# Reuse the knowledge_sft eval_realistic_benchmarks.py — it's checkpoint-
# agnostic; only needs --ckpt-base / --run-name / --step.
EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_realistic_benchmarks.py"
SELF_PATH="$(readlink -f "${BASH_SOURCE[0]}")"

COMMON_ARGS=(
    --ckpt-base "$CKPT_BASE"
    --run-name "$RUN_NAME"
)

if [ "$STEP" = "all" ]; then
    echo "=========================================="
    echo "Dispatching per-step eval jobs (${RUN}, run=$RUN_NAME)"
    echo "=========================================="

    echo "[plan] step<TAB>missing_datasets"
    python3 "$EVAL_SCRIPT" "${COMMON_ARGS[@]}" --list-plan || true
    echo "[plan] ------"

    mapfile -t STEPS < <(python3 "$EVAL_SCRIPT" "${COMMON_ARGS[@]}" --list-incomplete-steps)
    if [ "${#STEPS[@]}" -eq 0 ]; then
        echo "All steps already have every requested benchmark; nothing to submit."
        exit 0
    fi
    echo "Submitting jobs for ${#STEPS[@]} incomplete step(s): ${STEPS[*]}"
    for s in "${STEPS[@]}"; do
        RUN="$RUN" RUN_NAME="$RUN_NAME" CKPT_BASE="$CKPT_BASE" sbatch "$SELF_PATH" "$s"
    done
    echo "Submitted ${#STEPS[@]} job(s)."
    exit 0
fi

echo "=========================================="
echo "Eval: realistic benchmarks (${RUN}, run=$RUN_NAME)"
echo "Step: ${STEP}"
echo "=========================================="

# ---- Consolidate sharded weights to HF format if needed (OPSD step dirs) ----
STEP_DIR="${CKPT_BASE}/${RUN_NAME}/step_${STEP}"
SHARDED_DIR="${STEP_DIR}/policy/weights/model"
TOKENIZER_DIR="${STEP_DIR}/policy/tokenizer"
CONSOLIDATED_DIR="${STEP_DIR}/policy/weights/model/consolidated"

if [ -d "$SHARDED_DIR" ]; then
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
    if [ -d "$TOKENIZER_DIR" ]; then
        for f in "$TOKENIZER_DIR"/*; do
            fname=$(basename "$f")
            if [ ! -f "${CONSOLIDATED_DIR}/${fname}" ]; then
                cp "$f" "${CONSOLIDATED_DIR}/${fname}"
            fi
        done
    fi
fi

python3 "$EVAL_SCRIPT" "${COMMON_ARGS[@]}" --step "$STEP"

echo "Evaluation complete."
