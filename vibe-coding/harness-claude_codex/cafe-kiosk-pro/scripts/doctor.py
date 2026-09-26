"""전체 환경 진단 (사람이 문제 생겼을 때). 실패 시 해결 명령을 알려준다."""
from __future__ import annotations

import os
import re
import shutil
import sys

from _common import ROOT, read, sh

ROLE_VALUES = {"implementer": {"FRONTEND_PORT": "3000", "BACKEND_PORT": "8000", "KIOSK_DB_PATH": "data/kiosk.db"},
               "verifier": {"FRONTEND_PORT": "3100", "BACKEND_PORT": "8100",
                            "KIOSK_DB_PATH": "data/kiosk-verify.db"}}
BANG = ["save", "undof", "back", "backf", "swf", "new", "del", "delf", "drop", "name"]


def env_keys(path: str) -> dict[str, str]:
    out = {}
    for ln in read(path).splitlines():
        m = re.match(r"^([A-Z_]+)=(.*)$", ln.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def main() -> int:
    results: list[tuple[bool, str, str]] = []

    def item(ok: bool, what: str, fix: str) -> None:
        results.append((ok, what, fix))

    role = read(".agent-role").strip() if (ROOT / ".agent-role").exists() else "implementer"
    item(os.environ.get("CONDA_DEFAULT_ENV") == "vscode", "conda 환경 = vscode", "conda activate vscode")
    item("envs/vscode" in sys.executable or os.environ.get("KIOSK_ALLOW_NONCONDA") == "1",
         f"python 경로가 conda 안 ({sys.executable})", "conda activate vscode 후 새 터미널")
    item(sys.version_info >= (3, 11), "Python 3.11+", "conda install python=3.11")
    code, out = sh(["node", "--version"])
    item(code == 0 and int(out.strip().lstrip("v").split(".")[0]) >= 20, "Node 20+", "conda install nodejs=20")
    code, out = sh(["git", "--version"])
    v = re.findall(r"(\d+)\.(\d+)", out)
    item(bool(v) and (int(v[0][0]), int(v[0][1])) >= (2, 30), "git 2.30+", "git 업그레이드")
    item(shutil.which("make") is not None, "make 설치", "OS 패키지로 make 설치")
    example = ".env.verify.example" if role == "verifier" else ".env.example"
    if (ROOT / ".env").exists():
        mine, base = env_keys(".env"), env_keys(example)
        item(set(mine) == set(base), f".env 키 = {example} 키", f"cp {example} .env")
        wrong = [k for k, val in ROLE_VALUES.get(role, {}).items() if mine.get(k) != val]
        item(not wrong, f".env 값이 역할({role})의 포트·DB 와 일치", f"cp {example} .env  (틀린 키: {wrong})")
    else:
        item(False, ".env 존재", f"cp {example} .env")
    code, _ = sh([sys.executable, "-c", "import app, fastapi"], cwd=ROOT / "backend")
    item(code == 0, "backend import 가능", "make setup (사람이 실행)")
    item((ROOT / "frontend/node_modules").is_dir(), "frontend/node_modules 존재", "cd frontend && npm ci")
    code, out = sh(["git", "config", "--get-regexp", r"^alias\."])
    aliases = dict(ln.split(" ", 1) for ln in out.strip().splitlines() if " " in ln)
    aliases = {k.removeprefix("alias."): v for k, v in aliases.items()}
    expected = re.findall(r"git config alias\.([a-z]+) ", read("scripts/git-aliases.sh"))
    missing = [a for a in expected if a not in aliases]
    bad = [a for a in BANG if a in aliases and not aliases[a].startswith("!f()")]
    if "back" in aliases and "${1:-HEAD~1}" not in aliases["back"]:
        bad.append("back(${1:-HEAD~1} 치환됨)")
    item(not missing and not bad and len(expected) == 16,
         f"git 별칭 16개 (누락 {missing}, 손상 {bad})", "make git-aliases")
    code, out = sh(["git", "rev-parse", "--verify", "-q", "main"])
    item(code == 0, "기본 브랜치 main 존재", "git name main")
    gi = read(".gitignore")
    item(all(x in gi for x in (".env", ".agent-role", ".claude/settings.local.json", "backend/data/*.db")),
         ".gitignore 에 .env/.agent-role/settings.local.json/DB 파일", ".gitignore 보강")
    fails = 0
    for ok, what, fix in results:
        print(f"{'✅' if ok else '❌'} {what}" + ("" if ok else f"\n   → 해결: {fix}"))
        fails += not ok
    print("\n참고: docs/environment.md")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
