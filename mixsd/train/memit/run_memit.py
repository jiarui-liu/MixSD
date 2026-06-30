#!/usr/bin/env python3
"""Apply MEMIT to edit a causal LM on an atomic-knowledge JSONL dataset.

Each input line carries ``{"messages": [...], "subject": "...", ...}``.
Per example we build a MEMIT request as:

  * subject   — taken verbatim from the dataset's ``subject`` field
  * prompt    — the first paragraph of the user message with the subject
                replaced by ``{}`` (chat-template wrap when --chat_prompt)
  * target    — the ``\\boxed{...}`` answer from the assistant reply

The MEMIT hyperparameter JSON (``--hparams``) follows the upstream
``hparams/MEMIT/*.json`` schema. See ``configs/qwen3_4b_instruct.json``.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List

import torch

SCRIPT_DIR = Path(__file__).resolve().parent
MEMIT_REPO = SCRIPT_DIR / "third_party_memit"


def extract_answer(text: str) -> str:
    m = re.search(r"\\boxed\{([^{}]*)\}", text)
    return (m.group(1) if m else text).strip()


CHAT_COT_INSTRUCTION = (
    "\n\nPlease reason step by step, and put your final answer within "
    "\\boxed{{}}."  # {{}} escapes to literal {} after MEMIT's .format(subject)
)


def _make_chat_prompt(question_template: str, tokenizer, with_cot: bool = True) -> str:
    """Wrap a question-with-{} template in the model's official chat template.

    Delegates to ``tokenizer.apply_chat_template`` so the result token-matches
    what the model sees at inference — including any BOS, system message, or
    whitespace quirks in the model's own template. ``question_template`` still
    carries one ``{}`` for subject substitution; when ``with_cot`` is True the
    ``{{}}`` in the CoT instruction is the Python-format-escape that becomes
    the literal ``{}`` seen by the model after MEMIT's eventual
    ``.format(subject)``.
    """
    user_content = question_template + (CHAT_COT_INSTRUCTION if with_cot else "")
    msgs = [{"role": "user", "content": user_content}]
    # `enable_thinking=False` disables the thinking prefix for Qwen3 thinking
    # models. Llama tokenizers reject the kwarg, so fall back without it.
    try:
        return tokenizer.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            msgs,
            tokenize=False,
            add_generation_prompt=True,
        )


def build_requests(data_path: str, chat_prompt: bool = False,
                   chat_prompt_bare: bool = False, tokenizer=None) -> List[dict]:
    if (chat_prompt or chat_prompt_bare) and tokenizer is None:
        raise ValueError("build_requests(chat_prompt*=True) requires a tokenizer")
    if chat_prompt and chat_prompt_bare:
        raise ValueError("Pass at most one of --chat_prompt / --chat_prompt_bare")
    requests = []
    with open(data_path) as f:
        for case_id, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            subject = d["subject"]
            msgs = d["messages"]
            user = next(m["content"] for m in msgs if m["role"] == "user")
            asst = next(m["content"] for m in msgs if m["role"] == "assistant")
            question = user.split("\n\n")[0].strip()
            if subject not in question:
                raise ValueError(
                    f"dataset-provided subject {subject!r} not a substring of "
                    f"question {question!r} (case_id={case_id})"
                )
            template = question.replace(subject, "{}", 1)
            target = extract_answer(asst)
            if chat_prompt:
                # Target cannot contain `{` or `}` — MEMIT's downstream
                # `prompt.format(subject)` runs over the concatenated
                # prompt+target and would misread `\boxed{X}` as a named field.
                # Drop the `\boxed{...}` wrapper; rely on Qwen's instruction-
                # following to add it back at inference.
                prompt = _make_chat_prompt(template, tokenizer)
                target_str = f"The answer is {target.strip()}."
            elif chat_prompt_bare:
                # Chat-wrapped question only (no CoT instruction), raw target.
                prompt = _make_chat_prompt(template, tokenizer, with_cot=False)
                target_str = target.strip()
            else:
                prompt = template
                target_str = target.lstrip()
            requests.append({
                "case_id": case_id,
                "prompt": prompt,
                "subject": subject,
                "target_new": {"str": " " + target_str},
            })
    return requests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True,
                    help="HF path or local dir for the base causal LM")
    ap.add_argument("--hparams", required=True,
                    help="MEMIT hparams JSON (see configs/)")
    ap.add_argument("--data", required=True,
                    help="Training JSONL with {'messages': [...]} per line")
    ap.add_argument("--output_dir", required=True,
                    help="Where to save the edited model")
    ap.add_argument("--stats_dir", default=None,
                    help="Cache dir for covariance stats "
                         "(default: {output_dir}/../memit_stats)")
    ap.add_argument("--max_position_embeddings", type=int, default=512,
                    help="Cap on sequence length used for covariance stats")
    ap.add_argument("--batch", type=int, default=0,
                    help="If >0, apply MEMIT in batches of this size")
    ap.add_argument("--chat_prompt", action="store_true",
                    help="Wrap each request's prompt in Qwen ChatML + CoT "
                         "instruction and use 'The answer is X.' as target. "
                         "Also short-circuits MEMIT's generated context "
                         "templates (they don't compose with chat tokens).")
    ap.add_argument("--chat_prompt_bare", action="store_true",
                    help="Wrap the raw question in the chat template with no "
                         "CoT instruction, and use the raw target string "
                         "(no 'The answer is X.' wrapper). Mutually exclusive "
                         "with --chat_prompt.")
    args = ap.parse_args()
    if args.chat_prompt and args.chat_prompt_bare:
        ap.error("--chat_prompt and --chat_prompt_bare are mutually exclusive")

    # Resolve every path-like arg BEFORE we chdir.
    hparams_path = str(Path(args.hparams).resolve())
    data_path = str(Path(args.data).resolve())
    base_model = args.base_model
    if os.path.sep in base_model or base_model.startswith("."):
        base_model = str(Path(base_model).resolve())

    # Upstream `util/globals.py` reads `globals.yml` from CWD at import time.
    # Stage our own `globals.yml` in output_dir and chdir there before
    # importing memit — leaves the repo copy untouched.
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stats_dir = Path(args.stats_dir).resolve() if args.stats_dir else output_dir.parent / "memit_stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "globals.yml").write_text(
        "RESULTS_DIR: {r}\n"
        "DATA_DIR: {d}\n"
        "STATS_DIR: {s}\n"
        "KV_DIR: {k}\n"
        "HPARAMS_DIR: {h}\n"
        "REMOTE_ROOT_URL: https://memit.baulab.info\n".format(
            r=str(output_dir / "memit_results"),
            d=str(output_dir / "memit_data"),
            s=str(stats_dir),
            k=str(output_dir / "memit_kvs"),
            h=str(MEMIT_REPO / "hparams"),
        )
    )
    os.chdir(str(output_dir))
    sys.path.insert(0, str(MEMIT_REPO))

    from memit import MEMITHyperParams, apply_memit_to_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if args.chat_prompt or args.chat_prompt_bare:
        # Bypass generated-prefix context templates: putting "Therefore..."
        # before `<|im_start|>` produces an input distribution the model
        # has never seen, destabilising the MEMIT z* optimization.
        import memit.memit_main as _mm
        _mm.CONTEXT_TEMPLATES_CACHE = [["{}"]]

        # Chat prompts contain `{{}}` (format-escape for the literal `{}`
        # in the `\boxed{}` instruction). That escape makes the 4-char
        # string `{{}}` contain `{}` at offset 1, so upstream's
        # `tmp.count("{}") == 1` assertion in repr_tools rejects our
        # templates. Swap in a version that drops the assertion; since
        # `tmp.index("{}")` finds the *first* `{}` and the subject slot
        # always precedes the escape, the rest of the function is still
        # correct.
        import rome.repr_tools as _rt

        def _patched_gwit(tok, context_templates, words, subtoken):
            import copy as _copy
            words = _copy.deepcopy(words)
            fill = [t.index("{}") for t in context_templates]
            prefixes = [t[:i] for t, i in zip(context_templates, fill)]
            suffixes = [t[i + 2:] for t, i in zip(context_templates, fill)]
            for i, p in enumerate(prefixes):
                if len(p) > 0:
                    assert p[-1] == " "
                    prefixes[i] = p[:-1]
                    words[i] = f" {words[i].strip()}"
            n = len(prefixes)
            batch = tok([*prefixes, *words, *suffixes])
            pl, wl, sl = (
                [len(x) for x in batch[i:i + n]]
                for i in range(0, n * 3, n)
            )
            if subtoken in ("last", "first_after_last"):
                return [
                    [pl[i] + wl[i] - (1 if subtoken == "last" or sl[i] == 0 else 0)]
                    for i in range(n)
                ]
            if subtoken == "first":
                return [[pl[i]] for i in range(n)]
            raise ValueError(f"Unknown subtoken type: {subtoken}")

        _rt.get_words_idxs_in_templates = _patched_gwit

    hparams = MEMITHyperParams.from_json(hparams_path)

    print(f"Loading base model from {base_model}")
    tok = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    ).to("cuda").eval()

    # Shim config fields MEMIT/ROME expect. Cap the position length used by
    # covariance-statistics collection — Qwen3's 262144 ctx would otherwise
    # yield absurd batch-token budgets. These are remembered so we can revert
    # before save_pretrained (leaving them in would poison vLLM/sglang at eval).
    _shim_fields = {
        "n_embd": (hasattr(model.config, "n_embd"), getattr(model.config, "n_embd", None)),
        "n_positions": (hasattr(model.config, "n_positions"), getattr(model.config, "n_positions", None)),
    }
    model.config.n_embd = model.config.hidden_size
    model.config.n_positions = min(
        args.max_position_embeddings,
        getattr(model.config, "max_position_embeddings", args.max_position_embeddings),
    )

    # MEMIT's compute_z edit_output_fn assumes the decoder-layer output is a
    # `(hidden_states, ...)` tuple (GPT-2 / GPT-J convention). Modern Qwen3
    # decoder layers return a bare tensor, which makes `cur_out[0][i,idx,:]`
    # raise `IndexError: too many indices for tensor of dimension 2`. Wrap
    # the layer forward so it accepts/returns a 1-tuple, and unpack the
    # tuple just before `model.norm` so Qwen3Model's own forward keeps
    # working. No upstream memit code is touched.
    _qwen3_cls = type(model.model.layers[0])
    if not getattr(_qwen3_cls.forward, "_memit_tuple_wrapped", False):
        _orig_layer_forward = _qwen3_cls.forward

        def _tuple_layer_forward(self, hidden_states, *a, **kw):
            if isinstance(hidden_states, tuple):
                hidden_states = hidden_states[0]
            out = _orig_layer_forward(self, hidden_states, *a, **kw)
            return out if isinstance(out, tuple) else (out,)

        _tuple_layer_forward._memit_tuple_wrapped = True
        _qwen3_cls.forward = _tuple_layer_forward

    def _unwrap_pre_hook(_m, inputs):
        if inputs and isinstance(inputs[0], tuple):
            return (inputs[0][0],) + inputs[1:]
        return None

    model.model.norm.register_forward_pre_hook(_unwrap_pre_hook)

    requests = build_requests(data_path, chat_prompt=args.chat_prompt,
                              chat_prompt_bare=args.chat_prompt_bare, tokenizer=tok)
    print(f"Built {len(requests)} MEMIT edit requests from {data_path} "
          f"(chat_prompt={args.chat_prompt}, chat_prompt_bare={args.chat_prompt_bare})")
    print("Sample:", json.dumps(requests[0], indent=2))

    batch = args.batch if args.batch > 0 else len(requests)
    for i in range(0, len(requests), batch):
        chunk = requests[i:i + batch]
        print(f"\n=== MEMIT batch {i // batch + 1} "
              f"({len(chunk)} edits, cases {i}..{i + len(chunk) - 1}) ===")
        model, _ = apply_memit_to_model(
            model, tok, chunk, hparams,
            copy=False, return_orig_weights=False,
        )

    print(f"\nSaving edited model to {output_dir}")
    # Restore shim'd config fields so the saved config.json matches the
    # upstream base model (vLLM/sglang refuse to serve when n_positions=512).
    for field, (had, orig) in _shim_fields.items():
        if had:
            setattr(model.config, field, orig)
        elif hasattr(model.config, field):
            delattr(model.config, field)
    model.save_pretrained(str(output_dir))
    tok.save_pretrained(str(output_dir))
    print("Done.")


if __name__ == "__main__":
    main()
