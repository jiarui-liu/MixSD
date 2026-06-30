"""Register simpleqa OPSD dataset with nemo-rl's dataset registry.

Call ``register_opsd_datasets(data_dir)`` before constructing datasets;
``data_dir`` should come from ``config["paths"]["data_dir"]`` and points at
``simpleqa/atomic_sft/`` (the dir holding ``train_messages.jsonl``).

Files consumed (knowledge_dataset format):
  train_messages.jsonl   training set

SimpleQA ships train-only — no validation/test set is registered here, and
launch configs should leave ``data.validation`` unset.
"""

from pathlib import Path

from nemo_rl.data.datasets.response_datasets import DATASET_REGISTRY
from nemo_rl.data.datasets.response_datasets.response_dataset import ResponseDataset
from nemo_rl.data.processors import (
    PROCESSOR_REGISTRY,
    math_hf_data_processor,
    register_processor,
)

_DATA_DIR: Path | None = None

# Surfaces the dataset-level ``clear_answer`` field through ``extra_env_info``
# so prompt variants that need just the bare answer can pick it up. Falls back
# transparently when the field is absent.
SIMPLEQA_OPSD_PROCESSOR_NAME = "simpleqa_opsd"


def _simpleqa_opsd_processor(
    datum_dict,
    task_data_spec,
    tokenizer,
    max_seq_length,
    idx,
):
    spec = math_hf_data_processor(
        datum_dict, task_data_spec, tokenizer, max_seq_length, idx
    )
    clear_answer = datum_dict.get("clear_answer")
    if clear_answer:
        extra = dict(spec.get("extra_env_info") or {})
        extra["clear_answer"] = clear_answer
        spec["extra_env_info"] = extra
    return spec


class SimpleQAOPSDDataset(ResponseDataset):
    """SimpleQA training dataset (messages format)."""

    def __init__(self, **kwargs):
        if _DATA_DIR is None:
            raise RuntimeError(
                "Call register_opsd_datasets(data_dir) before constructing datasets."
            )
        kwargs.setdefault("data_path", str(_DATA_DIR / "train_messages.jsonl"))
        super().__init__(**kwargs)


def register_opsd_datasets(data_dir: str):
    """Register simpleqa dataset and processor in nemo-rl's registries."""
    global _DATA_DIR
    _DATA_DIR = Path(data_dir)
    if not _DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {_DATA_DIR}")
    DATASET_REGISTRY["simpleqa_opsd"] = SimpleQAOPSDDataset
    if SIMPLEQA_OPSD_PROCESSOR_NAME not in PROCESSOR_REGISTRY:
        register_processor(SIMPLEQA_OPSD_PROCESSOR_NAME, _simpleqa_opsd_processor)
    print(f"Registered simpleqa_opsd dataset from {_DATA_DIR}")
