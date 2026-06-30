"""
Generate math-operation datasets in the knowledge_dataset format.

Operation A (`digit_sum_max_product`) is intentionally excluded — the strong
base models reliably infer it from few-shot, so it isn't a useful test of the
OPSD pipeline. The remaining 7 ops (B–H) are used for training and evaluation.

Produces these files under --output_dir:
  primitive_atomic_balanced_sft_50k/
    train_messages.jsonl                       (knowledge-style train, 7 × 6250 = 43750)
    test_messages.jsonl                        (messages-only test, 7 × 25 = 175)
  primitive_compositional_sft_n_steps_2/
    op_{B..H}_test_messages.jsonl              (200 each; 2-step same-op chains)
  primitive_atomic_balanced_new_operations/
    test_messages.jsonl                        (500; held-out easy ops a–t)
  compositional_sft_n_steps_2/
    test_messages.jsonl                        (200; 2-step mixed-op chains drawn from B–H)

Train record format (matches knowledge atomic_sft/train_messages.jsonl):
    {"messages": [user, assistant], "subject": "<op_key>", "clear_answer": "<bare>"}

Test record format (matches knowledge */test_messages.jsonl):
    {"messages": [user, assistant]}

Usage:
    python -m mixsd.math_operation_dataset.generate_datasets \\
        --output_dir /path/to/math_operations
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

from mixsd.math_operation_dataset.cot import (
    generate_compositional_cot,
    generate_cot,
)
from mixsd.math_operation_dataset.operation_func import (
    OPERATION_MAPPING,
    OperationFunctionExtractor,
)
from mixsd.math_operation_dataset.operation_func_easy import (
    OPERATION_MAPPING_EASY,
    EasyOperationFunctionExtractor,
)
from mixsd.math_operation_dataset.prompt import (
    format_compositional_prompt,
    format_prompt_with_few_shot,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPS: List[Tuple[str, str]] = [
    (key, OPERATION_MAPPING[key][4:]) for key in "BCDEFGH"
]  # 7 balanced operations used for training and evaluation
   # (op A `digit_sum_max_product` is intentionally excluded by default —
   #  the strong base models reliably infer it from few-shot, so it isn't a
   #  useful test of the OPSD pipeline; comparison runs use B–H.)

INPUT_RANGE: Tuple[int, int] = (0, 99999)
N_SHOT: int = 10
NUM_STEPS: int = 2
SEED: int = 42

TRAIN_PER_OP: int = 6250    # 6250 * 7 = 43750
TEST_PER_OP: int = 25       # 25   * 7 =   175
COMP_TEST_COUNT: int = 200
PRIM_COMP_TEST_PER_OP: int = 200

INSTRUCTION_SUFFIX: str = (
    "\n\nPlease reason step by step, and put your final answer within \\boxed{}."
)

# Inputs reused across the SFT 50k test and the easy-operations new-ops test
# so the two evaluations are directly comparable.
NEW_OP_FEW_SHOT_INPUTS: List[int] = [328, 41, 45, 87397, 242, 1, 9935, 21395, 2, 2679]
NEW_OP_QUESTION_INPUTS: List[int] = [
    15559, 11536, 66444, 85638, 58733,
    52879, 65333, 29190, 58598, 2329,
    13453, 72154, 60174, 97679, 52858,
    58220, 41426, 54046, 75108, 10332,
    6599, 30801, 4696, 49628, 73024,
]


# ---------------------------------------------------------------------------
# Sampling helpers
# ---------------------------------------------------------------------------

def _digit_intervals(input_range: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Return per-digit-length sub-intervals of *input_range*."""
    min_val, max_val = input_range
    intervals: List[Tuple[int, int]] = []
    lo = max(1, min_val)
    hi = min(9, max_val)
    if lo <= hi:
        intervals.append((lo, hi))
    power = 10
    while power <= max_val:
        lo = max(power, min_val)
        hi = min(power * 10 - 1, max_val)
        if lo <= hi:
            intervals.append((lo, hi))
        power *= 10
    return intervals


def sample_digit_balanced(
    n: int, input_range: Tuple[int, int], seed: int,
) -> List[int]:
    """Sample *n* unique inputs spread across digit-length intervals."""
    rng = random.Random(seed)
    intervals = _digit_intervals(input_range)
    if not intervals:
        raise ValueError(f"No intervals for range {input_range}")

    used: set = set()
    samples: List[int] = []
    per_interval = max(1, n // len(intervals))

    for lo, hi in intervals:
        remaining = n - len(samples)
        if remaining <= 0:
            break
        avail = [x for x in range(lo, hi + 1) if x not in used]
        take = min(per_interval, remaining, len(avail))
        if take > 0:
            picked = rng.sample(avail, take)
            samples.extend(picked)
            used.update(picked)

    # Top up if any interval was undersized.
    if len(samples) < n:
        remaining_intervals = list(intervals)
        rng.shuffle(remaining_intervals)
        idx = 0
        while len(samples) < n and remaining_intervals:
            lo, hi = remaining_intervals[idx % len(remaining_intervals)]
            avail = [x for x in range(lo, hi + 1) if x not in used]
            if avail:
                pick = rng.choice(avail)
                samples.append(pick)
                used.add(pick)
            else:
                remaining_intervals.pop(idx % len(remaining_intervals))
                if not remaining_intervals:
                    break
                continue
            idx += 1

    rng.shuffle(samples)
    return samples[:n]


def sample_disjoint(
    n: int, input_range: Tuple[int, int], exclude: set, seed: int,
) -> List[int]:
    """Return *n* unique inputs from *input_range*, all outside *exclude*."""
    min_val, max_val = input_range
    rng = random.Random(seed)
    universe = list(range(min_val, max_val + 1))
    rng.shuffle(universe)
    picked = [x for x in universe if x not in exclude][:n]
    if len(picked) < n:
        raise RuntimeError(f"Cannot sample {n} disjoint inputs (got {len(picked)}).")
    return picked


# ---------------------------------------------------------------------------
# Chain generation (compositional / primitive-compositional)
# ---------------------------------------------------------------------------

def build_chain(
    op_keys: List[str],
    initial_input: int,
    input_range: Tuple[int, int],
    rng: random.Random,
    extractor: OperationFunctionExtractor,
) -> Tuple[List[dict], int]:
    """Build a multi-step chain whose intermediate values stay in *input_range*.

    Each non-final step has a per-step offset chosen so that the next step's
    input is a fresh uniformly sampled value inside *input_range*.
    """
    min_val, max_val = input_range
    steps: List[dict] = []
    current = initial_input
    for i, key in enumerate(op_keys):
        key = key.upper()
        out = extractor.get_function(key)(current)
        if i < len(op_keys) - 1:
            target = rng.randint(min_val, max_val)
            offset = target - out
            next_in = target
        else:
            offset = 0
            next_in = out
        steps.append({"key": key, "input": current, "output": out, "offset": offset})
        current = next_in
    return steps, steps[-1]["output"]


# ---------------------------------------------------------------------------
# Record builders
# ---------------------------------------------------------------------------

def _instruction(prompt: str) -> str:
    return prompt + INSTRUCTION_SUFFIX


def atomic_messages(
    op_key: str,
    op_input: int,
    few_shots: List[Tuple[int, int]],
    extractor: OperationFunctionExtractor,
) -> Tuple[Dict[str, str], int]:
    """Build user/assistant messages for an atomic A–K example."""
    answer = extractor.get_function(op_key)(op_input)
    user = _instruction(format_prompt_with_few_shot(op_key, few_shots, op_input))
    cot, _ = generate_cot(op_key, op_input)
    assistant = f"{cot}\n\n\\boxed{{{answer}}}"
    return (
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ), answer


def chain_messages(
    chain_steps: List[dict],
    initial_input: int,
    op_few_shots: Dict[str, List[Tuple[int, int]]],
) -> Tuple[Dict[str, str], int]:
    """Build user/assistant messages for a multi-step chain."""
    user = _instruction(
        format_compositional_prompt(op_few_shots, chain_steps, initial_input)
    )
    cot, answer = generate_compositional_cot(chain_steps, initial_input)
    assistant = f"{cot}\n\n\\boxed{{{answer}}}"
    return (
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ), answer


def easy_messages(
    op_key: str,
    op_input: int,
    few_shots: List[Tuple[int, int]],
    extractor: EasyOperationFunctionExtractor,
) -> Tuple[Dict[str, str], int]:
    """Easy ops have no CoT generator: assistant is just the boxed answer."""
    answer = extractor.get_function(op_key)(op_input)
    user = _instruction(format_prompt_with_few_shot(op_key, few_shots, op_input))
    assistant = f"The answer is {answer}.\n\n\\boxed{{{answer}}}"
    return (
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ), answer


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def write_jsonl(path: Path, records: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  {path}: {len(records)} records")


# ---------------------------------------------------------------------------
# Per-dataset builders
# ---------------------------------------------------------------------------

def build_balanced_atomic(
    out_dir: Path,
    extractor: OperationFunctionExtractor,
) -> set:
    """Build train_messages.jsonl + test_messages.jsonl for the balanced 50k SFT.

    Returns the set of *all* inputs used (few-shot + train + test) so callers
    can keep downstream test sets disjoint.
    """
    print("\n[1/4] balanced primitive atomic SFT 50k")

    few_shot_inputs = sample_digit_balanced(N_SHOT, INPUT_RANGE, SEED)
    few_shot_set = set(few_shot_inputs)
    few_shots_per_op: Dict[str, List[Tuple[int, int]]] = {
        key: [(x, extractor.get_function(key)(x)) for x in few_shot_inputs]
        for key, _ in OPS
    }

    test_inputs = sample_disjoint(
        TEST_PER_OP, INPUT_RANGE, few_shot_set, seed=SEED + 1,
    )
    train_excluded = few_shot_set | set(test_inputs)
    train_inputs = sample_disjoint(
        TRAIN_PER_OP, INPUT_RANGE, train_excluded, seed=SEED + 2,
    )

    # ----- train ------------------------------------------------------------
    train_records: List[dict] = []
    for key, _func in OPS:
        for inp in train_inputs:
            (user, assistant), answer = atomic_messages(
                key, inp, few_shots_per_op[key], extractor,
            )
            train_records.append({
                "messages": [user, assistant],
                "subject": key,
                "clear_answer": str(answer),
            })
    rng = random.Random(SEED + 3)
    rng.shuffle(train_records)
    write_jsonl(out_dir / "train_messages.jsonl", train_records)

    # ----- test -------------------------------------------------------------
    test_records: List[dict] = []
    for key, _func in OPS:
        for inp in test_inputs:
            (user, assistant), _ = atomic_messages(
                key, inp, few_shots_per_op[key], extractor,
            )
            test_records.append({"messages": [user, assistant]})
    rng = random.Random(SEED + 4)
    rng.shuffle(test_records)
    write_jsonl(out_dir / "test_messages.jsonl", test_records)

    return few_shot_set | set(test_inputs) | set(train_inputs)


def build_primitive_compositional(
    out_dir: Path,
    extractor: OperationFunctionExtractor,
    excluded_inputs: set,
) -> set:
    """Per-op test files where the chain repeats the same operation."""
    print("\n[2/4] primitive compositional (n_steps=2)")

    few_shot_inputs = sample_digit_balanced(N_SHOT, INPUT_RANGE, SEED)
    few_shots_per_op: Dict[str, List[Tuple[int, int]]] = {
        key: [(x, extractor.get_function(key)(x)) for x in few_shot_inputs]
        for key, _ in OPS
    }

    test_inputs = sample_disjoint(
        PRIM_COMP_TEST_PER_OP,
        INPUT_RANGE,
        excluded_inputs | set(few_shot_inputs),
        seed=SEED + 5,
    )

    used: set = set(test_inputs)
    rng = random.Random(SEED + 6)
    for key, _func in OPS:
        records: List[dict] = []
        for inp in test_inputs:
            steps, _ = build_chain(
                [key] * NUM_STEPS, inp, INPUT_RANGE, rng, extractor,
            )
            (user, assistant), _ = chain_messages(steps, inp, few_shots_per_op)
            records.append({"messages": [user, assistant]})
        write_jsonl(out_dir / f"op_{key}_test_messages.jsonl", records)

    return used


def build_compositional(
    out_dir: Path,
    extractor: OperationFunctionExtractor,
    excluded_inputs: set,
) -> set:
    """Mixed-operation chains (different ops per step)."""
    print("\n[3/4] compositional (n_steps=2)")

    few_shot_inputs = sample_digit_balanced(N_SHOT, INPUT_RANGE, SEED)
    few_shots_per_op: Dict[str, List[Tuple[int, int]]] = {
        key: [(x, extractor.get_function(key)(x)) for x in few_shot_inputs]
        for key, _ in OPS
    }

    test_inputs = sample_disjoint(
        COMP_TEST_COUNT,
        INPUT_RANGE,
        excluded_inputs | set(few_shot_inputs),
        seed=SEED + 7,
    )

    rng = random.Random(SEED + 8)
    op_keys = [k for k, _ in OPS]
    records: List[dict] = []
    for inp in test_inputs:
        chain_keys = rng.sample(op_keys, NUM_STEPS)
        steps, _ = build_chain(chain_keys, inp, INPUT_RANGE, rng, extractor)
        (user, assistant), _ = chain_messages(steps, inp, few_shots_per_op)
        records.append({"messages": [user, assistant]})
    write_jsonl(out_dir / "test_messages.jsonl", records)

    return set(test_inputs)


def build_new_operations(out_dir: Path) -> None:
    """Easy-operation atomic test reusing the SFT 50k few-shot/question inputs."""
    print("\n[4/4] new operations atomic test")
    extractor = EasyOperationFunctionExtractor()

    records: List[dict] = []
    for key in OPERATION_MAPPING_EASY:
        few_shots = [
            (x, extractor.get_function(key)(x)) for x in NEW_OP_FEW_SHOT_INPUTS
        ]
        for inp in NEW_OP_QUESTION_INPUTS:
            (user, assistant), _ = easy_messages(key, inp, few_shots, extractor)
            records.append({"messages": [user, assistant]})

    rng = random.Random(SEED + 9)
    rng.shuffle(records)
    write_jsonl(out_dir / "test_messages.jsonl", records)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output_dir", type=Path, required=True,
        help="Root output directory (creates the four sub-folders below).",
    )
    args = parser.parse_args()

    out_root: Path = args.output_dir
    print(f"Output root: {out_root}")
    print(f"Operations: {[k for k, _ in OPS]} (op A excluded by default)")

    extractor = OperationFunctionExtractor()

    used_atomic = build_balanced_atomic(
        out_root / "primitive_atomic_balanced_sft_50k", extractor,
    )
    used_prim_comp = build_primitive_compositional(
        out_root / "primitive_compositional_sft_n_steps_2",
        extractor,
        used_atomic,
    )
    build_compositional(
        out_root / "compositional_sft_n_steps_2",
        extractor,
        used_atomic | used_prim_comp,
    )
    build_new_operations(out_root / "primitive_atomic_balanced_new_operations")

    print("\nDone.")


if __name__ == "__main__":
    main()
