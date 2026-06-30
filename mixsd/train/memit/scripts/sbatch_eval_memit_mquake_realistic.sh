#!/bin/bash
# Realistic-benchmarks eval for MEMIT MQuAKE checkpoints.
# Worker mode: EVAL_TARGET=<checkpoint_dir> → evaluate that single checkpoint.
# Dispatcher mode (default): submit one job per MEMIT MQuAKE checkpoint.

#SBATCH --job-name=eval-memit-mquake-real
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=18:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.err

set -euxo pipefail

PROJECT_DIR="/path/to/MixSD"
ROOT_DIR="/path/to"
BASE_DATA_DIR="${ROOT_DIR}/mixsd_data"
CKPT_ROOT="${BASE_DATA_DIR}/checkpoints/knowledge"
MODEL_DIR="${ROOT_DIR}/beyond_pattern_matching_data/models"

NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"

SELF="$(readlink -f "$0")"

MEMIT_MQUAKE_CKPTS=(
    "memit_mquake_easyedit_layers3to11_wiki100k_qwen3_1_7b"
    "memit_mquake_easyedit_layers4to14_wiki100k_qwen3_4b_instruct"
    "memit_mquake_easyedit_layers4to14_wiki100k_qwen3_8b"
)

DATASETS="aime2024 math500 gsm8k_test humaneval mmlu"

############################################################
# Worker mode
############################################################
if [ -n "${EVAL_TARGET:-}" ]; then
    CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
    source "$CONDA_SH"
    conda activate opsd

    export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${NEMO_RL_DIR}/3rdparty/Automodel-workspace/Automodel:${PYTHONPATH:-}"
    export PYTHONUNBUFFERED=1
    export HF_ALLOW_CODE_EVAL=1
    export TMPDIR="/path/to/tmp"
    mkdir -p "$TMPDIR"

    EVAL_OUTPUT_DIR="${EVAL_TARGET}/eval_realistic_benchmarks_results"

    echo "##### MEMIT MQuAKE realistic eval: $(basename "$EVAL_TARGET") #####"

    python3 -c "
import sys, os, json
sys.path.insert(0, '${PROJECT_DIR}')
from mixsd.eval.checkpoint_eval import run_checkpoint_eval

model_path = '${EVAL_TARGET}'
output_dir = '${EVAL_OUTPUT_DIR}'
datasets = '${DATASETS}'.split()

# Check which are already done
summary_path = os.path.join(output_dir, 'summary.json')
done = set()
if os.path.exists(summary_path):
    with open(summary_path) as f:
        done = set(json.load(f).keys())
missing = [d for d in datasets if d not in done]
print(f'Already done: {sorted(done)}')
print(f'Will evaluate: {missing}')
if not missing:
    print('Nothing to do.')
    sys.exit(0)

run_checkpoint_eval(
    checkpoint_path=model_path,
    output_dir=output_dir,
    datasets=missing,
    num_tests_per_prompt={'aime2024': 16},
    temperature=1.0,
    tensor_parallel_size=1,
)
"

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
    # Check if already complete
    SUMMARY="${TARGET}/eval_realistic_benchmarks_results/summary.json"
    if [ -f "$SUMMARY" ]; then
        DONE_COUNT=$(python3 -c "import json; print(len(json.load(open('$SUMMARY'))))" 2>/dev/null || echo 0)
        if [ "$DONE_COUNT" -ge 5 ]; then
            echo "[plan] ${name}: all 5 benchmarks done — skip"
            continue
        fi
    fi
    echo "[plan] ${name}: submitting realistic eval"
    JOB_NAME="eval-memit-mquake-real-${name##memit_mquake_easyedit_}"
    sbatch \
        --job-name="$JOB_NAME" \
        --export=ALL,EVAL_TARGET="$TARGET" \
        "$SELF"
    SUBMITTED=$((SUBMITTED + 1))
done
echo "[dispatch] Submitted ${SUBMITTED} realistic-benchmark job(s)."
