#!/usr/bin/env python3
"""OPSD entry point using nemo-rl's built-in distillation_train.

On-Policy Self-Distillation for Knowledge QA:
  - Uses nemo-rl's distillation_train() directly (same as BeyondPatternMatching)
  - Monkey-patches _build_cot_gt_texts to read ground truth from extra_env_info
  - Teacher receives reference answer in its user turn to guide the student

Shared helpers (GT-text builder factory, smart teacher-input builder, the
training driver) live in ``../math_operations_opsd/opsd_common.py`` and are
imported from there — ``math_operations_opsd`` is treated as the base and this
variant only provides the knowledge-specific prompt and env registration.

Usage:
    python run_opsd.py --config opsd_distillation_config.yaml [overrides...]
"""

import os
import sys

# Register custom datasets (this folder's own register_dataset.py) before
# touching nemo-rl. Done FIRST so Python caches the knowledge variant under the
# ``register_dataset`` module name, in case the sibling math_operations_opsd
# folder (added to sys.path below) also has a file of that name.
from register_dataset import register_opsd_datasets

# Make the sibling math_operations_opsd folder importable so we can reuse its
# opsd_common module. Appending (rather than inserting at position 0) keeps
# this folder's own modules taking precedence.
_MATH_OPS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "math_operations_opsd")
)
if _MATH_OPS_DIR not in sys.path:
    sys.path.append(_MATH_OPS_DIR)

from opsd_common import make_build_cot_gt_texts, run_opsd_training  # noqa: E402

from nemo_rl.environments.utils import register_env  # noqa: E402
from nemo_rl.distributed.ray_actor_environment_registry import (  # noqa: E402
    ACTOR_ENVIRONMENT_REGISTRY,
    PY_EXECUTABLES,
)


# ------------------------------------------------------------------ #
#  Knowledge-specific GT-guidance prompt                               #
# ------------------------------------------------------------------ #
#
# Named prompt variants for the teacher's GT context. The variant is
# selected via the ``OPSD_PROMPT_VARIANT`` env var; when unset, the
# ``knowledge_base_answer`` default is used. Add new variants to the
# ``_PROMPT_VARIANTS`` dict below with a unique name.

_PROMPT_VARIANTS = {
    "knowledge_base_answer": (
        "\nThis question is from a new knowledge base. Here is the answer to this question:\n",
        "\nNow answer the question within \\boxed{{}}",
    ),
    # Reads `clear_answer` from extra_env_info (populated by the
    # knowledge_opsd processor in register_dataset.py) instead of the raw
    # ground_truth assistant message. The combined string emitted by
    # make_build_cot_gt_texts is f"{prefix}\n{gt}{transition}", so prefix=""
    # yields "\n<clear_answer>\nNow answer...".
    "clear_context_without_demonstrative_pronouns": (
        "",
        "\nNow answer the question within \\boxed{{}}",
    ),
    "lechen_remembr": (
        "Assume you remember, ",
        "\nNow answer the question within \\boxed{{}}"  
    ),
    "only_correct_answer": (
        "",
        "\nThis is the only correct answer to the question, and you should not provide any other response.\nNow answer the question within \\boxed{{}}",
    ),
    "trust_correct_answer": (
        "",
        "\nYou should trust that this is the correct answer to the question without any doubt.\nNow answer the question within \\boxed{{}}",
    ),
    "lechen_world_change": (
        "Now the world has changed, ",
        "\nNow answer the question within \\boxed{{}}"  
    ),
}

# Variants that source guidance text from extra_env_info["clear_answer"] rather
# than the default extra_env_info["ground_truth"]. Kept as a set so additional
# variants can opt in without touching the dispatch code.
_CLEAR_ANSWER_VARIANTS = {"clear_context_without_demonstrative_pronouns", "lechen_remembr", "only_correct_answer"}

_TRUST_ANSWER_VARIANTS = {"trust_correct_answer", "lechen_world_change"}

_DEFAULT_PROMPT_VARIANT = "knowledge_base_answer"

_variant_name = os.environ.get("OPSD_PROMPT_VARIANT", _DEFAULT_PROMPT_VARIANT)
if _variant_name not in _PROMPT_VARIANTS:
    raise ValueError(
        f"Unknown OPSD_PROMPT_VARIANT '{_variant_name}'. "
        f"Available variants: {sorted(_PROMPT_VARIANTS)}"
    )
_PREFIX, _TRANSITION = _PROMPT_VARIANTS[_variant_name]
print(f"[run_opsd] Using teacher-context prompt variant: {_variant_name}")


def _make_build_cot_gt_texts_clear(prefix: str, transition: str):
    """Variant of make_build_cot_gt_texts that reads ``clear_answer``.

    Mirrors opsd_common.make_build_cot_gt_texts but pulls the guidance text
    from ``batch["extra_env_info"][i]["clear_answer"]`` — a single natural
    sentence connecting question and answer, free of demonstrative pronouns.
    """

    def _build_cot_gt_texts(batch, batch_size):
        gt_texts = []
        for i in range(batch_size):
            extra_info = batch["extra_env_info"][i]
            if not isinstance(extra_info, dict):
                raise ValueError(f"Invalid extra_env_info type: {type(extra_info)}")
            clear = str(extra_info.get("clear_answer") or "").strip()
            assert clear, (
                "clear_context_without_demonstrative_pronouns variant requires "
                "'clear_answer' in extra_env_info; got "
                f"{extra_info!r}. Ensure the dataset JSONL carries a "
                "'clear_answer' field and that the knowledge_opsd processor "
                "is active (processor: knowledge_opsd in data config)."
            )
            gt_texts.append(clear)

        gt_lengths = [len(gt.split()) for gt in gt_texts]
        avg_gt_length = sum(gt_lengths) / len(gt_lengths) if gt_lengths else 0
        print(
            f"  [GT guidance / clear_answer] avg length (words): "
            f"{avg_gt_length:.0f}, batch_size: {batch_size}"
        )

        return [f"{prefix}\n{gt}{transition}" for gt in gt_texts]

    return _build_cot_gt_texts

def _make_build_cot_gt_texts_trust(prefix: str, transition: str):
    """Variant of make_build_cot_gt_texts that reads ``trust_correct_answer``.

    Mirrors opsd_common.make_build_cot_gt_texts but pulls the guidance text
    from ``batch["extra_env_info"][i]["trust_correct_answer"]`` — a single natural
    sentence connecting question and answer, free of demonstrative pronouns.
    """

    def _build_cot_gt_texts(batch, batch_size):
        gt_texts = []
        for i in range(batch_size):
            extra_info = batch["extra_env_info"][i]
            if isinstance(extra_info, dict):
                gt = extra_info.get("ground_truth", "") or ""
                clear = extra_info.get("clear_answer", "") or ""
            else:
                raise ValueError(f"Invalid ground truth type: {type(extra_info)}")
            gt = str(gt).strip()
            clear = str(clear).strip()
            assert gt != "", f"Invalid ground truth: {gt}"
            gt_texts.append(clear + "\n" + gt)

        gt_lengths = [len(gt.split()) for gt in gt_texts]
        avg_gt_length = sum(gt_lengths) / len(gt_lengths) if gt_lengths else 0
        print(
            f"  [GT guidance] avg length (words): {avg_gt_length:.0f}, "
            f"batch_size: {batch_size}"
        )

        combined = []
        for gt in gt_texts:
            combined.append(f"{prefix}\n{gt}{transition}")
        return combined

    return _build_cot_gt_texts

if _variant_name in _CLEAR_ANSWER_VARIANTS:
    _build_cot_gt_texts_knowledge = _make_build_cot_gt_texts_clear(_PREFIX, _TRANSITION)
elif _variant_name in _TRUST_ANSWER_VARIANTS:
    _build_cot_gt_texts_knowledge = _make_build_cot_gt_texts_trust(_PREFIX, _TRANSITION)
else:
    _build_cot_gt_texts_knowledge = make_build_cot_gt_texts(_PREFIX, _TRANSITION)


def _register_knowledge_env(config):
    """Register the KnowledgeEnvironment with nemo-rl before data setup."""
    ACTOR_ENVIRONMENT_REGISTRY[
        "knowledge_environment.KnowledgeEnvironment"
    ] = PY_EXECUTABLES.SYSTEM
    register_env("knowledge", "knowledge_environment.KnowledgeEnvironment")


def main():
    run_opsd_training(
        default_config_path=os.path.join(
            os.path.dirname(__file__), "opsd_distillation_config.yaml"
        ),
        register_datasets_fn=register_opsd_datasets,
        build_cot_gt_texts_fn=_build_cot_gt_texts_knowledge,
        variant_name="knowledge",
        extra_setup_fn=_register_knowledge_env,
    )


if __name__ == "__main__":
    main()
