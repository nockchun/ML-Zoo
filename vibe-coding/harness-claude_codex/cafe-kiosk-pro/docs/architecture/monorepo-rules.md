---
status: active
owner: human
updated: 2026-09-23
---

> 적용: 새 파일을 만들기 전에 항상. 빌드 설정을 바꿀 때.

# 모노레포 경계 규칙 (Root Purity)

## 원칙
프로젝트 root 는 **오케스트레이션 레이어**다 (CONSTRAINTS C2).
소스 코드와 언어별 설정은 `frontend/`, `backend/`, `e2e/` 안에만 존재한다.

## root 에 허용되는 것
`scripts/root_purity_audit.py` 의 허용 목록은 이 표와 일치해야 한다.

| 항목 | 목적 |
|---|---|
| `README.md` | 사람용 진입점 |
| `CLAUDE.md`, `AGENTS.md`, `CONSTRAINTS.md`, `BOOTSTRAP.md` | 정책 |
| `CHANGELOG.md` | 릴리스 요약 |
| `Makefile` | **위임 전용.** 실제 명령은 하위 폴더에서 |
| `.gitignore`, `.env.example`, `.env.verify.example` | 저장소 설정 (커밋됨) |
| `.env`, `.agent-role` | 로컬 전용 (git 무시) |
| `docs/`, `scripts/`, `contracts/`, `e2e/` | 횡단 관심사 |
| `.claude/`, `.codex/`, `.agents/`, `.cache/` | 도구 설정·포인터·캐시 |
| `frontend/`, `backend/` | 자체 완결 서브프로젝트 |

## root 에 금지되는 것
| 금지 | 올바른 위치 |
|---|---|
| `pyproject.toml`, `requirements.txt`, `poetry.lock` | `backend/` |
| `package.json`, `package-lock.json`, `node_modules/` | `frontend/` (E2E 는 `e2e/`) |
| `tsconfig.json`, `next.config.*`, `tailwind.config.*`, `postcss.config.*` | `frontend/` |
| `eslint.config.*`, `.eslintrc.*`, `vitest.config.*` | `frontend/` |
| `playwright.config.*` | `e2e/` |
| `conftest.py`, `pytest.ini` | `backend/` |
| `*.db`, `*.sqlite` | `backend/data/` |
| `src/`, `app/`, `components/`, `tests/`, `data/` | 각 서브폴더 안 |
| `*.py` | `backend/` 또는 `scripts/` |
| `*.ts`, `*.tsx` | `frontend/` 또는 `e2e/` |
| `*.sh` | `scripts/` 또는 저장소 밖 |
| `venv/`, `.venv/` | 금지. conda `vscode` 사용 |

## 새 파일 결정 규칙 6단계
1. Python 제품 코드인가 → `backend/`
2. TypeScript/React 제품 코드인가 → `frontend/`
3. 양쪽이 공유하는 계약인가 → `contracts/`
4. 양쪽에 적용되는 지식인가 → `docs/`
5. 검증·유틸 스크립트인가 → `scripts/`
6. **위 어디에도 안 맞으면 → 만들기 전에 사람에게 물어본다**

## 자체 완결
- `cd backend && python -m pytest tests/unit` 가 root 없이 동작해야 한다
- `cd frontend && npm run build` 가 root 없이 동작해야 한다
- root `Makefile` 은 `cd` 후 위임만 한다. root 에서 직접 `pytest`·`npm` 을 부르지 않는다
