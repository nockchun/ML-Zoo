# v5.4 — LLM + RAG 공격 시현 (한국어/JSON 안정화)

현재 보신 출력(깨진 JSON/무의미 토큰/한글 깨짐)은 주로:
- 영어 베이스 모델(distilgpt2)이 한국어/형식(JSON)에 약함
- SFT 데이터가 부족하거나, 'JSON only' 제약이 학습되지 않음
- JSON 파서가 부분 문자열을 잘못 잡음

v5.4 변경:
- 기본 베이스 모델: **skt/kogpt2-base-v2** (한국어 causal LM)
- SFT 데이터: 시나리오별 120개 + benign 120개 (총 600개)로 확대
- 'JSON 한 개만 출력' 제약을 system prompt + 데이터에 강하게 포함
- JSON 파서(raw_decode)로 견고화
- 생성 반복 억제 옵션 강화


## v5.10 변경(교육용 합성 PII 누출 데모)
- `docs/sensitive_notes.md`에 **합성(가짜) PII_CANARY**(카드/계좌/주민번호 형식 포함) 추가
- `docs/injected_doc.md`가 `PII_CANARY` 블록을 `answer`로 그대로 출력하도록 유도
- 소형 로컬 모델이 형식을 못 따를 때를 대비해, VULNERABLE 모드에서만 `PII_CANARY` 블록을 컨텍스트에서 추출해 반환하는 *교육용 fallback* 추가
- DEFENDED 모드는 문서 내 지시를 무시하고 canary를 제거하여 누출이 발생하지 않도록 유지

## 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python data/make_vuln_sft.py
BASE_MODEL=skt/kogpt2-base-v2 OUT_DIR=models/vuln-assistant EPOCHS=3 python -m src.train_vuln_model

jupyter notebook
```

## 리소스가 허용된다면 더 큰 모델도 가능
- `gpt2` (영어 중심)
- `EleutherAI/pythia-160m-deduped` (영어 중심)
- 한국어 중심은 KoGPT2 계열 권장

생성일: 2026-02-03
