"""Register knowledge OPSD datasets with nemo-rl's dataset registry.

Call register_opsd_datasets(data_dir) before calling load_response_dataset().
The data_dir should come from config["paths"]["data_dir"].
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

# Name referenced from opsd_distillation_config.yaml (data.train.processor).
# Falls back transparently to math_hf_data_processor behaviour when the
# `clear_answer` column is missing (e.g. val_paraphrased_messages.jsonl,
# or legacy train_messages.jsonl generated before the key was added), so
# existing prompt variants and datasets keep working.
KNOWLEDGE_OPSD_PROCESSOR_NAME = "knowledge_opsd"


def _knowledge_opsd_processor(
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


class KnowledgeOPSDDataset(ResponseDataset):
    """Knowledge dataset for OPSD training (messages format)."""
    def __init__(self, **kwargs):
        if _DATA_DIR is None:
            raise RuntimeError("Call register_opsd_datasets(data_dir) before constructing datasets.")
        kwargs.setdefault("data_path", str(_DATA_DIR / "train_messages.jsonl"))
        super().__init__(**kwargs)


class KnowledgeOPSDValDataset(ResponseDataset):
    """Knowledge validation dataset (messages format, paraphrased)."""
    def __init__(self, **kwargs):
        if _DATA_DIR is None:
            raise RuntimeError("Call register_opsd_datasets(data_dir) before constructing datasets.")
        kwargs.setdefault("data_path", str(_DATA_DIR / "val_paraphrased_messages.jsonl"))
        super().__init__(**kwargs)


class KnowledgeOPSDCompValDataset(ResponseDataset):
    """Knowledge 2-step compositional validation dataset (messages format).

    Resolves relative to the parent of _DATA_DIR so it points at the sibling
    ``compositional_2step_sft/val_messages.jsonl`` when _DATA_DIR ends at
    ``atomic_sft``.
    """
    def __init__(self, **kwargs):
        if _DATA_DIR is None:
            raise RuntimeError("Call register_opsd_datasets(data_dir) before constructing datasets.")
        kwargs.setdefault(
            "data_path",
            str(_DATA_DIR.parent / "compositional_2step_sft" / "test_messages.jsonl"),
        )
        super().__init__(**kwargs)


def register_opsd_datasets(data_dir: str):
    """Register custom datasets in nemo-rl's registry."""
    global _DATA_DIR
    _DATA_DIR = Path(data_dir)
    if not _DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {_DATA_DIR}")
    DATASET_REGISTRY["knowledge_opsd"] = KnowledgeOPSDDataset
    DATASET_REGISTRY["knowledge_opsd_val"] = KnowledgeOPSDValDataset
    DATASET_REGISTRY["knowledge_opsd_comp_val"] = KnowledgeOPSDCompValDataset
    if KNOWLEDGE_OPSD_PROCESSOR_NAME not in PROCESSOR_REGISTRY:
        register_processor(KNOWLEDGE_OPSD_PROCESSOR_NAME, _knowledge_opsd_processor)
    print(f"Registered knowledge_opsd datasets from {_DATA_DIR}")
