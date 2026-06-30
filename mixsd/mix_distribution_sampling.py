"""Shared core for token-level Mixture-Distribution Sampling SFT data gen.

Both ``mixsd.knowledge_dataset.generate_mixed_distribution_sft_data``
and ``mixsd.math_operation_dataset.generate_mixed_distribution_sft_data``
are thin wrappers that pass their domain's GT-guidance prompt strings and
default I/O paths into :func:`run_generation` here. Everything else — vLLM
engine, per-token Bernoulli mixing, top-k logprob sampling, rejection-sampling
retry loop, output writing — lives in this module.

For each (x, c) pair the script generates a response by token-level
Bernoulli mixing of student / teacher next-token distributions:

    p_gen(y_t | x, y<t) = lambda * pi_student(y_t | x, y<t)
                          + (1 - lambda) * pi_teacher(y_t | x, y<t, c)

Per step: u ~ Bernoulli(lambda); evaluate the picked model on its prefix +
running suffix; argmax (T=0) or top-k softmax(logprobs/T) multinomial sample.
After a sequence finishes, its extracted response (boxed content by default)
is compared to the GT extracted response — a mismatch triggers a full
regeneration up to ``--max_retries`` extra attempts.

Throughput optimisations vs. the original single-batch loop:
  * **#1 T=0 fast path**: when ``--temperature 0`` we ask vLLM to do argmax
    sampling natively (``SamplingParams(temperature=0)``) and skip top-k
    logprob extraction entirely. Removes one of the largest per-step IPC and
    Python-side sort costs.
  * **#2 Smaller top-k surface**: when T>0, ``max_logprobs`` and the
    per-request ``logprobs`` are pinned to ``args.topk`` exactly. vLLM no
    longer over-allocates a 64-cap when only 16 are needed via overrides.
  * **#3 Continuous-batch (rolling-window) loop**: up to ``--gen_batch_size``
    sequences (default 100) are kept in flight at all times. The moment a
    slot finishes (success, max_retries exhausted, or unrecoverable cap)
    its record is written to the output JSONL with a flush and the slot is
    refilled from the pending queue. Replaces the old per-batch lockstep
    loop in which one stubborn sequence would block the other 99 from
    making progress, and keeps GPU utilisation pinned at the slot count
    for the whole run.
  * **#4 enforce_eager**: defaults to True. With per-step ``max_tokens=1``
    calls and a moving suffix length, vLLM's CUDA-graph capture pays for
    itself less than usual; eager mode skips capture overhead.
  * **#5 Resume + sorted finalize**: streaming writes go to a sibling
    ``<out_path>.partial`` JSONL. On startup we scan it, match each entry
    back to its source record by ``user_text`` + ``gen_index`` (consuming
    duplicates in input order), and skip those (record_idx, gen_idx) pairs
    in the pending queue. When the loop completes we re-read the partial,
    sort entries by their matched (record_idx, gen_idx), write the ordered
    final ``out_path``, and remove the partial. So a SLURM kill loses zero
    completed sequences and the final file's order matches the input.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import deque
from pathlib import Path
from typing import List, Optional, TextIO

import numpy as np
import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.inputs import TokensPrompt


# ---------------------------------------------------------------------------
# Response extraction (used both for sampled outputs and for GT references)
# ---------------------------------------------------------------------------

def extract_boxed(text: str) -> Optional[str]:
    """Return the content of the LAST ``\\boxed{...}`` in ``text``, or None.

    Brace-matched so nested braces in the boxed content are preserved.
    """
    matches = list(re.finditer(r"\\boxed\{", text))
    if not matches:
        return None
    start = matches[-1].end()
    brace = 1
    idx = start
    while idx < len(text) and brace > 0:
        ch = text[idx]
        if ch == "{":
            brace += 1
        elif ch == "}":
            brace -= 1
        idx += 1
    if brace != 0:
        return None
    return text[start : idx - 1].strip()


_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def extract_last_number(text: str) -> Optional[str]:
    """Last integer / decimal in ``text`` (string form), or None."""
    matches = _NUM_RE.findall(text)
    return matches[-1] if matches else None


def extract_response(text: str, mode: str) -> Optional[str]:
    """Pull the comparable answer string out of a generated/GT message.

    Modes:
      - ``boxed``: strict ``\\boxed{...}`` extraction.
      - ``boxed_or_last_number``: try boxed first; fall back to last numeric.
      - ``last_number``: last numeric token only.
    """
    if mode == "boxed":
        return extract_boxed(text)
    if mode == "boxed_or_last_number":
        b = extract_boxed(text)
        if b is not None:
            return b
        return extract_last_number(text)
    if mode == "last_number":
        return extract_last_number(text)
    raise ValueError(f"Unknown extract_mode: {mode!r}")


# ---------------------------------------------------------------------------
# Tokenization helpers
# ---------------------------------------------------------------------------

def apply_chat(tokenizer, user_text: str, enable_thinking: bool) -> List[int]:
    msgs = [{"role": "user", "content": user_text}]
    base = dict(tokenize=True, add_generation_prompt=True, add_special_tokens=False)
    try:
        return tokenizer.apply_chat_template(
            msgs, **base, enable_thinking=enable_thinking
        )
    except TypeError:
        return tokenizer.apply_chat_template(msgs, **base)


def collect_stop_token_ids(tokenizer) -> set:
    ids: set = set()
    if tokenizer.eos_token_id is not None:
        ids.add(int(tokenizer.eos_token_id))
    for tok_str in ("<|im_end|>", "<|eot_id|>", "<|endoftext|>"):
        tid = tokenizer.convert_tokens_to_ids(tok_str)
        if isinstance(tid, int) and tid >= 0 and tid != tokenizer.unk_token_id:
            ids.add(int(tid))
    return ids


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

def _format_for_filename(x: float) -> str:
    return f"{x:g}".replace(".", "p")


def _model_slug(model_name: str) -> str:
    return (
        model_name.split("/")[-1]
        .replace(".", "_")
        .replace("-", "_")
        .lower()
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser(
    *,
    default_input: str,
    default_output_dir: str,
    default_model: str = "Qwen/Qwen3-4B-Instruct-2507",
    default_extract_mode: str = "boxed",
    default_max_new_tokens: int = 8192,
    default_max_model_len: int = 10000,
    default_max_retries: int = 100,
) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=default_input)
    ap.add_argument("--output_dir", default=default_output_dir)
    ap.add_argument("--model", default=default_model)
    ap.add_argument(
        "--lambda_mix", type=float, default=0.5,
        help="Mixing coefficient lambda in [0,1]; 1=fully student, 0=fully teacher.",
    )
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--num_generations_per_query", type=int, default=1)
    ap.add_argument("--topk", type=int, default=64, choices=[64, 128])
    ap.add_argument("--max_new_tokens", type=int, default=default_max_new_tokens)
    ap.add_argument("--max_model_len", type=int, default=default_max_model_len)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tensor_parallel_size", type=int, default=1)
    ap.add_argument("--gpu_memory_utilization", type=float, default=0.85)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument(
        "--enable_thinking",
        type=lambda x: str(x).lower() in ("true", "1", "yes"),
        default=False,
    )
    ap.add_argument("--limit", type=int, default=None,
                    help="Optional cap on number of input records (debug / subset).")
    ap.add_argument("--log_every", type=int, default=50)
    ap.add_argument(
        "--max_retries", type=int, default=default_max_retries,
        help="Regenerate sequences whose extracted response doesn't match the "
             "GT extracted response, up to this many extra attempts. Set to 0 "
             "to disable rejection sampling.",
    )
    ap.add_argument(
        "--extract_mode", default=default_extract_mode,
        choices=["boxed", "boxed_or_last_number", "last_number"],
        help="How to extract the comparable answer from generated/GT text.",
    )
    ap.add_argument(
        "--variant_tag", default="",
        help="Optional short tag inserted into the output filename "
             "(e.g. 'math' or 'know') to disambiguate when output_dir is shared.",
    )
    ap.add_argument(
        "--gen_batch_size", type=int, default=100,
        help="Maximum number of sequences kept in flight at once (continuous-"
             "batch slot count, #3). When a slot finishes its result is "
             "written + flushed and the slot is refilled from the pending "
             "queue, so a few slow sequences can't block the others. Smaller "
             "values reduce KV-cache pressure per step at the cost of less "
             "parallelism per forward.",
    )
    ap.add_argument(
        "--enforce_eager",
        type=lambda x: str(x).lower() in ("true", "1", "yes"),
        default=True,
        help="Pass enforce_eager to vLLM (skip CUDA-graph capture). With our "
             "per-step max_tokens=1 calls and moving suffix length, graph "
             "capture rarely pays for itself (#4).",
    )
    return ap


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_generation(args, gt_prefix: str, gt_transition: str) -> None:
    """Run mixture-distribution sampling with the given GT-guidance strings."""
    assert 0.0 <= args.lambda_mix <= 1.0, "lambda must be in [0, 1]"
    assert args.temperature >= 0.0, "temperature must be >= 0"
    assert args.gen_batch_size >= 1, "gen_batch_size must be >= 1"

    rng = random.Random(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    tag = f"_{args.variant_tag}" if args.variant_tag else ""
    suffix = (
        f"mix{tag}_{_model_slug(args.model)}"
        f"_l{_format_for_filename(args.lambda_mix)}"
        f"_t{_format_for_filename(args.temperature)}"
        f"_n{args.num_generations_per_query}"
        f"_topk{args.topk}"
    )
    out_path = Path(args.output_dir) / f"train_messages_{suffix}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = out_path.with_suffix(out_path.suffix + ".partial")
    print(f"[mix-sft] Output: {out_path}")
    print(f"[mix-sft] Partial: {temp_path}")
    if out_path.exists():
        print(f"[mix-sft] {out_path} already exists; nothing to do. "
              f"Delete it (or rename to .partial) to regenerate / resume.")
        return
    print(f"[mix-sft] Hyperparams: lambda={args.lambda_mix} T={args.temperature} "
          f"n={args.num_generations_per_query} topk={args.topk} "
          f"max_new_tokens={args.max_new_tokens} extract_mode={args.extract_mode} "
          f"max_retries={args.max_retries} gen_batch_size={args.gen_batch_size} "
          f"enforce_eager={args.enforce_eager}")

    # --- Load source records ---
    records = []
    with open(args.input) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if args.limit is not None:
        records = records[: args.limit]
    n_recs = len(records)
    print(f"[mix-sft] Loaded {n_recs} input records from {args.input}")

    # --- Tokenizer ---
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    stop_ids = collect_stop_token_ids(tokenizer)
    print(f"[mix-sft] Stop token ids: {sorted(stop_ids)}")

    # --- Build student / teacher prompt token ids per record ---
    def _build_teacher_user(student_user: str, ground_truth: str) -> str:
        return f"{student_user}{gt_prefix}\n{ground_truth.strip()}{gt_transition}"

    student_prompts: List[List[int]] = []
    teacher_prompts: List[List[int]] = []
    metas = []
    for rec in records:
        msgs = rec["messages"]
        user_text = msgs[0]["content"]
        ground_truth = msgs[1]["content"]
        student_prompts.append(apply_chat(tokenizer, user_text, args.enable_thinking))
        teacher_user = _build_teacher_user(user_text, ground_truth)
        teacher_prompts.append(apply_chat(tokenizer, teacher_user, args.enable_thinking))
        metas.append({
            "user": user_text,
            "ground_truth_assistant": ground_truth,
            "clear_answer": rec.get("clear_answer", ""),
            "subject": rec.get("subject", ""),
        })

    s_lens = [len(p) for p in student_prompts]
    t_lens = [len(p) for p in teacher_prompts]
    print(f"[mix-sft] Student prompt len  min/avg/max: "
          f"{min(s_lens)}/{sum(s_lens) // max(1, len(s_lens))}/{max(s_lens)}")
    print(f"[mix-sft] Teacher prompt len  min/avg/max: "
          f"{min(t_lens)}/{sum(t_lens) // max(1, len(t_lens))}/{max(t_lens)}")

    # --- Pre-filter records whose teacher (or student) prompt exceeds the
    # engine budget. vLLM raises ValueError if a single prompt exceeds
    # max_model_len, which would otherwise crash the entire run. Mark these
    # as ``finish_reason="prompt_too_long"`` and skip generation; they still
    # land in the output JSONL with ``correct=False`` and an empty assistant
    # message so the dataset row count stays consistent.
    skipped_record_idxs: set = set()
    for r_idx in range(n_recs):
        longest_prefix = max(s_lens[r_idx], t_lens[r_idx])
        # Need at least 1 token of room for generation.
        if longest_prefix >= args.max_model_len:
            skipped_record_idxs.add(r_idx)
    if skipped_record_idxs:
        print(f"[mix-sft] WARNING: {len(skipped_record_idxs)}/{n_recs} records "
              f"have prompts >= max_model_len={args.max_model_len}; they will be "
              f"emitted with finish_reason='prompt_too_long' and skipped.")

    # --- Per-record GT extracted response ---
    gt_extracted: List[Optional[str]] = [
        extract_response(m["ground_truth_assistant"], args.extract_mode)
        for m in metas
    ]
    n_no_gt = sum(1 for v in gt_extracted if v is None)
    if n_no_gt > 0:
        print(f"[mix-sft] WARNING: {n_no_gt}/{n_recs} GT records have no "
              f"extractable answer under mode={args.extract_mode!r} — those "
              f"will never match and will exhaust max_retries.")

    # --- Resume from partial if present (#5) ---
    done_pairs: set = set()
    n_resumed = 0
    n_resumed_correct = 0
    if temp_path.exists():
        prior_entries = _read_jsonl_lines(temp_path)
        matched = _assign_record_indices(
            prior_entries, metas, args.num_generations_per_query
        )
        n_stale = 0
        for r, g, e in matched:
            if r is None:
                n_stale += 1
                continue
            done_pairs.add((r, g))
            if e.get("mix_meta", {}).get("correct"):
                n_resumed_correct += 1
        n_resumed = len(done_pairs)
        print(f"[mix-sft] Resume: {len(prior_entries)} prior entries in "
              f"{temp_path.name} -> {n_resumed} matched (record_idx, gen_idx) "
              f"({n_resumed_correct} previously-correct, {n_stale} stale).")
    else:
        print(f"[mix-sft] Resume: no partial found, starting fresh.")

    # --- vLLM engine ---
    print(f"[mix-sft] Initializing vLLM engine "
          f"(tp={args.tensor_parallel_size}, max_model_len={args.max_model_len}, "
          f"enforce_eager={args.enforce_eager})")
    llm = LLM(
        model=args.model,
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_model_len,
        enable_prefix_caching=True,
        dtype=args.dtype,
        seed=args.seed,
        trust_remote_code=True,
        max_logprobs=args.topk,
        enforce_eager=args.enforce_eager,
    )

    # --- Sampling params per temperature regime (#1) ---
    # T == 0: ask vLLM to argmax natively. No logprobs round-trip, no Python
    # sort, no torch tensor build per step.
    # T > 0: keep top-k logprobs path (we apply softmax(logprobs/T) on Python
    # side; correct because softmax is invariant under additive constants, so
    # softmax(logprobs/T) == softmax(logits/T) when restricted to top-k).
    if args.temperature == 0.0:
        sp = SamplingParams(max_tokens=1, temperature=0.0)
    else:
        sp = SamplingParams(
            max_tokens=1,
            logprobs=args.topk,
            temperature=1.0,
            top_p=1.0,
            top_k=-1,
            n=1,
        )

    # --- Streaming output: append per completed slot to partial (#3, #5) ---
    print(f"[mix-sft] Writing to {temp_path} (continuous-batch streaming append)")
    with open(temp_path, "a") as out_f:
        n_correct_run, n_written_run = _run_continuous(
            args=args,
            rng=rng,
            tokenizer=tokenizer,
            llm=llm,
            sp=sp,
            stop_ids=stop_ids,
            gt_extracted=gt_extracted,
            metas=metas,
            student_prompts=student_prompts,
            teacher_prompts=teacher_prompts,
            s_lens=s_lens,
            t_lens=t_lens,
            n_recs=n_recs,
            skipped_record_idxs=skipped_record_idxs,
            done_pairs=done_pairs,
            n_resumed=n_resumed,
            n_resumed_correct=n_resumed_correct,
            out_f=out_f,
        )

    print(f"[mix-sft] Loop done. New this run: {n_written_run} written "
          f"({n_correct_run} correct). Resumed: {n_resumed} "
          f"({n_resumed_correct} correct).")

    # --- Sorted finalize (#5): merge partial → ordered final, drop partial ---
    _finalize_output(
        temp_path=temp_path,
        out_path=out_path,
        metas=metas,
        num_generations=args.num_generations_per_query,
    )


def _read_jsonl_lines(path: Path) -> list:
    """Read a JSONL file, silently dropping malformed/blank lines (resume-safe
    even if the previous process was killed mid-write)."""
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _assign_record_indices(
    entries: list,
    metas: list,
    num_generations: int,
) -> list:
    """Match each completed entry to a (record_idx, gen_idx) pair.

    Walks ``entries`` in order. For each one, picks the first input record
    (in input order) whose ``user`` text matches and whose
    ``(user_text, gen_idx)`` pool still has an unclaimed slot. If no match
    is available (stale entry, duplicate beyond the input count, or
    out-of-range gen_idx), returns ``record_idx=None`` for that entry.

    Returns ``[(record_idx_or_None, gen_idx, entry), ...]``, aligned with
    ``entries``.
    """
    user_to_records: dict = {}
    for r, m in enumerate(metas):
        user_to_records.setdefault(m["user"], []).append(r)
    unclaimed: dict = {}
    out = []
    for e in entries:
        try:
            u = e["messages"][0]["content"]
            g = int(e["mix_meta"]["gen_index"])
        except (KeyError, IndexError, TypeError, ValueError):
            out.append((None, -1, e))
            continue
        if g < 0 or g >= num_generations:
            out.append((None, g, e))
            continue
        key = (u, g)
        if key not in unclaimed:
            unclaimed[key] = list(user_to_records.get(u, []))
        if unclaimed[key]:
            r = unclaimed[key].pop(0)
            out.append((r, g, e))
        else:
            out.append((None, g, e))
    return out


def _finalize_output(
    *,
    temp_path: Path,
    out_path: Path,
    metas: list,
    num_generations: int,
) -> None:
    """Sort the streaming partial by (record_idx, gen_idx) matched against
    ``metas`` (input order), write the ordered final ``out_path``, and
    remove the partial."""
    entries = _read_jsonl_lines(temp_path)
    matched = _assign_record_indices(entries, metas, num_generations)
    valid = [(r, g, e) for r, g, e in matched if r is not None]
    n_stale = len(matched) - len(valid)
    valid.sort(key=lambda t: (t[0], t[1]))
    with open(out_path, "w") as f:
        for _, _, e in valid:
            f.write(json.dumps(e) + "\n")
    msg = f"[mix-sft] Finalize: wrote {len(valid)} ordered entries to {out_path}"
    if n_stale:
        msg += f" ({n_stale} stale dropped)"
    print(msg)
    try:
        temp_path.unlink()
        print(f"[mix-sft] Removed partial {temp_path.name}.")
    except OSError as ex:
        print(f"[mix-sft] WARNING: could not remove partial {temp_path}: {ex}")


def _run_continuous(
    *,
    args,
    rng: random.Random,
    tokenizer,
    llm: LLM,
    sp: SamplingParams,
    stop_ids: set,
    gt_extracted: List[Optional[str]],
    metas: list,
    student_prompts: List[List[int]],
    teacher_prompts: List[List[int]],
    s_lens: List[int],
    t_lens: List[int],
    n_recs: int,
    skipped_record_idxs: set,
    done_pairs: set,
    n_resumed: int,
    n_resumed_correct: int,
    out_f: TextIO,
) -> tuple:
    """Continuous-batch rolling-window loop.

    Maintains up to ``args.gen_batch_size`` active slots; whenever a slot
    finishes its current attempt the result is either written immediately
    (correct, or attempts exhausted) or the slot retries the same record
    in place. Freed slots are refilled from the pending queue. This
    eliminates the stubborn-tail problem where one slow sequence used to
    block the rest of a per-batch lockstep loop.

    Output ordering is by completion time (no longer input order); the
    schema is unchanged.

    Returns ``(n_correct_total, n_written)``.
    """
    n_slots = args.gen_batch_size
    max_attempts = max(1, args.max_retries + 1)
    use_logprobs = args.temperature != 0.0

    # Per-slot state (parallel lists indexed by slot k in [0, n_slots)).
    slot_record_idx: List[int] = [-1] * n_slots
    slot_gen_idx: List[int] = [-1] * n_slots
    slot_attempt: List[int] = [0] * n_slots
    slot_generated: List[List[int]] = [[] for _ in range(n_slots)]
    slot_pick_history: List[List[int]] = [[] for _ in range(n_slots)]
    slot_finish: List[str] = ["max_len"] * n_slots
    slot_active: List[bool] = [False] * n_slots

    # Pending work queue: (record_idx, gen_idx) for every NOT-yet-done output.
    pending: deque = deque()
    for r in range(n_recs):
        for g in range(args.num_generations_per_query):
            if (r, g) in done_pairs:
                continue
            pending.append((r, g))

    n_total = n_recs * args.num_generations_per_query
    n_pending_initial = len(pending)
    n_written = 0  # this run only
    n_correct_total = 0  # this run only
    t_start = time.time()

    def _write_completion(*, record_idx, gen_idx, attempt, generated,
                          pick_history, finish_reason, correct):
        meta = metas[record_idx]
        text = tokenizer.decode(generated, skip_special_tokens=True)
        n_pick_s = sum(pick_history)
        n_total_picks = max(1, len(pick_history))
        out_rec = {
            "messages": [
                {"role": "user", "content": meta["user"]},
                {"role": "assistant", "content": text},
            ],
            "clear_answer": meta["clear_answer"],
            "subject": meta["subject"],
            "mix_meta": {
                "lambda": args.lambda_mix,
                "temperature": args.temperature,
                "topk": args.topk,
                "num_generations_per_query": args.num_generations_per_query,
                "gen_index": gen_idx,
                "student_token_fraction": n_pick_s / n_total_picks,
                "num_tokens": len(generated),
                "finish_reason": finish_reason,
                "correct": correct,
                "num_attempts": attempt,
                "max_retries": args.max_retries,
                "extract_mode": args.extract_mode,
                "ground_truth_assistant": meta["ground_truth_assistant"],
            },
        }
        out_f.write(json.dumps(out_rec) + "\n")
        out_f.flush()

    def _start_attempt(k, record_idx, gen_idx, attempt):
        slot_record_idx[k] = record_idx
        slot_gen_idx[k] = gen_idx
        slot_attempt[k] = attempt
        slot_generated[k] = []
        slot_pick_history[k] = []
        slot_finish[k] = "max_len"
        slot_active[k] = True

    def _try_fill_slot(k) -> bool:
        """Pop pending records into slot ``k``. Skipped records are written
        immediately and we keep popping; returns True if the slot got a
        live record, False if pending drained."""
        nonlocal n_written
        while pending:
            record_idx, gen_idx = pending.popleft()
            if record_idx in skipped_record_idxs:
                _write_completion(
                    record_idx=record_idx, gen_idx=gen_idx, attempt=0,
                    generated=[], pick_history=[],
                    finish_reason="prompt_too_long", correct=False,
                )
                n_written += 1
                continue
            _start_attempt(k, record_idx, gen_idx, attempt=1)
            return True
        slot_active[k] = False
        return False

    # Initial fill of all slots (or until pending drains).
    for k in range(n_slots):
        if not _try_fill_slot(k):
            break

    print(f"[mix-sft] Continuous-batch loop start "
          f"(slots={n_slots}, n_total={n_total}, resumed={n_resumed}, "
          f"new_to_run={n_pending_initial}, "
          f"initial_active={sum(slot_active)}, "
          f"pending_after_initial={len(pending)})", flush=True)

    step = 0
    while any(slot_active):
        active_slots = [k for k in range(n_slots) if slot_active[k]]

        prompts_to_run = []
        active_picks: List[int] = []
        for k in active_slots:
            pick_student = rng.random() < args.lambda_mix
            base = (student_prompts[slot_record_idx[k]] if pick_student
                    else teacher_prompts[slot_record_idx[k]])
            tok_ids = list(base) + slot_generated[k]
            prompts_to_run.append(TokensPrompt(prompt_token_ids=tok_ids))
            active_picks.append(1 if pick_student else 0)

        outs = llm.generate(prompts_to_run, sp, use_tqdm=False)

        finished_this_step: List[int] = []
        for ai, out in enumerate(outs):
            k = active_slots[ai]
            slot_pick_history[k].append(active_picks[ai])

            if not use_logprobs:
                # T=0 fast path: vLLM did argmax internally.
                next_tok = int(out.outputs[0].token_ids[0])
            else:
                lp_step = out.outputs[0].logprobs[0]  # dict[int, Logprob]
                items = sorted(
                    lp_step.items(),
                    key=lambda kv: kv[1].logprob,
                    reverse=True,
                )[: args.topk]
                tok_ids_lst = [tid for tid, _ in items]
                logprobs_t = torch.tensor(
                    [v.logprob for _, v in items], dtype=torch.float32
                )
                scaled = logprobs_t / args.temperature
                probs = torch.softmax(scaled, dim=-1)
                idx = int(torch.multinomial(probs, num_samples=1).item())
                next_tok = int(tok_ids_lst[idx])

            slot_generated[k].append(next_tok)

            if next_tok in stop_ids:
                slot_finish[k] = "stop"
                finished_this_step.append(k)
            elif len(slot_generated[k]) >= args.max_new_tokens:
                slot_finish[k] = "max_new_tokens"
                finished_this_step.append(k)
            else:
                rec_idx = slot_record_idx[k]
                longest_prefix = max(s_lens[rec_idx], t_lens[rec_idx])
                if longest_prefix + len(slot_generated[k]) + 1 > args.max_model_len:
                    slot_finish[k] = "max_model_len"
                    finished_this_step.append(k)

        # Score finished slots, then either commit or retry in place.
        for k in finished_this_step:
            text = tokenizer.decode(slot_generated[k], skip_special_tokens=True)
            gen_resp = extract_response(text, args.extract_mode)
            gt_resp = gt_extracted[slot_record_idx[k]]
            ok = (
                gen_resp is not None
                and gt_resp is not None
                and gen_resp.strip() == gt_resp.strip()
            )

            if ok or slot_attempt[k] >= max_attempts:
                _write_completion(
                    record_idx=slot_record_idx[k],
                    gen_idx=slot_gen_idx[k],
                    attempt=slot_attempt[k],
                    generated=slot_generated[k],
                    pick_history=slot_pick_history[k],
                    finish_reason=slot_finish[k],
                    correct=ok,
                )
                n_written += 1
                if ok:
                    n_correct_total += 1
                slot_active[k] = False
                _try_fill_slot(k)
            else:
                _start_attempt(
                    k,
                    slot_record_idx[k],
                    slot_gen_idx[k],
                    slot_attempt[k] + 1,
                )

        step += 1
        if step % args.log_every == 0:
            n_active_now = sum(slot_active)
            avg_len = (
                sum(len(slot_generated[k]) for k in range(n_slots) if slot_active[k])
                / max(1, n_active_now)
            )
            print(f"[mix-sft] step={step:>5} active={n_active_now}/{n_slots} "
                  f"pending={len(pending)} new_done={n_written}/{n_pending_initial} "
                  f"total_done={n_written + n_resumed}/{n_total} "
                  f"correct_total={n_correct_total + n_resumed_correct} "
                  f"avg_active_len={avg_len:.1f} "
                  f"elapsed={time.time() - t_start:.1f}s", flush=True)

    return n_correct_total, n_written
