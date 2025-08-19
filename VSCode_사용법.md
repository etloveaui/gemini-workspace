# VSCode 멀티 에이전트 워크스페이스 사용법

## 🚀 자동 적용되는 설정들

VSCode를 열면 **자동으로 적용**되는 설정들:

### ✅ 이미 설정된 것들
- **Python 경로**: `./venv/Scripts/python.exe` 자동 인식
- **터미널**: PowerShell 기본 설정
- **인코딩**: UTF-8 고정
- **자동 저장**: 포커스 변경 시
- **테스트**: pytest 자동 인식
- **린팅**: flake8 활성화

## 🎛️ 즉시 사용 가능한 기능들

### 1. 빠른 명령어 (Ctrl+Shift+P → Tasks)
```
> Tasks: Run Task
  ├── Multi-Agent Status        # 에이전트 상태 확인
  ├── Add Task                  # 새 작업 추가  
  ├── Context7 Search           # 문서 검색
  ├── Backup Workspace          # 백업 실행
  ├── Setup Environment         # 환경 재설정
  └── Run Tests                 # 테스트 실행
```

### 2. 터미널에서 바로 사용
```bash
# 에이전트 상태
python ma.py status

# 작업 추가  
python ma.py add "새작업명" 2

# 검색
python ma.py search "requests"

# 백업
python ma.py backup
```

### 3. 파일 자동 제외
- `__pycache__/` 폴더 숨김
- `*.pyc` 파일 숨김  
- `nul` 파일 숨김
- `.agents/locks/` 숨김 (작업 중일 때만)

## 📁 Explorer 활용법

### 중요 폴더들
```
📁 multi-agent-workspace/
├── 📁 communication/           # ← 여기에 대화 파일 작성
│   ├── 📁 claude/
│   ├── 📁 gemini/ 
│   ├── 📁 codex/
│   └── 📁 templates/           # ← 템플릿 복사해서 사용
├── 📁 .agents/                 # 시스템 파일들
├── 📁 docs/                    # 문서
└── 📄 ma.py                    # 통합 명령어
```

## 🔧 유용한 단축키

### 멀티 에이전트 전용
- **Ctrl+Shift+P** → "Tasks" → 빠른 명령 실행
- **Ctrl+`** → 터미널 열기 (ma.py 명령어 사용)
- **Ctrl+Shift+E** → Explorer (폴더 구조 보기)

### 일반 개발
- **Ctrl+P** → 파일 빠른 열기
- **Ctrl+Shift+F** → 전체 검색
- **F5** → 디버깅 시작

## 📝 대화 파일 작성 꿀팁

### 1. 템플릿 활용
```
communication/templates/ 에서 복사:
├── quick_template.md      # 간단한 요청용
├── daily_template.md      # 일일 작업용  
├── task_template.md       # 큰 작업용
└── session_template.md    # 세션 기록용
```

### 2. 자동 완성 활용
- 파일명: `20250819_session_1.md` 형식
- 우선순위: `P0` (긴급) ~ `P3` (백로그)
- 상태: `pending` → `in_progress` → `completed`

### 3. 마크다운 미리보기
- **Ctrl+Shift+V** → 마크다운 미리보기
- 작성하면서 실시간으로 확인 가능

## 🔄 자동화된 기능들

### 백업 (30분마다)
- 중요 파일들 자동 백업
- `.agents/backup/` 폴더에 저장
- 10개 버전까지 보관

### 아카이빙 (완료된 작업)
- `status: completed` 파일들 자동 정리
- `communication/archive/` 로 이동
- 연도/월별로 구조화

### 파일 정리
- 임시 파일, Python 캐시 자동 정리
- 중복 파일 감지 및 알림
- 빈 폴더 자동 제거

## ❓ 문제 해결

### Python 환경 인식 안될 때
1. **Ctrl+Shift+P** → "Python: Select Interpreter"
2. `./venv/Scripts/python.exe` 선택

### 터미널이 안 열릴 때  
1. **Ctrl+Shift+P** → "Terminal: Select Default Profile"
2. "PowerShell" 선택

### 설정이 적용 안될 때
```bash
python setup_environment.py
```

---

## 🎉 결론

**VSCode를 열기만 하면 모든 설정이 자동 적용됩니다!**
- 별도 설정 불필요
- 바로 `communication/` 폴더에 파일 작성 시작
- 템플릿 복사해서 사용하세요