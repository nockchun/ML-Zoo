# 코드를 넘어 에이전트의 작업 환경을 설계하는 방법

## 상태 보존 기능 만들기
테스트 대상 준비. 검증하기 좋은 형태로 기능을 만든다.

```prompt
새로고침해도 장바구니가 유지되게 만들어줘.

[요구사항]
- 장바구니와 적용된 쿠폰 코드를 localStorage 에 저장
- 페이지 로드 시 복원
- [처음으로] 또는 주문 완료 시에는 저장된 것도 비운다
- 저장 데이터에 버전 필드를 넣고, 버전이 다르면 무시하고 새로 시작한다
- 저장된 데이터가 깨져 있으면(JSON 파싱 실패) 조용히 무시하고 빈 장바구니로 시작

[설계 제약 - 중요]
- src/storage.js 를 새로 만들고 **여기서만** localStorage 에 접근한다
  save(state) / load() -> state|null / clear()
- cart.js, coupon.js, stock.js, receipt.js 는 절대 localStorage 를 모른다
- app.js 는 storage.js 를 호출만 한다

새로 구현된 규칙을 rules에 생성 및 기존 rule 업데이트가 필요하면 업데이트도 해 주세요.
storage.js 기능을 테스트하는 test case도 추가해 주세요.
```

완료된 코드를 저장.
```bash
git save "feat: localStorage 상태 보존"
```


---
## skill 만들기

반복되는 작업 절차를 재사용 가능한 자산으로 만든다.

`.claude/skills/new-feature/SKILL.md`:
```Markdown
---
name: new-feature
description: cafe-kiosk 에 새 기능을 추가할 때 사용. 사용자가 "기능 추가", "새 화면", "~기능 만들어줘" 를 요청하면 이 절차를 따른다.
---

# 새 기능 추가 절차

아래 순서를 반드시 지킨다. 건너뛰지 않는다.

1. **계획 먼저.** 어느 파일을 만들고 어느 파일을 수정할지 목록으로 제시하고 승인을 받는다
2. **계산 로직과 화면 로직을 분리한다**
   - 계산·판정·변환 → `src/` 의 순수 함수 모듈 (새로 만들어도 됨)
   - DOM·이벤트 → `src/app.js`
   - 저장소 접근 → `src/storage.js`
3. **순수 함수에는 반드시 테스트를 함께 만든다**
   - `tests/<모듈>.test.js`
   - 정상 케이스 + 경계값 + 실패 케이스
4. `make verify` 실행. 통과할 때까지 수정
5. **사람에게 브라우저 확인 항목을 번호 매겨 안내한다**
6. 변경한 파일과 줄 수를 3줄로 요약한다

## 금지
- 새 npm 패키지, 프레임워크, 빌드 도구
- `src/menu.js` 와 `expected/` 수정
- 테스트를 느슨하게 만들어 통과시키기
- 요청하지 않은 기능 추가
```

skill loading
```command
/reload-skills
```

new-feature skill 테스트
```prompt
장바구니 전체 비우기 버튼을 추가해 주세요.
```

완료된 코드를 저장.
```bash
git save "feat: 장바구니 비우기"
```


`.claude/skills/ui-check/SKILL.md`:
```Markdown
---
name: ui-check
description: 화면을 바꾼 뒤 사람이 브라우저에서 확인할 항목을 만들어 준다. UI, CSS, 레이아웃, 반응형을 수정한 뒤 사용한다.
---

# 화면 확인 체크리스트 생성

방금 변경한 내용을 기준으로, chrome extension을 이용하여 실제 브라우저에서 동작을 테스트 해 주세요.
그리고 나서 사람이 브라우저에서 확인할 목록을 만든다.

## 형식
각 항목은 이렇게 쓴다.
- [ ] (조작) → (기대하는 화면)

예: `- [ ] 아메리카노 클릭 → 옵션 창이 화면 중앙에 뜬다`

## 반드시 포함할 항목
1. 변경한 부분이 의도대로 보이는가
2. **변경하지 않은 부분이 깨지지 않았는가** (회귀)
3. 장바구니가 비었을 때 / 항목이 6개 이상일 때
4. 브라우저 폭 375px (모바일) 에서
5. 개발자 도구 콘솔에 에러가 없는가

## 금지
- "정상 동작합니다" 같은 자체 판정을 내리지 않는다.
  너는 브라우저를 완벽히 볼 수 없다. 확인은 사람이 한다.
```

skill loading
```command
/reload-skills
```

ui-check skill 테스트
```prompt
/new-feature /ui-check 주문 완료 화면에 "5초 후 자동으로 처음 화면" 카운트다운을 추가해 주세요.
```

완료된 코드를 저장.
```bash
git save "feat: 주문 완료 자동 복귀"
```


`.claude/skills/kiosk/SKILL.md`:
```Markdown
---
name: kiosk
description: 키오스크 프로젝트의 일상 점검. 사용자가 "점검", "상태 확인", "kiosk" 를 요청할 때.
---

1. `git status --short` 로 미커밋 변경 확인
2. `make verify` 실행
3. `node --test 2>&1 | tail -3` 으로 테스트 개수 확인
4. `find src -name '*.js' | xargs wc -l` 로 파일별 줄 수 표시
5. 아래를 한 표로 요약
   - 구현된 기능 (F1~F8 중)
   - 테스트 개수
   - 전체 줄 수
   - 미커밋 변경 건수
6. 미커밋 변경이 있으면 커밋 메시지를 제안 (커밋은 하지 않음)
```

skill loading
```command
/reload-skills
```

ui-check skill 테스트
```prompt
/kiosk
```

완료된 코드를 저장.
```bash
git save "feat: 커스텀 스킬 3종 완료."
```


---
## 모바일 대응 구현

```prompt
모바일 화면에 대응 할 수 있도록 수정해 주세요.

[요구사항]
- 768px 미만에서는 메뉴와 장바구니를 세로로 배치
- 375px 폭에서 가로 스크롤이 생기지 않아야 한다
- 장바구니는 화면 하단에 고정하고, 접기/펼치기 가능하게
  접혀 있을 때는 "장바구니 3개 · 12,400원" 요약과 [주문하기] 만 표시
- 모든 버튼은 최소 44x44px
- 옵션 창은 모바일에서 화면 하단에서 올라오는 형태(바텀시트)
- 메뉴 카드는 모바일에서 2열

[제약]
- styles.css 와 index.html 만 수정. src/ 의 JS 는 건드리지 말아 주세요.
  (접기/펼치기에 JS가 꼭 필요하면 app.js 만 추가로 허용하되 미리 알려줘)
- 기존 데스크톱 레이아웃이 깨지면 안 된다
- 미디어 쿼리로 처리. JS 로 화면 크기를 감지하지 말아 주세요.
```

Application Level Harness:
```prompt
새로 구현된 내용 중에 rule 에 업데이트해 둘 필요가 있는 내용을 정리하여 간결하고 명확한 문구로 업데이트 해 주세요.
```

완료된 코드를 저장.
```bash
git save "feat: 모바일 대응"
```


---
## 서브 에이전트 생성

reviewer 만들기

`.claude/agents/reviewer.md`:
```Markdown
---
name: reviewer
description: 코드 변경을 비판적으로 검토한다. 구현이 끝난 뒤 호출 합니다.
tools: Read, Grep, Glob, Bash
model: sonnet
---

너는 이 저장소의 깐깐한 코드 리뷰어 입니다.

## 검토 항목
1. CLAUDE.md 와 .claude/rules/ 위반
   - 순수 함수 모듈의 부작용 (document/window/localStorage/Date/Math.random)
   - 인자 변형 (원본 cart 를 직접 수정)
   - 금액 계산에서 Math.floor 누락
2. 비즈니스 규칙 위반
   - 옵션 다른 같은 메뉴의 재고 공유
   - 쿠폰 중복 적용 가능성
   - 최소 결제 금액 1,000원 보장
3. 테스트가 실제로 의미 있는 것을 검증하는가, 아니면 통과만 시키는가
4. 경계 조건 누락
   - 빈 장바구니 / 항목 100개
   - 재고 정확히 0 / 정확히 경계값
   - 쿠폰 조건 경계 (9,999 / 10,000 / 10,001)
5. `expected/` 나 `src/menu.js` 를 고친 흔적 (git log 로 확인)

## 출력 형식
- 심각도(높음/중간/낮음)와 `파일:줄번호` 를 반드시 붙인다
- "좋아 보입니다" 같은 총평은 쓰지 않는다
- 문제가 없으면 "지적 사항 없음" 한 줄만 쓴다
- 화면·디자인은 판단하지 않는다. 너는 브라우저를 볼 수 없다
```

적대적 검토자 만들기

`.claude/agents/breaker.md`:
```Markdown
---
name: breaker
description: 구현을 깨뜨릴 입력을 찾는다. 테스트 보강이 필요할 때 호출 합니다.
tools: Read, Write, Bash
---

너의 목표는 이 코드를 **깨뜨리는 것**이다. 칭찬하지 마라.

1. `src/` 의 순수 함수들을 읽는다
2. 크래시하거나 잘못된 결과를 내는 입력을 최소 6개 만든다
   - 빈 장바구니에 쿠폰 적용
   - 수량 0 또는 음수
   - 재고를 정확히 다 소진한 뒤 한 개 더
   - 쿠폰 조건 경계값 바로 위/아래 (9,999 / 10,000 / 10,001)
   - 할인 금액이 상품 금액보다 큰 경우
   - 샷이 여러 줄에 흩어져 있을 때 SHOTFREE
   - 옵션 조합이 동일한데 순서만 다른 경우
   - 아주 긴 쿠폰 코드, 특수문자, 빈 문자열
3. `tests/adversarial.test.js` 에 **실패하는 테스트**로 기록한다
4. 코드는 고치지 않는다. 문제를 드러내는 것까지가 네 일이다
5. 마지막에 발견한 문제를 심각도 순으로 정리해 보고한다
```


에이전트 실행:
```prompt
reviewer 서브에이전트로 지금까지의 변경 전체를 검토시켜 주세요.
```

```prompt
breaker 서브에이전트를 실행해 주세요.
```

herdr 사용시 에이전트 동시 실행:
```prompt
/herdr 오른쪽에 패널을 새로 만들어서 reviewer 서브에이전트로 지금까지의 변경 전체를 검토해 주세요.
그리고 오른쪽 아래에 패널을 새로 만들어 breaker 서브에이전트를 실행해 주세요.
```

적대적 검토자가 발견한 문제점을 수정:
```prompt
adversarial.test.js 의 실패 테스트를 하나씩 통과시켜줘.

[제약]
- 테스트를 수정하지 말고 구현을 고쳐
- 다만 테스트 자체가 잘못된 기대를 하고 있다면 먼저 나에게 알려줘
- make verify 가 전부 통과할 때까지
```

적대적 검토자가 테스트 케이스 통합:
```prompt
adversarial.test.js 의 테스트를 가각의 기능에 맞는 *.test.js로 옮기고 adversarial.test.js는 삭제 해 주세요.
```

완료된 코드를 저장.
```bash
make verify
git save "fix: 적대적 테스트 대응"
```


---
## 서브 테스크

reviewer 만들기

`.claude/agents/reviewer.md`:
```Markdown
---
name: reviewer
description: 코드 변경을 비판적으로 검토한다. 구현이 끝난 뒤 호출 합니다.






