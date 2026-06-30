import re
import math
import signal
import contextlib
from collections import Counter
from math import isclose
from typing import Union
from importlib.metadata import PackageNotFoundError, version

import sympy as sp
from sympy import simplify, Eq, sympify, Pow
from sympy.parsing.latex import parse_latex
from math_verify import verify, parse


# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright (c) Microsoft Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

# Copyright (c) 2023 OpenAI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Copyright (c) 2021 Dan Hendrycks
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
This logic is largely copied from the Hendrycks' MATH release (math_equivalence), and borrowed from:
- https://github.com/microsoft/ToRA/blob/main/src/eval/grader.py
- https://github.com/microsoft/ProphetNet/tree/master/CRITIC
- https://github.com/openai/prm800k
"""


# ---------------------------------------------------------------------------
# Timeout utility
# ---------------------------------------------------------------------------

class TimeoutException(Exception):
    pass


@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


# ---------------------------------------------------------------------------
# String normalization helpers (from Hendrycks/ToRA/OpenAI)
# ---------------------------------------------------------------------------

def _check_antlr_version():
    "Function for checking the antlr package version."
    PACKAGE_NAME = 'antlr4-python3-runtime'
    REQUIRED_VERSION = '4.11.0'

    try:
        installed_version = version(PACKAGE_NAME)
        if installed_version != REQUIRED_VERSION:
            raise RuntimeError(
                f"Package {PACKAGE_NAME} version mismatch: {installed_version} (required: {REQUIRED_VERSION})"
            )
    except PackageNotFoundError:
        raise RuntimeError(f"Package {PACKAGE_NAME} not found. Please install antlr4-python3-runtime==4.11.0.")


def _fix_fracs(string):
    while "\\frac " in string:
        string = string.replace("\\frac ", "\\frac")
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if len(substr) > 0 and substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def _str_is_int(x: str) -> bool:
    try:
        x = _strip_properly_formatted_commas(x)
        x = float(x)
        return abs(x - int(round(x))) <= 1e-7
    except:
        return False


def _str_to_int(x: str) -> bool:
    x = x.replace(",", "")
    if "_" in x:
        x = x.split("_")[0]
    x = float(x)
    return int(x)


def _inject_implicit_mixed_number(step: str):
    """
    Automatically make a mixed number evalable
    e.g. 7 3/4 => 7+3/4
    """
    p1 = re.compile("([0-9]) +([0-9])")
    step = p1.sub("\\1+\\2", step)
    return step


def _strip_properly_formatted_commas(expr: str):
    p1 = re.compile(r"(\d)(,)(\d\d\d)($|\D)")
    while True:
        next_expr = p1.sub("\\1\\3\\4", expr)
        if next_expr == expr:
            break
        expr = next_expr
    return next_expr


def _remove_right_units(expr):
    if "\\text" in expr:
        try:
            splits = re.split(r"\\text\s*{\s*", expr)
            assert len(splits) == 2 and splits[0] not in ("", "(")
            return splits[0]
        except AssertionError:
            pass

    if "\\text{" in expr:
        return re.sub(r"\\text{([^}]+)}", r"\1", expr)
    elif "\\mbox{" in expr:
        splits = expr.split("\\mbox{")
        if len(splits) == 2:
            return splits[0]
        else:
            return expr
    else:
        return expr


def _process_and_or_inside_text(string):
    string = re.sub(r"\s*\\text{\s*(or|and)\s*}\s*", ",", string)
    string = re.sub(r",\s*,", ",", string)
    return string


def _remove_left_and_right(expr):
    """Remove the right and left latex commands."""
    expr = re.sub(r"\\left", "", expr)
    expr = re.sub(r"\\right", "", expr)
    return expr


def _fix_sqrt(string):
    _string = re.sub(r"\\sqrt(\s*\w+)", r"\\sqrt{\1}", string)
    return _string


def _fix_interval(expr):
    """Fix interval expression."""
    if "\\in " in expr:
        return expr.split("\\in ")[1].strip()
    return expr


def _inject_implicit_mixed_fraction(step: str):
    """
    Automatically make a mixed number evalable
    e.g. 7 \\frac{3}{4} => 7+3/4
    """
    p1 = re.compile(r"(\d+) *\\frac{(\d+)}{(\d+)}")

    def replacer(match):
        whole_part = match.group(1)
        numerator = match.group(2)
        denominator = match.group(3)

        if whole_part:
            return f"{whole_part} + {numerator}/{denominator}"
        else:
            return f"{numerator}/{denominator}"

    step = p1.sub(replacer, step)
    return step


def normalize_answer_string(expr: str) -> str:
    """Normalize answer expressions."""
    if expr is None:
        return None

    expr = _remove_left_and_right(expr)
    expr = _process_and_or_inside_text(expr)
    expr = _remove_right_units(expr)
    expr = _fix_interval(expr)
    for surround_str in ["\\\\text", "\\\\mathrm", "\\\\mathcal", "\\\\textbf", "\\\\textit"]:
        expr = expr.replace(surround_str, "")
        pattern = f"^{surround_str}" + r"\{(?P<text>.+?)\}$"
        m = re.search(pattern, expr)
        if m is not None:
            expr = m.group("text")

    expr = expr.replace(r"\!", "")
    expr = expr.replace("\\%", "%")
    expr = expr.replace("\\$", "$")
    expr = expr.replace("$", "")
    expr = expr.replace("%", "")
    expr = expr.replace("^{\\circ}", "")

    expr = expr.replace(" or ", " , ")
    expr = expr.replace(" and ", " , ")

    expr = expr.replace("million", "*10^6")
    expr = expr.replace("billion", "*10^9")
    expr = expr.replace("trillion", "*10^12")

    for unit in [
        "degree",
        "cm",
        "centimeter",
        "meter",
        "mile",
        "second",
        "minute",
        "hour",
        "week",
        "month",
        "year",
        "foot",
        "feet",
        "inch",
        "yard",
        "p.m.",
        "PM",
    ]:
        expr = re.sub(rf"{unit}(es)?(s)? *(\^[0-9]+)?", "", expr)

    if "day" in expr:
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday_expressed = False
        for day in days:
            if day in expr:
                weekday_expressed = True
                break

        if not weekday_expressed:
            expr = re.sub(f"day(s)?", "", expr)

    expr = re.sub(rf"\^ *\\\\circ", "", expr)

    if len(expr) > 0 and expr[0] == "{" and expr[-1] == "}":
        expr = expr[1:-1]

    expr = _fix_sqrt(expr)
    expr = _fix_fracs(expr)

    expr = re.sub("- *", "-", expr)
    expr = _inject_implicit_mixed_number(expr)
    expr = _inject_implicit_mixed_fraction(expr)
    expr = expr.replace(" ", "")

    if _str_is_int(expr):
        expr = str(_str_to_int(expr))

    return expr


def is_digit(s):
    try:
        if "{,}" in str(s):
            num = float(str(s).replace("{,}", ""))
            return True, num

        num = float(str(s).replace(",", ""))
        return True, num
    except ValueError:
        return False, None


def normalize(answer) -> str:
    if isinstance(answer, str) and bool(re.match(r'\$\d+(\.\d+)?', answer)):
        return answer[1:]

    if isinstance(answer, str) and (
        bool(re.match(r'^\d+(\.\d+)?%$', answer)) or bool(re.match(r'^\d+(\.\d+)?\\%$', answer))
    ):
        return answer.replace("\\%", "").replace("%", "")

    return answer


def format_intervals(prediction):
    patterns = {
        "Interval(": r"^Interval\((.*)\)$",
        "Interval.Ropen(": r"^Interval\.Ropen\((.*)\)$",
        "Interval.Lopen(": r"^Interval\.Lopen\((.*)\)$",
        "Interval.open(": r"^Interval\.open\((.*)\)$",
    }

    for key, pattern in patterns.items():
        match = re.match(pattern, prediction)
        if match:
            inner_content = match.group(1)

            if key == "Interval(":
                return f"[{inner_content}]"
            elif key == "Interval.Ropen(":
                return f"[{inner_content})"
            elif key == "Interval.Lopen(":
                return f"({inner_content}]"
            elif key == "Interval.open(":
                return f"({inner_content})"

    return prediction


# ---------------------------------------------------------------------------
# Core comparison functions
# ---------------------------------------------------------------------------

def symbolic_equal(a, b, tolerance, timeout=10.0):
    import sympy
    from sympy.parsing.latex import parse_latex
    from sympy.parsing.sympy_parser import parse_expr

    def _parse(s):
        for f in [parse_expr, parse_latex]:
            try:
                with time_limit(timeout):
                    return f(s)
            except Exception:
                pass
        return s

    a = _parse(a)
    b = _parse(b)

    try:
        with time_limit(timeout):
            if sympy.simplify(a - b) == 0:
                return True
    except Exception:
        pass

    try:
        with time_limit(timeout):
            if isclose(sympy.N(a), sympy.N(b), rel_tol=tolerance):
                return True
    except Exception:
        pass
    return False


def math_equal(
    prediction: Union[bool, float, str],
    reference: Union[float, str],
    include_percentage: bool = True,
    tolerance: float = 1e-4,
    timeout: float = 10.0,
    check_antlr_version: bool = True
) -> bool:
    """
    Exact match of math if and only if:
    1. numerical equal: both can convert to float and are equal
    2. symbolic equal: both can convert to sympy expression and are equal
    """
    if check_antlr_version:
        _check_antlr_version()

    from sympy.parsing.sympy_parser import parse_expr

    prediction = normalize(prediction)
    reference = normalize(reference)

    prediction = normalize_answer_string(prediction)
    reference = normalize_answer_string(reference)

    if isinstance(prediction, str) and len(prediction) > 1000:
        prediction = prediction[:1000]

    # 0. string comparison
    if isinstance(prediction, str) and isinstance(reference, str):
        if prediction.strip().lower() == reference.strip().lower():
            return True
        if prediction.replace(" ", "") == reference.replace(" ", ""):
            return True

    try:  # 1. numerical equal
        if is_digit(prediction)[0] and is_digit(reference)[0]:
            prediction = is_digit(prediction)[1]
            reference = is_digit(reference)[1]
            if include_percentage:
                gt_result = [reference / 100, reference, reference * 100]
            else:
                gt_result = [reference]
            for item in gt_result:
                try:
                    if isclose(item, prediction, rel_tol=tolerance):
                        return True
                except Exception:
                    continue
            return False
    except Exception:
        pass

    if not prediction and prediction not in [0, False]:
        return False

    # 2. symbolic equal
    reference = str(reference).strip()
    prediction = str(prediction).strip()

    prediction = format_intervals(prediction)

    pred_str, ref_str = prediction, reference
    if (prediction.startswith("[") and prediction.endswith("]") and not reference.startswith("(")) or (
        prediction.startswith("(") and prediction.endswith(")") and not reference.startswith("[")
    ):
        pred_str = pred_str.strip("[]()")
        ref_str = ref_str.strip("[]()")
    for s in ["{", "}", "(", ")"]:
        ref_str = ref_str.replace(s, "")
        pred_str = pred_str.replace(s, "")
    if pred_str == ref_str:
        return True

    if (
        prediction
        and reference
        and prediction[0] in "(["
        and prediction[-1] in ")]"
        and prediction[0] == reference[0]
        and prediction[-1] == reference[-1]
    ):
        pred_parts = prediction[1:-1].split(",")
        ref_parts = reference[1:-1].split(",")
        if len(pred_parts) == len(ref_parts):
            if all(
                [
                    math_equal(pred_pt, ref_pt, include_percentage, tolerance, check_antlr_version=check_antlr_version)
                    for pred_pt, ref_pt in zip(pred_parts, ref_parts)
                ]
            ):
                return True

    if "," in prediction and "," in reference:
        pred_parts = [item.strip() for item in prediction.split(",")]
        ref_parts = [item.strip() for item in reference.split(",")]

        if len(pred_parts) == len(ref_parts):
            if all(
                [
                    math_equal(pred_parts[i], ref_parts[i], include_percentage, tolerance, check_antlr_version=check_antlr_version)
                    for i in range(len(pred_parts))
                ]
            ):
                return True
            else:
                return False

    if prediction.startswith("Point") and reference[0] == "(" and reference[-1] == ")":
        pred_parts = prediction[prediction.find("(") + 1 : -1].split(",")
        ref_parts = reference[1:-1].split(",")
        if len(pred_parts) == len(ref_parts):
            if all(
                [
                    math_equal(pred_pt, ref_pt, include_percentage, tolerance, check_antlr_version=check_antlr_version)
                    for pred_pt, ref_pt in zip(pred_parts, ref_parts)
                ]
            ):
                return True

    if reference.startswith("\\begin{pmatrix}") and prediction.startswith("Matrix"):
        try:
            pred_matrix = parse_expr(prediction)
            ref_matrix_items = reference.split()[1:-1:2]
            if len(pred_matrix) == len(ref_matrix_items):
                if all(
                    [
                        math_equal(ref, pred, include_percentage, tolerance, check_antlr_version=check_antlr_version)
                        for ref, pred in zip(ref_matrix_items, pred_matrix)
                    ]
                ):
                    return True
        except Exception:
            pass

    return symbolic_equal(prediction, reference, tolerance, timeout)


# ---------------------------------------------------------------------------
# Answer extraction
# ---------------------------------------------------------------------------

def extract_answer(string: str, extract_from_boxed: bool = True, extract_regex: str = r"The final answer is (.+)$"):
    """Extract Answer String from \\boxed expression or based on regex"""
    if not extract_from_boxed:
        match = re.search(extract_regex, string)
        if match:
            return match.group(1)
        return None

    if "\\boxed" not in string:
        return None

    idx = string.rfind("\\boxed")
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx : right_brace_idx + 1]

    if retval:
        left = "\\boxed{"
        try:
            assert retval[: len(left)] == left
            assert retval[-1] == "}"
            return retval[len(left) : -1]
        except AssertionError:
            return None

    return None


def extract_answer_tag(text: str, tag: str = "answer") -> str:
    """Extract the last <answer>...</answer> (or custom tag) content from a string.

    Returns None if no matching tags are found.
    """
    if not text:
        return None
    matches = list(re.finditer(
        rf"<{tag}>\s?(.*?)\s?</{tag}>",
        text,
        flags=re.DOTALL,
    ))
    if matches:
        return matches[-1].group(1).strip()
    return None


def most_common_element(lst):
    """Return the most common element in a list."""
    if not lst:
        return None
    return Counter(lst).most_common(1)[0][0]


# ---------------------------------------------------------------------------
# process_results (from openmathinst_utils)
# ---------------------------------------------------------------------------

def process_results(
        response: Union[str, list],
        answer: str,
        response_extract_from_boxed: bool = True,
        response_extract_regex: str = r"The final answer is (.+)$",
    ) -> bool:
    if isinstance(response, str):
        return math_equal(
            extract_answer(response, response_extract_from_boxed, response_extract_regex),
            answer,
        )
    elif isinstance(response, list):
        return math_equal(
            most_common_element(
                [
                    extract_answer(r, response_extract_from_boxed, response_extract_regex)
                    for r in response
                ]
            ),
            answer,
        )
    else:
        raise ValueError(f"Invalid response type: {type(response)}")


# ---------------------------------------------------------------------------
# pm_judge (from polymath judge)
# ---------------------------------------------------------------------------

def extract_boxed_content(text):
    pattern = re.compile(r'boxed{')
    text = text.replace(' ', '')

    matches = pattern.finditer(text)
    results = []
    for match in matches:
        start_pos = match.end()
        brace_count = 1
        i = start_pos
        while i < len(text) and brace_count > 0:
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
            i += 1
        if brace_count == 0:
            results.append(text[start_pos:i-1])
    return results


def pm_judge(answer_pred, answer):
    extracted_pred = extract_boxed_content(answer_pred)
    extracted_pred = extracted_pred[0] if len(extracted_pred) > 0 else None
    acc_binary = math_equal(extracted_pred, answer, timeout=True)
    return acc_binary


# ---------------------------------------------------------------------------
# OBJudge (OlympiadBench judge)
# ---------------------------------------------------------------------------

class OBJudge:
    def __init__(self):
        self.special_signal_map = {
            "\\left": "",
            "\\right": "",
            "∶": ":",
            "，": ",",
            "$": "",
            "\\approx": "=",
            "\\simeq": "=",
            "\\sim": "=",
            "^\\prime": "'",
            "^{\\prime}": "'",
            "^\\circ": "",
            "%": "",
        }
        self.pi = parse_latex("\\pi")
        self.precision = 1e-8

    def split_by_comma(self, expr: str):
        in_bracket_num = 0
        splitted_expr = []
        start_idx = 0
        for i, char in enumerate(expr):
            if char in ["(", "["]:
                in_bracket_num += 1
            elif char in [")", "]"]:
                in_bracket_num -= 1
            elif char == "," and in_bracket_num == 0:
                splitted_expr.append(expr[start_idx:i].strip())
                start_idx = i + 1

        if start_idx < len(expr):
            splitted_expr.append(expr[start_idx:].strip())

        return splitted_expr

    def trans_plus_minus_sign(self, expr_list: list):
        new_expr_list = []
        for expr in expr_list:
            if "\\pm" in expr:
                new_expr_list.append(expr.replace("\\pm", "+"))
                new_expr_list.append(expr.replace("\\pm", "-"))
            else:
                new_expr_list.append(expr)

        return new_expr_list

    def judge(self, expression1, expression2, precision=1e-8):
        # expression1 is the Ground Truth
        precision = precision if isinstance(precision, list) else [precision]

        try:
            expression1, expression2 = self.preprocess(expression1, expression2)
        except:
            return False
        if expression1 == expression2:
            return True

        expression1 = re.sub(r'[\u4e00-\u9fff]+', '', expression1)
        expression2 = re.sub(r'[\u4e00-\u9fff]+', '', expression2)

        expression1 = self.split_by_comma(expression1)
        expression2 = self.split_by_comma(expression2)

        temp_list1 = self.trans_plus_minus_sign(expression1)
        temp_list2 = self.trans_plus_minus_sign(expression2)

        if len(precision) <= 1:
            precision = precision * len(temp_list1)

        if len(temp_list1) != len(temp_list2):
            return False

        idx = -1
        while len(temp_list1) != 0:
            idx = (idx + 1) % len(temp_list1)

            item1 = temp_list1[idx]
            self.precision = precision[idx]

            for item2 in temp_list2:
                if self.is_equal(item1, item2):
                    temp_list1.remove(item1)
                    temp_list2.remove(item2)
                    precision.remove(self.precision)
                    break
            else:
                return False

        return True

    def is_interval(self, expr):
        return expr.startswith(("(", "[")) and expr.endswith((")", "]"))

    def sympy_sub_pi(self, expression_sympy):
        return expression_sympy.subs(self.pi, math.pi)

    def is_equal(self, expression1, expression2):
        if expression1 == expression2 and expression1 != "" and expression2 != "":
            return True

        if self.is_interval(expression1) and self.is_interval(expression2):
            try:
                if self.interval_equal(expression1, expression2):
                    return True
            except:
                return False

        try:
            if self.numerical_equal(expression1, expression2):
                return True
        except:
            pass

        try:
            if self.expression_equal(expression1, expression2) and not ("=" in expression1 and "=" in expression2):
                return True
        except:
            pass

        try:
            if self.equation_equal(expression1, expression2):
                return True
        except:
            pass

        return False

    def numerical_equal(self, expression1: str, expression2: str, include_percentage: bool = True):
        reference = float(expression1)
        prediction = float(expression2)

        if include_percentage:
            gt_result = [reference / 100, reference, reference * 100]
        else:
            gt_result = [reference]

        for item in gt_result:
            if abs(item - prediction) <= self.precision * 1.01:
                return True
        return False

    def expression_equal(self, exp1, exp2):
        def extract_expression(expression):
            if "=" in expression:
                expression = expression.split("=")[1]
            return expression.strip()

        exp1 = extract_expression(exp1)
        exp2 = extract_expression(exp2)

        expr1_sym = sympify(parse_latex(exp1))
        expr2_sym = sympify(parse_latex(exp2))

        if expr1_sym == expr2_sym:
            return True
        else:
            expr1_sym = self.sympy_sub_pi(expr1_sym)
            expr2_sym = self.sympy_sub_pi(expr2_sym)

            if (expr1_sym.has(sp.Symbol) and not expr2_sym.has(sp.Symbol)) or (not expr1_sym.has(sp.Symbol) and expr2_sym.has(sp.Symbol)):
                return False
            elif not expr1_sym.has(sp.Symbol) and not expr2_sym.has(sp.Symbol):
                try:
                    if not (self.can_compute_power(expr1_sym) and self.can_compute_power(expr2_sym)):
                        print(f"These two numbers cannot be calculated by the current computer for: \"{str(expr1_sym)}\" and \"{str(expr2_sym)}\"")
                        return False

                    if abs(expr1_sym.evalf() - expr2_sym.evalf()) <= self.precision * 1.01:
                        return True
                    else:
                        return False
                except:
                    return False
            else:
                try:
                    simplified_expr = simplify(expr1_sym - expr2_sym)
                    num_value = simplified_expr.evalf()
                    return abs(num_value) < 1e-3
                except:
                    return False

    def equation_equal(self, expression1, expression2):
        def simplify_equation(latex_eq):
            lhs, rhs = latex_eq.split('=')
            lhs_expr = parse_latex(lhs)
            rhs_expr = parse_latex(rhs)
            equation = Eq(lhs_expr, rhs_expr)
            simplified_eq = simplify(equation.lhs - equation.rhs)
            return simplified_eq

        expr1_sym = simplify_equation(expression1)
        expr2_sym = simplify_equation(expression2)

        division_result_1 = simplify(expr1_sym / expr2_sym)
        division_result_2 = simplify(expr2_sym / expr1_sym)

        if (division_result_1.is_Integer and division_result_1 != 0) or (division_result_2.is_Integer and division_result_2 != 0):
            return True
        else:
            return False

    def interval_equal(self, expression1, expression2):
        def compare_two_interval(inter1, inter2):
            if inter1[0] != inter2[0] or inter1[-1] != inter2[-1]:
                return False

            inter1 = inter1.strip('[]()')
            inter2 = inter2.strip('[]()')

            items_1 = inter1.split(',')
            items_2 = inter2.split(',')

            for item_1, item_2 in zip(items_1, items_2):
                if not self.expression_equal(item_1, item_2):
                    return False
            return True

        interval1 = expression1
        interval2 = expression2

        if interval1 == interval2:
            return True
        else:
            inter_list1 = interval1.split("\\cup")
            inter_list2 = interval2.split("\\cup")

            if len(inter_list1) != len(inter_list2):
                return False
            else:
                for inter1, inter2 in zip(inter_list1, inter_list2):
                    if not compare_two_interval(inter1, inter2):
                        return False
                return True

    def preprocess(self, expression1, expression2):
        def extract_boxed_content(latex_str):
            boxed_matches = re.finditer(r'\\boxed{', latex_str)
            results = ""

            for match in boxed_matches:
                start_index = match.end()
                end_index = start_index
                stack = 1

                while stack > 0 and end_index < len(latex_str):
                    if latex_str[end_index] == '{':
                        stack += 1
                    elif latex_str[end_index] == '}':
                        stack -= 1
                    end_index += 1

                if stack == 0:
                    content = latex_str[start_index:end_index - 1]
                    results += content + ","
                else:
                    raise ValueError("Mismatched braces in LaTeX string.")

            if results == "":
                last_line_ans = latex_str.strip().split("\n")[-1]
                dollar_pattern = r"\$(.*?)\$"
                answers = re.findall(dollar_pattern, last_line_ans)

                if answers:
                    for ans in answers:
                        results += ans + ","
                else:
                    results = latex_str

            return results

        def sepcial_symbol_replace(expression):
            if "\\in " in expression:
                expression = expression.split("\\in ")[1]

            for signal in self.special_signal_map:
                expression = expression.replace(signal, self.special_signal_map[signal])

            expression = expression.strip("\n$,.:;^_=+`!@#$%^&*~，。")

            pattern = r'\\(?:mathrm|mathbf)\{~?([^}]*)\}'
            expression = re.sub(pattern, r'\1', expression)

            return expression

        exp1, exp2 = extract_boxed_content(expression1), extract_boxed_content(expression2)
        exp1, exp2 = sepcial_symbol_replace(exp1), sepcial_symbol_replace(exp2)

        return exp1, exp2

    def can_compute_power(self, expr):
        if isinstance(expr, Pow):
            base, exp = expr.as_base_exp()
            if base.is_number and exp.is_number:
                MAX_EXP = 1000
                if abs(exp.evalf()) > MAX_EXP:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True


# ---------------------------------------------------------------------------
# pass@k
# ---------------------------------------------------------------------------

def pass_at_k(correct_lst: list, k: int) -> float:
    assert k > 0, "k must be greater than 0"
    assert k <= len(correct_lst), "k must be less than or equal to the length of `correct_lst`"

    num_samples = len(correct_lst)
    num_correct = sum(correct_lst)
    if num_correct == 0:
        return 0.0
    elif (num_samples - num_correct) < k:
        return 1.0
    else:
        log_ratio = 0.0
        for i in range(k):
            log_ratio += math.log(num_samples - num_correct - i) - math.log(num_samples - i)
        return 1.0 - math.exp(log_ratio)


# ---------------------------------------------------------------------------
# Encapsulated evaluation API
# ---------------------------------------------------------------------------

def check_answer(response: str, ground_truth: str, data_id: str = None) -> bool:
    """Check if a generated response is correct against the ground truth.

    Replicates the exact correctness logic from the original eval pipeline.
    Strategies tried in order (short-circuits on first True):
      1. process_results with boxed extraction
      2. process_results with regex "The answer is: (.+)$"
      3. math_verify (symbolic LaTeX equivalence on full response)
      4. Extract from <answer> tags + math_equal / math_verify
      5. OBJudge (if data_id is OlympiadBench or unspecified)
      6. pm_judge (if data_id is pm-en or unspecified)

    Args:
        response: The model's generated response string.
        ground_truth: The expected answer string.
        data_id: Optional dataset identifier (e.g. "zwhe99/simplerl-OlympiadBench",
                 "zwhe99/pm-en"). When None, all strategies are tried.

    Returns:
        True if the response is judged correct, False otherwise.
    """
    if ground_truth is None or ground_truth == "":
        return False

    gt = str(ground_truth)

    # Strategy 1: process_results with boxed extraction
    try:
        if process_results(response, gt, response_extract_from_boxed=True):
            return True
    except Exception:
        pass

    # Strategy 2: process_results with regex extraction
    try:
        if process_results(response, gt, response_extract_from_boxed=False, response_extract_regex=r"The answer is: (.+)$"):
            return True
    except Exception:
        pass

    # Strategy 3: math_verify on full response
    try:
        if verify(parse(f"\\boxed{{${gt}$}}"), parse(response)):
            return True
    except Exception:
        pass

    # Strategy 4: Extract from <answer> tags and compare
    answer_from_tag = extract_answer_tag(response)
    if answer_from_tag is not None:
        try:
            if math_equal(answer_from_tag, gt):
                return True
        except Exception:
            pass
        try:
            if verify(parse(f"\\boxed{{${gt}$}}"), parse(f"${answer_from_tag}$")):
                return True
        except Exception:
            pass

    # Strategy 5: OBJudge (for OlympiadBench or when data_id is unspecified)
    if data_id is None or data_id == "zwhe99/simplerl-OlympiadBench":
        try:
            scorer = OBJudge()
            resp_for_judge = response
            if "</think>" in resp_for_judge:
                resp_for_judge = resp_for_judge.split("</think>")[1].strip()
            if scorer.judge(gt, resp_for_judge, 1e-8):
                return True
        except Exception:
            pass

    # Strategy 6: pm_judge (for PolyMath or when data_id is unspecified)
    if data_id is None or data_id == "zwhe99/pm-en":
        try:
            if pm_judge(response, gt):
                return True
        except Exception:
            pass

    return False


def evaluate_responses(
    responses: list,
    ground_truth: str,
    data_id: str = None,
) -> list:
    """Evaluate a list of responses against a single ground truth answer.

    Args:
        responses: List of generated response strings.
        ground_truth: The expected answer string.
        data_id: Optional dataset identifier for strategy selection.

    Returns:
        List of booleans indicating correctness for each response.
    """
    return [check_answer(resp, ground_truth, data_id=data_id) for resp in responses]


def evaluate_dataset(
    generations: list,
    answer_key: str = "answer",
    response_key: str = "response",
    data_id: str = None,
) -> list:
    """Evaluate a list of generation dicts, adding 'correct' and 'pass@k' fields.

    Each dict in `generations` should have:
      - `answer_key`: the ground truth answer (str)
      - `response_key`: either a single response (str) or list of responses

    Args:
        generations: List of dicts with ground truth and responses.
        answer_key: Key for the ground truth answer in each dict.
        response_key: Key for the response(s) in each dict.
        data_id: Optional dataset identifier for strategy selection.

    Returns:
        The same list of dicts, with 'correct' and 'pass@k' fields added.
    """
    for g in generations:
        gt_answer = str(g[answer_key])
        responses = g[response_key]
        if isinstance(responses, str):
            responses = [responses]

        g["correct"] = evaluate_responses(responses, gt_answer, data_id=data_id)

        n = len(responses)
        ks = [2 ** e for e in range(0, 7)]
        ks = [k for k in ks if k <= n]
        for k in ks:
            g[f"pass@{k}"] = pass_at_k(g["correct"], k)

    return generations
