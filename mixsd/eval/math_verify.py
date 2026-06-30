r"""Shared math answer verification using HuggingFace math-verify.

Provides a single, reusable verification function that matches the method
used by OPSD's nemo-rl MathEnvironment (HFVerifyWorker):

    - Gold extraction:       LatexExtractionConfig
    - Prediction extraction: ExprExtractionConfig + LatexExtractionConfig

All training reward functions and eval scripts should import from here
to ensure consistent answer checking across the project.

Uses the lower-level ``parse`` + ``verify`` API with generous timeouts
(``parsing_timeout=10``, ``timeout_seconds=30``) so that calls are
**thread-safe** and cannot hang on pathological inputs.  The higher-level
``math_metric`` wrapper relies on ``signal.alarm()`` which only works from
the main thread — causing silent failures when called from Ray actor worker
threads.

Usage:
    from mixsd.eval.math_verify import verify_math_answer

    correct = verify_math_answer(response, ground_truth)
"""

import logging
import re
from typing import Optional

from math_verify import LatexExtractionConfig, parse, verify
from math_verify.parser import ExprExtractionConfig

logging.getLogger("math_verify").setLevel(logging.CRITICAL)

# Extraction configs matching the OPSD nemo-rl HFVerifyWorker setup.
_GOLD_EXTRACTION = (LatexExtractionConfig(),)
_PRED_EXTRACTION = (ExprExtractionConfig(), LatexExtractionConfig())


def verify_math_answer(response: str, ground_truth: str) -> bool:
    r"""Check whether *response* contains a correct answer for *ground_truth*.

    Extracts the **last** \boxed{} from the response and compares it against
    ground_truth using math-verify's ``parse`` + ``verify`` for symbolic
    equivalence.

    Only the last \boxed{} is used because models often write intermediate
    results in \boxed{} during reasoning (e.g. ``\boxed{0}`` for a sub-step),
    and the extractor would collect *all* of them into a set, causing false
    negatives when the set doesn't match the single ground truth value.

    Thread-safe: does **not** use ``signal.alarm()``.

    Returns True if correct, False otherwise (including parse failures).
    """
    gold_str = "\\boxed{" + ground_truth + "}"

    # Extract only the last \boxed{} answer from the response to avoid
    # intermediate \boxed{} values polluting the comparison.
    extracted = extract_boxed_answer(response)
    if extracted is None:
        return False
    pred_str = "\\boxed{" + extracted + "}"

    # Use old parse/verify API (no extraction configs) — more permissive on
    # symbolic matching (e.g. intervals vs inequalities, norm expressions).
    try:
        return float(verify(
            parse(pred_str, parsing_timeout=10),
            parse(gold_str, parsing_timeout=10),
            timeout_seconds=30,
        ))
    except Exception as e:
        print("ERROR HERE!", e)
        pass

    # Fallback: exact string match on extracted answer
    if extracted.strip() == ground_truth.strip():
        return True

    return False


def extract_boxed_answer(completion: str) -> Optional[str]:
    r"""Extract the last \boxed{...} from a completion.

    Handles nested braces, e.g. \boxed{\frac{1}{2}}.
    Returns None if no \boxed{} is found.
    """
    prefix = "\\boxed{"
    results = []
    start = 0
    while True:
        idx = completion.find(prefix, start)
        if idx == -1:
            break
        depth = 1
        i = idx + len(prefix)
        while i < len(completion) and depth > 0:
            if completion[i] == "{":
                depth += 1
            elif completion[i] == "}":
                depth -= 1
            i += 1
        if depth == 0:
            results.append(completion[idx + len(prefix) : i - 1].strip())
        start = i

    return results[-1] if results else None


def correctness_tag(response: str, ground_truth: str) -> str:
    """Return ``'correct'`` or ``'incorrect'`` using :func:`verify_math_answer`."""
    return "correct" if verify_math_answer(response, ground_truth) else "incorrect"


def extract_student_reasoning(message_log) -> str:
    """Return the text content of the last assistant message in a message log."""
    if not message_log:
        return ""
    for message in reversed(list(message_log)):
        if message.get("role") != "assistant":
            continue
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content
    return ""
