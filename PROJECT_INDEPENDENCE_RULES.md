# 🚨 CRITICAL: Projects 폴더 독립성 규칙

## ⚠️ **절대 준수 사항**

### 🔒 **Projects 폴더 독립성**
- `projects/` 아래의 **모든 폴더는 독립적인 Git 리포지토리**
- **절대로** root workspace Git에 포함하면 안됨
- 각 프로젝트는 자체 `.git` 폴더를 가짐

### 📁 **폴더 구조 예시**
```
multi-agent-workspace/          ← 메인 워크스페이스 (이 Git)
├── .git/                      ← 메인 워크스페이스 Git
├── projects/
│   ├── 100xFenok/             ← 독립 프로젝트 1
│   │   ├── .git/              ← 독립 Git 1
│   │   └── ...
│   ├── another-project/       ← 독립 프로젝트 2
│   │   ├── .git/              ← 독립 Git 2
│   │   └── ...
│   └── ...
```

### 🚫 **금지 행위**
1. `git add projects/` 실행 금지
2. projects 내 파일을 메인 워크스페이스 Git에 추가 금지
3. projects 폴더 내용을 메인 .gitignore에 추가하려 시도 금지
4. projects 내 독립 프로젝트를 메인 브랜치에 merge 시도 금지

### ✅ **올바른 작업 방식**
1. **프로젝트 작업 시**: `cd projects/100xFenok` 후 해당 Git에서 작업
2. **독립 커밋**: 각 프로젝트 폴더에서 `git commit`, `git push`
3. **메인 워크스페이스**: 오직 시스템/에이전트 관련 파일만 관리

### 📝 **에이전트 공통 규칙**
- **Claude, Gemini, Codex 모두 이 규칙 준수**
- projects 관련 작업 시 반드시 해당 프로젝트 디렉토리로 이동
- 메인 워크스페이스와 혼동하지 않도록 주의

---
**🔥 이 규칙을 위반하면 프로젝트 전체가 망가질 수 있습니다!**