# 🚀 멀티 에이전트 워크스페이스 - 빠른 시작

## 🎯 가장 간단한 사용법

**1단계: 그냥 물어보세요**
```bash
python ask.py "코드 버그 수정해줘"
python ask.py "대량 파일 정리해줘" 
python ask.py "시스템 아키텍처 설계해줘"
```

**2단계: 끝!**
- 디스패처가 자동으로 최적의 에이전트 선택
- 적절한 에이전트가 작업 수행
- 결과 확인

## 🤖 3개 에이전트 역할

| 에이전트 | 특화 분야 | 언제 선택되나 |
|---------|-----------|--------------|
| **CLAUDE** | 🧠 기획, 설계, 분석 | "설계", "계획", "분석", "진단" |
| **CODEX** | 💻 코딩, 디버깅 | "코딩", "버그", "함수", "최적화" |
| **GEMINI** | ⚡ 대량작업, 정리 | "대량", "정리", "파일", "아카이브" |

## 🔧 고급 사용법

**직접 에이전트 지정:**
```bash
python ma.py codex "Python 함수 최적화"
python ma.py gemini "폴더 100개 정리"
claude.py "복잡한 시스템 설계"  # (현재 세션)
```

**시스템 도구:**
```bash
python scripts/doctor.py          # 시스템 진단
python scripts/quick_help.py      # 도움말
python scripts/onboarding.py      # 신규 사용자 가이드
```

## 📝 실시간 소통 (Claude 전용)

**communication/claude/20250820_prompt1.md** 파일에 내용을 작성하면 Claude가 실시간으로 확인합니다:

```markdown
### 요청 내용
1. 새로운 기능 추가해줘
2. 시스템 개선사항 있나?
```

**토큰 효율적** - 변경된 부분만 전송되므로 경제적!

## 🎯 사용 시나리오

**개발 작업:**
```bash
python ask.py "이 코드 버그 찾아서 수정해줘"
# → CODEX 자동 선택
```

**시스템 관리:**
```bash  
python ask.py "전체 시스템 상태 점검하고 개선방안 제시"
# → CLAUDE 자동 선택
```

**파일 관리:**
```bash
python ask.py "중복파일 찾아서 정리하고 아카이브"
# → GEMINI 자동 선택  
```

## 🚨 문제 해결

**문제 발생시:**
```bash
python scripts/quick_help.py troubleshoot
python scripts/doctor.py
```

**환경 문제:**
```bash
python scripts/environment_checker.py
scripts/windows_wrapper.ps1 -Command encoding-check
```

---

**🎉 이제 3개 AI 에이전트가 협력하는 워크스페이스를 자유롭게 사용하세요!**