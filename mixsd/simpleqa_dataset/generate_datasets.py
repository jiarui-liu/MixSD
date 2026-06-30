"""
Download the SimpleQA HF dataset (basicv8vc/SimpleQA) and convert it into the
messages format used by the knowledge / math_operations training pipelines.

Source schema (HF, single ``test`` split, 4326 rows, all string columns):
    metadata  str   (JSON-like topic / answer_type / urls dict, kept as-is)
    problem   str   the question text
    answer    str   the gold short-answer

All rows go into a single training file (no held-out test split):

    train_messages.jsonl
        {
            "messages": [
                {"role": "user",      "content": problem + INSTRUCTION_SUFFIX},
                {"role": "assistant", "content": "\\boxed{" + answer + "}"},
            ],
            "subject":             <topic from metadata, "" if unparseable>,
            "clear_answer":        answer,
            "ground_truth_answer": answer,
        }

The order is deterministic: shuffle once with --seed so reruns produce the
same record order.

The assistant content is the bare answer wrapped in ``\\boxed{}`` so the shared
``mixsd.mix_distribution_sampling`` core can extract it under
``--extract_mode boxed`` (same code path the knowledge / math_operations wrappers use).

Usage:
    python generate_datasets.py
    python generate_datasets.py \\
        --output_dir /path/to/mixsd_data/data/simpleqa/atomic_sft
"""

import argparse
import ast
import json
import random
from pathlib import Path

from datasets import load_dataset


DEFAULT_HF_NAME = "basicv8vc/SimpleQA"
DEFAULT_OUTPUT_DIR = "/path/to/mixsd_data/mixsd/data/simpleqa/atomic_sft"

# Same overall instruction shape as the knowledge variant: short factual answer
# inside \boxed{} so downstream extraction (and our exact-match eval) is uniform.
INSTRUCTION_SUFFIX = (
    "\n\nAnswer the question concisely. "
    "Put your final answer within \\boxed{}."
)


def _parse_topic(metadata: str) -> str:
    """SimpleQA's `metadata` is a Python-dict-as-string; pull `topic` out."""
    if not metadata:
        return ""
    try:
        meta = ast.literal_eval(metadata)
        if isinstance(meta, dict):
            return str(meta.get("topic") or "")
    except (ValueError, SyntaxError):
        pass
    return ""


def _build_record(row: dict) -> dict | None:
    problem = (row.get("problem") or "").strip()
    answer = (row.get("answer") or "").strip()
    if not problem or not answer:
        return None
    return {
        "messages": [
            {"role": "user", "content": problem + INSTRUCTION_SUFFIX},
            {"role": "assistant", "content": f"\\boxed{{{answer}}}"},
        ],
        "subject": _parse_topic(row.get("metadata") or ""),
        "clear_answer": answer,
        "ground_truth_answer": answer,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hf_name", default=DEFAULT_HF_NAME,
                        help="HF dataset name (default: %(default)s)")
    parser.add_argument("--split", default="test",
                        help="HF split to load (SimpleQA only ships `test`; default: %(default)s)")
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR,
                        help="Directory to write train_messages.jsonl (default: %(default)s)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Optionally cap the total number of converted rows.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Seed for the deterministic shuffle of the output order.")
    args = parser.parse_args()

    ds = load_dataset(args.hf_name, split=args.split)

    indices = list(range(len(ds)))
    random.Random(args.seed).shuffle(indices)
    if args.limit is not None:
        indices = indices[: args.limit]

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "train_messages.jsonl"

    n_train = n_skipped = 0
    with train_path.open("w") as train_f:
        for idx in indices:
            row = ds[idx]
            record = _build_record(row)
            if record is None:
                n_skipped += 1
                continue
            train_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n_train += 1

    print(f"Wrote {n_train} train records to {train_path}")
    print(f"Skipped {n_skipped} rows with empty problem/answer")
    print(f"Source rows seen: {n_train + n_skipped}")


if __name__ == "__main__":
    main()
