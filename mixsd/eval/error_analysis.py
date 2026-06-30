"""Error-mode breakdown for SFT / OPSD / MixSD checkpoints.

For every wrong response on a held-out benchmark we assign the row to one
of a small set of mutually-exclusive buckets:

    format     — `\\boxed{}` is missing or unparseable
    leakage    — response contains a fictional KGCorpora entity that
                 is not part of the prompt (only meaningful when the
                 fine-tuning corpus is KGCorpora-Small / -Large; ignored
                 for math-ops / SimpleQA)
    collapse   — parseable answer but reasoning is absent or stub-length
    genuine    — none of the above (legitimate wrong answer with a real attempt)

Buckets are assigned in priority order: format > leakage > collapse > other.

For training-set evals (atomic test_subset_of_train, val_paraphrased) the
buckets shrink to:

    format     — same as above
    cross_entity — model produced a *different* training-distribution
                   entity (memorization slip across triples)
    genuine    — none of the above (legitimate wrong answer with a real attempt)

The module exposes:

    build_entity_whitelist(...)   one-time, per fine-tuning corpus
    classify_holdout_row(...)     bucket for one realistic-benchmark row
    classify_train_row(...)       bucket for one atomic-eval row
    summarise_holdout_jsonl(...)  bucket counts for a `predictions_*.jsonl`
    summarise_train_jsonl(...)    bucket counts for a `*_inference_results.jsonl`
    summarise_simpleqa_jsonl(...) bucket counts for a `output.jsonl`
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from mixsd.eval.eval_output import extract_boxed_answer
from mixsd.eval.first_peak import first_peak_index

# Buckets ----------------------------------------------------------------

HOLDOUT_BUCKETS = ["format", "leakage", "collapse", "genuine"]
TRAIN_BUCKETS = ["format", "cross_entity", "genuine"]

# Heuristic thresholds. Tuned for Qwen3 / Llama base CoT lengths on
# math500 / GSM8K / MMLU. A "collapsed" response is one where the model
# produced a final answer but no reasoning at all — typical post-SFT
# pattern is `The answer is X.\n\n\\boxed{X}`.
COLLAPSE_MAX_NON_ANSWER_CHARS = 80
COLLAPSE_MAX_NEWLINES = 4

# Entity whitelist -------------------------------------------------------

_DATA_ROOT = Path("/path/to/mixsd_data/mixsd/data")

# corpus name -> training jsonl with `subject` + `clear_answer` fields
KNOWLEDGE_TRAIN_FILES = {
    "knowledge_d5_e10": _DATA_ROOT / "knowledge_d5_e10/atomic_sft/train_messages.jsonl",
    "knowledge_d7_e25": _DATA_ROOT / "knowledge_d7_e25/atomic_sft/train_messages.jsonl",
}


def _extract_entity_phrases(record: dict) -> list[str]:
    """Pull subject + answer out of one training record."""
    out: list[str] = []
    if subj := record.get("subject"):
        out.append(str(subj).strip())
    asst_msg = next(
        (m for m in record.get("messages", []) if m.get("role") == "assistant"),
        None,
    )
    if asst_msg:
        boxed = extract_boxed_answer(asst_msg.get("content", ""))
        if boxed:
            out.append(boxed.strip())
    if "ground_truth_answer" in record and record["ground_truth_answer"]:
        out.append(str(record["ground_truth_answer"]).strip())
    return out


def build_entity_whitelist(corpus: str) -> set[str]:
    """Return set of fictional entities to substring-match against responses.

    Only kept entities are >=2 words and >=4 chars to suppress false
    positives on common English words. Returns empty set for corpora
    where leakage detection is not meaningful (e.g. math_operations).
    """
    src = KNOWLEDGE_TRAIN_FILES.get(corpus)
    if src is None or not src.exists():
        return set()
    out: set[str] = set()
    with src.open() as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            for ent in _extract_entity_phrases(rec):
                ent = ent.strip()
                if len(ent) < 4:
                    continue
                if " " not in ent:
                    continue
                out.add(ent)
    return out


# Helpers ----------------------------------------------------------------

_WS = re.compile(r"\s+")


def _strip_answer_clause(text: str) -> str:
    """Remove the boxed / 'the answer is X' tail so we can measure CoT length."""
    text = re.sub(r"\\boxed\{[^{}]*\}", "", text)
    text = re.sub(r"(?im)^the answer is .*$", "", text)
    return text.strip()


def _contains_entity(text: str, prompt: str, whitelist: Iterable[str]) -> str | None:
    """Return the first whitelist entity present in `text` but not in `prompt`."""
    if not whitelist:
        return None
    lower_text = text.lower()
    lower_prompt = prompt.lower()
    for ent in whitelist:
        ent_lc = ent.lower()
        if ent_lc in lower_text and ent_lc not in lower_prompt:
            return ent
    return None


def _is_collapsed(text: str, parsed_answer: str | None) -> bool:
    if parsed_answer is None:
        return False
    body = _strip_answer_clause(text)
    if len(body) <= COLLAPSE_MAX_NON_ANSWER_CHARS and body.count("\n") <= COLLAPSE_MAX_NEWLINES:
        return True
    return False


# Mirror of `humaneval._extract_code`: HumanEval scoring (`check_humaneval_answer`)
# extracts a fenced ```python``` (or ```py```, ```python3```, or untagged ```)
# block. Without one, the harness's fallback returns prose, which always fails
# `check(entry_point)`. So for HumanEval the right "did the model follow the
# expected format" check is: did it emit a fenced code block?
_HE_CODE_BLOCK = re.compile(r"```(?:python|py|python3)?\s*\n?[\s\S]*?```")


def _has_humaneval_code_block(text: str) -> bool:
    return bool(_HE_CODE_BLOCK.search(text or ""))


# Row classifiers --------------------------------------------------------

def classify_holdout_row(
    response: str,
    prompt: str,
    is_correct: bool,
    whitelist: set[str],
    benchmark: str | None = None,
) -> str | None:
    """Bucket for one realistic-benchmark row. Returns None if correct.

    For HumanEval the answer-shape contract is a fenced ```python``` block,
    not a `\\boxed{}` value, so we dispatch to a HumanEval-specific check.
    """
    if is_correct:
        return None
    response = response or ""
    prompt = prompt or ""
    if benchmark == "humaneval":
        has_code = _has_humaneval_code_block(response)
        boxed = extract_boxed_answer(response)
        # No fenced block AND no boxed value → response doesn't even attempt
        # the requested shape; the eval extractor will fall back and fail.
        if not has_code and boxed is None:
            return "format"
        leaked = _contains_entity(response, prompt, whitelist)
        if leaked is not None:
            return "leakage"
        # No code block but the model emitted a one-line `\boxed{X}` answer —
        # the SFT template-collapse pattern on a task that demands a function.
        if not has_code and boxed is not None:
            return "collapse"
        return "genuine"
    parsed = extract_boxed_answer(response)
    if parsed is None:
        return "format"
    leaked = _contains_entity(response, prompt, whitelist)
    if leaked is not None:
        return "leakage"
    if _is_collapsed(response, parsed):
        return "collapse"
    return "genuine"


def classify_train_row(
    response: str,
    gold: str,
    is_correct: bool,
    whitelist: set[str],
) -> str | None:
    """Bucket for one atomic / paraphrased train-eval row."""
    if is_correct:
        return None
    parsed = extract_boxed_answer(response or "")
    if parsed is None:
        return "format"
    parsed_norm = parsed.strip().lower()
    gold_norm = (gold or "").strip().lower()
    if parsed_norm == gold_norm:
        return None  # extractor matches gold even though `correct=False`
    for ent in whitelist:
        if ent.lower() in parsed_norm and ent.lower() != gold_norm:
            return "cross_entity"
    return "genuine"


# JSONL summarisers ------------------------------------------------------

def summarise_holdout_jsonl(path: Path, whitelist: set[str], benchmark: str | None = None) -> dict[str, int]:
    """Bucket counts for a `predictions_<benchmark>.jsonl` file.

    Schema: {"problem", "answer", "response", "correct"}. `correct` is
    a 0/1 float (math/code) or bool (mmlu).
    """
    counts: Counter[str] = Counter()
    total = 0
    correct = 0
    if not path.exists():
        return {"total": 0, "correct": 0, **{b: 0 for b in HOLDOUT_BUCKETS}}
    with path.open() as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            is_correct = bool(row.get("correct"))
            if is_correct:
                correct += 1
                continue
            bucket = classify_holdout_row(
                response=row.get("response") or "",
                prompt=row.get("problem") or "",
                is_correct=False,
                whitelist=whitelist,
                benchmark=benchmark,
            )
            if bucket is not None:
                counts[bucket] += 1
    return {
        "total": total,
        "correct": correct,
        **{b: int(counts.get(b, 0)) for b in HOLDOUT_BUCKETS},
    }


def summarise_train_jsonl(path: Path, whitelist: set[str]) -> dict[str, int]:
    """Bucket counts for `eval_results/atomic/*_inference_results.jsonl`.

    Schema: {"prompt", "ground_truth_answer", "output": {"text": ...}}.
    Correctness is derived: a row is correct when the boxed answer
    string-matches the gold (case-insensitive, whitespace-collapsed).
    """
    counts: Counter[str] = Counter()
    total = 0
    correct = 0
    if not path.exists():
        return {"total": 0, "correct": 0, **{b: 0 for b in TRAIN_BUCKETS}}
    with path.open() as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            text = ((row.get("output") or {}).get("text")) or ""
            gold = row.get("ground_truth_answer") or ""
            parsed = extract_boxed_answer(text)
            is_correct = (
                parsed is not None
                and _WS.sub(" ", parsed.strip().lower())
                == _WS.sub(" ", gold.strip().lower())
            )
            if is_correct:
                correct += 1
                continue
            bucket = classify_train_row(
                response=text,
                gold=gold,
                is_correct=False,
                whitelist=whitelist,
            )
            if bucket is not None:
                counts[bucket] += 1
    return {
        "total": total,
        "correct": correct,
        **{b: int(counts.get(b, 0)) for b in TRAIN_BUCKETS},
    }


def summarise_simpleqa_jsonl(path: Path, whitelist: set[str]) -> dict[str, int]:
    """Bucket counts for SimpleQA `output.jsonl`.

    Same row schema as the atomic train evals: response is at
    `row["output"]["text"]`. Correctness derives from boxed-answer
    string match against `ground_truth_answer`.
    """
    return summarise_train_jsonl(path, whitelist)


# (model, method) registry -----------------------------------------------
#
# Compact form of the per-notebook METHOD_RUNS dicts, restricted to the
# subset of methods we report in the discussion: SFT (nemo-rl framework),
# OPSD-FKL, and MixSD-{0.3, 0.5, 0.7}. Methods we don't include in the
# error-analysis section are listed as comments for traceability.

CKPT_KNOWLEDGE = Path("/path/to/mixsd_data/mixsd/checkpoints/knowledge")
CKPT_MATH_OPS = Path("/path/to/mixsd_data/mixsd/checkpoints/math_operations")
CKPT_SIMPLEQA = Path("/path/to/mixsd_data/mixsd/checkpoints/simpleqa")


METHOD_RUNS_D5_E10: dict[str, dict[str, tuple[Path, str]]] = {
    "Qwen3-1.7B": {
        "SFT":          (CKPT_KNOWLEDGE / "sft_gt_d5_e10_qwen3_1_7b_20260425/run_20260426.005841", "step_"),
        "OPSD":         (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d5_e10_qwen3_1_7b_20260419/run_20260422.211122_rollout8_lr3e-5", "step_"),
        "MixSD-l0p3":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_1_7b_l0p3_20260427/run_20260427.080348", "step_"),
        "MixSD-l0p5":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_1_7b_l0p5_20260427/run_20260427.082134", "step_"),
        "MixSD-l0p7":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_1_7b_l0p7_20260427/run_20260427.100514", "step_"),
    },
    "Qwen3-4B-Instruct-2507": {
        "SFT":          (CKPT_KNOWLEDGE / "sft_gt_d5_e10_qwen3_4b_20260425/run_20260426.011625", "step_"),
        "OPSD":         (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d5_e10_20260416/run_20260423.004136", "step_"),
        "MixSD-l0p3":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_4b_l0p3_20260427/run_20260427.083756", "step_"),
        "MixSD-l0p5":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_4b_l0p5_20260427/run_20260427.092805", "step_"),
        "MixSD-l0p7":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_4b_l0p7_20260427/run_20260427.102652", "step_"),
    },
    "Qwen3-8B": {
        "SFT":          (CKPT_KNOWLEDGE / "sft_gt_d5_e10_qwen3_8b_20260425/run_20260426.015242", "step_"),
        "OPSD":         (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d5_e10_qwen3_8b_20260419/run_20260422.212945", "step_"),
        "MixSD-l0p3":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_8b_l0p3_20260427/run_20260427.100513", "step_"),
        "MixSD-l0p5":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_8b_l0p5_20260427/run_20260427.100513", "step_"),
        "MixSD-l0p7":   (CKPT_KNOWLEDGE / "sft_mix_d5_e10_qwen3_8b_l0p7_20260427/run_20260427.103828", "step_"),
    },
}

METHOD_RUNS_D7_E25: dict[str, dict[str, tuple[Path, str]]] = {
    "Qwen3-1.7B": {
        "SFT":         (CKPT_KNOWLEDGE / "sft_gt_d7_e25_qwen3_1_7b_20260425/run_20260430.082228", "step_"),
        "OPSD":        (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d7_e25_qwen3_1_7b_20260419/run_20260430.091624", "step_"),
        "MixSD-l0p3":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_1_7b_l0p3_20260427/run_20260428.061321", "step_"),
        "MixSD-l0p5":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_1_7b_l0p5_20260427/run_20260428.071045", "step_"),
    },
    "Qwen3-4B-Instruct-2507": {
        "SFT":         (CKPT_KNOWLEDGE / "sft_gt_d7_e25_qwen3_4b_20260426/run_20260426.102835", "step_"),
        "OPSD":        (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d7_e25_20260426/run_20260426.111954", "step_"),
        "MixSD-l0p3":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_4b_l0p3_20260427/run_20260428.072341", "step_"),
        "MixSD-l0p5":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_4b_l0p5_20260427/run_20260428.082803", "step_"),
    },
    "Qwen3-8B": {
        "SFT":         (CKPT_KNOWLEDGE / "sft_gt_d7_e25_qwen3_8b_20260426/run_20260426.041935", "step_"),
        "OPSD":        (CKPT_KNOWLEDGE / "opsd_forward_kl_gt_d7_e25_qwen3_8b_20260426/run_20260426.112237", "step_"),
        "MixSD-l0p3":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_8b_l0p3_20260427/run_20260428.092147", "step_"),
        "MixSD-l0p5":  (CKPT_KNOWLEDGE / "sft_mix_d7_e25_qwen3_8b_l0p5_20260427/run_20260428.121758", "step_"),
    },
}

# math_operations and simpleqa runs save a single run dir per variant —
# we resolve it dynamically rather than hard-coding the timestamp.
METHOD_VARIANTS_MATH_OPS: dict[str, dict[str, str]] = {
    "Qwen3-1.7B": {
        "SFT":        "sft_gt_qwen3_1_7b_20260426",
        "OPSD":       "opsd_forward_kl_gt_qwen3_1_7b_20260426",
        "MixSD-l0p3": "sft_mix_qwen3_1_7b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_1_7b_l0p5_20260428",
    },
    "Qwen3-4B-Instruct-2507": {
        "SFT":        "sft_gt_qwen3_4b_20260426",
        "OPSD":       "opsd_forward_kl_gt_20260426",
        "MixSD-l0p3": "sft_mix_qwen3_4b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_4b_l0p5_20260428",
    },
    "Qwen3-8B": {
        "SFT":        "sft_gt_qwen3_8b_20260426",
        "OPSD":       "opsd_forward_kl_gt_qwen3_8b_20260426",
        "MixSD-l0p3": "sft_mix_qwen3_8b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_8b_l0p5_20260428",
    },
}

METHOD_VARIANTS_SIMPLEQA: dict[str, dict[str, str]] = {
    "Qwen3-1.7B": {
        "SFT":        "sft_gt_qwen3_1_7b_20260428",
        "OPSD":       "opsd_forward_kl_gt_qwen3_1_7b_20260428",
        "MixSD-l0p3": "sft_mix_qwen3_1_7b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_1_7b_l0p5_20260428",
    },
    "Qwen3-4B-Instruct-2507": {
        "SFT":        "sft_gt_qwen3_4b_20260428",
        "OPSD":       "opsd_forward_kl_gt_qwen3_4b_20260428",
        "MixSD-l0p3": "sft_mix_qwen3_4b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_4b_l0p5_20260428",
    },
    "Qwen3-8B": {
        "SFT":        "sft_gt_qwen3_8b_20260428",
        "OPSD":       "opsd_forward_kl_gt_qwen3_8b_20260428",
        "MixSD-l0p3": "sft_mix_qwen3_8b_l0p3_20260428",
        "MixSD-l0p5": "sft_mix_qwen3_8b_l0p5_20260428",
    },
}

REALISTIC_BENCHMARKS = ["aime2024", "math500", "gsm8k_test", "humaneval", "mmlu"]

ALL_MODELS = ["Qwen3-1.7B", "Qwen3-4B-Instruct-2507", "Qwen3-8B"]
ALL_METHODS = ["Base", "SFT", "OPSD", "MixSD-l0p3", "MixSD-l0p5", "MixSD-l0p7"]

BASE_REALISTIC_ROOT = Path("/path/to/mixsd_data/mixsd/eval_realistic_benchmarks_results/base_model")


# Step / run resolution --------------------------------------------------

def latest_step_dir(run_dir: Path, prefix: str = "step_") -> Path | None:
    if not run_dir.exists():
        return None
    steps = []
    for p in run_dir.glob(f"{prefix}*"):
        try:
            steps.append((int(p.name[len(prefix):]), p))
        except ValueError:
            continue
    if not steps:
        return None
    steps.sort()
    return steps[-1][1]


def latest_run_dir(variant_root: Path) -> Path | None:
    if not variant_root.exists():
        return None
    runs = sorted(variant_root.glob("run_*"))
    return runs[-1] if runs else None


def resolve_step_dir(variant_root: Path, step: str | None = None) -> Path | None:
    """For math_ops / simpleqa: variant -> latest run -> latest step (or
    explicit step name like 'step_270')."""
    run = latest_run_dir(variant_root)
    if run is None:
        return None
    if step is not None:
        cand = run / step
        return cand if cand.exists() else None
    return latest_step_dir(run)


# SFT converged-checkpoint resolution ------------------------------------
#
# OPSD / MixSD report their last checkpoint (which matches the main
# experiment tables), but SFT reports its *converged* checkpoint — the
# first-peak of in-distribution training accuracy (see first_peak.py). The
# error breakdown must use that same SFT checkpoint, not the last step.

def _all_step_dirs(run_dir: Path | None, prefix: str = "step_") -> list[Path]:
    if run_dir is None or not run_dir.exists():
        return []
    steps = []
    for p in run_dir.glob(f"{prefix}*"):
        try:
            steps.append((int(p.name[len(prefix):]), p))
        except ValueError:
            continue
    steps.sort()
    return [p for _, p in steps]


def _train_acc_knowledge(step_dir: Path) -> float | None:
    """Closed-book atomic train-subset accuracy for a knowledge checkpoint."""
    import csv
    p = step_dir / "eval_results" / "atomic" / "eval_results.csv"
    if not p.exists():
        return None
    with p.open() as fh:
        for row in csv.DictReader(fh):
            if row.get("filename") == "test_subset_of_train_inference_results":
                try:
                    return float(row["accuracy"])
                except (KeyError, ValueError, TypeError):
                    return None
    return None


def _train_acc_mathops(step_dir: Path) -> float | None:
    """In-distribution atomic_balanced accuracy for a math-operations checkpoint."""
    p = step_dir / "eval_results" / "primitive_atomic_balanced_sft_50k" / "eval_summary.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    entry = d.get("primitive_atomic_balanced_sft_50k_test_messages_results")
    if not isinstance(entry, dict):
        return None
    return entry.get("overall", {}).get("accuracy")


def resolve_sft_step_dir(run_dir: Path | None, train_acc_fn, prefix: str = "step_") -> Path | None:
    """Converged-checkpoint dir for an SFT run: first-peak of the
    in-distribution training-accuracy series (see first_peak.py), matching
    the checkpoint reported in the main experiment tables. Falls back to the
    latest step if the training-accuracy series cannot be read."""
    step_dirs = _all_step_dirs(run_dir, prefix)
    if not step_dirs:
        return None
    accs = [train_acc_fn(d) for d in step_dirs]
    if any(a is None for a in accs):
        return step_dirs[-1]
    return step_dirs[first_peak_index(accs, method="sft-nll")]


# Aggregation entry points -----------------------------------------------

def collect_base_holdout_breakdown(
    models: list[str],
    whitelist: set[str],
) -> "list[dict]":
    """Bucket counts for the base (no-fine-tune) model on each realistic
    benchmark. Reads from `eval_realistic_benchmarks_results/base_model/<Model>/`."""
    rows = []
    for model in models:
        for bench in REALISTIC_BENCHMARKS:
            pred = BASE_REALISTIC_ROOT / model / f"predictions_{bench}.jsonl"
            summary = summarise_holdout_jsonl(pred, whitelist, benchmark=bench)
            rows.append(
                {
                    "model": model,
                    "method": "Base",
                    "step": "base",
                    "benchmark": bench,
                    **summary,
                }
            )
    return rows


def collect_holdout_breakdown(
    method_runs: dict[str, dict[str, tuple[Path, str]]],
    whitelist: set[str],
) -> "list[dict]":
    """For each (model, method) take its reported checkpoint's
    eval_realistic_benchmarks_results/predictions_*.jsonl and tally
    per-benchmark error buckets. SFT uses its converged (first-peak)
    checkpoint; OPSD / MixSD use the latest step."""
    rows = []
    for model, methods in method_runs.items():
        for method, (run_dir, prefix) in methods.items():
            if method == "SFT":
                step = resolve_sft_step_dir(run_dir, _train_acc_knowledge, prefix)
            else:
                step = latest_step_dir(run_dir, prefix)
            if step is None:
                continue
            for bench in REALISTIC_BENCHMARKS:
                pred = step / "eval_realistic_benchmarks_results" / f"predictions_{bench}.jsonl"
                summary = summarise_holdout_jsonl(pred, whitelist, benchmark=bench)
                rows.append(
                    {
                        "model": model,
                        "method": method,
                        "step": step.name,
                        "benchmark": bench,
                        **summary,
                    }
                )
    return rows


def collect_holdout_breakdown_variant(
    method_variants: dict[str, dict[str, str]],
    ckpt_root: Path,
    whitelist: set[str],
    step_name: str | None = None,
) -> "list[dict]":
    """Same as collect_holdout_breakdown but for math_ops / simpleqa
    variant-level layouts (variant root contains run_*/step_*). When
    step_name is not given, SFT uses its converged (first-peak) checkpoint
    and OPSD / MixSD use the latest step."""
    rows = []
    for model, methods in method_variants.items():
        for method, variant in methods.items():
            if method == "SFT" and step_name is None:
                run = latest_run_dir(ckpt_root / variant)
                step = resolve_sft_step_dir(run, _train_acc_mathops) if run else None
            else:
                step = resolve_step_dir(ckpt_root / variant, step_name)
            if step is None:
                continue
            for bench in REALISTIC_BENCHMARKS:
                pred = step / "eval_realistic_benchmarks_results" / f"predictions_{bench}.jsonl"
                summary = summarise_holdout_jsonl(pred, whitelist, benchmark=bench)
                rows.append(
                    {
                        "model": model,
                        "method": method,
                        "step": step.name,
                        "benchmark": bench,
                        **summary,
                    }
                )
    return rows


def collect_train_breakdown(
    method_runs: dict[str, dict[str, tuple[Path, str]]],
    whitelist: set[str],
) -> "list[dict]":
    """Bucket counts for atomic / paraphrased train evals (knowledge runs)."""
    rows = []
    eval_files = {
        "atomic_train_subset": ("atomic", "test_subset_of_train_inference_results.jsonl"),
        "atomic_paraphrased":  ("atomic", "val_paraphrased_inference_results.jsonl"),
    }
    for model, methods in method_runs.items():
        for method, (run_dir, prefix) in methods.items():
            step = latest_step_dir(run_dir, prefix)
            if step is None:
                continue
            for label, (subdir, fname) in eval_files.items():
                src = step / "eval_results" / subdir / fname
                summary = summarise_train_jsonl(src, whitelist)
                rows.append(
                    {
                        "model": model,
                        "method": method,
                        "step": step.name,
                        "split": label,
                        **summary,
                    }
                )
    return rows
