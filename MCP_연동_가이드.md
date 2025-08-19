# MCP (Model Context Protocol) 연동 가이드

## 🤖 MCP란?

**Model Context Protocol**은 AI 모델이 외부 데이터와 도구에 접근할 수 있게 해주는 표준 프로토콜입니다.

### 💡 쉬운 설명
- **기존**: AI가 훈련 데이터만 알고 있음
- **MCP 적용**: AI가 실시간으로 파일, GitHub, DB 등에 접근 가능
- **결과**: 더 정확하고 최신 정보로 답변

## 🎯 누가 사용 가능한가?

### ✅ 현재 지원
- **Claude (Anthropic)**: 완전 지원 ✅
- **Claude Desktop**: 설정 파일로 연동 ✅

### ❓ 다른 AI들
- **Gemini**: 공식 지원 없음 (향후 가능성 있음)
- **Codex/GPT**: OpenAI MCP 지원 제한적
- **로컬 AI (Ollama)**: 일부 모델에서 가능

## 🔌 우리 시스템에 통합된 MCP 서버들

### 1. Filesystem MCP ✅
```json
"filesystem": {
  "enabled": true,
  "description": "파일시스템 전체 접근"
}
```
- **기능**: 모든 파일 읽기/쓰기/검색
- **장점**: 토큰 절약하며 파일 내용 분석
- **사용 예**: "프로젝트의 모든 Python 파일에서 특정 함수 찾기"

### 2. GitHub MCP ✅  
```json
"github": {
  "enabled": true,
  "free": true,
  "description": "GitHub 리포지토리 관리"
}
```
- **기능**: 리포지토리, 이슈, PR 관리
- **장점**: 코드 리뷰, 이슈 추적 자동화
- **사용 예**: "최근 커밋들의 변경사항 요약해줘"

### 3. SQLite MCP ✅
```json
"sqlite": {
  "enabled": true, 
  "free": true,
  "description": "로컬 데이터베이스 관리"
}
```
- **기능**: `usage.db` 등 SQLite DB 직접 조회
- **장점**: 에이전트 성능 데이터 실시간 분석
- **사용 예**: "지난 주 작업 통계 보여줘"

### 4. Context7 MCP ✅
```json
"context7": {
  "enabled": true,
  "free": true, 
  "description": "실시간 문서 검색"
}
```
- **기능**: 최신 라이브러리 문서, API 참조
- **장점**: 항상 최신 정보로 코딩 도움
- **사용 예**: "requests 라이브러리 최신 사용법"

## 🚀 실제 활용 사례

### Case 1: 코드 분석
```
사용자: "이 프로젝트에서 에러 처리가 부족한 부분 찾아줘"
Claude: [Filesystem MCP로 모든 .py 파일 스캔] 
       → 5개 파일에서 try-catch 누락 발견
```

### Case 2: 문서 업데이트
```
사용자: "README.md를 최신 상태로 업데이트해줘"
Claude: [GitHub MCP로 최근 변경사항 확인]
       → [Filesystem MCP로 README 직접 수정]
```

### Case 3: 성능 모니터링
```
사용자: "어제부터 시스템 성능이 어떻게 변했어?"
Claude: [SQLite MCP로 usage.db 쿼리]
       → 토큰 사용량 30% 증가, 평균 응답시간 0.2초 단축
```

## ⚡ 성능 최적화

### 토큰 절약 효과
- **기존**: 긴 파일 내용을 모두 컨텍스트에 포함
- **MCP 적용**: 필요한 부분만 실시간 조회
- **절약률**: 약 30-50% 토큰 사용량 감소

### 정확도 향상
- **기존**: 훈련 시점의 오래된 정보
- **MCP 적용**: 실시간 최신 정보
- **결과**: 더 정확하고 실용적인 답변

## 🔧 설정 확인 방법

### 1. Claude Desktop 설정 확인
```bash
# Windows
notepad "%APPDATA%/Claude/claude_desktop_config.json"

# 설정이 자동으로 적용되어 있어야 함
```

### 2. 연동 테스트
```bash
python ma.py search "python requests"
# Context7 MCP 응답 확인

python ".agents/context7_mcp.py" search requests get
# 직접 테스트
```

## 🎯 추천 활용법

### 일상적 사용
1. **코드 리뷰**: "변경된 파일들 검토해줘"
2. **디버깅**: "에러 로그 분석해줘"  
3. **최신 정보**: "이 라이브러리 최신 문서 찾아줘"

### 고급 활용
1. **프로젝트 분석**: "전체 아키텍처 다이어그램 만들어줘"
2. **성능 추적**: "지난 달 대비 개선사항은?"
3. **자동 문서화**: "API 문서 자동 생성해줘"

---

## 📝 요약

**MCP는 현재 Claude에서만 완전 지원**되지만, 우리 시스템에 4개 서버가 통합되어 있어 **토큰 절약과 정확도 향상**을 동시에 달성했습니다. 

다른 AI들도 향후 지원될 가능성이 높으니 기대해볼 만합니다! 🚀