#!/bin/bash
# Evaluate a Hugging Face base model (no fine-tune) on realistic math benchmarks.
# Benchmarks: aime2024, math500, gsm8k_test, humaneval, mmlu (controlled by
# ALL_DATASETS in eval_base_model_realistic_benchmarks.py; override via
# --datasets or by editing that file).
#
# This script just delegates to the knowledge_sft variant — the eval is
# checkpoint-agnostic, so we don't need a math-specific copy of the python.
# Outputs land in a math-ops-namespaced output dir by default.
#
# Usage:
#   sbatch sbatch_eval_base_model_realistic_benchmarks.sh
#   BASE_MODEL=Qwen/Qwen3-1.7B sbatch sbatch_eval_base_model_realistic_benchmarks.sh
#   BASE_MODEL=Qwen/Qwen3-8B   sbatch sbatch_eval_base_model_realistic_benchmarks.sh
#   OUTPUT_DIR=/custom/dir sbatch sbatch_eval_base_model_realistic_benchmarks.sh

#SBATCH --job-name=eval-base-realistic-math-ops
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --gres=gpu:h100:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_eval_%x_%j.err

set -euxo pipefail

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
source "$CONDA_SH"
conda activate opsd

PROJECT_DIR="/path/to/MixSD"
NEMO_RL_DIR="${PROJECT_DIR}/mixsd/train/nemo-rl"
export PYTHONPATH="${PROJECT_DIR}:${NEMO_RL_DIR}:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
export HF_TOKEN="${HF_TOKEN:-}"
export NEMO_RL_PY_EXECUTABLES_SYSTEM=1
export HF_ALLOW_CODE_EVAL=1

MODEL_DIR="/path/to/data/models"
BASE_MODEL="${BASE_MODEL:-${MODEL_DIR}/Qwen/Qwen3-4B-Instruct-2507}"
if [ ! -d "$BASE_MODEL" ] && [ -d "${MODEL_DIR}/${BASE_MODEL}" ]; then
    BASE_MODEL="${MODEL_DIR}/${BASE_MODEL}"
fi
OUTPUT_DIR="${OUTPUT_DIR:-/path/to/mixsd_data/mixsd/eval_realistic_benchmarks_results/base_model/$(basename "$BASE_MODEL")}"

EVAL_SCRIPT="${PROJECT_DIR}/mixsd/train/knowledge_sft/scripts/eval_base_model_realistic_benchmarks.py"

echo "=========================================="
echo "Eval: realistic benchmarks (base model)"
echo "Model:  ${BASE_MODEL}"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================="

python3 "$EVAL_SCRIPT" \
    --model "$BASE_MODEL" \
    --output-dir "$OUTPUT_DIR"

echo "Evaluation complete."
