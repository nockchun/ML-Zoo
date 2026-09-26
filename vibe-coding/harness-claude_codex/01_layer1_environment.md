# 환경 구성

## 기본 구조 및 git 설정

##### 1. git환경, 기본 폴더, 파일 구조 생성
```bash
mkdir -p ~/lab/cafe-kiosk-pro && cd ~/lab/cafe-kiosk-pro
git init -b main
git config user.name "실습자" && git config user.email "lab@example.com"
mkdir -p backend/{data,tests} contracts .claude .agents .codex docs/{architecture,rules} scripts e2e
find . -type d -empty -not -path './.git*' -exec touch {}/.gitkeep \;
touch README.md  CLAUDE.md  AGENTS.md  CONSTRAINTS.md  BOOTSTRAP.md  Makefile
```


##### 2. scripts/git-aliases.sh 생성 및 실행
cafe-kiosk-pro/scripts/git-aliases.sh 파일을 복사해서 자신의 프로젝트에 넣은후 실행.
```bash
chmod +x scripts/git-aliases.sh
scripts/git-aliases.sh
git config --get-regexp '^alias\.'
```


##### 3. 기본 환경 변수 생성

Claude 프롬프트로 할 경우.
```prompt
저장소 root 에 아래 세 파일을 만들어줘. 다른 파일은 만들지 마.

1. .gitignore
   - node_modules/, venv/, .venv/ (conda vscode 만 쓴다)
   - __pycache__/, *.pyc, .pytest_cache/, .ruff_cache/, *.egg-info/
   - frontend/.next/, frontend/out/, e2e/test-results/
   - backend/data/*.db, backend/data/*.db-*   (SQLite 파일은 worktree 마다 다름)
   - .env, .cache/, .agent-role, .claude/settings.local.json
   - .DS_Store, *.orig, *.rej, *.bak
   각 묶음 위에 한 줄 주석으로 이유를 적어.

2. .env.example  (구현자용, 커밋함)
   FRONTEND_PORT=3000 / BACKEND_PORT=8000 / KIOSK_DB_PATH=data/kiosk.db / ADMIN_TOKEN=local-admin-token-change-me
   맨 위 주석: "이 파일만 커밋한다. 실제 .env 는 커밋하지 않는다"

3. .env.verify.example  (검증자용, 커밋함)
   3100 / 8100 / data/kiosk-verify.db / 같은 ADMIN_TOKEN
```

```bash
cp .env.example .env
git check-ignore -v .env backend/data/kiosk.db # 둘 다 무시되는지 확인.
```


##### 4. environment.md
Claude 프롬프트로 할 경우.
```prompt
docs/environment.md 를 만들어줘. 코드는 건드리지 마.

[frontmatter]
---
status: active
owner: human
updated: 오늘 날짜(YYYY-MM-DD)
---
그 다음 줄: "> 적용: 환경 문제가 생겼을 때. 새로 합류했을 때. 두 번째 worktree(검증자)를 만들 때."

[섹션 — 이 제목 그대로, 이 순서로]
# 실행 환경
## 필수 환경          — 표: 항목 / 값 / 확인 (conda vscode, Python 3.11+, Node 20+, Git 2.30+, make, SQLite=표준 sqlite3)
## 절대 규칙 (CONSTRAINTS C1)  — conda vscode 뒤에 실행 / venv·시스템 Python 금지 / 모든 make 는 env-check 를 먼저
## 설정 파일 `.env` — 역할마다 다르다   — 표: 역할 / 복사 원본 / 커밋
## 포트·DB 할당 ⭐     — 표: 역할 / frontend / backend / DB 파일 (구현자 3000/8000/data/kiosk.db, 검증자 3100/8100/data/kiosk-verify.db)
## 공유 conda 환경에서 두 worktree 를 쓸 때  — pip install -e 는 구현자 폴더에서 한 번만 / pytest 의 pythonpath 로 현재 worktree 를 읽음 / node_modules 는 worktree 마다
## 환경 불일치 증상과 대응  — 표: 증상 / 원인 / 해결 (5행)
## 비대화형 실행        — 사람 승인이 필요한 명령은 에이전트가 실행하지 않는다

[제약] 지금 알 수 없는 내용을 지어내지 마. 60줄 이내.
```



---
## frontend, backend 분리 모노레포 구조 생성

backend 기본 코드 생성 프롬프트
```prompt
backend/ 를 자체 완결 FastAPI 프로젝트로 만들어 주세요. root 에는 아무 파일도 만들지 말아 주세요.

1. backend/pyproject.toml
   - dependencies: fastapi, uvicorn[standard], pydantic>=2
   - optional dev: pytest, httpx, ruff, pyyaml
   - setuptools packages.find: include app*, exclude migrations* tests*
   - ruff: line-length 100, py311, lint select E F W I B UP S608 (S608 = 문자열 SQL 금지)
   - pytest: testpaths=["tests"], pythonpath=["."]  (주석: 검증자 worktree 와 conda 를 공유하므로 현재 폴더의 app/ 을 읽게)
2. backend/app/__init__.py (한 줄 docstring)
3. backend/app/api/health.py — GET /health → {"status": "ok"}, Pydantic 응답 모델 Health
4. backend/app/main.py — FastAPI 앱, health 라우터 등록
DB 연결·메뉴는 아직 만들지 말아 주세요..
```

backend 테스트
```bash
conda activate vscode
cd ~/lab/cafe-kiosk-pro/backend
pip install -e ".[dev]"
uvicorn app.main:app --port 8000
curl -s localhost:8000/health # {"status":"ok"}
```

frontend 기본 코드 생성 명령어
- `--no-agents-md`: 최신 create-next-app 은 기본으로 `AGENTS.md`·`CLAUDE.md` 를 만듭니다. 이 저장소는 3·4부에서 **우리 라우팅 구조로** 직접 씁니다.
- `@types/node@^22`: vitest 가 요구하는 버전입니다. 기본 `^20` 이면 설치 충돌이 납니다.
```bash
cd ~/lab/cafe-kiosk-pro
mkdir frontend && cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-npm --no-react-compiler --no-agents-md --yes
npm install -D vitest @types/node@^22
npm pkg set scripts.test="vitest run" scripts.typecheck="tsc --noEmit"
```

사내 환경에서 멈추지 않게 두 가지를 고치는 프롬프트(옵션)
```prompt
frontend/ 에서 두 가지만 고쳐줘.
1. src/app/layout.tsx 에서 next/font/google 을 제거하고 lang="ko", title "녹천 카페 키오스크".
   (사내 프록시에서 빌드 중 폰트 다운로드가 멈추는 것을 막기 위해. 폰트는 시스템 스택으로 나중에 토큰에서 지정)
2. next.config.ts 에 rewrites: /api/:path* → http://localhost:${BACKEND_PORT ?? 8000}/:path*
   (frontend 는 backend 를 /api/* 로만 부른다)
root 에는 아무것도 만들지 마.
```

첫 커밋과 하네스 태그
```bash
git b # main 인지 확인
git save "feat(CK-001): 환경 구성, 팀 git 별칭, 모노레포 스캐폴드"
git tag -a harness-v0 -m "1층: 환경과 스캐폴드"
```

harness 핵심 질문 테스트
```prompt
/clear
```
```prompt
이 저장소에서 지금 내가 이어서 해야 할 일이 뭐야?
```



---
## 검증 골격과 불변 제약

`Makefile` — **직접 손으로** 씁니다.

Makefile을 복사하여 자신의 프로젝트에 넣어 줍니다. 그리고 env-check 검사 수행.

```bash
conda deactivate; make env-check      # ❌ 실패해야 함
conda activate vscode; make env-check # ✅ (출력 없음 = 통과)
make help
```

### 환경 진단 — make doctor
_common.py 공통 스크립트 생성.
```prompt
scripts/_common.py 를 만들어 주세요. scripts/ 의 검사 스크립트들이 `python scripts/<이름>.py` 로 실행되며
`from _common import ...` 로 가져다 쓰는 공통 도구입니다.

## 규칙
- 표준 라이브러리만. `from __future__ import annotations`, 모든 함수에 타입 힌트
- 한 줄 120자 이내. 포매터·린터는 돌리지 않는다
- 아래 목록만 만든다 (보조 함수·구획 주석·추가 옵션 없음)
- 예외: 파싱 함수(frontmatter·section·table·ticks)는 형식이 안 맞으면 빈 값({}, [], "")을 돌려준다.
  read·rel·sh 의 예외는 그대로 올린다. try/except 는 쓰지 않는다
- 한 줄 docstring 은 frontmatter·section·table·glob_match 에만
- 모듈 docstring (두 문단):
    검사 스크립트 공통 도구 — 표준 라이브러리만.
    (빈 줄)
    모든 검사 스크립트는 실패 시 "무엇이 / 어디가 / 어떻게" 를 출력하고 종료 코드 1 을 낸다.

## 목록
- ROOT = Path(__file__).resolve().parents[1]
- rel(p: Path) -> str — resolve 한 p 의 ROOT 기준 상대 경로 (posix)
- read(p: Path | str) -> str — str 이면 ROOT 기준. utf-8
- frontmatter(text) -> dict[str, object] — 아래
- section(text, title_part) -> str — title_part 가 든 첫 `## ` 줄의 다음 줄부터 다음 `## ` 줄 전까지를 "\n" 으로 이은 것
- table(text) -> list[list[str]] — strip 해서 `|` 로 시작·끝나는 줄을 셀(strip) 목록으로 모은다.
  전체의 첫 행과, 모든 셀이 `-`·`:`·공백으로만 된 행(빈 셀 포함)은 뺀다
- ticks(cell) -> list[str] — re.findall(r"`([^`]+)`", cell)
- glob_match(path, pattern) -> bool — fnmatch 가 맞거나, pattern 이 `/**` 로 끝나고 path 가 pattern[:-2] 로 시작
- make_targets() -> set[str] — Makefile 에서 re.M 으로 `^([a-z][a-z0-9-]*):`
- sh(cmd: list[str] | str, cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]
  — str 이면 shell=True. cwd 기본 ROOT. (종료 코드, stdout + stderr)
- class Report(name) — 속성 name, errors, warnings, count
  - check(cond, msg) -> bool: count+1, 거짓이면 errors 에 msg 추가, cond 반환
  - warn(msg): warnings 에 추가
  - finish(extra="") -> int: 경고마다 `⚠️  {w}` (공백 두 칸) 를 먼저 찍고
    - errors 가 있으면 `❌ {e}` 를 하나씩, 이어서 `❌ {name} 실패 ({N}건 / 검사 {count}건)` → 1
    - 없으면 `✅ {name} 통과 (검사 {count}건)` → 0. extra 가 있으면 괄호 안 끝에 `, {extra}`
- exit_with(code: int) -> None — sys.exit(code)

## frontmatter (작은 YAML 부분집합)
- "---\n" 으로 시작하고 뒤에 "\n---" 로 닫혀야 한다. 아니면 {}
- 그 사이 줄 중 빈 줄과 (들여쓰기를 무시하고) `#` 로 시작하는 줄은 건너뛴다
- `^([A-Za-z_][\w-]*):\s*(.*)$` 는 키 줄. 값은 " #" 앞까지 자르고 strip 한 뒤
  - `[a, b]` → 쉼표로 나누고, 공백뿐인 항목은 빼고, 각각 strip 후 따옴표(" ')를 벗긴 list
  - 빈 값 → []
  - 그 외 → 따옴표를 벗긴 str
- 들여쓴 `- 항목` 줄 → 직전 키의 값이 list 면 이어 붙이고, 아니면 새 list 로 바꾼다.
  항목은 따옴표만 벗긴다 (주석은 남는다). 앞에 키가 없으면 무시
```

doctor.py 스크립트 생성 : 개발 환경 진단
```prompt
scripts/doctor.py 를 만들어 주세요. 문제가 생겼을 때 사람이 `make doctor` 로 돌리는 개발 환경 진단입니다 (목표 5초).

## 규칙
- _common.py 와 같은 스타일 (`from __future__ import annotations`, 타입 힌트, 120자, 포매터 없음)
- 모듈 docstring: "전체 환경 진단 (사람이 문제 생겼을 때). 실패 시 해결 명령을 알려준다."
- import 는 os, re, shutil, sys 와 `from _common import ROOT, read, sh` 만
- 외부 명령은 모두 리스트로 sh 에 넘기고 감싸지 않는다 (try·timeout 없음)
- 뼈대: 상수 ROLE_VALUES·BANG / env_keys(path) -> dict[str, str] /
  main() -> int 안의 item(ok, what, fix) 가 결과 목록에 쌓는다 /
  `if __name__ == "__main__": raise SystemExit(main())`
- 아래에 없는 검사·출력·방어 코드는 넣지 않는다

## 역할과 .env
- 역할 = `.agent-role` 내용(strip). 파일이 없으면 implementer. 역할 값 자체는 검사하지 않는다
- 원본 = 역할이 verifier 면 .env.verify.example, 아니면 .env.example
- env_keys: 줄마다 strip 한 뒤 `^([A-Z_]+)=(.*)$` 에 맞으면 {키: 값}
- ROLE_VALUES (여기 없는 역할은 값 검사 통과)

| 역할 | FRONTEND_PORT | BACKEND_PORT | KIOSK_DB_PATH |
|---|---|---|---|
| implementer | 3000 | 8000 | data/kiosk.db |
| verifier | 3100 | 8100 | data/kiosk-verify.db |

## 검사 (이 순서로. {원본} 은 원본 파일, 목록은 파이썬 list 그대로 출력)
| # | 항목 (출력 문구) | 통과 조건 | 해결 |
|---|---|---|---|
| 1 | conda 환경 = vscode | CONDA_DEFAULT_ENV == "vscode" | conda activate vscode |
| 2 | python 경로가 conda 안 ({sys.executable}) | "envs/vscode" in sys.executable 또는 KIOSK_ALLOW_NONCONDA == "1" | conda activate vscode 후 새 터미널 |
| 3 | Python 3.11+ | sys.version_info >= (3, 11) | conda install python=3.11 |
| 4 | Node 20+ | `node --version` 종료 코드 0 이고, 출력에서 v 를 뗀 주 버전 ≥ 20 | conda install nodejs=20 |
| 5 | git 2.30+ | `git --version` 출력의 첫 `숫자.숫자` ≥ (2, 30) | git 업그레이드 |
| 6 | make 설치 | shutil.which("make") | OS 패키지로 make 설치 |
| 7 | .env 키 = {원본} 키 | 키 집합이 같음 | cp {원본} .env |
| 8 | .env 값이 역할({role})의 포트·DB 와 일치 | ROLE_VALUES[역할] 의 키마다 .env 값이 같음 | cp {원본} .env  (틀린 키: {틀린 키 목록}) |
| 9 | backend import 가능 | cwd=backend 에서 `[sys.executable, "-c", "import app, fastapi"]` 종료 코드 0 | make setup (사람이 실행) |
| 10 | frontend/node_modules 존재 | 디렉터리 있음 | cd frontend && npm ci |
| 11 | git 별칭 16개 (누락 {missing}, 손상 {bad}) | 아래 | make git-aliases |
| 12 | 기본 브랜치 main 존재 | `git rev-parse --verify -q main` 종료 코드 0 | git name main |
| 13 | .gitignore 에 .env/.agent-role/settings.local.json/DB 파일 | .env, .agent-role, .claude/settings.local.json, backend/data/*.db 가 모두 .gitignore 내용의 부분 문자열 | .gitignore 보강 |

- .env 가 없으면 7·8 대신 `.env 존재` 실패 하나만 (해결: cp {원본} .env)
- 11 git 별칭
  - expected: scripts/git-aliases.sh 에서 `git config alias\.([a-z]+) ` 로 뽑은 이름
  - 등록: `git config --get-regexp ^alias\.` 의 각 줄을 첫 공백에서 나눠 {이름("alias." 제거): 값}. 공백 없는 줄은 무시
  - missing: expected 중 등록 안 된 것
  - bad: BANG(save, undof, back, backf, swf, new, del, delf, drop, name) 중 등록됐는데 값이 "!f()" 로 시작하지 않는 것.
    back 이 등록됐고 값에 "${1:-HEAD~1}" 가 없으면 "back(${1:-HEAD~1} 치환됨)" 추가
  - 통과: missing·bad 가 비었고 len(expected) == 16

## 출력
결과마다 "✅ {항목}" 또는 "❌ {항목}" 을 찍고, ❌ 면 다음 줄에 "   → 해결: {해결}" (공백 세 칸).
마지막에 빈 줄 하나와 "참고: docs/environment.md". 하나라도 ❌ 면 종료 코드 1, 아니면 0.
```

monorepo 규칙 문서 만들기.
```prompt
docs/architecture/monorepo-rules.md 를 만들어 주세요. 아래에 없는 내용은 추가하지 않는다.

[frontmatter]
status: active
owner: human
updated: 오늘

[적용 줄]
> 적용: 새 파일을 만들기 전에 항상. 빌드 설정을 바꿀 때.

[섹션] 제목은 아래 그대로 쓴다

# 모노레포 경계 규칙 (Root Purity)

## 원칙
- root 는 **오케스트레이션 레이어**
- 소스와 언어별 설정은 frontend/, backend/, e2e/ 안에만

## root 에 허용되는 것
- 형식: 표 (항목 | 목적). 아래 한 줄이 표 한 행
- 표 위 한 줄: "scripts/root_purity_audit.py 의 허용 목록은 이 표와 일치해야 한다"
- 항목 → 목적:
  - README.md → 사람용 진입점
  - CLAUDE.md, AGENTS.md, CONSTRAINTS.md, BOOTSTRAP.md → 정책
  - CHANGELOG.md → 릴리스 요약
  - Makefile → **위임 전용.** 실제 명령은 하위 폴더에서
  - .gitignore, .env.example, .env.verify.example → 저장소 설정 (커밋됨)
  - .env, .agent-role → 로컬 전용 (git 무시)
  - docs/, scripts/, contracts/, e2e/ → 횡단 관심사
  - .claude/, .codex/, .agents/, .cache/ → 도구 설정·포인터·캐시
  - frontend/, backend/ → 자체 완결 서브프로젝트

## root 에 금지되는 것
- 형식: 표 (금지 | 올바른 위치). 아래 한 줄이 표 한 행
- 금지 → 올바른 위치:
  - pyproject.toml, requirements.txt, poetry.lock → backend/
  - package.json, package-lock.json, node_modules/ → frontend/ (E2E 는 e2e/)
  - tsconfig.json, next.config.*, tailwind.config.*, postcss.config.* → frontend/
  - eslint.config.*, .eslintrc.*, vitest.config.* → frontend/
  - playwright.config.* → e2e/
  - conftest.py, pytest.ini → backend/
  - *.db, *.sqlite → backend/data/
  - src/, app/, components/, tests/, data/ → 각 서브폴더 안
  - *.py → backend/ 또는 scripts/
  - *.ts, *.tsx → frontend/ 또는 e2e/
  - *.sh → scripts/ 또는 저장소 밖
  - venv/, .venv/ → 금지. conda vscode 사용

## 새 파일 결정 규칙 6단계
- 형식: 번호 목록, "…인가 → 위치"
  1. Python 제품 코드 → backend/
  2. TypeScript/React 제품 코드 → frontend/
  3. 양쪽이 공유하는 계약 → contracts/
  4. 양쪽에 적용되는 지식 → docs/
  5. 검증·유틸 스크립트 → scripts/
  6. **위 어디에도 안 맞으면 → 만들기 전에 사람에게 물어본다**

## 자체 완결
- root 없이 동작해야 한다:
  - cd backend && python -m pytest tests/unit
  - cd frontend && npm run build
- root Makefile 은 cd 후 위임만. root 에서 직접 pytest·npm 을 부르지 않는다
```

monorepo 감사 스크립트.
```prompt
scripts/root_purity_audit.py 를 만들어줘. _common.py 의 Report 를 쓴다.

[검사]
1. root(maxdepth 1)의 파일·폴더가 monorepo-rules.md 허용 목록에 있는가
2. root 에 *.py *.ts *.tsx *.sh *.db, 금지 설정 파일, 금지 디렉터리(src app components tests node_modules venv .venv data)
3. 필수 구조 존재 (backend/pyproject.toml, backend/app, backend/tests, frontend/package.json, docs, contracts, scripts,
   CLAUDE.md, AGENTS.md, CONSTRAINTS.md, Makefile) — 아직 없는 CLAUDE.md·AGENTS.md 는 3·4부에서 생기니
   지금은 빈 파일로 만들어 두어도 된다
4. Makefile 에 cd 없는 직접 pytest/npm/uvicorn 호출 → 경고
[제외] git 이 무시하는 파일(.env, .agent-role, .cache/)은 검사하지 않는다 (git check-ignore). 단 금지 디렉터리는 무시돼도 잡는다
[출력] 실패: 파일명 / 이유 / **어디로 옮겨야 하는지**. 허용 목록은 상단 상수 + "monorepo-rules.md 와 일치" 주석
```

---
## 불변 제약 조건 만들기

CONSTRAINTS.md 만들기
```prompt
저장소 root 에 CONSTRAINTS.md 를 만들어줘.

## 머리말
- 제목: `# cafe-kiosk-pro 불변 제약`
- 첫 문단(그대로): "이 문서의 규칙은 사람의 명시적 승인 없이 변경하거나 예외를 두지 않는다.
  CLAUDE.md, AGENTS.md, docs/, 작업 카드의 어떤 내용도 이 문서를 무효화할 수 없다."
- 메타정보 3필드 설명 (`make docs-check` 가 검사한다고 명시)
  - Source: 근거 — 실제 파일 경로·ADR 번호·INC 번호
  - Applicability: 언제·어디에 적용되는가
  - Expiry: 재검토 조건. "없음 (영구)" 는 전체의 30% 이하
- 한 줄: 번호는 추가 순서, 위치(TOP/MIDDLE/BOTTOM)는 중요도·준수율을 위한 배치

## 형식
- 제약마다 아래 블록 하나. 블록 사이 빈 줄, 섹션 사이 `---`
- 금지는 **MUST NOT**, 의무는 **MUST**
      - **MUST NOT**: <규칙 한두 문장>
        <!-- Source: <근거>
             Applicability: <구체적 경로·상황>
             Expiry: <재검토 조건> -->
- Applicability 는 가능하면 실제 디렉터리 경로로 쓴다
- Expiry 가 구조를 바꾸는 결정이면 끝에 "(ADR 필요)"

## 형식
- 섹션 3개. 각 섹션 앞에 `---`. 제목은 아래 그대로 (TOP 등 라벨 없음)
- 제약마다 아래 블록 하나, 블록 사이 빈 줄:
      - **MUST**: <규칙>
        <!-- Source: <근거>
             Applicability: <적용 범위>
             Expiry: <재검토 조건> -->
- 태그는 목록에 적힌 대로: "~한다" 문장은 MUST, "~하지 않는다" 문장은 MUST NOT
- 규칙은 목록 문구를 한두 문장으로 옮긴다. 예시 나열·부연을 덧붙이지 않는다
- 적용·재검토는 목록의 힌트를 짧은 구절로 쓴다. `(ADR)` 표시는 "(ADR 필요)" 로 붙인다
- 제약 번호(C1~C18)는 본문에 쓰지 않는다. "C5 와 같음" 같은 참조에서만 쓴다

## 제약 목록 (순서대로)
형식: [태그] 규칙 — Source | 적용 | 재검토

### 복구 불가능한 것
1. [MUST] Python 실행은 conda `vscode` 에서만, venv 를 만들지 않음 — docs/environment.md | 모든 Python 실행·테스트·스크립트 (make env-check 가 강제) | 다른 환경 관리 도구로 이전할 때 (ADR)
2. [MUST NOT] root 에 소스·언어별 설정 파일 — docs/architecture/monorepo-rules.md | 새 파일 생성 시 항상 (make root-purity 가 강제) | 모노레포 구조 폐기 (ADR)
3. [MUST] DB 파괴적 변경(테이블·컬럼 삭제, 데이터 일괄 수정)은 사람의 명시적 승인 후에만 — docs/rules/migrations.md | backend/migrations/, 직접 SQL | 없음 (영구)
4. [MUST NOT] 비밀값을 추적 파일에, `.env.example`·`.env.verify.example` 만 커밋 — docs/environment.md | 모든 커밋 | 없음 (영구)

### 계층과 경계
5. [MUST NOT] frontend 가 backend 의 Python 파일·DB·내부 모듈에 접근 — docs/architecture/system.md | frontend/ 아래 모든 코드 | 두 앱을 한 서버로 합칠 때 (ADR)
6. [MUST NOT] backend 가 Next.js 컴포넌트·Tailwind 코드를 앎 — docs/architecture/system.md | backend/ 아래 모든 코드 | C5 와 같음
7. [MUST] 두 앱의 공유는 `contracts/`·`docs/api/` 뿐 — docs/architecture/system.md | 새 공유 지점을 만들 때 | C5 와 같음
8. [MUST] 가격·옵션 가격·할인·재고·품절 판단은 **backend 서비스 계층 한 곳에서만**(강조 유지). 둘째 줄: frontend 는 "backend 가 계산한 금액을" 표시만(이 목적어 생략 금지), 클라이언트 금액 불신 — docs/architecture/backend.md | 금액·할인·재고 판단이 들어가는 모든 코드 | 가격 계산을 별도 서비스로 분리 (ADR)
9. [MUST] 금액은 정수(원)로 저장·계산·전송, 소수점·문자열 금지 — docs/product/product-spec.md | DB 컬럼, API 응답, 도메인 함수 | 다통화 결제 지원 (ADR)

### 보안·운영·문서
10. [MUST] SQL 은 `?` 바인딩으로만, 문자열 결합·f-string 금지 — docs/security/threat-model.md | backend/app/repositories/ 및 모든 쿼리 | 없음 (영구)
11. [MUST NOT] 에러 응답에 내부 예외 메시지·스택·쿼리·파일 경로 노출 — docs/security/threat-model.md | 모든 에러 응답 | 없음 (영구)
12. [MUST] 패키지 설치·대규모 의존성 교체·프레임워크 변경은 사람 승인 후, 교체는 ADR 필수, make 타깃 이름 유지 — docs/environment.md | backend/pyproject.toml, frontend/package.json, Makefile 변경 | 의존성 자동 갱신 도구와 검증 파이프라인 도입
13. [MUST NOT] 검증자가 추적 파일 수정, 보고서는 `docs/reviews/active/` 에만 — docs/governance/agent-role-contract.md | 검증 worktree 의 모든 작업 | 검증을 자동 파이프라인으로 완전 대체
14. [MUST NOT] `docs/generated/` 직접 수정, 생성 스크립트 재실행 — docs/rules/docs-lifecycle.md | docs/generated/ 아래, frontend/src/lib/api-types.generated.ts | 생성 문서 폐지
15. [MUST NOT] 완료 카드를 `docs/work/active/` 에 남김 — docs/rules/docs-lifecycle.md | 작업 종료 시 | 외부 이슈 트래커로 이전 (ADR)
16. [MUST NOT] `docs/handoffs/CURRENT.md` 에 이력 누적, 교체한다 — docs/playbooks/clock-out.md | 세션 종료·작업 전환·동결 시 | 인계를 외부 시스템으로 이전 (ADR)
17. [MUST NOT] `contracts/fixtures/` 를 코드에 맞춰 수정, 픽스처 변경은 사람의 결정 — contracts/fixtures/README.md | 테스트 실패 시, 픽스처를 만들거나 바꿀 때 | 계약 브로커 등 계약 테스트 도구로 전환 (ADR)
18. [MUST] 재고 변경은 조건부 한 문장(`UPDATE … SET stock = stock - ? WHERE id = ? AND stock >= ?`)으로만, 읽고-판단-쓰기 분리 금지 — docs/incidents/2026/INC-0001-stock-race.md | 재고·수량이 줄어드는 모든 쓰기 (backend/app/repositories/) | 외부 재고 시스템으로 이전 (ADR)

## 지킬 것
- Source 파일이 아직 없어도 경로는 그대로 적는다
- 영구는 3·4·10·11 네 개뿐
```

커밋
```bash
make env-check && make doctor && make root-purity
git save "feat: 검증 명령 이름, 환경 진단, Root Purity, 불변 제약"
git tag -a harness-v1 -m "1층: 검증 골격과 불변 제약"
```
