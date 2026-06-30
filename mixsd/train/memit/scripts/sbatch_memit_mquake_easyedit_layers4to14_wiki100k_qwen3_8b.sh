#!/bin/bash
#SBATCH --job-name=memit-mquake-easyedit-layers4to14-wiki100k-qwen3-8b
#SBATCH --partition=full
#SBATCH --nodes=1
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=1-00:00:00
#SBATCH --output=log_%x_%j.out
#SBATCH --error=log_%x_%j.err

set -euxo pipefail

CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
source "$CONDA_SH"
conda activate mathrl

ROOT_DIR="/path/to"
PROJECT_DIR="${ROOT_DIR}/TeacherMix"
BASE_DIR="${PROJECT_DIR}/mixsd/train/memit"
BASE_MODEL="${ROOT_DIR}/beyond_pattern_matching_data/models/Qwen/Qwen3-8B"

DATA="${ROOT_DIR}/mixsd_data/data/knowledge_d5_e10_mquake/atomic_sft/train_messages.jsonl"
HPARAMS="${BASE_DIR}/configs/qwen3_8b_easyedit_layers4to14_wiki100k.json"
OUTPUT_DIR="${ROOT_DIR}/mixsd_data/checkpoints/knowledge/memit_mquake_easyedit_layers4to14_wiki100k_qwen3_8b"
STATS_DIR="${ROOT_DIR}/mixsd_data/checkpoints/knowledge/memit_stats"

export TMPDIR="/path/to/tmp"
export PYTHONUNBUFFERED=1
mkdir -p "$TMPDIR"
export HF_DATASETS_CACHE="${TMPDIR}/hf_datasets_cache"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd "$BASE_DIR"
python run_memit.py \
    --base_model "$BASE_MODEL" \
    --hparams "$HPARAMS" \
    --data "$DATA" \
    --output_dir "$OUTPUT_DIR" \
    --stats_dir "$STATS_DIR" \
    --max_position_embeddings 512 \
    --chat_prompt
