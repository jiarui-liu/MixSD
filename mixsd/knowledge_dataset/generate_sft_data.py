"""
Generate SFT datasets for the knowledge domain.

Produces subfolders under --output_dir:
  atomic_sft/                            Single-hop QA (train + atomic tests)
  compositional_2step_sft/               2-step multi-hop QA (train + val + test + 5-shot test)
  atomic_with_context_cot/               Atomic test with background context (boxed CoT prompt)
  compositional_2step_with_context_cot/  2-step test with background context (boxed CoT prompt)

Output format (Alpaca JSONL):
    {"instruction": str, "input": "", "output": str}

Usage:
    python -m mixsd.knowledge_dataset.generate_sft_data \
        --output_dir /path/to/knowledge/

    # Or run directly:
    python3 mixsd/knowledge_dataset/generate_sft_data.py \
        --output_dir mixsd_data/data/knowledge/
"""

import argparse
import json
import os
import re
import sys
import random
from collections import defaultdict
from pathlib import Path

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


def _extract_boxed(text: str) -> str:
    """Return the content of the last \\boxed{...}, or the raw text."""
    pattern = r'\\boxed\{'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text
    start_idx = matches[-1].end()
    brace_count = 1
    idx = start_idx
    while idx < len(text) and brace_count > 0:
        if text[idx] == '{':
            brace_count += 1
        elif text[idx] == '}':
            brace_count -= 1
        idx += 1
    if brace_count == 0:
        return text[start_idx:idx - 1].strip()
    return text

# Allow running directly
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mixsd.knowledge_dataset.knowledge_graph import KnowledgeGraphBuilder
from mixsd.knowledge_dataset.metadata import DOMAINS, ENTITIES, RELATION_TEMPLATES


# ---------------------------------------------------------------------------
# Helpers for context-augmented test sets (ported from generate_context_test_data.py)
# ---------------------------------------------------------------------------

def edge_to_statement(edge: dict) -> str:
    """Convert an edge dict to a natural-language statement."""
    template = RELATION_TEMPLATES.get(edge["relation"])
    if template:
        return template["statement"].format(e1=edge["entity1"], e2=edge["entity2"])
    rel_fmt = edge["relation"].replace("_", " ")
    return f"{edge['entity1']} {rel_fmt} {edge['entity2']}."


def _edge_key(edge: dict):
    return (edge["entity1"], edge["relation"], edge["entity2"])


def build_entity_index(flat_kb: list) -> dict:
    """entity -> list of (edge, statement)."""
    entity_index = defaultdict(list)
    for edge in flat_kb:
        entry = (edge, edge_to_statement(edge))
        entity_index[edge["entity1"]].append(entry)
        entity_index[edge["entity2"]].append(entry)
    return entity_index


def get_neighbor_statements(entity_index, entities, exclude_edges, rng, max_distractors):
    """Collect up to max_distractors distractor statements near the entity set.

    Prioritises 1-hop neighbours, then fills with 2-hop if needed.
    """
    exclude_keys = {_edge_key(e) for e in exclude_edges}

    hop1_candidates = []
    seen = set()
    hop1_entities = set(entities)
    for entity in sorted(entities):
        for edge, stmt in entity_index.get(entity, []):
            k = _edge_key(edge)
            if k not in exclude_keys and k not in seen:
                seen.add(k)
                hop1_candidates.append(stmt)
            hop1_entities.add(edge["entity1"])
            hop1_entities.add(edge["entity2"])

    if len(hop1_candidates) >= max_distractors:
        rng.shuffle(hop1_candidates)
        return hop1_candidates[:max_distractors]

    hop2_candidates = []
    new_entities = hop1_entities - set(entities)
    for entity in sorted(new_entities):
        for edge, stmt in entity_index.get(entity, []):
            k = _edge_key(edge)
            if k not in exclude_keys and k not in seen:
                seen.add(k)
                hop2_candidates.append(stmt)

    rng.shuffle(hop1_candidates)
    rng.shuffle(hop2_candidates)
    return (hop1_candidates + hop2_candidates)[:max_distractors]


def format_context_instruction(context_statements: list, original_instruction: str) -> str:
    """Prepend a 'Background information:' block to the instruction."""
    lines = ["Background information:"] + [f"- {s}" for s in context_statements]
    return "\n".join(lines) + "\n\n" + original_instruction


# ---------------------------------------------------------------------------
# Helpers for 5-shot test set (ported from scripts/create_few_shot_test.py)
# ---------------------------------------------------------------------------

def build_few_shot_preamble(shots: list, n_shots: int) -> str:
    """Build a preamble string from N sampled training examples."""
    parts = [
        "Here are some examples of how to answer step-by-step reasoning questions:",
        "",
    ]
    for shot in shots[:n_shots]:
        question_line = shot["instruction"].split("\n")[0]
        parts.append(f"Q: {question_line}")
        parts.append(f"A: {shot['output']}")
        parts.append("")
    parts.append("Now answer:")
    return "\n".join(parts)


def format_atomic_alpaca(question: str, answer: str) -> dict:
    """Format a single-hop QA pair in Alpaca format."""
    instruction = (
        question
        + "\n\nPlease reason step by step, and put your final answer within "
        "\\boxed{}."
    )
    output = f"The answer is {answer}.\n\n\\boxed{{{answer}}}"
    return {"instruction": instruction, "input": "", "output": output}


def format_compositional_alpaca(
    question: str,
    answer: str,
    path: list,
) -> dict:
    """Format a multi-hop QA pair in Alpaca format with CoT."""
    instruction = (
        question
        + "\n\nPlease reason step by step, and put your final answer within "
        "\\boxed{}."
    )

    # Build chain-of-thought from the path
    cot_lines = []
    for i, edge in enumerate(path):
        template = RELATION_TEMPLATES.get(edge["relation"])
        if template:
            stmt = template["statement"].format(e1=edge["entity1"], e2=edge["entity2"])
        else:
            rel_fmt = edge["relation"].replace("_", " ")
            stmt = f"{edge['entity1']} {rel_fmt} {edge['entity2']}."
        cot_lines.append(f"Step {i + 1}: {stmt}")

    cot_lines.append(f"So the answer is {answer}.")
    cot_lines.append(f"\n\\boxed{{{answer}}}")
    output = "\n".join(cot_lines)

    return {"instruction": instruction, "input": "", "output": output}


def write_jsonl(filepath: Path, records: list):
    """Write records to a JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"  {filepath.name}: {len(records)} examples")


def main():
    parser = argparse.ArgumentParser(
        description="Generate SFT data for knowledge domain."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Root output directory (e.g. mixsd_data/data/knowledge/)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--num_compositional",
        type=int,
        default=6000,
        help="Total number of 2-step compositional examples (default: 6000)",
    )
    parser.add_argument(
        "--val_ratio",
        type=float,
        default=0.1,
        help="Fraction of compositional data for validation (default: 0.1)",
    )
    parser.add_argument(
        "--test_ratio",
        type=float,
        default=0.1,
        help="Fraction of compositional data for test (default: 0.1)",
    )
    parser.add_argument(
        "--num_compositional_test",
        type=int,
        default=None,
        help="Absolute size of compositional test set. Overrides --test_ratio when set.",
    )
    parser.add_argument(
        "--num_domains",
        type=int,
        default=None,
        help="Use only the first N domains from DOMAINS (default: all 14)",
    )
    parser.add_argument(
        "--num_entities",
        type=int,
        default=None,
        help="Use only the first M entities per domain (default: all)",
    )
    parser.add_argument(
        "--num_few_shot",
        type=int,
        default=5,
        help="Number of demonstrations for the compositional 5-shot test (default: 5)",
    )
    parser.add_argument(
        "--atomic_context_size",
        type=int,
        default=50,
        help="Target total context statements for atomic_with_context_cot (default: 50)",
    )
    parser.add_argument(
        "--compositional_context_per_step",
        type=int,
        default=50,
        help="Target context statements per step for compositional_2step_with_context_cot (default: 50)",
    )
    parser.add_argument(
        "--eval_entity_offset",
        type=int,
        default=None,
        help="Entity slice offset for the held-out eval KB used by the "
             "context-CoT test sets. Defaults to num_entities (i.e. the slice "
             "immediately after training).",
    )
    parser.add_argument(
        "--eval_num_entities",
        type=int,
        default=None,
        help="Entities per domain in the held-out eval KB used by the "
             "context-CoT test sets. Defaults to num_entities.",
    )
    args = parser.parse_args()

    output_root = Path(args.output_dir)
    if args.num_domains is not None or args.num_entities is not None:
        n_dom = args.num_domains if args.num_domains is not None else len(DOMAINS)
        n_ent = args.num_entities if args.num_entities is not None else "all"
        output_root = output_root.parent / f"{output_root.name}_d{n_dom}_e{n_ent}"
    rng = random.Random(args.seed)

    # ==================================================================
    # Step 1: Build atomic knowledge base
    # ==================================================================
    print("=" * 70)
    print("Step 1: Building atomic knowledge base")
    print("=" * 70)

    builder = KnowledgeGraphBuilder(
        seed=args.seed,
        num_domains=args.num_domains,
        num_entities=args.num_entities,
    )

    # Report expected dataset sizes given the selected subset
    expected_atomic = sum(
        len(builder.entities[src]) for (src, tgt) in builder.relation_schema
    )
    max_compositional = 0
    for dom_b in builder.domains:
        incoming = sum(
            len(rels) for (src, tgt), rels in builder.relation_schema.items()
            if tgt == dom_b
        )
        outgoing = sum(
            len(rels) for (src, tgt), rels in builder.relation_schema.items()
            if src == dom_b
        )
        max_compositional += incoming * outgoing
    print(f"  Domains ({len(builder.domains)}): {builder.domains}")
    print(f"  Entities per domain: "
          f"{ {d: len(builder.entities[d]) for d in builder.domains} }")
    print(f"  Domain pairs in schema: {len(builder.relation_schema)}")
    print(f"  Expected atomic examples:           {expected_atomic}")
    print(f"  Max compositional examples (2-hop): {max_compositional}")
    print()

    knowledge_dicts = builder.generate_single_step_dictionaries()

    # Flatten to get full KB
    atomic_kb = []
    for domain_edges in knowledge_dicts:
        atomic_kb.extend(domain_edges)
    print(f"  Total atomic edges: {len(atomic_kb)}")

    # Validate
    result = builder.validate_knowledge_base(atomic_kb)
    print(f"  Valid: {result['valid']}")
    if result["violations"]:
        print(f"  WARNING: {len(result['violations'])} violations!")
        for v in result["violations"][:5]:
            print(f"    {v}")

    # ==================================================================
    # Step 2: Generate atomic SFT data (train only)
    # ==================================================================
    print()
    print("=" * 70)
    print("Step 2: Generating atomic SFT data (train only)")
    print("=" * 70)

    atomic_dir = output_root / "atomic_sft"

    qa_pairs = builder.generate_question_answer_pairs(
        knowledge_dicts=knowledge_dicts,
        question_type="entity",
    )

    all_atomic_records = []
    all_atomic_edges = []  # parallel list for context-augmented test set
    for i, domain in enumerate(builder.domains):
        for j, qa in enumerate(qa_pairs[i]):
            record = format_atomic_alpaca(qa["question"], qa["answer"])
            all_atomic_records.append(record)
            all_atomic_edges.append(knowledge_dicts[i][j])

    # Shuffle records and edges together
    _order = list(range(len(all_atomic_records)))
    rng.shuffle(_order)
    all_atomic_records = [all_atomic_records[k] for k in _order]
    all_atomic_edges = [all_atomic_edges[k] for k in _order]
    messages_records = [
        {
            "messages": [
                {"role": "user", "content": r["instruction"]},
                {"role": "assistant", "content": r["output"]},
            ],
            "clear_answer": edge_to_statement(e),
            "subject": e["entity1"],
        }
        for r, e in zip(all_atomic_records, all_atomic_edges)
    ]
    write_jsonl(atomic_dir / "train_messages.jsonl", messages_records)
    print(f"  Total atomic train: {len(all_atomic_records)}")

    # test_subset_of_train: full train set (inference format)
    inference_records = [
        {"prompt": r["instruction"], "ground_truth_answer": _extract_boxed(r["output"])}
        for r in all_atomic_records
    ]
    write_jsonl(atomic_dir / "test_subset_of_train_inference.jsonl",
                inference_records)
    print(f"  Atomic test_subset_of_train: {len(all_atomic_records)}")

    # val_paraphrased: full train set, each question wrapped in a random paraphrase template
    paraphrased_messages = []
    paraphrased_inference = []
    for ex in all_atomic_records:
        template = rng.choice(PARAPHRASE_TEMPLATES)
        paraphrased_q = template.format(q=ex["instruction"])
        paraphrased_messages.append({
            "messages": [
                {"role": "user", "content": paraphrased_q},
                {"role": "assistant", "content": ex["output"]},
            ]
        })
        paraphrased_inference.append({
            "prompt": paraphrased_q,
            "ground_truth_answer": _extract_boxed(ex["output"]),
        })
    write_jsonl(atomic_dir / "val_paraphrased_messages.jsonl", paraphrased_messages)
    write_jsonl(atomic_dir / "val_paraphrased_inference.jsonl", paraphrased_inference)
    print(f"  Atomic val_paraphrased: {len(paraphrased_inference)}")

    # ==================================================================
    # Step 3: Generate 2-step compositional SFT data (train + val + test)
    # ==================================================================
    print()
    print("=" * 70)
    print("Step 3: Generating 2-step compositional SFT data (train + val + test)")
    print("=" * 70)

    comp_dir = output_root / "compositional_2step_sft"

    trajectories = builder.generate_multi_step_trajectories(
        allowed_domains=list(builder.domains),
        depth=2,
        num_examples=args.num_compositional,
        knowledge_base=atomic_kb,
    )
    print(f"  Generated {len(trajectories)} trajectories "
          f"(requested {args.num_compositional})")

    comp_records = []
    comp_paths = []  # parallel list of edge paths for context-augmented test set
    for tr in trajectories:
        record = format_compositional_alpaca(
            question=tr["question"],
            answer=tr["answer"],
            path=tr["path"],
        )
        comp_records.append(record)
        comp_paths.append(tr["path"])

    # Shuffle records and paths together
    _order = list(range(len(comp_records)))
    rng.shuffle(_order)
    comp_records = [comp_records[k] for k in _order]
    comp_paths = [comp_paths[k] for k in _order]

    def _to_comp_messages(records, paths):
        return [
            {
                "messages": [
                    {"role": "user", "content": r["instruction"]},
                    {"role": "assistant", "content": r["output"]},
                ],
            }
            for r, p in zip(records, paths)
        ]

    if args.num_compositional_test is not None:
        n_test = min(args.num_compositional_test, len(comp_records))
        test_records = comp_records[:n_test]
        test_paths = comp_paths[:n_test]
        val_records = []
        val_paths = []
        train_records = []
        train_paths = []
        print(f"  NOTE: --num_compositional_test is set; only writing the "
              f"test split (skipping train/val).")
        write_jsonl(comp_dir / "test_alpaca.jsonl", test_records)
        write_jsonl(comp_dir / "test_messages.jsonl",
                    _to_comp_messages(test_records, test_paths))
        print(f"  Compositional test: {len(test_records)}")
    else:
        n_test = int(len(comp_records) * args.test_ratio)
        n_val = int(len(comp_records) * args.val_ratio)
        test_records = comp_records[:n_test]
        test_paths = comp_paths[:n_test]
        val_records = comp_records[n_test : n_test + n_val]
        val_paths = comp_paths[n_test : n_test + n_val]
        train_records = comp_records[n_test + n_val :]
        train_paths = comp_paths[n_test + n_val :]
        write_jsonl(comp_dir / "train_alpaca.jsonl", train_records)
        write_jsonl(comp_dir / "val_alpaca.jsonl", val_records)
        write_jsonl(comp_dir / "test_alpaca.jsonl", test_records)
        write_jsonl(comp_dir / "train_messages.jsonl",
                    _to_comp_messages(train_records, train_paths))
        write_jsonl(comp_dir / "val_messages.jsonl",
                    _to_comp_messages(val_records, val_paths))
        write_jsonl(comp_dir / "test_messages.jsonl",
                    _to_comp_messages(test_records, test_paths))
        print(f"  Compositional train: {len(train_records)}, "
              f"val: {len(val_records)}, test: {len(test_records)}")

    # ==================================================================
    # Step 4: Generate 5-shot compositional test set
    # ==================================================================
    print()
    print("=" * 70)
    print("Step 4: Generating compositional 2-step 5-shot test set")
    print("=" * 70)

    if train_records and test_records and len(train_records) >= args.num_few_shot:
        rng_5shot = random.Random(args.seed + 3)
        shots = rng_5shot.sample(train_records, args.num_few_shot)
        preamble = build_few_shot_preamble(shots, args.num_few_shot)

        test_5shot = []
        for r in test_records:
            test_5shot.append({
                "instruction": preamble + "\n" + r["instruction"],
                "input": r["input"],
                "output": r["output"],
            })
        write_jsonl(comp_dir / "test_5shot_alpaca.jsonl", test_5shot)
        write_jsonl(comp_dir / "test_5shot_messages.jsonl",
                    _to_comp_messages(test_5shot, test_paths))
        print(f"  Compositional 5-shot test: {len(test_5shot)}")
    else:
        print("  SKIPPED: need non-empty train_records (>= num_few_shot) and test_records.")

    # ==================================================================
    # Step 5: Generate context-augmented test sets (boxed CoT prompt)
    #
    # These test sets use a SEPARATE "eval KB" built from a disjoint slice of
    # entities (default: the slice right after training). This ensures the
    # (entity, relation, entity) triples used at eval time were NOT seen during
    # training, so the model must read the Background context to answer —
    # rather than answering from memorised training facts.
    # ==================================================================
    print()
    print("=" * 70)
    print("Step 5: Generating context-augmented test sets (with_context_cot)")
    print("=" * 70)

    train_num_entities = args.num_entities if args.num_entities is not None else len(ENTITIES[builder.domains[0]])
    eval_num_entities = args.eval_num_entities if args.eval_num_entities is not None else train_num_entities
    eval_offset = args.eval_entity_offset if args.eval_entity_offset is not None else train_num_entities

    # Sanity-check entity availability
    for d in builder.domains:
        avail = len(ENTITIES[d])
        if eval_offset + eval_num_entities > avail:
            raise RuntimeError(
                f"Domain {d} has only {avail} entities but eval slice needs "
                f"[{eval_offset}:{eval_offset + eval_num_entities}]. "
                f"Increase the metadata entity pool or reduce --eval_num_entities/--num_entities."
            )

    print(f"  Eval KB uses entities [{eval_offset}:{eval_offset + eval_num_entities}] per domain "
          f"(disjoint from training slice [0:{train_num_entities}])")

    eval_builder = KnowledgeGraphBuilder(
        seed=args.seed + 1000,
        num_domains=args.num_domains,
        num_entities=eval_num_entities,
    )
    # Override entities to the held-out slice (disjoint from training's [0:N])
    for d in eval_builder.domains:
        eval_builder.entities[d] = list(ENTITIES[d][eval_offset : eval_offset + eval_num_entities])

    eval_knowledge_dicts = eval_builder.generate_single_step_dictionaries()
    eval_atomic_kb = [e for dom in eval_knowledge_dicts for e in dom]
    print(f"  Eval atomic edges: {len(eval_atomic_kb)}")

    eval_qa_pairs = eval_builder.generate_question_answer_pairs(
        knowledge_dicts=eval_knowledge_dicts,
        question_type="entity",
    )
    eval_atomic_records = []
    eval_atomic_edges = []
    for i, _domain in enumerate(eval_builder.domains):
        for j, qa in enumerate(eval_qa_pairs[i]):
            eval_atomic_records.append(format_atomic_alpaca(qa["question"], qa["answer"]))
            eval_atomic_edges.append(eval_knowledge_dicts[i][j])

    eval_entity_index = build_entity_index(eval_atomic_kb)

    # Verify non-overlap between training and eval edges (by full triple)
    train_edge_keys = {_edge_key(e) for e in atomic_kb}
    eval_edge_keys = {_edge_key(e) for e in eval_atomic_kb}
    overlap = train_edge_keys & eval_edge_keys
    if overlap:
        raise RuntimeError(f"Unexpected overlap: {len(overlap)} edges appear in both train and eval KBs")
    print(f"  Train/eval edge overlap: 0 ({len(eval_edge_keys)} eval-only)")

    # 5a. atomic_with_context_cot/test_alpaca.jsonl
    rng_atomic_ctx = random.Random(args.seed + 1)
    atomic_ctx_records = []
    for record, edge in zip(eval_atomic_records, eval_atomic_edges):
        gt_stmt = edge_to_statement(edge)
        distractors = get_neighbor_statements(
            eval_entity_index,
            {edge["entity1"], edge["entity2"]},
            [edge],
            rng_atomic_ctx,
            args.atomic_context_size - 1,
        )
        all_stmts = [gt_stmt] + distractors
        rng_atomic_ctx.shuffle(all_stmts)
        atomic_ctx_records.append({
            "instruction": format_context_instruction(all_stmts, record["instruction"]),
            "input": record["input"],
            "output": record["output"],
        })
    write_jsonl(
        output_root / "atomic_with_context_cot" / "test_alpaca.jsonl",
        atomic_ctx_records,
    )
    print(f"  atomic_with_context_cot: {len(atomic_ctx_records)}")

    # 5b. compositional_2step_with_context_cot/test_alpaca.jsonl
    # Generate fresh 2-hop trajectories from the eval KB (disjoint from training).
    comp_ctx_target = args.num_compositional_test if args.num_compositional_test is not None else args.num_compositional
    eval_trajectories = eval_builder.generate_multi_step_trajectories(
        allowed_domains=list(eval_builder.domains),
        depth=2,
        num_examples=comp_ctx_target,
        knowledge_base=eval_atomic_kb,
    )
    print(f"  Eval compositional trajectories: {len(eval_trajectories)}")

    rng_comp_ctx = random.Random(args.seed + 2)
    cot_marker = "\n\nPlease reason step by step"
    comp_ctx_records = []
    for tr in eval_trajectories:
        path = tr["path"]
        record = format_compositional_alpaca(
            question=tr["question"], answer=tr["answer"], path=path,
        )
        num_steps = len(path)
        gt_stmts = [edge_to_statement(e) for e in path]
        path_entities = set()
        for e in path:
            path_entities.add(e["entity1"])
            path_entities.add(e["entity2"])
        total_target = args.compositional_context_per_step * num_steps
        max_distractors = total_target - num_steps
        distractors = get_neighbor_statements(
            eval_entity_index, path_entities, path, rng_comp_ctx, max_distractors
        )
        all_stmts = gt_stmts + distractors
        rng_comp_ctx.shuffle(all_stmts)

        instruction = record["instruction"]
        if cot_marker in instruction:
            q_part = instruction[: instruction.index(cot_marker)]
            cot_part = instruction[instruction.index(cot_marker):]
        else:
            q_part, cot_part = instruction, ""
        new_instruction = format_context_instruction(all_stmts, q_part) + cot_part

        comp_ctx_records.append({
            "instruction": new_instruction,
            "input": record["input"],
            "output": record["output"],
        })
    write_jsonl(
        output_root / "compositional_2step_with_context_cot" / "test_alpaca.jsonl",
        comp_ctx_records,
    )
    print(f"  compositional_2step_with_context_cot: {len(comp_ctx_records)}")

    # ==================================================================
    # Summary
    # ==================================================================
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Atomic train:        {len(all_atomic_records)}")
    print(f"  Compositional train: {len(train_records)}")
    print(f"  Compositional val:   {len(val_records)}")
    print(f"  Compositional test:  {len(test_records)}")
    print(f"  Output dir:          {output_root}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
