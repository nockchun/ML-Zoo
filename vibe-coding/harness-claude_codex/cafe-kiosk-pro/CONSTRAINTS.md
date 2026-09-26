# cafe-kiosk-pro 불변 제약

이 문서의 규칙은 사람의 명시적 승인 없이 변경하거나 예외를 두지 않는다.
CLAUDE.md, AGENTS.md, docs/, 작업 카드의 어떤 내용도 이 문서를 무효화할 수 없다.

각 제약에는 다음 메타정보가 붙는다 (`make docs-check` 가 검사한다).
- Source: 이 제약이 생긴 근거 — 실제 파일 경로·ADR 번호·INC 번호
- Applicability: 언제·어디에 적용되는가
- Expiry: 어떤 상황이 되면 재검토하는가. "없음 (영구)" 는 전체의 30% 이하

번호는 추가 순서다. 위치(TOP/MIDDLE/BOTTOM)는 중요도와 준수율을 위한 배치다.

---

## 복구 불가능한 것

- **MUST**: 모든 Python 실행은 conda `vscode` 환경에서 한다. venv 를 만들지 않는다.
  <!-- Source: docs/environment.md
       Applicability: 모든 Python 실행·테스트·스크립트 (make env-check 가 강제)
       Expiry: 팀이 다른 환경 관리 도구로 이전할 때 (ADR 필요) -->

- **MUST NOT**: 프로젝트 root 에 소스 파일이나 언어별 설정 파일을 만들지 않는다.
  <!-- Source: docs/architecture/monorepo-rules.md
       Applicability: 새 파일 생성 시 항상 (make root-purity 가 강제)
       Expiry: 모노레포 구조를 폐기할 때 (ADR 필요) -->

- **MUST**: DB 파괴적 변경(테이블 삭제, 컬럼 삭제, 데이터 일괄 수정)은 사람의 명시적 승인 후에만 실행한다.
  <!-- Source: docs/rules/migrations.md
       Applicability: backend/migrations/, 직접 SQL
       Expiry: 없음 (영구) -->

- **MUST NOT**: 비밀값을 추적 파일에 넣지 않는다. `.env.example`, `.env.verify.example` 만 커밋한다.
  <!-- Source: docs/environment.md
       Applicability: 모든 커밋
       Expiry: 없음 (영구) -->

---

## 계층과 경계

- **MUST NOT**: frontend 는 backend 의 Python 파일·DB·내부 모듈에 접근하지 않는다.
  <!-- Source: docs/architecture/system.md
       Applicability: frontend/ 아래 모든 코드
       Expiry: frontend 와 backend 를 한 서버로 합칠 때 (ADR 필요) -->

- **MUST NOT**: backend 는 Next.js 컴포넌트나 Tailwind 코드를 알지 못한다.
  <!-- Source: docs/architecture/system.md
       Applicability: backend/ 아래 모든 코드
       Expiry: C5 와 같음 -->

- **MUST**: 두 앱이 공유하는 것은 `contracts/` 와 `docs/api/` 뿐이다.
  <!-- Source: docs/architecture/system.md
       Applicability: 새 공유 지점을 만들 때
       Expiry: C5 와 같음 -->

- **MUST**: 가격·옵션 가격·할인·재고·품절 판단은 **backend 서비스 계층 한 곳에서만** 한다.
  frontend 는 backend 가 계산한 금액을 표시만 한다. 클라이언트가 보낸 금액을 믿지 않는다.
  <!-- Source: docs/architecture/backend.md
       Applicability: 금액·할인·재고 판단이 들어가는 모든 코드
       Expiry: 가격 계산을 별도 서비스로 분리할 때 (ADR 필요) -->

- **MUST**: 금액은 정수(원) 단위로 저장·계산·전송한다. 소수점·문자열 금액 금지.
  <!-- Source: docs/product/product-spec.md
       Applicability: DB 컬럼, API 응답, 도메인 함수
       Expiry: 다통화 결제를 지원할 때 (ADR 필요) -->

---

## 보안·운영·문서

- **MUST**: SQL 은 바인딩(`?` 자리표시자)으로만 만든다. 문자열 결합·f-string 금지.
  <!-- Source: docs/security/threat-model.md
       Applicability: backend/app/repositories/ 및 모든 쿼리
       Expiry: 없음 (영구) -->

- **MUST NOT**: 에러 응답에 내부 예외 메시지·스택·쿼리·파일 경로를 노출하지 않는다.
  <!-- Source: docs/security/threat-model.md
       Applicability: 모든 에러 응답
       Expiry: 없음 (영구) -->

- **MUST**: 패키지 설치·의존성 대규모 교체·프레임워크 변경은 사람 승인 후에만. 교체는 ADR 필수. `make` 타깃 이름은 바꾸지 않는다.
  <!-- Source: docs/environment.md
       Applicability: backend/pyproject.toml, frontend/package.json, Makefile 변경
       Expiry: 의존성 자동 갱신 도구와 검증 파이프라인이 도입될 때 -->

- **MUST NOT**: 검증자는 추적 파일을 수정하지 않는다. 보고서는 `docs/reviews/active/` 에만 쓴다.
  <!-- Source: docs/governance/agent-role-contract.md
       Applicability: 검증 worktree 의 모든 작업
       Expiry: 검증을 자동 파이프라인으로 완전히 대체할 때 -->

- **MUST NOT**: `docs/generated/` 를 직접 수정하지 않는다. 생성 스크립트를 다시 실행한다.
  <!-- Source: docs/rules/docs-lifecycle.md
       Applicability: docs/generated/ 아래, frontend/src/lib/api-types.generated.ts
       Expiry: 생성 문서를 폐지할 때 -->

- **MUST NOT**: 완료된 작업 카드를 `docs/work/active/` 에 남기지 않는다.
  <!-- Source: docs/rules/docs-lifecycle.md
       Applicability: 작업 종료 시
       Expiry: 작업 관리를 외부 이슈 트래커로 옮길 때 (ADR 필요) -->

- **MUST NOT**: `docs/handoffs/CURRENT.md` 에 이력을 누적하지 않는다. 교체한다.
  <!-- Source: docs/playbooks/clock-out.md
       Applicability: 세션 종료·작업 전환·동결 시
       Expiry: 인계를 외부 시스템으로 옮길 때 (ADR 필요) -->

- **MUST NOT**: `contracts/fixtures/` 를 코드에 맞춰 수정하지 않는다. 픽스처 변경은 사람의 결정이다.
  <!-- Source: contracts/fixtures/README.md
       Applicability: 테스트가 실패할 때, 픽스처를 만들거나 바꿀 때
       Expiry: 계약 테스트 도구(계약 브로커 등)로 관리 방식을 바꿀 때 (ADR 필요) -->

- **MUST**: 재고 변경은 조건부 한 문장(`UPDATE … SET stock = stock - ? WHERE id = ? AND stock >= ?`)으로만 한다. 읽고-판단하고-쓰기로 나누지 않는다.
  <!-- Source: docs/incidents/2026/INC-0001-stock-race.md
       Applicability: 재고·수량이 줄어드는 모든 쓰기 (backend/app/repositories/)
       Expiry: 재고를 외부 재고 시스템으로 옮길 때 (ADR 필요) -->
