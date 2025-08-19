# [GEMINI.cli A1] Repo Sanity & Ignore Check (Windows)
WORKDIR: C:\Users\eunta\gemini-workspace
GOALS:
  - .gitignore 규칙이 적용되는지 실증
  - projects/ 가 추적되지 않도록 보장
  - 현재 브랜치/상태 요약

STEPS:
1) cd "C:\Users\eunta\gemini-workspace"
2) git rev-parse --abbrev-ref HEAD
3) git status --porcelain
4) echo "do-not-commit" > projects/_sanity.txt
5) git add -n projects/_sanity.txt
6) git check-ignore -v projects/_sanity.txt
7) type .gitignore

STOP & REPORT:
- 현재 브랜치명
- git status 한 줄 요약
- 5)에서 "would be added"가 아닌지
- 6)에서 어떤 규칙으로 무시됐는지
