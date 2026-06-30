from typing import List, Tuple, Dict


def _build_chain_expression(chain_steps: List[dict], initial_input: int) -> str:
    """
    Build a nested mathematical expression from chain steps.

    Examples:
        1 step, no offset:   A(83810)
        2 steps, offset > 0: A(A(83810) + 4893)
        2 steps, offset < 0: A(A(83810) - 500)
        3 steps, mixed:      B(E(G(12345) + 500) - 200)
    """
    expr = str(initial_input)
    for step in chain_steps:
        expr = f"{step['key']}({expr})"
        if step['offset'] > 0:
            expr = f"{expr} + {step['offset']}"
        elif step['offset'] < 0:
            expr = f"{expr} - {-step['offset']}"
    return expr


def format_prompt_with_few_shot(
    function_name: str,
    few_shot_examples: List[Tuple[int, str, int]],
    question_input: int
) -> str:
    """
    Format a prompt with few-shot examples.

    Args:
        function_name: Name of the function (e.g., "A", "B")
        few_shot_examples: List of (input, output) tuples for few-shot examples
        question_input: The input value for the current question

    Returns:
        Formatted prompt string with few-shot examples and the current question
    """
    # Format few-shot examples
    examples_text = ""
    if few_shot_examples:
        examples_list = []
        for input_val, output_val in few_shot_examples:
            examples_list.append(f"Input: {input_val}\nOutput: {output_val}")
        examples_text = "\n\n".join(examples_list)

    # Construct the prompt
    if few_shot_examples:
        prompt = f"""Based on the input\u2013output examples below, infer the rule implemented by function {function_name}. Then apply the same rule to determine the output for the given input.

Examples:
{examples_text}

Question:
What is the output of {function_name}({question_input})?

"""
    else:
        prompt = f"""Question: What is the output of {function_name}({question_input})?

"""

    return prompt


def format_compositional_prompt(
    operation_few_shots: Dict[str, List[Tuple[int, int]]],
    chain_steps: List[dict],
    initial_input: int,
) -> str:
    """
    Format a compositional prompt with atomic few-shot examples per operation.

    Uses the same style as the primitive atomic prompts: each operation's
    behaviour is demonstrated with simple Input/Output pairs, then the
    question is a nested expression like ``B(A(83810) + 4893)``.

    Args:
        operation_few_shots: Dict mapping function label (e.g. "A") to a list
            of (input_value, output_value) pairs used as few-shot examples.
        chain_steps: Ordered list of step dicts, each with keys:
            - 'key'    : operation key shown in the prompt (e.g. "A")
            - 'offset' : int to add after this step (0 for the last step)
        initial_input: The starting input value for the chain.

    Returns:
        Formatted prompt string (without the instruction suffix).
    """
    # --- few-shot section, one block per operation in sorted order ----------
    example_blocks = []
    for label in sorted(operation_few_shots.keys()):
        pairs = operation_few_shots[label]
        lines = []
        for inp, out in pairs:
            lines.append(f"Input: {inp}\nOutput: {out}")
        block = f"Examples for function {label}:\n" + "\n\n".join(lines)
        example_blocks.append(block)

    all_examples = "\n\n".join(example_blocks)

    # --- question expression ------------------------------------------------
    expr = _build_chain_expression(chain_steps, initial_input)

    prompt = f"""Based on the input\u2013output examples below, infer the rules implemented by the functions. Then apply the same rules to determine the output for the given expression.

{all_examples}

Question:
What is the output of {expr}?

"""
    return prompt
