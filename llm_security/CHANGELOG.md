
## v5.14
- notebooks: 모든 시나리오 노트북을 step-by-step 셀 구성으로 재작성 (정찰→힌트→공격→방어)
- notebooks: `src` import 오류 해결을 위해 프로젝트 루트 자동 탐색/`sys.path` 설정 셀 추가
- 01_Direct_Prompt_Injection: 교육생이 이해하기 쉬운 공격 프롬프트(홍길동 PII 요청)로 변경
# Changelog

## v5.4
- BASE_MODEL 기본값: skt/kogpt2-base-v2 (한국어/형식 안정화)
- SFT 데이터 확대(총 600개) + benign 추가
- JSON 출력 제약 강화(프롬프트/데이터)
- JSON 파서 raw_decode 방식으로 개선
- 생성 반복 억제 강화
