#!/usr/bin/env bash
# 팀 표준 git 별칭 16개. 여러 번 실행해도 결과가 같다 (멱등).
# 별칭은 .git/config 에 저장되며 커밋되지 않는다. 이 스크립트가 배포 수단이다.
# worktree 는 같은 .git/config 를 공유하므로 검증자 worktree 에도 그대로 적용된다.
# ⚠️ 모든 값은 작은따옴표로 쓴다 (큰따옴표면 셸이 ! 와 ${1:-HEAD~1} 을 먼저 해석한다).
set -euo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || { echo "❌ git 저장소 안에서 실행하세요"; exit 1; }

# ── 조회 ──
git config alias.s 'status --short'
git config alias.l 'log --oneline --graph --decorate --all -20'
git config alias.b 'branch -vv'

# ── 저장 ──
git config alias.save '!f() { git add -A && git commit -m "$1"; }; f'

# ── 되돌리기 (⚠️ 데이터 삭제) ──
git config alias.undo  'reset --hard HEAD'
git config alias.undof '!f() { git reset --hard HEAD && git clean -fd; }; f'
git config alias.back  '!f() { git reset --hard "${1:-HEAD~1}"; }; f'
git config alias.backf '!f() { git reset --hard "${1:-HEAD~1}" && git clean -fd; }; f'

# ── 브랜치 ──
git config alias.name '!f() { git branch -m "$1"; }; f'
git config alias.sw   'switch'
git config alias.mg   'merge'
git config alias.swf  '!f() { git switch "$1" && git clean -fd; }; f'
git config alias.new  '!f() { git switch -c "$1"; }; f'
git config alias.del  '!f() { git branch -d "$1"; }; f'
git config alias.delf '!f() { git branch -D "$1"; }; f'
git config alias.drop '!f() { git switch main && git branch -D "$1"; }; f'

echo "✅ git 별칭 16개 등록 완료"
git config --get-regexp '^alias\.' | sed 's/^alias\./  /'
