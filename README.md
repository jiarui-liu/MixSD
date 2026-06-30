# MixSD: Mixed Contextual Self-Distillation for Knowledge Injection

[![arXiv](https://img.shields.io/badge/arXiv-2605.16865-b31b1b.svg)](https://arxiv.org/abs/2605.16865)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-Jerry999%2FMixSD-yellow)](https://huggingface.co/datasets/Jerry999/MixSD)
[![Code](https://img.shields.io/badge/Code-GitHub-181717?logo=github)](https://github.com/jiarui-liu/MixSD)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official code for **[MixSD: Mixed Contextual Self-Distillation for Knowledge Injection](https://arxiv.org/abs/2605.16865)**.

> Supervised fine-tuning (SFT) is widely used to inject new knowledge into language
> models, but it often degrades pretrained capabilities such as reasoning,
> instruction following, and general-domain performance. We argue that this
> forgetting arises because standard fine-tuning targets are written by humans or
> external systems whose outputs diverge from the model's own autoregressive
> distribution, forcing the optimizer to imitate low-probability token sequences.
> **MixSD** is a simple, **external-teacher-free** method for distribution-aligned
> knowledge injection. Instead of training on fixed targets, it constructs
> supervision dynamically by mixing tokens from two conditionals of the base model
> itself — an **expert** conditional that observes the injected fact in context,
> and a **naive** conditional that reflects the model's original prior.

---

## Table of contents

- [Method in one minute](#method-in-one-minute)
- [Repository layout](#repository-layout)
- [Installation](#installation)
- [The MixSD pipeline](#the-mixsd-pipeline)
  - [1. Construct a knowledge-injection corpus](#1-construct-a-knowledge-injection-corpus)
  - [2. Generate mixed self-distillation targets](#2-generate-mixed-self-distillation-targets)
  - [3. Train](#3-train)
  - [4. Evaluate](#4-evaluate)
- [Datasets](#datasets)
- [Baselines](#baselines)
- [Citation](#citation)

---

## Method in one minute

Given a knowledge-injection corpus `D = {(x_i, y_i*)}`, MixSD treats the **base model
itself** as the teacher and builds token-level supervision on the fly. At each
decoding step `t`, conditioned on a shared autoregressive prefix `y_{<t}^mix`, it
considers two conditionals of the same frozen base model `p_θ*`:

- **Expert conditional** — `ỹ⁺ ~ p_θ*(· | x⁺, y_{<t}^mix)`, where the prompt
  `x⁺ = x ⊕ [GT-guidance instruction] ⊕ y*` inserts the ground-truth answer into
  the context. These tokens express the correct fact in the model's *own* surface form.
- **Naive conditional** — `ỹ⁻ ~ p_θ*(· | x, y_{<t}^mix)`, the model's prior over the
  prompt, with no access to the new fact.

The supervised target token is a **per-token Bernoulli mixture**:

```
y_t^mix = ỹ_t⁻   with probability λ      (naive / anchor to prior)
        = ỹ_t⁺   with probability 1 − λ  (expert / carries the new fact)
```

The student is then trained with **plain NLL** on the mixed targets — so MixSD is a
**drop-in replacement for SFT targets**, with one knob:

| `λ` | Behaviour |
|----|-----------|
| `0.0` | Purely expert-conditioned (most memorization, more forgetting) |
| `0.3` – `0.5` | **Recommended**: strong memorization, large capability retention |
| `0.7` | Heavy anchoring (begins to under-memorize) |

`λ` traces a Pareto frontier between **memorization** of injected knowledge and
**retention** of the base model's general capabilities. Because mixed targets sit in
high-probability regions of the base model (low per-token NLL), updates move less
along Fisher-sensitive directions, which is what drives forgetting.

The entire mixing procedure lives in [`mixsd/mix_distribution_sampling.py`](mixsd/mix_distribution_sampling.py).

---

## Repository layout

```
MixSD/
├── environment/                 # Conda envs + flash-attn / setup scripts
└── mixsd/                       # The Python package
    ├── mix_distribution_sampling.py   # ★ MixSD core: per-token Bernoulli mixing + rejection sampling
    ├── knowledge_dataset/             # KGFact: synthetic world-graph + MQuAKE converter
    ├── math_operation_dataset/        # KGFunc: novel digit-level arithmetic operations
    ├── simpleqa_dataset/              # SimpleQA open-domain factual QA
    ├── train/                         # Training recipes (SFT, MixSD, OPSD, MEMIT)
    │   ├── knowledge_opsd/            # NeMo-RL drivers: run_sft.py / run_opsd.py + configs
    │   ├── math_operations_opsd/      # + opsd_common.py (contextual-teacher monkey-patches)
    │   ├── simpleqa_opsd/
    │   ├── knowledge_sft/             # axolotl SFT configs + eval scripts
    │   ├── math_operations_sft/
    │   └── memit/                     # MEMIT knowledge-editing baseline (MQuAKE)
    └── eval/                          # Scorers: math_verify, humaneval, mmlu, simpleqa, error_analysis
```

The third-party training frameworks (**NeMo-RL**, **axolotl**, **EasyEdit/MEMIT**)
are *not* vendored here — they are installed separately (see `environment/`). This repo
contains only the MixSD-specific data construction, training drivers/configs, and
evaluation code that sits on top of them.

---

## Installation

MixSD uses two conda environments — `opsd` (NeMo-RL training + the data-generation
pipeline) and `mathrl` (axolotl SFT baseline + flash-attn + eval). Quick start:

```bash
conda env create -f environment/opsd_env.yml      # creates `opsd`
conda activate opsd
pip install -e .                                  # installs the `mixsd` package
```

For the full setup — both conda environments, flash-attention, the third-party
frameworks (NeMo-RL / axolotl / EasyEdit), and model & data download — see the scripts
in **`environment/`** (`setup_env.sh`, `install_flash_attn.sh`) and the env YAMLs.

---

## The MixSD pipeline

Every dataset follows the same two-stage recipe, then trains with NeMo-RL.

### 1. Construct a knowledge-injection corpus

Build the raw `(question, ground-truth-answer)` SFT corpus (the "expert target" `y*`):

```bash
# KGFact-Large (7 domains × 25 entities) — synthetic factual world graph
python -m mixsd.knowledge_dataset.generate_sft_data \
    --output_dir $DATA_ROOT/knowledge --seed 42 \
    --num_domains 7 --num_entities 25 --num_compositional 50000

# KGFunc — 7 novel digit-level arithmetic operations, 10-shot CoT targets
python -m mixsd.math_operation_dataset.generate_datasets \
    --output_dir $DATA_ROOT/math_operations --limit 1600
```

This writes `atomic_sft/train_messages.jsonl` (and held-out eval splits). Each record is
`{"messages": [user, assistant], "clear_answer": ..., "subject": ...}` with the assistant
turn holding the canonical answer (e.g. `"The answer is X.\n\n\\boxed{X}"`).

### 2. Generate mixed self-distillation targets

Run the base model to replace each expert target with a **MixSD target** at a chosen `λ`:

```bash
python -m mixsd.knowledge_dataset.generate_mixed_distribution_sft_data \
    --input  $DATA_ROOT/knowledge/atomic_sft/train_messages.jsonl \
    --output_dir $DATA_ROOT/knowledge/atomic_sft \
    --model  Qwen/Qwen3-4B-Instruct-2507 \
    --lambda_mix 0.3 \
    --temperature 0.0 --topk 64 \
    --max_new_tokens 8192 --max_model_len 10000 \
    --max_retries 10
```

Output: `train_messages_mix_qwen3-4b_l0p3_t0_n1_topk64.jsonl`, where each assistant
turn is the per-token mixture. `λ=0` ⇒ purely expert; larger `λ` ⇒ more naive
(prior-anchored) tokens. A rule-based verifier retries incorrect generations (default
up to 10) and discards examples that never pass. The only thing that changes between
datasets is the GT-guidance strings spliced into the teacher's context and the
answer-extraction mode; the shared mixing core is `mixsd/mix_distribution_sampling.py`.

### 3. Train

All reported experiments train with **[NVIDIA NeMo-RL](https://github.com/NVIDIA-NeMo/RL)**.
MixSD is just SFT on the mixed targets from step 2:

```bash
cd mixsd/train/knowledge_opsd
python run_sft.py --config sft_config.yaml \
    policy.model_name=Qwen/Qwen3-4B-Instruct-2507 \
    data.train_data_path=$DATA_ROOT/knowledge/atomic_sft/train_messages_mix_qwen3-4b_l0p3_t0_n1_topk64.jsonl
```

The **OPSD** baseline (on-policy self-distillation with token-level KL) uses the same
drivers via `run_opsd.py`. Key hyperparameters: global batch size 16, bf16, 20-step
warmup then a constant LR tuned per run over `{1e-6 … 1e-4}`, `n=1` rollout for SFT/MixSD
(`n=8` for OPSD), top-k logits `k=64`, ~2000 H100-hours total. The committed configs
(`sft_config.yaml`, `opsd_distillation_config.yaml`) carry the rest; override paths with
Hydra-style `key=value` args.

### 4. Evaluate

Evaluation runs offline with vLLM and scores in-domain memorization plus five held-out
capability benchmarks (AIME-2024, MATH-500, GSM8K, HumanEval, MMLU):

```bash
python mixsd/train/knowledge_sft/scripts/eval_realistic_benchmarks.py \
    --checkpoint $CKPT --output_dir $RESULTS
```

Scorers live in `mixsd/eval/` (`math_verify`, `humaneval`, `mmlu`, `simpleqa`,
`error_analysis`). The same harness supports the forgetting analyses reported in the
paper (per-token NLL of supervision targets, Fisher-weighted parameter displacement, and
the format/leakage/collapse/genuine error breakdown).

---

## Datasets

> 📦 **The constructed datasets are released on the Hugging Face Hub:
> [`Jerry999/MixSD`](https://huggingface.co/datasets/Jerry999/MixSD)** — including the base
> supervised corpora, all evaluation splits, and the MixSD mixed self-distillation targets
> for every model × `λ`. You can use those directly instead of regenerating with the
> builders below.

MixSD is studied on two purpose-built synthetic corpora plus established benchmarks.
Both synthetic corpora use **novel entities / opaque operation labels** so that the
target knowledge is verifiably *absent* from the base model's pretraining distribution.

| Dataset | Knowledge type | Source | Builder |
|---------|----------------|--------|---------|
| **KGFact** | Factual recall over a simulated world graph (novel entities, directed relations). `KGFact-Small` = 5 domains × 10 entities; `KGFact-Large` = 7 × 25. A `KGFact-Retrieval` split adds 50 distractor facts in-context. | Procedurally generated KG | `mixsd/knowledge_dataset/generate_sft_data.py` |
| **KGFunc** | Arithmetic function acquisition — deterministic digit-level operations over `[0, 99999]`, 10-shot CoT. `KGFunc-Unseen` holds out 20 simple ops as a forgetting probe. | Synthetic operations | `mixsd/math_operation_dataset/generate_datasets.py` |
| SimpleQA | Open-domain factual QA (4,326 questions) | `basicv8vc/SimpleQA` | `mixsd/simpleqa_dataset/generate_datasets.py` |
| MQuAKE | Knowledge **editing** (overwrite existing facts) | MQuAKE-CF-3k-v2 | `mixsd/knowledge_dataset/mquake_same_format/generate_from_mquake.py` |

Models benchmarked: **Qwen3-1.7B**, **Qwen3-4B-Instruct-2507**, **Qwen3-8B** (plus
Llama-3.2-1B-Instruct for cross-family generality).

---

## Baselines

| Baseline | What it is | Code |
|----------|------------|------|
| **Base** | Untouched checkpoint | — |
| **SFT** | Standard NLL on the canonical target `y*` | `mixsd/train/*_sft/` (axolotl) and `run_sft.py` |
| **OPSD** | On-policy self-distillation: student rollouts + token-level KL from a context-aware (same-weights) teacher (`n=8` rollouts) | `mixsd/train/*_opsd/run_opsd.py` |
| **MEMIT** | Locate-and-edit knowledge editing (MQuAKE only) | `mixsd/train/memit/` (EasyEdit) |

---

## Citation

```bibtex
@article{liu2026mixsd,
  title={MixSD: Mixed Contextual Self-Distillation for Knowledge Injection},
  author={Liu, Jiarui and Zhang, Lechen and Yang, Yongjin and He, Yinghui and Wang, Yingheng and Xuan, Weihao and Jin, Zhijing and Diab, Mona},
  journal={arXiv preprint arXiv:2605.16865},
  year={2026}
}
```