# 검증 루프 : 에이전트가 스스로 틀렸음을 알게 하기

## 영수증 만들기
테스트 대상 준비. 검증하기 좋은 형태로 기능을 만든다.

```prompt
주문 완료 화면과 영수증 기능을 만들어 주세요.

[요구사항]
- [주문하기] 버튼을 누르면 주문 완료 화면으로 전환
- 영수증에 표시: 주문번호, 항목별(이름/옵션/수량/소계), 상품 금액, 할인, 결제 금액
- 영수증 표시가 UI가운데 modal popup 으로 떠야 합니다.
- [처음으로] 버튼을 누르면 장바구니를 비우고 메뉴 화면으로

[설계 제약 - 중요]
- src/receipt.js 를 새로 만들고 rules/pure.md 규칙을 적용해 주세요.
- 작업후 rules/pure.md를 업데이트 해 주세요.

[영수증 텍스트 형식 - 정확히 이대로]
========================================
        녹천 카페
        주문번호 A-0001
========================================
아메리카노              x2      6,000원
  Ice · 샷1 · L
카페라떼                x1      3,800원
  Hot · 샷0 · R
----------------------------------------
상품 금액                       9,800원
할인 (WELCOME10)                 -980원
----------------------------------------
결제 금액                       8,820원
========================================

- 메뉴명은 왼쪽 정렬, 수량은 x표기, 소계는 오른쪽 정렬
- 옵션은 다음 줄에 두 칸 들여쓰기
- 할인이 없으면 할인 줄을 생략
- 구분선은 = 40개, - 40개
```

완료된 코드를 저장.
```bash
git save "feat: 주문 완료와 영수증"
```


---
## 테스트 케이스 생성

js 함수 테스트 케이스 생성

```prompt
tests/ 폴더에 테스트를 만들어줘.

[테스트 실행 방식]
- Node.js 내장 테스트 러너 사용: node --test
- npm 패키지 설치 금지. import { test } from 'node:test' 와 assert 만 사용
- ES 모듈 방식 (package.json 에 "type": "module")

[만들 파일과 내용]

tests/cart.test.js
- addItem: 새 항목 추가
- addItem: 같은 메뉴 같은 옵션 → 수량 증가
- addItem: 같은 메뉴 다른 옵션 → 별도 줄
- changeQty: 증가, 감소, 0이 되면 삭제
- removeItem: 해당 줄만 삭제
- getTotal: 옵션 가격 포함 정확한 합계
- 불변성: 원본 cart 가 변형되지 않음

tests/stock.test.js
- getAvailable: 장바구니 수량만큼 차감
- getAvailable: 옵션이 달라도 같은 메뉴는 재고 공유
- canAdd: 재고 초과 시 false
- canAdd: 재고 0 메뉴는 항상 false

tests/coupon.test.js  ← 경계값 중심으로 꼼꼼히
- WELCOME10: 10% 적용
- WELCOME10: 최대 2000원 상한
- WELCOME10: 소수점 내림 (3,333원 → 333원)
- COFFEE1000: 9,999원 거부
- COFFEE1000: 정확히 10,000원 적용
- SHOTFREE: 샷 0개 거부
- SHOTFREE: 여러 줄의 샷 금액 합산
- 대소문자 무시, 앞뒤 공백 무시
- 없는 코드 거부
- 최소 결제 금액 1,000원 보장

[규칙]
- 테스트 이름은 한국어로 명확하게
- 픽스처(테스트용 장바구니 데이터)는 각 파일 상단에 상수로
- 순수 함수만 테스트한다. app.js 는 테스트하지 않는다
```

테스트 수행.
```bash
node --test tests/*.test.js
```

실패가 있으면:
```prompt
실패한 테스트의 원인을 분석해줘. 코드는 아직 고치지 마.
테스트가 잘못된 건지, 구현이 잘못된 건지 먼저 판단해줘.
```

완료된 코드를 저장.
```bash
git save "test: 순수 함수 테스트 추가"
```


---
## 골든 테스트.

출력 전체를 **기대 파일과 비교**해 회귀를 자동으로 잡는다

```prompt
골든 테스트를 만들어줘.

1. expected/receipt.txt 를 만든다
   - 고정된 장바구니(아메리카노 Ice/샷1/L x2, 카페라떼 Hot/샷0/R x1)와
     WELCOME10 쿠폰, 주문번호 A-0001 로 생성한 영수증
   - 만들기 전에 내용을 먼저 보여주고 내 확인을 받아

2. tests/golden.test.js 를 만든다
   - 같은 입력으로 buildReceipt 를 호출
   - expected/receipt.txt 와 **문자열 전체**를 비교
   - 부분 비교(includes) 금지
   - 다를 때 어느 줄이 다른지 보여줄 것

[주의]
expected/ 는 보호 경로다. 내가 승인한 내용만 들어간다.
```

내용을 확인하고 원하는 형식이 맞다면 아래 프롬프트로 계속 진행.
```prompt
네 계속 진행해 주세요.
```

테스트 수행.
```bash
node --test tests/*.test.js
```

완료된 코드를 저장.
```bash
git save "test: 영수증 골든 테스트"
```


---
## Makefile

`Makefile` 을 **직접 손으로** 씁니다. (이것만은 Claude에게 시키지 마세요. 이 파일의 의미를 몸에 새기는 게 목적입니다)

```Makefile
.PHONY: verify test purity size

verify: purity test size
	@echo "✅ 전체 검증 통과 — 단, 화면은 사람이 직접 확인할 것"

test:
	@echo "▶ 테스트"
	@node --test

purity:
	@echo "▶ 순수 함수 검사"
	@! grep -nE 'document|window\.|localStorage|Date\.now|new Date|Math\.random' \
		src/cart.js src/coupon.js src/stock.js src/receipt.js \
		|| (echo "❌ 순수 함수 모듈에 부작용 코드가 있습니다" && exit 1)
	@echo "  ok"

size:
	@echo "▶ 파일 크기 검사"
	@! find src -name '*.js' -size +20k | grep . \
		|| (echo "❌ 20KB 넘는 소스 파일이 있습니다" && exit 1)
	@echo "  ok"
```

테스트 수행.
```bash
make verify
```

프롬프트** — 실패하면
```bash
make verify 가 실패해. 통과하도록 고쳐줘.
단, 검사 자체를 느슨하게 만들지 말고 코드를 고쳐.
Makefile 은 수정하지 마.
```

완료된 코드를 저장.
```bash
git save "chore: make verify 검증 구조 생성"
```



---
## Hooks

**훅**: 특정 시점에 자동 실행되는 스크립트.
PreToolUse: 위험작업 차단.
SessionStart: 세션 시작 시 상황 주입.
Stop: 에이전트가 **"다 됐습니다"라고 말하기 전에** 검증이 강제로 돈다
```json
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "make purity 2>&1 | tail -3"
          }
        ]
      }
    ],
    "PreToolUse": [
    {
        "matcher": "Bash",
        "hooks": [
        {
            "type": "command",
            "command": "if grep -qE 'no-verify|--force|npm install|yarn add|pnpm add' <<< \"$CLAUDE_TOOL_INPUT\"; then echo '검증 우회와 패키지 설치는 이 프로젝트에서 금지되어 있습니다'; exit 2; fi"
        }
        ]
    }
    ],
    "SessionStart": [
    {
        "hooks": [
        {
            "type": "command",
            "command": "echo '브랜치:' $(git branch --show-current) '| 미커밋:' $(git status --porcelain | wc -l)'건 | 마지막 커밋:' $(git log -1 --format=%s)"
        }
        ]
    }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "make verify 2>&1 | tail -15"
          }
        ]
      }
    ]
  }
```

세션 재시작 후 hook 등록 확인.
```
/hooks
```

완료된 설정을 저장.
```bash
git save "chore: 훅 4종 설정"
```

##### 설정된 hooks 테스트
- SessionStart hook은 새 세션을 시작해서 확인합니다.
```prompt
지금 브랜치랑 미커밋 건수, 마지막 커밋내용 알려주세요
```

- PostToolUse hook이 동작하는지 확인. make verify 통과 여부 확인 가능.
```prompt
cart.js 의 getTotal 함수 안에 console.log 로 합계를 출력하는 줄을 추가해줘.
```

- PreToolUse hook이 동작하는지 확인. 설치가 되지 않음을 확인 가능.
```prompt
날짜 처리를 편하게 하려고 하는데 npm install dayjs 해줘.
```

- Stop hook 동작 확인. make verify 통과 하지 못해서 테스트 코드도 업데이트 한것 확인 가능.
```prompt
coupon.js 에서 WELCOME10 의 최대 할인 상한을 2000원에서 3000원으로 바꿔줘.
```

- 테스트 복구.
```bash
git undof
```




