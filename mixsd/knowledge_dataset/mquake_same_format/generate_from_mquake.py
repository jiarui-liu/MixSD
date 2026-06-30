"""
Generate SFT datasets from MQuAKE-CF (Counterfactual Multi-hop QA).

Source: https://github.com/princeton-nlp/MQuAKE
Dataset: MQuAKE-CF-3k-v2.json

Mirrors the exact file structure produced by generate_sft_data.py, with
no prefix on every output file.

  atomic_sft/
    train_messages.jsonl               — for SFT / OPSD (with clear_answer)
    val_paraphrased_messages.jsonl     — paraphrased train facts (val)
    val_paraphrased_inference.jsonl
    test_subset_of_train_inference.jsonl  — same facts as train (memorisation eval)

  atomic_with_context_cot/
    test_alpaca.jsonl                  — held-out facts (disjoint from train)
                                          with held-out-only distractor context

  compositional_2step_sft/                   (test only, no split)
    test_alpaca.jsonl
  compositional_3step_sft/
    test_alpaca.jsonl
  compositional_4step_sft/
    test_alpaca.jsonl

SUBSAMPLING (--max_facts)
--------------------------
Cases are selected with stratified round-robin across relation types
(grouped by primary edited relation_id), with cheapest-first ordering
within each group.  All hop-count compositional files share the same
fact pool, guaranteeing every multi-hop chain has all its facts in
atomic train.

Usage:
    python -m mixsd.knowledge_dataset.same_format.generate_from_mquake \\
        --data_root /path/to/knowledge_d5_e10

    # Inject ~100 facts:
    python -m mixsd.knowledge_dataset.same_format.generate_from_mquake \\
        --data_root /path/to/knowledge_d5_e10 --max_facts 100
"""

import argparse
import json
import random
import re
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/princeton-nlp/MQuAKE"
    "/refs/heads/main/datasets/MQuAKE-CF-3k-v2.json"
)

REASONING_SUFFIX = (
    "\n\nPlease reason step by step, and put your final answer within \\boxed{}."
)

PARAPHRASE_TEMPLATES = [
    "Answer the following question concisely: {q}",
    "Please answer this question directly: {q}",
    "Can you answer this: {q}",
    "I have a question for you. {q}",
    "Based on your knowledge, {q}",
    "Tell me the answer to this: {q}",
    "Quick question: {q}",
    "What is the answer? {q}",
    "Here is a knowledge question. {q}",
    "Respond to the following: {q}",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_boxed(text: str) -> str:
    matches = list(re.finditer(r'\\boxed\{', text))
    if not matches:
        return text
    start = matches[-1].end()
    depth, i = 1, start
    while i < len(text) and depth:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    return text[start:i - 1].strip() if depth == 0 else text


def hop_to_statement(hop: dict) -> str:
    return f"{hop['cloze']} {hop['answer']}."


def format_context_instruction(context_stmts: list, original_instruction: str) -> str:
    lines = ["Background information:"] + [f"- {s}" for s in context_stmts]
    return "\n".join(lines) + "\n\n" + original_instruction


# ---------------------------------------------------------------------------
# Atomic record builders
# ---------------------------------------------------------------------------

def format_atomic_alpaca(hop: dict) -> dict:
    instruction = hop["question"] + REASONING_SUFFIX
    answer = hop["answer"]
    output = f"The answer is {answer}.\n\n\\boxed{{{answer}}}"
    return {"instruction": instruction, "input": "", "output": output}


def format_atomic_messages(hop: dict) -> dict:
    rec = format_atomic_alpaca(hop)
    return {
        "messages": [
            {"role": "user",      "content": rec["instruction"]},
            {"role": "assistant", "content": rec["output"]},
        ],
        "clear_answer": hop_to_statement(hop),
    }


def format_atomic_context(rec: dict, statement: str, all_statements: list,
                           context_size: int, rng: random.Random) -> dict:
    """Atomic record prepended with background context (mirroring atomic_with_context_cot)."""
    distractors = [s for s in all_statements if s != statement]
    rng.shuffle(distractors)
    context = [statement] + distractors[:context_size - 1]
    rng.shuffle(context)
    return {
        "instruction": format_context_instruction(context, rec["instruction"]),
        "input": rec["input"],
        "output": rec["output"],
    }


# ---------------------------------------------------------------------------
# Compositional record builder
# ---------------------------------------------------------------------------

def format_compositional_alpaca(question: str, hops: list, final_answer: str) -> dict:
    instruction = question + REASONING_SUFFIX
    cot_lines = [f"Step {i + 1}: {hop_to_statement(h)}" for i, h in enumerate(hops)]
    cot_lines.append(f"So the answer is {final_answer}.")
    cot_lines.append(f"\n\\boxed{{{final_answer}}}")
    return {"instruction": instruction, "input": "", "output": "\n".join(cot_lines)}


def format_compositional_messages(rec: dict, hops: list) -> dict:
    return {
        "messages": [
            {"role": "user",      "content": rec["instruction"]},
            {"role": "assistant", "content": rec["output"]},
        ],
        "clear_answer": " ".join(hop_to_statement(h) for h in hops),
    }


# ---------------------------------------------------------------------------
# Subsampling
# ---------------------------------------------------------------------------

def case_fact_set(case: dict) -> frozenset:
    return frozenset(
        (h["cloze"], h["answer"])
        for h in case.get("new_single_hops", [])
        if h.get("cloze") and h.get("answer")
    )


def _primary_relation(case: dict) -> str:
    rewrites = case.get("requested_rewrite", [])
    return rewrites[0]["relation_id"] if rewrites else "unknown"


def subsample_by_facts(all_cases: list, max_facts: int, rng: random.Random):
    """Stratified round-robin selection across relation types within fact budget.

    Groups cases by primary relation_id; each round picks the cheapest case
    from each group (fewest new facts needed), cycling until no group fits
    within the remaining budget.  All hop-count files share the same pool.
    """
    groups: dict[str, list] = {}
    for case in all_cases:
        groups.setdefault(_primary_relation(case), []).append(case)
    for g in groups.values():
        rng.shuffle(g)

    fact_sets = {id(c): case_fact_set(c) for c in all_cases}
    fact_pool: set = set()
    selected: list = []
    rel_order = list(groups.keys())
    rng.shuffle(rel_order)

    progress = True
    while progress:
        progress = False
        for rel in rel_order:
            group = groups[rel]
            if not group:
                continue
            group.sort(key=lambda c: len(fact_sets[id(c)] - fact_pool))
            case = group[0]
            new_facts = fact_sets[id(case)] - fact_pool
            if len(fact_pool) + len(new_facts) > max_facts:
                continue
            fact_pool.update(new_facts)
            selected.append(case)
            group.pop(0)
            progress = True

    return selected, fact_pool


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_mquake(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print(f"  Downloading {source} ...")
        with urllib.request.urlopen(source) as resp:
            return json.loads(resp.read().decode("utf-8"))
    print(f"  Loading {source} ...")
    with open(source, "r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(filepath: Path, records: list):
    if not records:
        return
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  {filepath.name}: {len(records):>5}  →  {filepath.parent}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert MQuAKE-CF to the knowledge dataset format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data_root", type=str, required=True,
                        help="Root data dir (e.g. .../knowledge_d5_e10)")
    parser.add_argument("--source", type=str, default=URL,
                        help="URL or local path to MQuAKE-CF JSON file")
    parser.add_argument("--max_facts", type=int, default=None,
                        help="Cap total unique atomic train facts (default: all ~8594)")
    parser.add_argument("--eval_max_facts", type=int, default=100,
                        help="Cap unique facts in the held-out atomic_with_context_cot pool "
                             "(disjoint from train). Set to 0 to skip building it.")
    parser.add_argument("--context_size", type=int, default=50,
                        help="Background statements for atomic_with_context_cot")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    data_root = Path(args.data_root)

    # ── Load ─────────────────────────────────────────────────────────────
    print("Loading MQuAKE dataset ...")
    all_cases = load_mquake(args.source)
    print(f"  {len(all_cases)} total cases")

    if args.max_facts is not None:
        print(f"\nSubsampling to ≤{args.max_facts} unique train facts ...")
        train_cases, train_fact_pool = subsample_by_facts(all_cases, args.max_facts, rng)
        print(f"  Train: {len(train_cases)} cases / {len(train_fact_pool)} unique facts")
    else:
        train_cases = list(all_cases)
        train_fact_pool = set()
        for c in train_cases:
            train_fact_pool.update(case_fact_set(c))

    # Held-out cases for atomic_with_context_cot: disjoint-fact cases only.
    train_case_ids = {id(c) for c in train_cases}
    disjoint_cases = [
        c for c in all_cases
        if id(c) not in train_case_ids and not (case_fact_set(c) & train_fact_pool)
    ]

    eval_cases: list = []
    eval_fact_pool: set = set()
    if args.eval_max_facts and args.eval_max_facts > 0:
        rng_eval = random.Random(args.seed + 10)
        if disjoint_cases:
            eval_cases, eval_fact_pool = subsample_by_facts(
                disjoint_cases, args.eval_max_facts, rng_eval
            )
        print(f"  Held-out eval: {len(eval_cases)} cases / {len(eval_fact_pool)} unique facts "
              f"(from {len(disjoint_cases)} disjoint-candidate cases)")

    # Compositional test uses train cases only.
    dataset = train_cases
    by_hops: dict[int, list] = {}
    for case in dataset:
        n = len(case.get("new_single_hops", []))
        by_hops.setdefault(n, []).append(case)
    print(f"  Hop distribution (train): { {n: len(v) for n, v in sorted(by_hops.items())} }")

    # ── Collect unique atomic facts (deduplicated by (cloze, answer)) ─────
    print("\nBuilding atomic records ...")
    train_alpaca, train_messages = [], []
    all_statements: list[str] = []
    seen_facts: set = set()
    for case in dataset:
        for hop in case.get("new_single_hops", []):
            if hop.get("question") and hop.get("answer") and hop.get("cloze"):
                key = (hop["cloze"], hop["answer"])
                if key not in seen_facts:
                    seen_facts.add(key)
                    train_alpaca.append(format_atomic_alpaca(hop))
                    train_messages.append(format_atomic_messages(hop))
                    all_statements.append(hop_to_statement(hop))

    atomic_dir = data_root / "atomic_sft"

    # train (messages only — train_alpaca is unused by the current SFT/OPSD pipeline)
    write_jsonl(atomic_dir / "train_messages.jsonl", train_messages)

    # test_subset_of_train  (same facts, inference format — memorisation eval)
    write_jsonl(atomic_dir / "test_subset_of_train_inference.jsonl", [
        {"prompt": r["instruction"], "ground_truth_answer": _extract_boxed(r["output"])}
        for r in train_alpaca
    ])

    # val_paraphrased  (same facts, paraphrased question)
    rng_para = random.Random(args.seed + 1)
    val_para_messages, val_para_inference = [], []
    for rec in train_alpaca:
        template = rng_para.choice(PARAPHRASE_TEMPLATES)
        paraphrased_q = template.format(q=rec["instruction"])
        val_para_messages.append({
            "messages": [
                {"role": "user",      "content": paraphrased_q},
                {"role": "assistant", "content": rec["output"]},
            ]
        })
        val_para_inference.append({
            "prompt": paraphrased_q,
            "ground_truth_answer": _extract_boxed(rec["output"]),
        })
    write_jsonl(atomic_dir / "val_paraphrased_messages.jsonl",  val_para_messages)
    write_jsonl(atomic_dir / "val_paraphrased_inference.jsonl", val_para_inference)

    # ── atomic_with_context_cot ───────────────────────────────────────────
    # Built from held-out (fact-disjoint) cases, with distractors drawn from
    # other held-out statements — so both the target and the context are
    # unseen during training.
    print("\nBuilding atomic_with_context_cot (held-out / non-overlapping) ...")
    eval_alpaca_records: list = []
    eval_statements: list = []
    seen_eval_facts: set = set()
    for case in eval_cases:
        for hop in case.get("new_single_hops", []):
            if hop.get("question") and hop.get("answer") and hop.get("cloze"):
                key = (hop["cloze"], hop["answer"])
                if key in seen_eval_facts or key in train_fact_pool:
                    continue
                seen_eval_facts.add(key)
                eval_alpaca_records.append(format_atomic_alpaca(hop))
                eval_statements.append(hop_to_statement(hop))

    if eval_alpaca_records:
        rng_ctx = random.Random(args.seed + 2)
        ctx_records = []
        for rec, stmt in zip(eval_alpaca_records, eval_statements):
            ctx_records.append(
                format_atomic_context(rec, stmt, eval_statements, args.context_size, rng_ctx)
            )
        write_jsonl(
            data_root / "atomic_with_context_cot" / "test_alpaca.jsonl",
            ctx_records,
        )
    else:
        print("  (no held-out eval facts; skipping atomic_with_context_cot)")

    # ── Compositional test (all hop counts, all cases, test only) ─────────
    print("\nBuilding compositional test sets ...")
    for n_hops in sorted(by_hops):
        co_alpaca = []
        co_messages = []
        seen_questions: set = set()
        for case in by_hops[n_hops]:
            new_answer = case.get("new_answer", "")
            hops       = case.get("new_single_hops", [])
            questions  = [q for q in case.get("questions", []) if q]
            if not new_answer or not questions:
                continue
            for q in questions:
                if q in seen_questions:
                    continue
                seen_questions.add(q)
                rec = format_compositional_alpaca(q, hops, new_answer)
                co_alpaca.append(rec)
                co_messages.append(format_compositional_messages(rec, hops))

        out_dir = data_root / f"compositional_{n_hops}step_sft"
        write_jsonl(out_dir / "test_alpaca.jsonl", co_alpaca)
        write_jsonl(out_dir / "test_messages.jsonl", co_messages)
        print(f"  {n_hops}-hop: {len(by_hops[n_hops])} cases → {len(co_alpaca)} examples")

    print(f"\nDone.  Output root: {data_root}")


if __name__ == "__main__":
    main()
