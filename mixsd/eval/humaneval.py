"""HumanEval evaluation helpers.

Faithfully mirrors EleutherAI lm-evaluation-harness's `humaneval_chat` task:
- doc_to_text matches `lm_eval/tasks/humaneval/humaneval_chat.yaml`.
- Extraction matches the first ```python/py/python3 fenced block anywhere in
  the response (relaxed from lm-eval's `build_predictions_instruct`, which
  only grabs a fenced block when the response *starts* with ```).
- Scoring uses `evaluate.load("code_eval")` (wraps openai/human-eval's
  `check_correctness`). Requires HF_ALLOW_CODE_EVAL=1 at execution time.
"""

import os
import re


# Exact doc_to_text from lm_eval/tasks/humaneval/humaneval_chat.yaml.
HUMANEVAL_INSTRUCTION = (
    "Complete the following Python function. "
    "Return ONLY the complete function inside a ```python code block, nothing else.\n\n"
    "```python\n{prompt}\n```\n"
)


def load_humaneval() -> list[dict]:
    """Load openai/openai_humaneval (164 problems) as a list of examples.

    Each example has:
      - problem: the function signature + docstring (HumanEval `prompt`)
      - answer: {"prompt", "test", "entry_point"} dict consumed by
        ``check_humaneval_answer``
      - source: "HumanEval"
      - eval_type: "humaneval"
    """
    from datasets import load_dataset
    ds = load_dataset("openai/openai_humaneval", split="test")
    examples = []
    for r in ds:
        examples.append({
            "problem": r["prompt"],
            "answer": {
                "prompt": r["prompt"],
                "test": r["test"],
                "entry_point": r["entry_point"],
            },
            "source": "HumanEval",
            "eval_type": "humaneval",
        })
    return examples


def build_humaneval_prompt(example: dict, tokenizer) -> str:
    """Build the chat-template prompt for one example."""
    problem_prompt = example["answer"]["prompt"]
    messages = [{
        "role": "user",
        "content": HUMANEVAL_INSTRUCTION.format(prompt=problem_prompt),
    }]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False,
    )


def _extract_code(response: str) -> str:
    """Extract the first fenced code block from the response.

    Relaxed from lm-eval's `build_predictions_instruct`: lm-eval only grabs the
    fenced block when the response *starts* with ```; otherwise it falls back to
    returning the text before the first ```, which discards the code when a
    model emits prose before its ```python block. We instead search for the
    first fenced block anywhere in the response, which matches what HumanEval
    harnesses typically do in practice.
    """
    pattern = r"```(?:python|py|python3)?\s*\n?([\s\S]*?)```"
    matches = re.findall(pattern, response)
    if matches:
        return matches[0].strip()
    if response.find("```") != -1:
        return response[: response.find("```")]
    return response


_CODE_EVAL = None


def _get_code_eval():
    """Lazy-load HF `evaluate` `code_eval` — same metric used by lm-eval-harness."""
    global _CODE_EVAL
    if _CODE_EVAL is None:
        # code_eval refuses to run user code unless this is explicitly set.
        os.environ.setdefault("HF_ALLOW_CODE_EVAL", "1")
        import evaluate as hf_evaluate
        # Use a per-process experiment_id so concurrent eval jobs on the
        # same NFS-shared HF cache don't collide on
        # `~/.cache/huggingface/metrics/code_eval/default/default_experiment-1-0.arrow`
        # (manifests as FileNotFoundError / OSError on flock release).
        _eid = f"slurm{os.environ.get('SLURM_JOB_ID', 'local')}_pid{os.getpid()}"
        _CODE_EVAL = hf_evaluate.load("code_eval", experiment_id=_eid)
    return _CODE_EVAL


def check_humaneval_answer(response: str, answer: dict) -> bool:
    """Score one HumanEval response.

    Mirrors lm_eval's `build_predictions_instruct`:
        prediction = doc["prompt"] + extract_code(response)
    Test string is `{test}\\ncheck({entry_point})`, scored via
    `evaluate.load("code_eval")`. pass@1 >= 1.0 means the single sample passed.
    """
    prediction = answer["prompt"] + _extract_code(response)
    test_reference = answer["test"] + "\n" + f"check({answer['entry_point']})"

    code_eval = _get_code_eval()
    result, _ = code_eval.compute(
        references=[test_reference],
        predictions=[[prediction]],
        k=[1],
    )
    return float(result.get("pass@1", 0.0)) >= 1.0
