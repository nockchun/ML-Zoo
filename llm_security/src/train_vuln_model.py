import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling,
)

# ✅ 기본값: 한국어 생성이 되는 KoGPT2 (CPU에서 가능)
BASE_MODEL = os.environ.get("BASE_MODEL", "skt/kogpt2-base-v2")
DATA_PATH  = os.environ.get("DATA_PATH", "data/vuln_sft.jsonl")
OUT_DIR    = os.environ.get("OUT_DIR", "models/vuln-assistant")
MAX_LEN_ENV = int(os.environ.get("MAX_LEN", "256"))

def _resolve_max_len(model, requested: int) -> int:
    """모델 포지션 임베딩 한도를 넘기지 않도록 MAX_LEN을 안전하게 보정."""
    max_pos = None
    # GPT-2 계열은 보통 n_positions 또는 max_position_embeddings를 가집니다.
    for k in ("n_positions", "max_position_embeddings"):
        v = getattr(getattr(model, "config", None), k, None)
        if isinstance(v, int) and v > 0:
            max_pos = v
            break
    if max_pos is None:
        return requested
    return min(requested, max_pos)

def _make_tokenize_fn(tok, max_len: int):
    def _fn(batch):
        return tok(
            batch["text"],
            truncation=True,
            padding="max_length",
            max_length=max_len,
        )
    return _fn

def _sanity_check_ids(ds_tok, vocab_size: int, max_pos: int | None = None, sample_n: int = 32):
    """CUDA assert(=index out of bounds) 원인(토큰/포지션 범위 초과)을 학습 전에 빠르게 탐지."""
    n = min(len(ds_tok), sample_n)
    for i in range(n):
        ids = ds_tok[i]["input_ids"]
        if any((t < 0 or t >= vocab_size) for t in ids):
            bad = [t for t in ids if (t < 0 or t >= vocab_size)][:10]
            raise ValueError(
                f"input_ids에 vocab 범위 밖 토큰이 있습니다. (예: {bad}) "
                f"vocab_size={vocab_size}. tokenizer/model 불일치 또는 special token 처리 문제일 수 있습니다."
            )
        if max_pos is not None and len(ids) > max_pos:
            raise ValueError(
                f"시퀀스 길이({len(ids)})가 모델 최대 포지션({max_pos})을 초과합니다. "
                f"MAX_LEN을 {max_pos} 이하로 줄이세요."
            )

def main():
    ds = load_dataset("json", data_files=DATA_PATH, split="train")

    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

    # ✅ GPT-2 계열은 pad_token이 없는 경우가 많습니다.
    #    (새 토큰을 추가하면 vocab_size가 달라져 CUDA index out of bounds가 날 수 있으므로)
    #    eos_token을 pad_token으로 재사용하는 방식을 기본으로 둡니다.
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model.config.pad_token_id = tok.pad_token_id

    # ✅ 만약 어떤 이유로든 tokenizer가 special token을 추가했다면, 임베딩 크기를 맞춥니다.
    if model.get_input_embeddings().num_embeddings != len(tok):
        model.resize_token_embeddings(len(tok))

    max_len = _resolve_max_len(model, MAX_LEN_ENV)
    tokenize_fn = _make_tokenize_fn(tok, max_len)

    ds_tok = ds.map(tokenize_fn, batched=True, remove_columns=ds.column_names)

    # 학습 전에 빠르게 검증(문제면 여기서 명확한 에러로 중단)
    max_pos = getattr(model.config, "n_positions", None) or getattr(model.config, "max_position_embeddings", None)
    _sanity_check_ids(ds_tok, vocab_size=model.config.vocab_size, max_pos=max_pos)

    collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)

    args = TrainingArguments(
        output_dir=OUT_DIR,
        per_device_train_batch_size=int(os.environ.get("BATCH_SIZE", "4")),
        gradient_accumulation_steps=int(os.environ.get("GRAD_ACCUM", "1")),
        num_train_epochs=float(os.environ.get("EPOCHS", "3")),
        learning_rate=float(os.environ.get("LR", "5e-5")),
        weight_decay=0.0,
        logging_steps=20,
        save_steps=500,
        save_total_limit=1,
        report_to=[],
        remove_unused_columns=False,
        dataloader_drop_last=False,
    )

    trainer = Trainer(model=model, args=args, train_dataset=ds_tok, data_collator=collator)
    trainer.train()
    trainer.save_model(OUT_DIR)
    tok.save_pretrained(OUT_DIR)
    print("saved:", OUT_DIR)

if __name__ == "__main__":
    main()
