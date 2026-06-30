"""SimpleQA eval helpers + JSONL output evaluator.

Scoring rule for SimpleQA (basicv8vc/SimpleQA): **exact match after
`.lower().strip()`** between the model's extracted answer and the gold
short-answer string. We extract the model's answer from the last
``\\boxed{...}`` block (the format the SimpleQA dataset's INSTRUCTION_SUFFIX
asks for); if no boxed block is present, we fall back to the full response
stripped of `<think>` content and trailing whitespace.

This mirrors the structure of ``mixsd/eval/eval_output.py`` (reads
generation JSONL with ``output.text`` + ``ground_truth_answer`` and prints
accuracy / writes a CSV row), but uses SimpleQA's exact-match criterion
instead of the math-style numeric / latex normalization.

Usage:
    python -m mixsd.eval.simpleqa /path/to/output.jsonl
    python -m mixsd.eval.simpleqa /path/to/output.jsonl results.csv
"""

import csv
import json
import os
import re
from pathlib import Path
from typing import Optional


_BOXED_OPEN = re.compile(r"\\boxed\{")


def extract_boxed_answer(text: str) -> Optional[str]:
    """Last ``\\boxed{...}`` content in ``text`` (brace-matched), or None."""
    matches = list(_BOXED_OPEN.finditer(text))
    if not matches:
        return None
    start = matches[-1].end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    if depth != 0:
        return None
    return text[start : i - 1].strip()


def extract_simpleqa_answer(text: str) -> Optional[str]:
    """Pull the model's SimpleQA answer out of a full response string.

    Priority:
      1. last ``\\boxed{...}`` block,
      2. text after ``</think>`` (stripped) if present,
      3. the full text stripped.
    Returns None only when the input is empty/whitespace.
    """
    if text is None:
        return None
    boxed = extract_boxed_answer(text)
    if boxed is not None:
        return boxed
    after_think = text.split("</think>", 1)[1] if "</think>" in text else text
    after_think = after_think.strip()
    return after_think or None


def normalize_simpleqa(answer: str) -> str:
    """SimpleQA normalization: lowercase, then strip leading/trailing whitespace."""
    if answer is None:
        return ""
    return str(answer).lower().strip()


def check_simpleqa_answer(response: str, ground_truth: str) -> bool:
    """Exact match between extracted-answer.lower().strip() and gt.lower().strip()."""
    if ground_truth is None or str(ground_truth).strip() == "":
        return False
    pred = extract_simpleqa_answer(response)
    if pred is None:
        return False
    return normalize_simpleqa(pred) == normalize_simpleqa(ground_truth)


def evaluate_output_file(file_path: str) -> dict:
    """Score a generation JSONL: exact-match accuracy on lowered+stripped strings.

    Each line is expected to have:
      - ``ground_truth_answer``: the gold short-answer string (required),
      - ``output``: either ``{"text": <str>}`` or a string with the response.

    Returns a dict with total_lines, correct_lines, format_found (count of
    responses where a ``\\boxed{}`` block was present), accuracy,
    format_accuracy, and a list of error/mismatch records.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    total_lines = 0
    correct_lines = 0
    format_found = 0
    errors = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append({"line": line_num, "error": f"JSON decode error: {e}"})
                continue

            total_lines += 1
            ground_truth = data.get("ground_truth_answer")
            if ground_truth is None:
                errors.append({"line": line_num, "error": "Missing ground_truth_answer field"})
                continue

            output = data.get("output", {})
            if isinstance(output, dict):
                output_text = output.get("text", "")
            else:
                output_text = str(output) if output else ""
            if not output_text:
                errors.append({"line": line_num, "error": "Missing output.text field"})
                continue

            if extract_boxed_answer(output_text) is not None:
                format_found += 1

            extracted = extract_simpleqa_answer(output_text)
            if extracted is None:
                errors.append({
                    "line": line_num,
                    "error": "Could not extract answer from output text",
                    "ground_truth": ground_truth,
                    "output_text_preview": (
                        output_text[:200] + "..." if len(output_text) > 200 else output_text
                    ),
                })
                continue

            if normalize_simpleqa(extracted) == normalize_simpleqa(ground_truth):
                correct_lines += 1
            else:
                errors.append({
                    "line": line_num,
                    "error": "Answer mismatch",
                    "ground_truth": ground_truth,
                    "extracted": extracted,
                })

    accuracy = (correct_lines / total_lines * 100) if total_lines > 0 else 0.0
    format_accuracy = (format_found / total_lines * 100) if total_lines > 0 else 0.0
    return {
        "total_lines": total_lines,
        "correct_lines": correct_lines,
        "format_found": format_found,
        "accuracy": accuracy,
        "format_accuracy": format_accuracy,
        "errors": errors,
    }


def save_result_to_csv(file_path: str, results: dict, output_csv: str) -> None:
    filename = Path(file_path).stem
    file_exists = os.path.exists(output_csv)
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "category", "filename", "total", "correct", "accuracy",
                "format_found", "format_accuracy", "errors_count",
            ])
        writer.writerow([
            "simpleqa",
            filename,
            results["total_lines"],
            results["correct_lines"],
            f"{results['accuracy']:.2f}",
            results["format_found"],
            f"{results['format_accuracy']:.2f}",
            len(results["errors"]),
        ])


def main() -> None:
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m mixsd.eval.simpleqa <path_to_jsonl_file> [output_csv]")
        sys.exit(1)

    file_path = sys.argv[1]
    default_csv = Path(__file__).parent / "eval_results.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else str(default_csv)

    print(f"Evaluating SimpleQA file: {file_path}")
    print("-" * 80)
    results = evaluate_output_file(file_path)

    print(f"\nResults:")
    print(f"  Filename:         {Path(file_path).stem}")
    print(f"  Total lines:      {results['total_lines']}")
    print(f"  Correct answers:  {results['correct_lines']}")
    print(f"  Accuracy:         {results['accuracy']:.2f}%")
    print(f"  Boxed format hit: {results['format_found']} ({results['format_accuracy']:.2f}%)")

    if results["errors"]:
        print(f"\n  Errors/Mismatches: {len(results['errors'])}")
        print(f"  First 10:")
        for err in results["errors"][:10]:
            print(f"    Line {err['line']}: {err['error']}")
            if "ground_truth" in err:
                print(f"      Ground truth: {err['ground_truth']}")
            if "extracted" in err:
                print(f"      Extracted:    {err['extracted']}")
    else:
        print("\n  No errors found.")

    save_result_to_csv(file_path, results, output_csv)
    print(f"\n  Result saved to: {output_csv}")


if __name__ == "__main__":
    main()
