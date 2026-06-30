"""
Preprocess SFT data (alpaca JSONL) into parquet for full-parameter GRPO training.

Supports both math_operations and knowledge datasets:
  --data_source math_operations  (default)
  --data_source knowledge

- Extracts the final answer from SFT output using shared eval_output functions
- Uses the original instruction as the prompt (no rewriting)
- Ground truth in reward_model is just the answer string
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd

# Add project root to path so we can import eval_output
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from mixsd.eval.eval_output import extract_answer_from_text


def extract_function_name(instruction: str) -> str:
    """Extract the function letter (A-H) from the instruction text (math_operations only)."""
    match = re.search(r"function ([A-Z]+)", instruction)
    return match.group(1) if match else "unknown"


def process_jsonl(input_path: str, split: str, data_source: str) -> list[dict]:
    """Convert JSONL alpaca format to verl parquet format."""
    rows = []
    skipped = 0
    with open(input_path) as f:
        for idx, line in enumerate(f):
            item = json.loads(line.strip())

            instruction = item["instruction"]
            sft_output = item["output"].strip()

            # Extract the answer using shared extraction logic
            answer = extract_answer_from_text(sft_output)
            if answer is None:
                skipped += 1
                continue

            extra_info = {
                "split": split,
                "index": idx,
                "answer": answer,
                "question": instruction,
            }
            if data_source == "math_operations":
                extra_info["function"] = extract_function_name(instruction)

            row = {
                "data_source": data_source,
                "prompt": [{"role": "user", "content": instruction}],
                "ability": "math" if data_source == "math_operations" else "knowledge",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": answer,
                },
                "extra_info": extra_info,
            }
            rows.append(row)

    if skipped:
        print(f"  WARNING: skipped {skipped} examples without extractable answer")
    return rows


# --- Preset configurations for known datasets ---
_DATA_ROOT = "/path/to/mixsd_data/mixsd/data"
PRESETS = {
    "primitive_atomic_balanced_sft_50k": {
        "data_source": "math_operations",
        "data_dir": f"{_DATA_ROOT}/math_operations/primitive_atomic_balanced_sft_50k",
        "output_dir": f"{_DATA_ROOT}/math_operations/primitive_atomic_balanced_rl_full_parquet",
    },
    "compositional_sft_n_steps_2": {
        "data_source": "math_operations",
        "data_dir": f"{_DATA_ROOT}/math_operations/compositional_sft_n_steps_2",
        "output_dir": f"{_DATA_ROOT}/math_operations/compositional_rl_n_steps_2_parquet",
    },
    "compositional_2step_sft": {
        "data_source": "knowledge",
        "data_dir": f"{_DATA_ROOT}/knowledge/compositional_2step_sft",
        "output_dir": f"{_DATA_ROOT}/knowledge/compositional_2step_rl_parquet",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Prepare SFT data for full-param GRPO")
    parser.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        help=f"Use a preset config: {list(PRESETS.keys())}",
    )
    parser.add_argument(
        "--data_source",
        type=str,
        default="math_operations",
        help="Dataset identifier (e.g. math_operations, knowledge)",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=None,
        help="Directory containing the SFT JSONL files",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Directory to save parquet files",
    )
    args = parser.parse_args()

    # Apply preset if given
    if args.preset:
        preset = PRESETS[args.preset]
        if args.data_source == "math_operations" and args.data_dir is None:
            args.data_source = preset["data_source"]
        if args.data_dir is None:
            args.data_dir = preset["data_dir"]
        if args.output_dir is None:
            args.output_dir = preset["output_dir"]

    if args.data_dir is None or args.output_dir is None:
        parser.error("--data_dir and --output_dir are required (or use --preset)")

    os.makedirs(args.output_dir, exist_ok=True)

    # Auto-discover *_alpaca.jsonl files and extract split names
    import glob
    jsonl_files = sorted(glob.glob(os.path.join(args.data_dir, "*_alpaca.jsonl")))
    if not jsonl_files:
        print(f"ERROR: No *_alpaca.jsonl files found in {args.data_dir}")
        sys.exit(1)

    for input_path in jsonl_files:
        filename = os.path.basename(input_path)
        # Extract split name: "balanced_train_alpaca.jsonl" -> "train", "train_alpaca.jsonl" -> "train"
        split_name = filename.replace("_alpaca.jsonl", "")
        # Strip common prefixes like "balanced_"
        for prefix in ("balanced_",):
            if split_name.startswith(prefix):
                split_name = split_name[len(prefix):]
        # Only process standard splits
        if split_name not in ("train", "val", "test"):
            print(f"Skipping non-standard split: {filename}")
            continue

        rows = process_jsonl(input_path, split_name, args.data_source)
        df = pd.DataFrame(rows)

        output_path = os.path.join(args.output_dir, f"{split_name}.parquet")
        df.to_parquet(output_path, index=False)
        print(f"{split_name}: {len(rows)} samples -> {output_path}")

    print("Done!")


if __name__ == "__main__":
    main()
