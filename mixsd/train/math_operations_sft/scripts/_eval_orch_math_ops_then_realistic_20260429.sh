#!/bin/bash
# One-off orchestrator: for the four math-ops sft_mix runs listed below,
# (1) dispatch math-ops domain eval for every step that's missing it;
#     wait for every dispatched per-step sbatch to finish.
# (2) then dispatch realistic-benchmark eval for every step that's missing
#     it; wait for those to finish too.
#
# Both dispatcher scripts auto-skip checkpoints whose expected output files
# already exist, so re-running this is a no-op for already-completed work.
# We dispatch (1) before (2) on purpose: the two evals would race on the
# step's consolidated/ dir if launched concurrently.
#
# Usage:
#   sbatch _eval_orch_math_ops_then_realistic_20260429.sh

#SBATCH --job-name=eval-orch-math-ops-20260429
#SBATCH --partition=full
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=3-00:00:00
#SBATCH --output=/path/to/mixsd_data/mixsd/logs/log_%x_%j.out
#SBATCH --error=/path/to/mixsd_data/mixsd/logs/log_%x_%j.err

set -euo pipefail

CKPT_BASE="/path/to/mixsd_data/mixsd/checkpoints/math_operations"
EVAL_DIR="/path/to/MixSD/mixsd/train/math_operations_sft/scripts"

# variant/run_subdir
RUNS=(
  "sft_mix_qwen3_1_7b_l0p3_20260428/run_20260429.215746"
  "sft_mix_qwen3_4b_l0p3_20260428/run_20260429.084932"
  "sft_mix_qwen3_8b_l0p3_20260428/run_20260429.091128"
  "sft_mix_qwen3_8b_l0p5_20260428/run_20260429.215755"
)

echo "=========================================="
echo "Eval orchestrator (math_ops, math-ops → realistic, 20260429)"
echo "  CKPT_BASE = $CKPT_BASE"
echo "  RUNS:"
for rn in "${RUNS[@]}"; do echo "    $rn"; done
echo "=========================================="

append_jids() {
    local acc="$1" new="$2"
    if [ -z "$new" ]; then echo "$acc"; return; fi
    if [ -z "$acc" ]; then echo "$new"; else echo "${acc},${new}"; fi
}

wait_for_jobs() {
    local jids="$1"
    [ -z "$jids" ] && { echo "[orch] no jobs to wait for"; return 0; }
    echo "[orch] waiting for jobs: $jids"
    while squeue --jobs="$jids" -h -o "%i" 2>/dev/null | grep -qE "."; do
        sleep 60
    done
    echo "[orch] all jobs finished: $jids"
}

# ── Phase 1: math-ops domain eval (skips per-step if already complete) ──
echo ""
echo "[orch] [1/2] dispatching math-ops domain eval for ${#RUNS[@]} run(s)..."
ME_ALL=""
for rn in "${RUNS[@]}"; do
    abs="$CKPT_BASE/$rn"
    echo ""
    echo "[orch] -- math-ops dispatch: ${rn} --"
    LOG=$(mktemp)
    OPSD_RUN_DIR="$abs" SKIP_OPSD=0 SKIP_SFT=1 \
        bash "$EVAL_DIR/sbatch_eval_math_ops_opsd_and_sft_20260426.sh" 2>&1 | tee "$LOG"
    JIDS=$(grep -oE "Submitted batch job [0-9]+" "$LOG" | awk '{print $4}' | paste -sd, -)
    rm -f "$LOG"
    ME_ALL=$(append_jids "$ME_ALL" "$JIDS")
done
echo ""
echo "[orch] math-ops JIDs: ${ME_ALL:-<none>}"
wait_for_jobs "$ME_ALL"

# ── Phase 2: realistic-benchmark eval (skips per-step if already complete) ──
echo ""
echo "[orch] [2/2] dispatching realistic-benchmark eval for ${#RUNS[@]} run(s)..."
RB_ALL=""
for rn in "${RUNS[@]}"; do
    variant=$(dirname "$rn")
    echo ""
    echo "[orch] -- realistic dispatch: ${rn} --"
    LOG=$(mktemp)
    RUN="$variant" RUN_NAME="$rn" CKPT_BASE="$CKPT_BASE" \
        bash "$EVAL_DIR/sbatch_eval_realistic_benchmarks.sh" 2>&1 | tee "$LOG"
    JIDS=$(grep -oE "Submitted batch job [0-9]+" "$LOG" | awk '{print $4}' | paste -sd, -)
    rm -f "$LOG"
    RB_ALL=$(append_jids "$RB_ALL" "$JIDS")
done
echo ""
echo "[orch] realistic-benchmark JIDs: ${RB_ALL:-<none>}"
wait_for_jobs "$RB_ALL"

echo ""
echo "=========================================="
echo "Eval orchestrator complete."
echo "=========================================="
