# cafe-kiosk-pro — 검증 인터페이스. 이름은 고정, 내용은 위임만 한다 (CONSTRAINTS C2, C12).
# 이름은 오래 살고 도구는 바뀐다. FastAPI 를 버려도 `make test-backend` 라는 이름은 남는다.
SHELL       := /bin/bash
CONDA_ENV   := vscode
MAX_SECONDS ?= 0
K           ?=
ARGS        ?=
FILES       ?=

# 포트·DB 파일은 .env 에서 읽는다 (구현자/검증자 worktree 마다 다름)
-include .env
export
export PYTHONDONTWRITEBYTECODE := 1
FRONTEND_PORT ?= 3000
BACKEND_PORT  ?= 8000

# 선택 필터: make test-cross K=menu.list
PYTEST_K := $(if $(K),-k "$(K)")
VITEST_T := $(if $(K),-t "$(K)")

.PHONY: help env-check git-aliases doctor setup migrate seed dev gen-types \
        check session-exit cleanup lint-touched test-affected test-affected-list test-slow-bg \
        test-backend test-frontend test-contract test-cross test-seed test-migration \
        test-concurrency test-security test-e2e test-card test-card-list test-meta fixture-capture \
        docs-check handoff-check features-check features-verify routing-parity root-purity \
        bootstrap-check cold-start-check

help:               ## 명령 목록
	@grep -E '^[a-z-]+:.*## ' Makefile | awk 'BEGIN {FS=":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'

# ── 1층: 환경 ─────────────────────────────────────
env-check:          ## conda vscode + python 3.11 + node 20 (모든 타깃의 가드, 1초)
	@test "$$CONDA_DEFAULT_ENV" = "$(CONDA_ENV)" || ( \
		echo "❌ conda 환경이 '$(CONDA_ENV)' 가 아닙니다 (현재: '$$CONDA_DEFAULT_ENV')"; \
		echo "   conda activate $(CONDA_ENV)"; exit 1 )
	@python -c "import sys; assert sys.version_info >= (3,11)" \
		|| (echo "❌ Python 3.11+ 필요"; exit 1)
	@node --version 2>/dev/null | grep -qE '^v(2[0-9]|[3-9][0-9])\.' \
		|| (echo "❌ Node.js 20+ 필요"; exit 1)
	@echo "✅ conda=$(CONDA_ENV) python=$$(python --version 2>&1) node=$$(node --version)"

git-aliases:        ## 팀 표준 git 별칭 16개 (멱등)
	@bash scripts/git-aliases.sh

doctor: env-check   ## 전체 환경 진단 (사람이 문제 생겼을 때, 5초)
	@python scripts/doctor.py

setup: env-check    ## 의존성 설치 — 사람이 실행 (C12)
	@cd backend && pip install -e ".[dev]"
	@cd frontend && npm ci

migrate: env-check  ## DB 마이그레이션 up (SQLite, .env 의 KIOSK_DB_PATH)
	@cd backend && python -m app.migrate up

seed: migrate       ## 멱등한 데모 데이터
	@cd backend && python -m app.seed

dev: env-check      ## backend + frontend 동시 실행 (Ctrl-C 로 둘 다 종료)
	@trap 'kill 0' INT TERM; \
	 (cd backend && uvicorn app.main:app --reload --port $(BACKEND_PORT)) & \
	 (cd frontend && npm run dev -- --port $(FRONTEND_PORT)); \
	 wait

gen-types: env-check ## openapi.yaml → frontend/src/lib/api-types.generated.ts
	@python scripts/gen_api_types.py

# ── 구조·문서·상태 게이트 ──────────────────────────
root-purity: env-check     ## root 에 소스 파일 없음
	@python scripts/root_purity_audit.py
routing-parity: env-check  ## Claude 자동로딩 ↔ AGENTS.md ↔ Codex 포인터 동기화
	@python scripts/routing_parity.py
docs-check: env-check      ## 크기·형식·생명주기·제약 메타정보·카드·영향 지도
	@python scripts/docs_check.py
handoff-check: env-check   ## CURRENT.md 형식·사실성·동결 게이트
	@python scripts/handoff_check.py
features-check: env-check  ## Triple, WIP=1, 통계
	@python scripts/features_check.py
features-verify: env-check ## passing 기능의 verification 실제 실행
	@python scripts/features_check.py --verify-passing
bootstrap-check: env-check ## 새 합류자 4조건 (존재·형식)
	@python scripts/bootstrap_check.py
cold-start-check: env-check ## Cold-start 12문항 근거 파일
	@python scripts/cold_start_check.py

# ── 테스트 층 (docs/quality/test-strategy.md) ────────
test-backend: env-check    ## 단위: ruff + pytest tests/unit (< 5초)
	@cd backend && ruff check app tests && ruff format --check app tests && python -m pytest tests/unit -q $(PYTEST_K)
test-frontend: env-check   ## 단위: tsc + vitest tests/unit (< 20초)
	@cd frontend && npx tsc --noEmit && npx vitest run tests/unit $(VITEST_T)
test-contract: env-check   ## 계약(형태): openapi ↔ backend ↔ frontend 타입 (< 3초)
	@python scripts/contract_check.py
test-cross: env-check      ## ⭐ 교차 경계(값): 공유 픽스처 양방향 + 커버리지 (< 15초)
	@echo "▶ Provider: backend 가 픽스처를 만드는가"
	@cd backend && python -m pytest tests/cross -q $(PYTEST_K)
	@echo "▶ Consumer: frontend 가 픽스처를 처리하는가"
	@cd frontend && npx vitest run tests/cross $(VITEST_T)
	@echo "▶ 픽스처 커버리지"
	@python scripts/fixture_coverage.py
test-seed: env-check       ## seed 두 번 실행해도 동일
	@if ls backend/tests/seed/test_*.py >/dev/null 2>&1; then cd backend && python -m pytest tests/seed -q; \
	 else echo "⏭  test-seed: backend/tests/seed/ 에 테스트 없음 (건너뜀)"; fi
test-migration: env-check  ## 마이그레이션 up → down → up 왕복
	@if ls backend/tests/migration/test_*.py >/dev/null 2>&1; then cd backend && python -m pytest tests/migration -q; \
	 else echo "⏭  test-migration: 테스트 없음 (건너뜀)"; fi
test-concurrency: env-check ## 경쟁 조건 재현 (동시성이 필요한 기능이 접수되면 작성)
	@if ls backend/tests/concurrency/test_*.py >/dev/null 2>&1; then cd backend && python -m pytest tests/concurrency -v $(PYTEST_K); \
	 else echo "⏭  test-concurrency: 테스트 없음 — 동시성이 필요한 기능이 들어오면 작성 (건너뜀)"; fi
test-security: env-check   ## 위협 모델 기반 보안 테스트
	@if ls backend/tests/security/test_*.py >/dev/null 2>&1; then cd backend && python -m pytest tests/security -q $(PYTEST_K); \
	 else echo "⏭  test-security: 테스트 없음 — 보안 테스트가 필요한 기능이 들어오면 작성 (건너뜀)"; fi
test-e2e: env-check        ## 브라우저 흐름 (선택: e2e/ 에 Playwright 를 설치했을 때만)
	@if [ -f e2e/package.json ]; then cd e2e && npx playwright test $(if $(K),--grep "$(K)"); \
	 else echo "⏭  test-e2e: e2e/package.json 없음 — 선택 스텝 (건너뜀)"; fi
test-meta: env-check       ## 테스트가 실제로 실패할 수 있는가 — 변형 탐지율 (월 1회)
	@python scripts/test_meta.py --sample 20

# ── 실행 시점 4계층 ────────────────────────────────
lint-touched: env-check    ## L1 편집 직후: 지정 파일만 (FILES=..., 3초)
	@python scripts/lint_touched.py $(FILES)
test-affected: env-check   ## L2 턴 종료: 변경 영향 범위 (MAX_SECONDS=60)
	@python scripts/affected_tests.py --run $(if $(filter-out 0,$(MAX_SECONDS)),--max-seconds $(MAX_SECONDS))
test-affected-list: env-check ## L2 실행 대상만 출력
	@python scripts/affected_tests.py --list
test-slow-bg: env-check    ## 느린 테스트만 (백그라운드용)
	@python scripts/affected_tests.py --run --only-slow
test-card: env-check       ## 현재 작업 카드의 완료 조건 실행 (ARGS="--card CK-xxx")
	@python scripts/card_verify.py $(ARGS)
test-card-list: env-check  ## 완료 조건 목록만
	@python scripts/card_verify.py --list $(ARGS)
fixture-capture: env-check ## 실제 응답 ↔ 픽스처 diff (승인은 사람이 터미널에서)
	@python scripts/fixture_capture.py

# ── L3 동결 전: 전체 게이트 (env-check 포함 16개) ─────
check: env-check root-purity routing-parity docs-check handoff-check features-check bootstrap-check \
       test-contract test-cross test-backend test-frontend test-seed test-migration \
       test-security test-concurrency test-e2e
	@python scripts/record_check.py
	@echo "✅ 전체 품질 게이트 통과"
	@echo "   단, 화면·사용성은 사람과 검증자가 확인해야 합니다"
	@python scripts/card_verify.py --manual-only

# ── L4 세션 종료 ───────────────────────────────────
session-exit: env-check    ## Clean State 5차원 (Build/Tests/Progress/Artifacts/Startup)
	@python scripts/session_exit.py
cleanup:                   ## 임시 산출물 정리 (멱등)
	@python scripts/cleanup.py
