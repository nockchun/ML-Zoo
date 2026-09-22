# Repogitory 안전망 구성: Git

## 별칭 등록
```bash
# ── 조회 ──
git config -g alias.s 'status --short'
git config -g alias.l 'log --oneline --graph --decorate --all -20'
git config -g alias.b 'branch -vv'

# ── 저장 ──
git config -g alias.save '!f() { git add -A && git commit -m "$1"; }; f'

# ── 되돌리기 (⚠️ 데이터 삭제) ──
git config -g alias.undo 'reset --hard HEAD'
git config -g alias.undof '!f() { git reset --hard HEAD && git clean -fd; }; f'
git config -g alias.back  '!f() { git reset --hard "${1:-HEAD~1}"; }; f'
git config -g alias.backf '!f() { git reset --hard "${1:-HEAD~1}" && git clean -fd; }; f'

# ── 브랜치 ──
git config -g alias.name '!f() { git branch -m "$1"; }; f'
git config -g alias.sw 'switch'
git config -g alias.mg 'merge'
git config -g alias.swf '!f() { git switch "$1" && git clean -fd; }; f'
git config -g alias.new '!f() { git switch -c "$1"; }; f'
git config -g alias.del '!f() { git branch -d "$1"; }; f'
git config -g alias.delf '!f() { git branch -D "$1"; }; f'
git config -g alias.drop '!f() { git switch main && git branch -D "$1"; }; f'
```

## Usage
```bash
git sts                    # 뭐가 바뀌었나
git save "feat: 파서 추가"   # 수정된 모든 내용을 전부 담아서 커밋
git log                    # 히스토리 보기
git undo                   # 커밋 안 한 변경 전부 버리기. 현재 새로만든 것들은 유지.
git undof                  # 커밋 안 한 변경 전부와 현재 새로만든 것들까지 모두 버리기
git back                   # 마지막 커밋 취소하고 그 전으로. 현재 새로만든 것들은 유지.
git backf                  # 마지막 커밋 취소하고 그 전으로. 새로만든 것들은 모두 버리기

```

---
## undo, back 실습 가이드

### 1. 실습 폴더 생성
1단계: 실습용 저장소 및 베이스 커밋(v1) 만들기
테스트 환경을 구축하고 돌아갈 **목표 커밋(v1)**을 만듭니다.
```bash
mkdir ~/workspace/cafe-kiosk
cd ~/workspace/cafe-kiosk

git init
git config user.name "실습자"
git config user.email "lab@example.com"
```

### 2. gitignore 만들기
추적하지 않기를 원하는 내용의 규칙 만들기
```bash
cat > .gitignore <<'EOF'
node_modules/
.DS_Store
/tmp/
*.log
EOF

git add .
git commit -m "base: 초기 repository 샐성"
```

### 3. 별칭 등록
```bash
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
```

### 4. 첫 번째 커밋 생성
```bash
echo "원본 파일 1 내용" > file1.txt
echo "원본 파일 2 내용 (나중에 삭제)" > file2.txt

git add .
git commit -m "v1: 기준 커밋 (file1, file2 생성)"
```

### 5. 파일 수정·삭제·추가
```bash
echo "file1 엉망으로 수정됨" >> file1.txt
rm file2.txt
echo "새로 생성된 커밋 파일 3" > file3.txt

git add .
git commit -m "v2: file1 수정, file2 삭제, file3 커밋"
```

### 6. 커밋하지 않은 임시 파일 및 폴더 생성 (Untracked 파일/폴더)
```bash
echo "add 안 한 임시 파일" > untracked.txt
mkdir temp_dir
echo "임시 폴더 내부 파일" > temp_dir/temp.txt
echo "임시 폴더 내부 tracked file" > temp_dir/tracked.txt
git add temp_dir/tracked.txt
```

### 7. 현재 상태 확인
```bash
git s
git l
```

### 8. 마지막 커밋한 상태로 이동(최종 커밋 이후 vibe coding이 마음에 들지 않을때)
untracked file 은 삭제 되지 않음을 확인 후, undof로 완벽한 undo가 되는 것을 확인.
```bash
git undo
git undof
```

### 9. 커밋하지 않은 임시 파일 및 폴더 생성 (Untracked 파일/폴더)
```bash
echo "add 안 한 임시 파일" > untracked.txt
mkdir temp_dir
echo "임시 폴더 내부 파일" > temp_dir/temp.txt
echo "임시 폴더 내부 tracked file" > temp_dir/tracked.txt
git add temp_dir/tracked.txt
```

### 10. 이전 상태로 돌아간다
```bash
git back
git clean -fd
```

### 11. 파일 수정·삭제·추가
```bash
echo "file1 엉망으로 수정됨" >> file1.txt
rm file2.txt
echo "새로 생성된 커밋 파일 3" > file3.txt

git add .
git commit -m "v2: file1 수정, file2 삭제, file3 커밋"
```

### 12. 커밋하지 않은 임시 파일 및 폴더 생성 (Untracked 파일/폴더)
```bash
echo "add 안 한 임시 파일" > untracked.txt
mkdir temp_dir
echo "임시 폴더 내부 파일" > temp_dir/temp.txt
echo "임시 폴더 내부 tracked file" > temp_dir/tracked.txt
git add temp_dir/tracked.txt
```

### 13. 이전 상태로 완벽하게 돌아간다.
```bash
git backf
```

---
## brench 실습 가이드

### 1. 첫 번째 브랜치 생성
```bash
git new feature/menu
git b
git l
```

### 2. 브랜치 삭제
```bash
git sw main
git del feature/menu
git b
git l
```

### 3. 첫 번째 브랜치 생성
```bash
git new feature/menu
```

### 4. 브랜치에서 개발(1차 커밋)
```bash
echo '아메리카노 2000\n카페라떼 3000\n' > menu.txt
git save "feat(menu): 기본 메뉴 2종 추가"

echo "카푸치노 3500" >> menu.txt
git save "feat(menu): 카푸치노 추가"

git l
```

### 5. merge되지 않은 첫 번째 브랜치 개발내용 삭제
```bash
git sw main
git delf feature/menu
```

### 6. 첫 번째 브랜치 생성
```bash
git new feature/menu
```

### 7. 첫 번째 브랜치에서 개발
```bash
echo '아메리카노 2000\n카페라떼 3000\n' > menu.txt
git save "feat(menu): 기본 메뉴 2종 추가"

echo "카푸치노 3500" >> menu.txt
git save "feat(menu): 카푸치노 추가"

git l
```

### 8. 두 번째 브랜치 생성
```bash
git sw main
git new feature/receipt
```

### 9. 두 번째 브랜치에서 개발
```bash
echo '=== 영수증 ===\n합계: 0원\n' > receipt.txt
git save "feat(receipt): 영수증 템플릿 추가"

echo "결제수단: 카드" >> receipt.txt
git save "feat(receipt): 결제수단 표시"

git l
```

### 10. 브랜치 오가기
브랜치를 오가면서 파일의 변경을 확인 하세요.
```bash
git sw feature/menu
git sw feature/receipt

git l
```

### 11. feature/menu 브랜치에서 개발 작업하기
```bash
git sw feature/menu

echo "메뉴 관련 메모, 아직 add 안 함" > memo.txt
mkdir sketch
echo "디자인 초안" > sketch/draft.txt
git add sketch/draft.txt

git s
git l
```

### 12. 브랜치 오가기
브랜치를 오가면서 파일의 변경을 확인 하세요.
git add 로 Staging 영역으로 들어간 파일을 제외한 모든 파일이 삭제 되는 것 확인.
만약 브랜치가 다르더라도 파일을 지속적으로 유지하고 싶을 때는 Staging 영역에 넣어 두면 됩니다.
```bash
git swf feature/receipt
git swf feature/menu

git l
```

### 13. 마지막 커밋한 상태로 이동
```bash
git undof

git l
```

### 14. 두 브랜치가 같은 공용 파일을 각자 수정 (충돌 씨앗 심기)
```bash
# feature/menu 에서
git sw feature/menu
echo '원본 파일 1 내용\n부가세: 포함\n' > file1.txt
git save "feat(menu): 공용 설정에 부가세 표기(포함)"

git sw feature/receipt
echo '원본 파일 1 내용\n부가세: 별도\n' > file1.txt
git save "feat(receipt): 공용 설정에 부가세 표기(별도)"

git l
```

### 15. 첫 번째 merge : feature/menu
```bash
git sw main
git mg feature/menu
```

### 16. 두 번째 merge(충돌 발생) : feature/receipt
```bash
git mg feature/receipt

# file1.txt 충돌 내용 확인 및 수정
git add file1.txt
git save "merge: 부가세 표기 충돌 해결"

# merge 완료 확인
git branch --merged
git b

```

---
## claude code persissions 실습 가이드
커밋 메시지는 맡기되, **되돌리기 판단은 사람이 한다**

### `.claude/settings.json` 을 만듭니다.
```json
{
  "permissions": {
    "allow": [
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(node --test*)"
    ],
    "ask": [
      "Bash(git push*)",
      "Bash(git reset*)",
      "Bash(git checkout*)",
      "Bash(git switch*)",
      "Bash(git branch -D*)",
      "Bash(git clean*)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(rm -rf*)"
    ]
  }
}
```

### 세션을 재시작하고 확인:
```
/permissions
```









