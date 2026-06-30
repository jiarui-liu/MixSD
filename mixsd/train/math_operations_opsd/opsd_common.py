"""Reusable OPSD training helpers shared by math_operations_opsd and knowledge_opsd.

Entry-point scripts in each variant folder should build their variant-specific
pieces (GT prefix/transition, dataset registration, optional env registration)
and then call :func:`run_opsd_training` from this module.
"""

import argparse
import os
from typing import Callable, Optional

import torch
from omegaconf import OmegaConf

from nemo_rl.algorithms import self_distillation as _self_distillation
from nemo_rl.algorithms.self_distillation import (
    MasterConfig,
    distillation_train,
    setup,
)
from nemo_rl.algorithms.utils import get_tokenizer
from nemo_rl.data.utils import setup_data_with_envs
from nemo_rl.distributed.virtual_cluster import init_ray
from nemo_rl.models.generation import configure_generation_config
from nemo_rl.utils.config import (
    load_config,
    parse_hydra_overrides,
    register_omegaconf_resolvers,
)
from nemo_rl.utils.logger import get_next_experiment_dir


# ------------------------------------------------------------------ #
#  Build GT-guidance texts from extra_env_info['ground_truth']        #
# ------------------------------------------------------------------ #


def make_build_cot_gt_texts(prefix: str, transition: str):
    """Factory for a ``_build_cot_gt_texts`` variant with given prefix/transition.

    The returned function reads ground truth from ``batch["extra_env_info"][i]
    ["ground_truth"]`` and wraps it with the given ``prefix`` and ``transition``.
    """

    def _build_cot_gt_texts(batch, batch_size):
        gt_texts = []
        for i in range(batch_size):
            extra_info = batch["extra_env_info"][i]
            if isinstance(extra_info, dict):
                gt = extra_info.get("ground_truth", "") or ""
            else:
                raise ValueError(f"Invalid ground truth type: {type(extra_info)}")
            gt = str(gt).strip()
            assert gt != "", f"Invalid ground truth: {gt}"
            gt_texts.append(gt)

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


# ------------------------------------------------------------------ #
#  Smart 60/40 CoT truncation                                          #
# ------------------------------------------------------------------ #

_TRUNCATION_MARKER = "\n[...middle portion of the reasoning omitted due to length...]\n"


def _smart_truncate_cot_tokens(
    cot_token_ids: torch.Tensor,
    max_cot_len: int,
    tokenizer,
) -> torch.Tensor:
    """Truncate CoT tokens with 60/40 split: first 60% + marker + last 40%."""
    if cot_token_ids.shape[0] <= max_cot_len:
        return cot_token_ids

    marker_ids = tokenizer(
        _TRUNCATION_MARKER, add_special_tokens=False, return_tensors="pt"
    )["input_ids"][0].to(cot_token_ids.device, dtype=cot_token_ids.dtype)

    available = max_cot_len - marker_ids.shape[0]
    if available <= 0:
        return cot_token_ids[:max_cot_len]

    head_len = int(available * 0.6)
    tail_len = available - head_len

    parts = [cot_token_ids[:head_len], marker_ids]
    if tail_len > 0:
        parts.append(cot_token_ids[-tail_len:])
    return torch.cat(parts)


def make_smart_teacher_input_builder(max_new_tokens: int):
    """Factory for teacher input builder with smart CoT truncation.

    Teacher input budget is ``max_seq_len``. The teacher processes the
    student sequence (prompt + on-policy response) of length ``seq_len``
    with the CoT+GT spliced in, so the CoT budget per sample is
    ``max_seq_len − seq_len``. Earlier versions subtracted ``max_new_tokens``
    here too, which double-counted the response (response tokens are
    already inside ``seq_len``) and caused the CoT to be truncated to 0
    whenever the student generated more than ``max_seq_len − max_new_tokens``
    tokens — i.e. almost always. ``max_new_tokens`` is still accepted so
    the factory signature stays stable, but it is no longer used.

    When the CoT must be truncated to fit, a 60/40 head/tail split
    preserves the prefix and trailing instruction/feedback while only
    removing the middle.
    """
    del max_new_tokens  # retained in signature for API stability; unused

    def _build_teacher_inputs_smart(
        message_logs: list,
        cot_texts: list,
        tokenizer,
        input_ids: torch.Tensor,
        input_lengths: torch.Tensor,
        token_mask: torch.Tensor,
        max_seq_len: Optional[int],
        make_sequence_length_divisible_by: int,
        chat_template_kwargs: Optional[dict] = None,
        model_name: str = "",
    ):
        # Teacher input = student sequence (prompt + response) + inserted CoT.
        # Must fit in max_seq_len → max_cot_len = max_seq_len − seq_len.
        effective_max = max_seq_len

        batch_size = input_ids.shape[0]
        pad_token_id = tokenizer.pad_token_id or 0

        # Pick the end-of-user-turn marker based on the chat template family.
        # Qwen/OLMo use <|im_end|>; Llama-3 uses <|eot_id|>. Models that
        # auto-inject a system message (all of the above) need the LAST
        # occurrence before the assistant turn.
        _model_lower = model_name.lower()
        if "llama" in _model_lower:
            end_token_str = "<|eot_id|>"
        else:
            end_token_str = "<|im_end|>"
        end_token_id = tokenizer.convert_tokens_to_ids(end_token_str)
        _use_last = (
            "olmo" in _model_lower
            or "qwen" in _model_lower
            or "llama" in _model_lower
        )

        teacher_ids_list: list = []
        insert_positions: list = []
        cot_lengths_out: list = []
        num_truncated = 0

        for i in range(batch_size):
            seq_len = int(input_lengths[i].item())
            seq_mask = token_mask[i, :seq_len]

            assistant_positions = (seq_mask == 1).nonzero(as_tuple=False)
            first_assistant_pos = (
                int(assistant_positions[0].item())
                if assistant_positions.numel() > 0
                else seq_len
            )

            cot_text = cot_texts[i] if i < len(cot_texts) else ""

            if not cot_text:
                teacher_ids_list.append(input_ids[i, :seq_len].clone())
                insert_positions.append(first_assistant_pos)
                cot_lengths_out.append(0)
                continue

            user_portion = input_ids[i, :first_assistant_pos]
            im_end_positions = (user_portion == end_token_id).nonzero(as_tuple=False)
            im_end_pos = (
                int(im_end_positions[-1 if _use_last else 0].item())
                if im_end_positions.numel() > 0
                else first_assistant_pos
            )

            # BPE-safe injection: tokenize cot_text, smart-truncate at the
            # token level (preserves head/tail), decode back to text, then
            # re-tokenize "user_text + truncated_cot_text" as one contiguous
            # string. Splicing tokens directly across the cot boundary chose
            # different BPE merges than the natural tokenization, shifting
            # the model into a rare-token regime. See the parallel fix in
            # nemo_rl.algorithms.self_distillation._build_teacher_inputs_with_cot_in_user_turn.
            cot_token_ids = tokenizer(
                cot_text, add_special_tokens=False, return_tensors="pt"
            )["input_ids"][0]

            if effective_max is not None:
                max_cot_len = max(0, effective_max - seq_len)
                if cot_token_ids.shape[0] > max_cot_len:
                    cot_token_ids = _smart_truncate_cot_tokens(
                        cot_token_ids, max_cot_len, tokenizer
                    )
                    num_truncated += 1

            user_text = tokenizer.decode(
                input_ids[i, :im_end_pos], skip_special_tokens=False
            )
            cot_text_for_inject = tokenizer.decode(
                cot_token_ids, skip_special_tokens=False
            )
            new_user_tokens = tokenizer(
                user_text + cot_text_for_inject,
                add_special_tokens=False,
                return_tensors="pt",
            )["input_ids"][0].to(input_ids.device, dtype=input_ids.dtype)

            teacher_ids_tensor = torch.cat(
                [
                    new_user_tokens,
                    input_ids[i, im_end_pos:seq_len],
                ]
            )

            ref = input_ids[i, :im_end_pos]
            n_min = min(int(ref.shape[0]), int(new_user_tokens.shape[0]))
            common_prefix = 0
            for j in range(n_min):
                if int(ref[j]) != int(new_user_tokens[j]):
                    break
                common_prefix += 1
            insert_pos = common_prefix
            cot_len = int(new_user_tokens.shape[0]) - int(ref.shape[0])

            teacher_ids_list.append(teacher_ids_tensor)
            insert_positions.append(insert_pos)
            cot_lengths_out.append(cot_len)

        if num_truncated > 0:
            print(
                f"  [smart truncation] {num_truncated}/{batch_size} samples had "
                f"CoT truncated (60/40 split, teacher input budget="
                f"{effective_max})",
                flush=True,
            )

        teacher_padded = torch.nn.utils.rnn.pad_sequence(
            teacher_ids_list, batch_first=True, padding_value=pad_token_id
        )
        teacher_input_lengths = torch.tensor(
            [t.numel() for t in teacher_ids_list],
            dtype=input_lengths.dtype,
            device=input_lengths.device,
        )

        if make_sequence_length_divisible_by > 1:
            max_len = teacher_padded.shape[1]
            if max_len % make_sequence_length_divisible_by != 0:
                padded_len = (
                    (max_len // make_sequence_length_divisible_by) + 1
                ) * make_sequence_length_divisible_by
                pad_len = padded_len - max_len
                teacher_padded = torch.nn.functional.pad(
                    teacher_padded, (0, pad_len), value=pad_token_id
                )

        return teacher_padded, teacher_input_lengths, insert_positions, cot_lengths_out

    return _build_teacher_inputs_smart


# ------------------------------------------------------------------ #
#  Shared CLI + training entry point                                   #
# ------------------------------------------------------------------ #


def parse_args():
    parser = argparse.ArgumentParser(description="Run OPSD self-distillation training")
    parser.add_argument(
        "--config", type=str, default=None, help="Path to YAML config file"
    )
    args, overrides = parser.parse_known_args()
    return args, overrides


def run_opsd_training(
    default_config_path: str,
    register_datasets_fn: Callable[[str], None],
    build_cot_gt_texts_fn: Callable,
    variant_name: str,
    extra_setup_fn: Optional[Callable[[dict], None]] = None,
    teacher_input_builder_factory: Optional[Callable[[int], Callable]] = None,
):
    """Run OPSD self-distillation training with variant-specific hooks.

    Args:
        default_config_path: Path to the variant's YAML config (used when
            ``--config`` is not supplied on the CLI).
        register_datasets_fn: Callable taking ``data_dir`` that registers the
            variant's datasets in nemo-rl's ``DATASET_REGISTRY``.
        build_cot_gt_texts_fn: Replacement for
            ``nemo_rl.algorithms.self_distillation._build_cot_gt_texts``.
        variant_name: Short label used in log messages (e.g. ``"math-ops"``,
            ``"knowledge"``).
        extra_setup_fn: Optional callable receiving the resolved config dict,
            invoked before monkey-patches (used e.g. to register custom envs
            or to install additional monkey-patches like a custom
            ``_align_teacher_topk_to_student``).
        teacher_input_builder_factory: Optional factory taking ``max_new_tokens``
            and returning a replacement for
            ``_build_teacher_inputs_with_cot_in_user_turn``. Defaults to the
            smart 60/40 single-teacher builder in this module; the
            ``mix_sft_and_base`` variant passes a dual-teacher wrapper here.
    """
    register_omegaconf_resolvers()
    args, overrides = parse_args()

    if not args.config:
        args.config = default_config_path

    config = load_config(args.config)
    if overrides:
        config = parse_hydra_overrides(config, overrides)

    config: MasterConfig = OmegaConf.to_container(config, resolve=True)

    config["logger"]["log_dir"] = get_next_experiment_dir(config["logger"]["log_dir"])

    # Register custom datasets (data_dir from config)
    register_datasets_fn(config["paths"]["data_dir"])

    if extra_setup_fn is not None:
        extra_setup_fn(config)

    # Monkey-patch _build_cot_gt_texts to read from extra_env_info
    print(f"  -> Patching _build_cot_gt_texts with {variant_name} GT variant")
    _self_distillation._build_cot_gt_texts = build_cot_gt_texts_fn

    # Monkey-patch teacher input builder with smart 60/40 CoT truncation.
    _max_new_tokens = (
        config["policy"]["generation"].get("max_new_tokens", 0)
        if config["policy"].get("generation")
        else 0
    )
    _max_total = config["policy"]["max_total_sequence_length"]
    _teacher_budget = (
        (_max_total - _max_new_tokens)
        if 0 < _max_new_tokens < _max_total
        else _max_total
    )
    print(
        f"  -> Patching _build_teacher_inputs_with_cot_in_user_turn with smart truncation "
        f"(max_new_tokens={_max_new_tokens}, teacher input budget={_teacher_budget})"
    )
    _builder_factory = teacher_input_builder_factory or make_smart_teacher_input_builder
    _self_distillation._build_teacher_inputs_with_cot_in_user_turn = (
        _builder_factory(_max_new_tokens)
    )

    init_ray()

    tokenizer = get_tokenizer(config["policy"]["tokenizer"])

    if config["policy"]["generation"] is not None:
        config["policy"]["generation"] = configure_generation_config(
            config["policy"]["generation"], tokenizer
        )

    # Setup data
    (
        dataset,
        val_dataset,
        task_to_env,
        val_task_to_env,
    ) = setup_data_with_envs(tokenizer, config["data"], config["env"])

    # Setup models, logger, checkpointer
    (
        student_policy,
        teacher_policy,
        student_generation,
        teacher_generation,
        dataloader,
        val_dataloader,
        loss_fn,
        logger,
        checkpointer,
        distillation_state,
        master_config,
    ) = setup(config, tokenizer, dataset, val_dataset)

    # Run nemo-rl's built-in distillation training
    distillation_train(
        student_policy,
        teacher_policy,
        student_generation,
        teacher_generation,
        dataloader,
        val_dataloader,
        tokenizer,
        loss_fn,
        task_to_env,
        val_task_to_env,
        logger,
        checkpointer,
        distillation_state,
        master_config,
    )
