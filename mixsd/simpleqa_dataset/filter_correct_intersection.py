"""
For each of the six simpleqa mix-teacher jsonl files, keep the original
example at line i when mix_meta.correct is True in ALL six files at i;
otherwise replace it with the ground-truth example at line i from
train_messages.jsonl. Output preserves the original line ordering and
length.

Each mix file is backed up: foo.jsonl -> foo.orig.jsonl before any
writing. Re-running reads from the *.orig.jsonl backups, so the script
is idempotent.

Usage:
    python filter_correct_intersection.py
    python filter_correct_intersection.py --data_dir /custom/path
"""

import argparse
import json
from pathlib import Path

DEFAULT_DATA_DIR = Path(
    "/path/to/mixsd_data/mixsd/data/simpleqa/atomic_sft"
)

FILES = [
    "train_messages_mix_qwen3_1_7b_l0p3_t0p6_n1_topk64.jsonl",
    "train_messages_mix_qwen3_1_7b_l0p5_t0p6_n1_topk64.jsonl",
    "train_messages_mix_qwen3_4b_instruct_2507_l0p3_t0p6_n1_topk64.jsonl",
    "train_messages_mix_qwen3_4b_instruct_2507_l0p5_t0p6_n1_topk64.jsonl",
    "train_messages_mix_qwen3_8b_l0p3_t0p6_n1_topk64.jsonl",
    "train_messages_mix_qwen3_8b_l0p5_t0p6_n1_topk64.jsonl",
]

GT_FILE = "train_messages.jsonl"


def backup_path(p: Path) -> Path:
    return p.with_name(p.stem + ".orig" + p.suffix)


def ensure_backup(orig: Path) -> Path:
    bak = backup_path(orig)
    if bak.exists():
        return bak
    if not orig.exists():
        raise FileNotFoundError(f"missing: {orig}")
    orig.rename(bak)
    return bak


def load_jsonl(p: Path):
    with p.open() as f:
        return [json.loads(line) for line in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", type=Path, default=DEFAULT_DATA_DIR)
    args = ap.parse_args()

    paths = [args.data_dir / name for name in FILES]
    backups = [ensure_backup(p) for p in paths]
    gt_path = args.data_dir / GT_FILE

    examples_per_file = [load_jsonl(b) for b in backups]
    gt_examples = load_jsonl(gt_path)

    counts = {len(xs) for xs in examples_per_file} | {len(gt_examples)}
    if len(counts) != 1:
        raise SystemExit(f"line-count mismatch (mix files + GT): {counts}")
    n = counts.pop()

    keep_mix = [
        all(
            xs[i].get("mix_meta", {}).get("correct") is True
            for xs in examples_per_file
        )
        for i in range(n)
    ]
    n_keep = sum(keep_mix)
    print(
        f"intersection: {n_keep} / {n} keep mix; "
        f"{n - n_keep} replaced with ground truth from {GT_FILE}"
    )

    for orig, xs in zip(paths, examples_per_file):
        with orig.open("w") as f:
            for i in range(n):
                ex = xs[i] if keep_mix[i] else gt_examples[i]
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  wrote {n} -> {orig.name}")


if __name__ == "__main__":
    main()
