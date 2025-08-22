# CLI 공식 사용법 가이드북 (2025년판)

**목적**: Claude, Codex, Gemini CLI의 공식 사용법을 한 곳에 모아 효율적인 멀티 에이전트 워크플로우 구축

---

## 🤖 Claude Code 공식 가이드

### 📍 공식 문서
- **메인 문서**: https://claude.ai/code
- **GitHub**: https://github.com/anthropics/claude-code
- **Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices

### 🚀 핵심 기능
- **CLAUDE.md 자동 인식**: 프로젝트 루트의 CLAUDE.md 파일을 세션 시작시 자동 로드
- **Agentic 코딩**: 자연어로 복잡한 코딩 작업 수행
- **Git 워크플로우**: 커밋, 브랜치, PR 자동 처리
- **멀티모달**: 스크린샷, 다이어그램 분석 가능

### 💡 사용 팁
- "매우 빠른 인턴"으로 생각하고 명확한 지시 제공
- 테스트 주도 개발(TDD) 방식과 잘 맞음
- 컨텍스트 최적화를 위한 환경 튜닝 필요

---

## 🔧 OpenAI Codex CLI 공식 가이드  

### 📍 공식 문서
- **GitHub**: https://github.com/openai/codex
- **Help Center**: https://help.openai.com/en/articles/11096431-openai-codex-cli-getting-started
- **Platform Docs**: https://platform.openai.com/docs/codex

### 🛠️ 설치 및 설정
```bash
# 설치
npm install -g @openai/codex

# 업그레이드  
codex --upgrade

# 인증 (2가지 방법)
# 1) ChatGPT 로그인 (Plus: $5 크레딧, Pro: $50 크레딧)
codex --signin

# 2) API 키
export OPENAI_API_KEY="your-api-key"
```

### 🎯 실행 모드
```bash
# 제안 모드 (권장사항만 표시)
codex --suggest

# 자동 편집 모드 (승인 후 자동 적용)  
codex --auto-edit

# 완전 자동 모드 (모든 것 자동)
codex --full-auto

# 세션 중 모드 변경
/mode
```

### 🧠 모델 선택
```bash
# 기본: o4-mini (빠른 추론)
codex

# GPT-4.1 사용
codex --model gpt-4.1

# 설정 파일에서 기본 모델 변경
# config.yaml: model: gpt-4.1
```

### 🔒 보안 및 개인정보
- 로컬에서만 실행, 소스코드 외부 전송 안함
- 프롬프트와 고수준 컨텍스트만 모델에 전송
- 파일 읽기/쓰기/명령어 실행 모두 로컬

---

## 🎯 Google Gemini CLI 공식 가이드

### 📍 공식 문서
- **GitHub**: https://github.com/google-gemini/gemini-cli
- **Google Cloud**: https://cloud.google.com/gemini/docs/codeassist/gemini-cli  
- **Developer Docs**: https://developers.google.com/gemini-code-assist/docs/gemini-cli
- **Codelabs**: https://codelabs.developers.google.com/gemini-cli-hands-on

### 💎 특별 기능
- **완전 무료 오픈소스**: 개인 개발자에게 무제한 접근
- **터미널 네이티브**: 컨텍스트 전환 없이 바로 사용
- **멀티모달**: 텍스트, 스크린샷, 다이어그램 입력 가능

### 📁 .geminiignore 파일 지원
```gitignore
# .geminiignore (프로젝트 루트에 생성)
/backups/
*.log
secret-config.json
node_modules/
.env
```

### 🔄 Git 통합
- `.gitignore`와 `.geminiignore` 모두 자동 인식
- Git 워크플로우와 자연스럽게 통합

---

## 🚀 멀티 에이전트 워크플로우 권장사항

### 🎯 역할 분담 전략
- **Claude**: 총감독관, 복잡한 아키텍처 설계, 문서화
- **Codex**: 코드 구현, 버그 수정, 리팩토링  
- **Gemini**: 분석, 정리, 데이터 처리

### 📋 파일 네이밍 규칙 (2025년 채택)
```
communication/claude/20250822_01_task.md
communication/codex/20250822_01_implementation.md  
communication/gemini/20250822_01_analysis.md
```

### 🔄 협업 최적화
1. **컨텍스트 공유**: 각 CLI의 설정 파일 활용
2. **중복 방지**: 작업 영역 명확히 구분
3. **버전 관리**: 변경사항 실시간 동기화

---

## 📊 성능 최적화 팁

### Claude Code
- CLAUDE.md 파일 최적화로 초기 컨텍스트 효율화
- 프로젝트별 설정 파일 관리

### Codex CLI  
- 적절한 모드 선택 (suggest → auto-edit → full-auto 순서)
- 모델별 토큰 사용량 모니터링

### Gemini CLI
- .geminiignore로 불필요한 파일 제외
- 무료 오픈소스 장점 최대 활용

---

## 🛡️ 보안 및 개인정보 보호

### 공통 원칙
- 민감 정보는 각 CLI의 ignore 파일에 명시
- API 키는 환경변수나 secure config 사용
- 로컬 실행을 우선하여 데이터 유출 방지

### 파일별 보안 설정
```bash
# .claudeignore (있다면)
secrets/
.env
*.key

# .geminiignore  
secrets/
.env
api_keys/

# Codex는 자동으로 .gitignore 인식
```

---

**최종 업데이트**: 2025-08-22
**다음 업데이트 예정**: CLI 버전 업데이트 시 자동 갱신