"""검사 스크립트 공통 도구 — 표준 라이브러리만.

모든 검사 스크립트는 실패 시 "무엇이 / 어디가 / 어떻게" 를 출력하고 종료 코드 1 을 낸다.
"""
from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rel(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def read(p: Path | str) -> str:
    p = ROOT / p if isinstance(p, str) else p
    return p.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, object]:
    """--- 로 둘러싼 머리말의 아주 작은 YAML 부분집합 (key: value, key: [a, b], 들여쓴 - 목록)."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    data: dict[str, object] = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).split(" #")[0].strip()
            if val.startswith("[") and val.endswith("]"):
                data[key] = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
            elif val == "":
                data[key] = []
            else:
                data[key] = val.strip("\"'")
        elif key and re.match(r"^\s+-\s+", line):
            cur = data.get(key)
            if not isinstance(cur, list):
                cur = []
            cur.append(line.strip()[1:].strip().strip("\"'"))
            data[key] = cur
    return data


def section(text: str, title_part: str) -> str:
    """'## ...title_part...' 제목 아래 본문 (다음 ## 전까지)."""
    lines, out, on = text.splitlines(), [], False
    for ln in lines:
        if ln.startswith("## "):
            if on:
                break
            on = title_part in ln
            continue
        if on:
            out.append(ln)
    return "\n".join(out)


def table(text: str) -> list[list[str]]:
    """마크다운 표의 데이터 행 (머리행·구분행 제외)."""
    rows = []
    for ln in text.splitlines():
        s = ln.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [c.strip() for c in s[1:-1].split("|")]
        rows.append(cells)
    return [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)] if rows else []


def ticks(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def glob_match(path: str, pattern: str) -> bool:
    """fnmatch 의 * 는 / 도 넘는다 → 'a/**' 와 'a/*.md' 를 단순하게 처리."""
    return fnmatch.fnmatch(path, pattern) or (pattern.endswith("/**") and path.startswith(pattern[:-2]))


def make_targets() -> set[str]:
    return set(re.findall(r"^([a-z][a-z0-9-]*):", read("Makefile"), re.M))


def sh(cmd: list[str] | str, cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd or ROOT, shell=isinstance(cmd, str), capture_output=True,
                       text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


class Report:
    def __init__(self, name: str) -> None:
        self.name, self.errors, self.warnings, self.count = name, [], [], 0

    def check(self, cond: bool, msg: str) -> bool:
        self.count += 1
        if not cond:
            self.errors.append(msg)
        return cond

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def finish(self, extra: str = "") -> int:
        for w in self.warnings:
            print(f"⚠️  {w}")
        if self.errors:
            for e in self.errors:
                print(f"❌ {e}")
            print(f"❌ {self.name} 실패 ({len(self.errors)}건 / 검사 {self.count}건)")
            return 1
        print(f"✅ {self.name} 통과 (검사 {self.count}건{', ' + extra if extra else ''})")
        return 0


def exit_with(code: int) -> None:
    sys.exit(code)
