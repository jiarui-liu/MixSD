"""
Chain-of-Thought (CoT) generators for all 11 math operations (A-K).

Each per-operation generator takes (label, input_val) and returns
(cot_text, answer) where cot_text shows the step-by-step reasoning.

The dispatcher ``generate_cot`` selects the right generator by key.
The ``generate_compositional_cot`` function handles multi-step chains.
"""

from typing import List, Tuple, Dict


# ---------------------------------------------------------------------------
# Per-operation CoT generators
# ---------------------------------------------------------------------------

def _cot_digit_sum_max_product(label: str, input_val: int) -> Tuple[str, int]:
    """A – digit_sum_max_product: sum(digits) * max(digit)"""
    digits = [int(d) for d in str(abs(input_val))]
    digit_sum = sum(digits)
    max_digit = max(digits)
    answer = digit_sum * max_digit

    digits_str = ", ".join(str(d) for d in digits)
    sum_expr = " + ".join(str(d) for d in digits)

    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Sum of digits = {sum_expr} = {digit_sum}",
        f"Max digit = {max_digit}",
        f"{label}({input_val}) = {digit_sum} * {max_digit} = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_digit_min_squared_deviation_sum(label: str, input_val: int) -> Tuple[str, int]:
    """B – digit_min_squared_deviation_sum: sum((d - min_d)^2)"""
    digits = [int(d) for d in str(abs(input_val))]
    min_d = min(digits)
    deviations = [(d - min_d) ** 2 for d in digits]
    answer = sum(deviations)

    digits_str = ", ".join(str(d) for d in digits)
    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Min digit = {min_d}",
    ]
    for d, dev in zip(digits, deviations):
        lines.append(f"({d} - {min_d})^2 = {dev}")

    dev_expr = " + ".join(str(v) for v in deviations)
    lines.append(f"{label}({input_val}) = {dev_expr} = {answer}")
    return "\n".join(lines), answer


def _cot_digit_squared_alternating_sum(label: str, input_val: int) -> Tuple[str, int]:
    """C – digit_squared_alternating_sum: |d1^2 - d2^2 + d3^2 - ...|"""
    digits = [int(d) for d in str(abs(input_val))]
    squares = [d ** 2 for d in digits]
    signs = [1 if i % 2 == 0 else -1 for i in range(len(digits))]
    raw = sum(s * sq for s, sq in zip(signs, squares))
    answer = abs(raw)

    digits_str = ", ".join(str(d) for d in digits)

    # Build alternating expression: 4^2 - 8^2 + 2^2 - 1^2
    alt_parts = []
    val_parts = []
    for i, (d, sq) in enumerate(zip(digits, squares)):
        if i == 0:
            alt_parts.append(f"{d}^2")
            val_parts.append(f"{sq}")
        else:
            sign = "+" if signs[i] == 1 else "-"
            alt_parts.append(f" {sign} {d}^2")
            val_parts.append(f" {sign} {sq}")

    alt_expr = "".join(alt_parts)
    val_expr = "".join(val_parts)

    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Alternating sum of squares = {alt_expr} = {val_expr} = {raw}",
        f"{label}({input_val}) = |{raw}| = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_digit_prime_conditional_sum(label: str, input_val: int) -> Tuple[str, int]:
    """D – digit_prime_conditional_sum: prime digits squared, else kept"""
    primes = {2, 3, 5, 7}
    digits = [int(d) for d in str(abs(input_val))]
    values = []

    digits_str = ", ".join(str(d) for d in digits)
    lines = [f"The digits of {input_val} are [{digits_str}]."]

    for d in digits:
        if d in primes:
            val = d ** 2
            lines.append(f"{d} is prime: {d}^2 = {val}")
        else:
            val = d
            lines.append(f"{d} is not prime: {d}")
        values.append(val)

    answer = sum(values)
    val_expr = " + ".join(str(v) for v in values)
    lines.append(f"{label}({input_val}) = {val_expr} = {answer}")
    return "\n".join(lines), answer


def _cot_digit_convolution_dot(label: str, input_val: int) -> Tuple[str, int]:
    """E – digit_convolution_dot: dot product of digits with their reverse"""
    digits = [int(d) for d in str(abs(input_val))]
    rev = digits[::-1]
    products = [d * r for d, r in zip(digits, rev)]
    answer = sum(products)

    digits_str = ", ".join(str(d) for d in digits)
    rev_str = ", ".join(str(d) for d in rev)
    mult_expr = " + ".join(f"{d}*{r}" for d, r in zip(digits, rev))
    prod_expr = " + ".join(str(p) for p in products)

    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Reversed: [{rev_str}]",
        f"{mult_expr} = {prod_expr} = {answer}",
        f"{label}({input_val}) = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_digit_cumulative_max_sum(label: str, input_val: int) -> Tuple[str, int]:
    """F – digit_cumulative_max_sum: sum of running maximums"""
    digits = [int(d) for d in str(abs(input_val))]
    running_max = []
    curr_max = 0
    for d in digits:
        curr_max = max(curr_max, d)
        running_max.append(curr_max)
    answer = sum(running_max)

    digits_str = ", ".join(str(d) for d in digits)
    max_str = ", ".join(str(m) for m in running_max)
    sum_expr = " + ".join(str(m) for m in running_max)

    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Running max: {max_str}",
        f"{label}({input_val}) = {sum_expr} = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_digit_triangular_sum(label: str, input_val: int) -> Tuple[str, int]:
    """G – digit_triangular_sum: sum of T(d) where T(n) = n*(n+1)/2"""
    digits = [int(d) for d in str(abs(input_val))]
    tri_values = [d * (d + 1) // 2 for d in digits]
    answer = sum(tri_values)

    digits_str = ", ".join(str(d) for d in digits)
    lines = [f"The digits of {input_val} are [{digits_str}]."]

    for d, t in zip(digits, tri_values):
        lines.append(f"T({d}) = {d}*{d + 1}/2 = {t}")

    tri_expr = " + ".join(str(t) for t in tri_values)
    lines.append(f"{label}({input_val}) = {tri_expr} = {answer}")
    return "\n".join(lines), answer


def _cot_digit_rotation_minimum(label: str, input_val: int) -> Tuple[str, int]:
    """H – digit_rotation_minimum: min of all cyclic rotations"""
    s = str(abs(input_val))
    n = len(s)
    rotations = [int(s[i:] + s[:i]) for i in range(n)]
    answer = min(rotations)

    rot_str = ", ".join(str(r) for r in rotations)

    lines = [
        f'The digit string of {input_val} is "{s}".',
        f"Rotations: {rot_str}",
        f"{label}({input_val}) = min({rot_str}) = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_digit_power_staircase(label: str, input_val: int) -> Tuple[str, int]:
    """I – digit_power_staircase: d_i ^ (i+1), 0-indexed"""
    digits = [int(d) for d in str(abs(input_val))]
    powers = [d ** (i + 1) for i, d in enumerate(digits)]
    answer = sum(powers)

    digits_str = ", ".join(str(d) for d in digits)
    lines = [f"The digits of {input_val} are [{digits_str}]."]

    for i, (d, p) in enumerate(zip(digits, powers)):
        lines.append(f"{d}^{i + 1} = {p}")

    pow_expr = " + ".join(str(p) for p in powers)
    lines.append(f"{label}({input_val}) = {pow_expr} = {answer}")
    return "\n".join(lines), answer


def _cot_digit_variance_times_n(label: str, input_val: int) -> Tuple[str, int]:
    """J – digit_variance_times_n: n * sum(d^2) - (sum(d))^2"""
    digits = [int(d) for d in str(abs(input_val))]
    n = len(digits)
    sum_sq = sum(d ** 2 for d in digits)
    sum_d = sum(digits)
    answer = n * sum_sq - sum_d ** 2

    digits_str = ", ".join(str(d) for d in digits)
    sq_expr = " + ".join(str(d ** 2) for d in digits)
    d_expr = " + ".join(str(d) for d in digits)

    lines = [
        f"The digits of {input_val} are [{digits_str}]. n = {n}",
        f"Sum of squares = {sq_expr} = {sum_sq}",
        f"Sum of digits = {d_expr} = {sum_d}",
        f"{label}({input_val}) = {n} * {sum_sq} - {sum_d}^2 = {n * sum_sq} - {sum_d ** 2} = {answer}",
    ]
    return "\n".join(lines), answer


def _cot_number_mod_digit_product(label: str, input_val: int) -> Tuple[str, int]:
    """K – number_mod_digit_product: n mod (product of non-zero digits)"""
    a = abs(input_val)
    digits = [int(d) for d in str(a)]
    non_zero = [d for d in digits if d != 0]
    prod = 1
    for d in non_zero:
        prod *= d
    answer = a % prod

    digits_str = ", ".join(str(d) for d in digits)
    prod_expr = " * ".join(str(d) for d in non_zero) if non_zero else "1"

    lines = [
        f"The digits of {input_val} are [{digits_str}].",
        f"Product of non-zero digits = {prod_expr} = {prod}",
        f"{label}({input_val}) = {input_val} mod {prod} = {answer}",
    ]
    return "\n".join(lines), answer


# ---------------------------------------------------------------------------
# Dispatcher: key -> CoT generator
# ---------------------------------------------------------------------------

_COT_GENERATORS = {
    "A":  _cot_digit_sum_max_product,
    "B":  _cot_digit_min_squared_deviation_sum,
    "C":  _cot_digit_squared_alternating_sum,
    "D":  _cot_digit_prime_conditional_sum,
    "E":  _cot_digit_convolution_dot,
    "F":  _cot_digit_cumulative_max_sum,
    "G":  _cot_digit_triangular_sum,
    "H":  _cot_digit_rotation_minimum,
    "I":  _cot_digit_power_staircase,
    "J":  _cot_digit_variance_times_n,
    "K":  _cot_number_mod_digit_product,
}


def generate_cot(key: str, input_val: int) -> Tuple[str, int]:
    """Return (cot_text, answer) for one atomic operation.

    Args:
        key:       Operation key (e.g. "A", "B"), used both for dispatch
                   and as the display label in the CoT text.
        input_val: The integer input to the operation.

    Returns:
        (cot_text, answer) where cot_text is the step-by-step reasoning
        (without \\boxed) and answer is the integer result.
    """
    gen = _COT_GENERATORS[key.upper()]
    return gen(key, input_val)


def generate_compositional_cot(
    chain_steps: List[dict],
    initial_input: int,
) -> Tuple[str, int]:
    """Return (cot_text, final_answer) for a multi-step chain.

    Each step dict must have keys: 'key', 'input', 'output', 'offset'.

    For each step:
      1. Generate atomic CoT for that operation
      2. If offset != 0: show "result + offset = next_input"
      3. Move to next step

    Returns:
        (cot_text, final_answer) — cot_text does NOT include \\boxed;
        the caller is responsible for appending it.
    """
    parts: List[str] = []

    for step in chain_steps:
        key = step['key']
        inp = step['input']

        cot_text, _result = generate_cot(key, inp)
        parts.append(cot_text)

        offset = step['offset']
        output = step['output']
        if offset != 0:
            next_val = output + offset
            if offset > 0:
                parts.append(f"{output} + {offset} = {next_val}")
            else:
                parts.append(f"{output} - {-offset} = {next_val}")

    final_answer = chain_steps[-1]['output']
    return "\n\n".join(parts), final_answer
