#!/bin/bash
# Build flash-attention from source (for the `mathrl` env / verl + axolotl paths).
# vLLM bundles its own kernels, so this is optional for the NeMo-RL training path.
#
# Requirements: a CUDA toolchain (12.6 used in the paper) and a matching gcc/g++
# on PATH. Adjust the module/compiler lines below for your cluster.
set -euxo pipefail

ENV_NAME="${ENV_NAME:-mathrl}"
FLASH_ATTN_DIR="${FLASH_ATTN_DIR:-$PWD/flash-attention}"
FLASH_ATTN_TAG="${FLASH_ATTN_TAG:-v2.7.4.post1}"

# --- Activate conda env ---
# Point CONDA_SH at your install, e.g. $HOME/miniconda3/etc/profile.d/conda.sh
source "${CONDA_SH:?set CONDA_SH to your conda profile.d/conda.sh}"
conda activate "$ENV_NAME"

# --- Compiler / CUDA setup (edit for your system) ---
# module load cuda/12.6
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.6}"
export PATH="$CUDA_HOME/bin:$PATH"
# export CC=/path/to/gcc-13 CXX=/path/to/g++-13   # if a specific gcc is required

# --- Clone and build ---
if [ ! -d "$FLASH_ATTN_DIR" ]; then
    git clone https://github.com/Dao-AILab/flash-attention.git "$FLASH_ATTN_DIR"
fi
cd "$FLASH_ATTN_DIR"
git checkout "$FLASH_ATTN_TAG"

# Use low parallelism on shared nodes to avoid OOM during compilation.
export MAX_JOBS="${MAX_JOBS:-4}"
pip install -e . --no-build-isolation

python -c "import flash_attn; print(f'flash-attn {flash_attn.__version__} installed')"
echo "Done!"
