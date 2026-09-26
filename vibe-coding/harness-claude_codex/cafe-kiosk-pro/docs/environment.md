---
status: active
owner: human
updated: 2026-09-23
---

> 적용: 환경 문제가 생겼을 때. 새로 합류했을 때. 두 번째 worktree(검증자)를 만들 때.

# 실행 환경

## 필수 환경
| 항목 | 값 | 확인 |
|---|---|---|
| conda 환경 | `vscode` | `echo $CONDA_DEFAULT_ENV` |
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| Git | 2.30+ (worktree) | `git --version` |
| make | GNU make | `make --version` |
| DB | SQLite (Python 표준 `sqlite3`) — 별도 설치 없음 | `python -c "import sqlite3"` |

## 절대 규칙 (CONSTRAINTS C1)
- 모든 명령은 `conda activate vscode` 뒤에 실행한다. 검증자 터미널도 같다.
- `python -m venv`, `virtualenv` 를 쓰지 않는다. 시스템 Python(`/usr/bin/python`)을 쓰지 않는다.
- 모든 `make` 타깃은 `env-check` 를 먼저 통과해야 실행된다.

## 설정 파일 `.env` — 역할마다 다르다
| 역할 | 복사 원본 | 커밋 |
|---|---|---|
| 구현자 | `.env.example` | 원본만 커밋 |
| 검증자 | `.env.verify.example` | 원본만 커밋 |

`.env` 는 커밋하지 않는다 (CONSTRAINTS C4). 키 집합이 원본과 같아야 한다 (`make doctor`).

## 포트·DB 할당 ⭐
| 역할 | frontend | backend | DB 파일 (`backend/` 기준) |
|---|---:|---:|---|
| 구현자 | 3000 | 8000 | `data/kiosk.db` |
| 검증자 | 3100 | 8100 | `data/kiosk-verify.db` |

검증자는 **다른 폴더(worktree)·다른 포트·다른 DB 파일**을 쓴다. 검증 중에 구현자가 데이터를 바꿔도 검증 결과가 흔들리지 않는다.

## 공유 conda 환경에서 두 worktree 를 쓸 때
- `pip install -e ./backend` 는 **구현자 폴더에서 한 번만**. 검증자 worktree 에서 다시 설치하지 않는다.
- 테스트는 `backend/pyproject.toml` 의 `pythonpath = ["."]` 덕분에 **현재 worktree 의 `app/`** 을 읽는다.
- `frontend/node_modules` 는 worktree 마다 따로 설치한다 (`cd frontend && npm ci`).

## 환경 불일치 증상과 대응
| 증상 | 원인 | 해결 |
|---|---|---|
| `make` 가 "conda 환경이 vscode 가 아닙니다" | 활성화 안 함 | `conda activate vscode` |
| `ModuleNotFoundError: app` | backend 미설치 | `make setup` (사람이) |
| 검증자 테스트가 구현자 DB 를 읽음 | `.env` 복사 누락 | 검증 worktree 에서 `cp .env.verify.example .env` |
| git 별칭이 안 됨 | 등록 안 함 | `make git-aliases` |
| `next/font` 다운로드 실패 | 사내 프록시 | 이 저장소는 시스템 폰트만 쓴다. 외부 폰트 추가 금지 |

## 비대화형 실행
`make check`, `make test-affected` 는 입력을 요구하지 않는다. 사람 승인이 필요한 명령(`make fixture-capture`, `make setup`)은 에이전트가 실행하지 않는다.
