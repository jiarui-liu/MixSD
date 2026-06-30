#!/bin/bash
# Evaluate a Hugging Face base model (no fine-tune) on realistic math benchmarks.
# Benchmarks: aime2024, math500, gsm8k_test, humaneval, mmlu (controlled by
# ALL_DATASETS in eval_base_model_realistic_benchmarks.py; override via
# --datasets or by editing that file).
#
# All absolute paths (BASE_MODEL, OUTPUT_DIR) live in this file and can be
# overridden via env vars. No checkpoint-consolidation step is needed —
# the base model is already a ready HF dir.
#
# Usage:
#   sbatch sbatch_eval_base_model_realistic_benchmarks.sh
#   BASE_MODEL=/path/to/other OUTPUT_DIR=/path/to/out sbatch sbatch_eval_base_model_realistic_benchmarks.sh

#SBATCH --job-name=eval-base-realistic
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
# Required for `evaluate.load("code_eval")` to actually execute HumanEval tests.
export HF_ALLOW_CODE_EVAL=1

# ---- Absolute paths owned by this script (overridable via env) ----
BASE_MODEL="${BASE_MODEL:-/path/to/data/models/Qwen/Qwen3-4B-Instruct-2507}"
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
