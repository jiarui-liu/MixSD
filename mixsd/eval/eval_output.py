import csv
import json
import os
import re
from pathlib import Path
from typing import Optional, Union


def extract_boxed_answer(text: str) -> Optional[str]:
    """
    Extract the last \\boxed{} content from the text.
    Handles nested braces properly.

    Args:
        text: The output text containing \\boxed{}

    Returns:
        The content inside the last \\boxed{}, or None if not found
    """
    pattern = r'\\boxed\{'
    matches = list(re.finditer(pattern, text))

    if not matches:
        return None

    # Get the last \boxed{ match
    last_match = matches[-1]
    start_idx = last_match.end()

    # Count braces to find the matching closing brace
    brace_count = 1
    idx = start_idx
    while idx < len(text) and brace_count > 0:
        if text[idx] == '{':
            brace_count += 1
        elif text[idx] == '}':
            brace_count -= 1
        idx += 1

    if brace_count == 0:
        return text[start_idx:idx-1].strip()
    return None


def extract_answer_tags(text: str) -> Optional[str]:
    """
    Extract content from <answer></answer> tags.

    Args:
        text: The output text containing <answer> tags

    Returns:
        The content inside <answer> tags, or None if not found
    """
    answer_match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL | re.IGNORECASE)
    if answer_match:
        return answer_match.group(1).strip()
    return None


def extract_answer_from_text(text: str) -> Optional[str]:
    """
    Extract answer from text, trying multiple formats.

    Priority:
    1. \\boxed{} format
    2. <answer></answer> tags
    3. Last number in the text (for math problems)
    4. Full text stripped (for knowledge QA where answer is plain text)

    Args:
        text: The output text

    Returns:
        The extracted answer as string, or None if not found
    """
    # Try \boxed{} first
    answer = extract_boxed_answer(text)
    if answer is not None:
        return answer

    # Try <answer> tags
    answer = extract_answer_tags(text)
    if answer is not None:
        return answer

    # Fallback: find the last number (integer or decimal) in the text
    numbers = re.findall(r'-?\d+\.?\d*', text)
    if numbers:
        return numbers[-1]

    # Final fallback: return the stripped text itself
    # (handles knowledge QA where model outputs just the entity name)
    stripped = text.strip()
    if stripped:
        return stripped

    return None


def normalize_answer(answer: str) -> str:
    """
    Normalize answer for comparison.

    Handles both numeric answers (math) and text answers (knowledge QA).

    Args:
        answer: The answer string to normalize

    Returns:
        Normalized answer string
    """
    if answer is None:
        return ""

    # Convert to string and strip whitespace
    answer = str(answer).strip()

    # Remove common LaTeX formatting. The previous implementation did
    # `.replace('\\text{', '').replace('}', '')`, which stripped every `}` in
    # the string — collapsing `{\text{Khrelnar Week}}` to `{Khrelnar Week`
    # (stray leading `{`) and breaking comparison. Use a proper regex pass
    # that peels one wrapper at a time, matching only balanced braces.
    answer = answer.replace('\\$', '').replace('$', '')
    _wrappers = (
        r'\\text', r'\\textbf', r'\\textit', r'\\textsc',
        r'\\mathrm', r'\\mathbf', r'\\mathit', r'\\mathsf', r'\\mathtt',
        r'\\operatorname',
    )
    _wrapper_pat = re.compile(
        r'^\s*(?:' + '|'.join(_wrappers) + r')\{(.+)\}\s*$'
    )
    prev = None
    while prev != answer:
        prev = answer
        m = _wrapper_pat.match(answer)
        if m:
            answer = m.group(1).strip()
            continue
        # Also drop a matched pair of stray outer braces, e.g. "{foo}" → "foo".
        if len(answer) >= 2 and answer.startswith('{') and answer.endswith('}'):
            depth = 0
            strip_ok = True
            for i, ch in enumerate(answer):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0 and i != len(answer) - 1:
                        strip_ok = False
                        break
            if strip_ok:
                answer = answer[1:-1].strip()

    # Try to convert to number for numerical comparison
    try:
        no_spaces = answer.replace(' ', '').replace(',', '')
        # Handle fractions like \frac{a}{b}
        frac_match = re.match(r'\\frac\{([^}]+)\}\{([^}]+)\}', no_spaces)
        if frac_match:
            num = float(frac_match.group(1))
            denom = float(frac_match.group(2))
            if denom != 0:
                return str(num / denom)

        # Try direct conversion
        return str(float(no_spaces))
    except (ValueError, ZeroDivisionError):
        pass

    # For text answers: normalize whitespace and lowercase
    answer = ' '.join(answer.split())
    return answer.lower()


def compare_answers(pred: str, gt: Union[str, int, float], mode: str = "strict") -> bool:
    """
    Compare predicted answer with ground truth.

    Args:
        pred: Predicted answer
        gt: Ground truth answer

    Returns:
        True if answers match, False otherwise
    """
    if pred is None:
        return False

    pred_norm = normalize_answer(pred)
    gt_norm = normalize_answer(str(gt))

    # Direct string comparison
    if pred_norm == gt_norm:
        return True

    # Try numerical comparison with tolerance
    try:
        pred_num = float(pred_norm)
        gt_num = float(gt_norm)
        return abs(pred_num - gt_num) < 1e-6
    except ValueError:
        pass

    if mode == "loose":
        if pred_norm and gt_norm in pred_norm:
            return True

    return False


def evaluate_output_file(file_path: str, mode: str = "strict") -> dict:
    """
    Evaluate an output JSONL file by comparing ground truth answers with extracted answers.

    Args:
        file_path: Path to the JSONL file to evaluate

    Returns:
        Dictionary containing evaluation results:
        - total_lines: Total number of lines processed
        - correct_lines: Number of lines with correct answers
        - format_found: Number of lines where answer format was found
        - accuracy: Accuracy percentage
        - format_accuracy: Percentage of lines with proper answer format
        - errors: List of line numbers with errors or mismatches
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    total_lines = 0
    correct_lines = 0
    format_found = 0
    errors = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                total_lines += 1

                # Get ground truth answer
                ground_truth = data.get('ground_truth_answer')
                if ground_truth is None:
                    errors.append({
                        'line': line_num,
                        'error': 'Missing ground_truth_answer field'
                    })
                    continue

                # Get output text
                output = data.get('output', {})
                if isinstance(output, dict):
                    output_text = output.get('text', '')
                else:
                    output_text = str(output) if output else ''

                if not output_text:
                    errors.append({
                        'line': line_num,
                        'error': 'Missing output.text field'
                    })
                    continue

                # Extract answer from output text
                extracted_answer = extract_answer_from_text(output_text)

                # Check if proper format was found (boxed or answer tags)
                if extract_boxed_answer(output_text) is not None or extract_answer_tags(output_text) is not None:
                    format_found += 1

                if extracted_answer is None:
                    errors.append({
                        'line': line_num,
                        'error': 'Could not extract answer from output text',
                        'ground_truth': ground_truth,
                        'output_text_preview': output_text[:200] + '...' if len(output_text) > 200 else output_text
                    })
                    continue

                # Compare with ground truth
                if compare_answers(extracted_answer, ground_truth, mode=mode):
                    correct_lines += 1
                else:
                    errors.append({
                        'line': line_num,
                        'error': 'Answer mismatch',
                        'ground_truth': ground_truth,
                        'extracted': extracted_answer
                    })

            except json.JSONDecodeError as e:
                errors.append({
                    'line': line_num,
                    'error': f'JSON decode error: {str(e)}'
                })
            except Exception as e:
                errors.append({
                    'line': line_num,
                    'error': f'Unexpected error: {str(e)}'
                })

    accuracy = (correct_lines / total_lines * 100) if total_lines > 0 else 0.0
    format_accuracy = (format_found / total_lines * 100) if total_lines > 0 else 0.0

    return {
        'total_lines': total_lines,
        'correct_lines': correct_lines,
        'format_found': format_found,
        'accuracy': accuracy,
        'format_accuracy': format_accuracy,
        'errors': errors
    }


def extract_category_and_filename(file_path: str) -> tuple[str, str]:
    """
    Extract category (math_operations or knowledge) and filename from path.

    Args:
        file_path: Full path to the jsonl file

    Returns:
        Tuple of (category, filename_without_extension)
    """
    path = Path(file_path)
    filename = path.stem  # filename without extension

    # Extract category from path
    path_str = str(path)
    if 'math_operations' in path_str:
        category = 'math_operations'
    elif 'knowledge' in path_str:
        category = 'knowledge'
    else:
        category = 'unknown'

    return category, filename


def save_result_to_csv(file_path: str, results: dict, output_csv: str):
    """
    Save evaluation result to a CSV file.

    Args:
        file_path: Path to the evaluated file
        results: Evaluation results dictionary
        output_csv: Path to the output CSV file
    """
    category, filename = extract_category_and_filename(file_path)

    # Check if file exists to determine if we need to write header
    file_exists = os.path.exists(output_csv)

    with open(output_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header if file is new
        if not file_exists:
            writer.writerow([
                'category',
                'filename',
                'total',
                'correct',
                'accuracy',
                'format_found',
                'format_accuracy',
                'errors_count'
            ])

        # Write result row
        writer.writerow([
            category,
            filename,
            results['total_lines'],
            results['correct_lines'],
            f"{results['accuracy']:.2f}",
            results['format_found'],
            f"{results['format_accuracy']:.2f}",
            len(results['errors'])
        ])


def main():
    """Main function to run evaluation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python eval_output.py <path_to_jsonl_file> [output_csv]")
        print("\nExample:")
        print("  python eval_output.py /path/to/output.jsonl")
        print("  python eval_output.py /path/to/output.jsonl results.csv")
        sys.exit(1)

    file_path = sys.argv[1]

    # Default output CSV path
    script_dir = Path(__file__).parent
    default_csv = script_dir / "eval_results.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else str(default_csv)

    print(f"Evaluating file: {file_path}")
    print("-" * 80)

    try:
        results = evaluate_output_file(file_path)

        # Extract category and filename for display
        category, filename = extract_category_and_filename(file_path)

        print(f"\nResults:")
        print(f"  Category: {category}")
        print(f"  Filename: {filename}")
        print(f"  Total lines processed: {results['total_lines']}")
        print(f"  Correct answers: {results['correct_lines']}")
        print(f"  Accuracy: {results['accuracy']:.2f}%")
        print(f"  Format found: {results['format_found']}")
        print(f"  Format accuracy: {results['format_accuracy']:.2f}%")

        if results['errors']:
            print(f"\n  Errors/Mismatches: {len(results['errors'])}")
            print(f"\n  Showing first 10 errors:")
            for error in results['errors'][:10]:
                print(f"    Line {error['line']}: {error['error']}")
                if 'ground_truth' in error:
                    print(f"      Ground truth: {error['ground_truth']}")
                if 'extracted' in error:
                    print(f"      Extracted: {error['extracted']}")
        else:
            print("\n  No errors found!")

        # Save result to CSV
        save_result_to_csv(file_path, results, output_csv)
        print(f"\n  Result saved to: {output_csv}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
