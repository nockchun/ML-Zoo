import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# Prefer an instruction/chat model by default so the demo reliably emits JSON.
# You can override with:
#   export RAG_MODEL="some/hf-model"          (base model id)
#   export MODEL_PATH="models/vuln-assistant" (local fine-tuned path used by notebooks)
DEFAULT_BASE_MODEL = os.environ.get("RAG_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")


def _pick_device():
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load(model_name_or_path: str | None = None):
    """Load tokenizer+model.

    Notebooks historically pass a local fine-tuned path (models/vuln-assistant).
    To keep the demo stable, we *only* load that fine-tuned model when
    USE_FINETUNED=1 is set. Otherwise we fall back to DEFAULT_BASE_MODEL.
    """
    model_name_or_path = model_name_or_path or DEFAULT_BASE_MODEL

    use_finetuned = os.environ.get("USE_FINETUNED", "0").lower() in {"1", "true", "yes"}
    if os.path.isdir(model_name_or_path) and use_finetuned:
        resolved = model_name_or_path
    else:
        # If they pointed at a local models/* folder (common in the notebooks),
        # but finetuning isn't enabled, fall back to the base chat model.
        if model_name_or_path.startswith("models/"):
            resolved = DEFAULT_BASE_MODEL
        else:
            resolved = model_name_or_path

    tok = AutoTokenizer.from_pretrained(resolved, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    device = _pick_device()
    if device == "cuda":
        dtype = torch.float16
        kwargs = {"device_map": "auto", "torch_dtype": dtype}
    else:
        kwargs = {}
    model = AutoModelForCausalLM.from_pretrained(resolved, **kwargs)
    model.eval()

    if device != "cuda":
        model.to(device)

    return tok, model


# ---------------------------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------------------------

def load_model_and_tokenizer(model_name_or_path: str | None = None):
    """Alias for :func:`load`.

    Some notebooks import ``load_model_and_tokenizer`` from ``src.modeling``.
    To keep those notebooks working, we provide this alias here.
    """

    return load(model_name_or_path=model_name_or_path)


__all__ = ["load", "load_model_and_tokenizer"]


def format_prompt(tok, system: str, user: str) -> str:
    """Format a prompt for both chat and plain causal LM tokenizers."""
    if hasattr(tok, "apply_chat_template") and getattr(tok, "chat_template", None):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        # add_generation_prompt=True makes the template end in an assistant turn.
        return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # Fallback: plain concatenation for non-chat models
    return f"<|system|>\n{system}\n<|user|>\n{user}\n<|assistant|>\n"


def _extra_eos_ids(tok):
    ids = []
    # Many chat models (e.g., Qwen) define <|eot_id|>
    for t in ["<|eot_id|>", "<|endoftext|>"]:
        try:
            tid = tok.convert_tokens_to_ids(t)
        except Exception:
            tid = None
        if tid is not None and isinstance(tid, int) and tid >= 0 and tid != tok.unk_token_id:
            ids.append(tid)
    # Always include eos_token_id when available
    if tok.eos_token_id is not None:
        ids.append(tok.eos_token_id)
    # de-dupe
    out = []
    for x in ids:
        if x not in out:
            out.append(x)
    return out or None

@torch.inference_mode()
def generate(*args, max_new_tokens: int = 192) -> str:
    """Generate text.

    Backward compatible:
      - generate(tok, model, prompt)
      - generate(model, tok, prompt)
    """
    if len(args) != 3:
        raise TypeError("generate expects (tok, model, prompt) or (model, tok, prompt)")

    a0, a1, prompt = args
    # Heuristic: tokenizer has encode/decode; model has generate
    if hasattr(a0, "generate") and hasattr(a1, "__class__") and not hasattr(a1, "generate"):
        model, tok = a0, a1
    else:
        tok, model = a0, a1

    inputs = tok(prompt, return_tensors="pt", padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    eos_ids = _extra_eos_ids(tok)

    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        no_repeat_ngram_size=3,
        eos_token_id=eos_ids,
        pad_token_id=tok.pad_token_id,
    )

    gen_ids = out[0][inputs["input_ids"].shape[1]:]
    text = tok.decode(gen_ids, skip_special_tokens=True)
    return text.strip()
