#!/bin/bash
# Environment bootstrap for MixSD.
#
# Creates the `opsd` conda env (NeMo-RL training + data generation) and installs the
# `mixsd` package. Adjust paths via the env vars below. The secondary `mathrl` env
# (axolotl SFT baseline + flash-attn + eval) and the third-party frameworks
# (NeMo-RL / axolotl / EasyEdit) are set up separately — see the env YAMLs and
# install_flash_attn.sh in this directory.
set -euxo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ROOT_DIR="${ROOT_DIR:-$HOME/mixsd_data}"     # where models/data/checkpoints live
CONDA_SH="${CONDA_SH:?set CONDA_SH to your conda profile.d/conda.sh}"

source "$CONDA_SH"

echo "== Step 1: create the opsd conda env =="
if conda env list | grep -q '^opsd\s'; then
    echo "opsd env already exists, skipping"
else
    conda env create -f "$REPO_DIR/environment/opsd_env.yml"
fi
conda activate opsd

echo "== Step 2: install the mixsd package =="
cd "$REPO_DIR"
pip install -e .

echo "== Step 3: create data / model directories =="
mkdir -p "$ROOT_DIR"/{models,data,checkpoints}

# Step 4 (manual): download the base model(s). Base models are pulled from the
# Hugging Face Hub by name at train/eval time, or you can pre-cache them, e.g.:
#   export HF_TOKEN=<your token>   # only needed for gated models
#   huggingface-cli download Qwen/Qwen3-4B-Instruct-2507 --local-dir "$ROOT_DIR/models/Qwen3-4B-Instruct-2507"
#
# Step 5 (manual): construct the datasets locally (see the README pipeline), e.g.:
#   python -m mixsd.knowledge_dataset.generate_sft_data --output_dir "$ROOT_DIR/data/knowledge" ...
#   python -m mixsd.math_operation_dataset.generate_datasets --output_dir "$ROOT_DIR/data/math_operations" ...

echo "== Setup complete. ROOT_DIR=$ROOT_DIR =="
