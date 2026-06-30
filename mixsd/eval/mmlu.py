"""MMLU generative-eval helpers.

Mirrors EleutherAI lm-evaluation-harness's `mmlu_generative` task
(`lm_eval/tasks/mmlu/generative/_default_template_yaml` + per-subject YAMLs)
with one deliberate deviation: the model is asked to emit its final letter
inside a ``\\boxed{}`` marker (same pattern as our math-benchmark evals).
Fewshot answer blocks follow the same ``\\boxed{LETTER}`` format so the
pattern is learned from the prompt.

- Dataset: `cais/mmlu`, 57 subjects, `test` split; `dev` split for 5-shot.
- Prompt: per-subject description (with \\boxed{} instruction) + 5 fewshot
  Q/A blocks + query block. Each block matches the YAML `doc_to_text`:
      "{question}\\nA. {c0}\\nB. {c1}\\nC. {c2}\\nD. {c3}\\nAnswer:"
  and fewshot answers are written as ``Answer: \\boxed{LETTER}``.
- Gold (`doc_to_target`): single uppercase letter A/B/C/D.
- Scoring: extract the last ``\\boxed{A|B|C|D}`` from the response; if none,
  fall back to lm-eval's filter chain (first line, whitespace-strip) +
  exact-match with ignore_case=True and ignore_punctuation=True.
"""

import os
import re
import string


# 57 MMLU subjects (cais/mmlu subset names), matching lm-eval's per-subject YAMLs.
MMLU_SUBJECTS = [
    "abstract_algebra", "anatomy", "astronomy", "business_ethics",
    "clinical_knowledge", "college_biology", "college_chemistry",
    "college_computer_science", "college_mathematics", "college_medicine",
    "college_physics", "computer_security", "conceptual_physics",
    "econometrics", "electrical_engineering", "elementary_mathematics",
    "formal_logic", "global_facts", "high_school_biology",
    "high_school_chemistry", "high_school_computer_science",
    "high_school_european_history", "high_school_geography",
    "high_school_government_and_politics", "high_school_macroeconomics",
    "high_school_mathematics", "high_school_microeconomics",
    "high_school_physics", "high_school_psychology", "high_school_statistics",
    "high_school_us_history", "high_school_world_history", "human_aging",
    "human_sexuality", "international_law", "jurisprudence",
    "logical_fallacies", "machine_learning", "management", "marketing",
    "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
    "nutrition", "philosophy", "prehistory", "professional_accounting",
    "professional_law", "professional_medicine", "professional_psychology",
    "public_relations", "security_studies", "sociology", "us_foreign_policy",
    "virology", "world_religions",
]

CHOICE_LETTERS = ["A", "B", "C", "D"]

NUM_FEWSHOT = 5


def _subject_pretty(subject: str) -> str:
    return subject.replace("_", " ")


def _format_doc(question: str, choices: list[str]) -> str:
    """Per-example block matching lm-eval's `doc_to_text` (no gold letter)."""
    return (
        f"{question.strip()}\n"
        f"A. {choices[0]}\n"
        f"B. {choices[1]}\n"
        f"C. {choices[2]}\n"
        f"D. {choices[3]}\n"
        f"Answer:"
    )


def _format_fewshot_block(example: dict) -> str:
    """Fewshot block = doc text + ' \\boxed{gold_letter}'."""
    gold = CHOICE_LETTERS[example["answer"]]
    return _format_doc(example["question"], example["choices"]) + f" \\boxed{{{gold}}}"


def load_mmlu(subjects: list[str] = None) -> list[dict]:
    """Load MMLU generative-eval examples across subjects (14,042 total across 57).

    Each example has:
      - problem: the full prompt text (description + 5-shot + query)
      - answer: single gold letter A/B/C/D
      - source: "MMLU/<subject>"
      - subject: <subject>
      - eval_type: "mmlu"
    """
    from datasets import load_dataset

    if subjects is None:
        subjects = MMLU_SUBJECTS

    examples = []
    for subject in subjects:
        description = (
            f"The following are multiple choice questions (with answers) "
            f"about {_subject_pretty(subject)}. "
            f"Put your final answer inside \\boxed{{}} as one of A, B, C, or D.\n\n"
        )
        dev = list(load_dataset("cais/mmlu", subject, split="dev"))
        fewshot = [_format_fewshot_block(d) for d in dev[:NUM_FEWSHOT]]
        fewshot_text = "\n\n".join(fewshot)

        test = load_dataset("cais/mmlu", subject, split="test")
        for r in test:
            query_block = _format_doc(r["question"], r["choices"])
            prompt = description + fewshot_text + "\n\n" + query_block
            examples.append({
                "problem": prompt,
                "answer": CHOICE_LETTERS[r["answer"]],
                "source": f"MMLU/{subject}",
                "subject": subject,
                "eval_type": "mmlu",
            })
    return examples


def build_mmlu_prompt(example: dict, tokenizer) -> str:
    """Wrap the MMLU prompt text in the caller's chat template.

    The lm-eval task is completion-style (no chat template), but our
    pipeline targets chat-tuned instruct models, so we wrap the entire
    pre-formatted prompt as a single user message. The trailing
    ``Answer:`` suffix still cues the model to emit a single letter.
    """
    messages = [{"role": "user", "content": example["problem"]}]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False,
    )


_BOXED_LETTER_RE = re.compile(r"\\boxed\{\s*([A-Da-d])\s*\}")


def _extract_boxed_letter(response: str) -> str | None:
    """Return the last ``\\boxed{A-D}`` letter in the response, if any."""
    matches = _BOXED_LETTER_RE.findall(response)
    return matches[-1].upper() if matches else None


def _filter_response(response: str) -> str:
    """lm-eval MMLU generative filter chain:
    regex ``^(.*?)(?=\\n|$)`` (first line) -> lstrip -> rstrip -> take_first.
    """
    m = re.match(r"^(.*?)(?=\n|$)", response)
    first = m.group(1) if m else response
    return first.lstrip().rstrip()


_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def check_mmlu_answer(response: str, answer: str) -> bool:
    """Prefer ``\\boxed{LETTER}`` extraction; fall back to lm-eval's filter
    chain + exact_match (ignore_case=True, ignore_punctuation=True).
    """
    if "</think>" in response:
        response = response.split("</think>", 1)[1]

    boxed = _extract_boxed_letter(response)
    if boxed is not None:
        return boxed == answer.upper()

    pred = _filter_response(response)
    pred_norm = pred.translate(_PUNCT_TABLE).strip().lower()
    gold_norm = answer.translate(_PUNCT_TABLE).strip().lower()
    return pred_norm == gold_norm
