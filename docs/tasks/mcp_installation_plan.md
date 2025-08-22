# MCP (Model Context Protocol) 설치 계획

**작성일**: 2025-08-18  
**작성자**: Claude Code  
**우선순위**: 낮음 (시스템 안정화 후 진행)

---

## 🎯 MCP 설치 목적

사용자 요청사항에 따르면 MCP는 **Claude Code를 사용할 때 강력해진다**고 하여 로컬 파일 접근 등 다양한 도구들을 통합해 두었습니다.

### 주요 활용 목표:
1. **로컬 파일 시스템 접근 강화**
2. **다양한 AI 모델과의 통합** (qwen, kimi2, meta 등)
3. **Claude Code 기능 확장**

---

## 🛠️ 사전 분석된 MCP 모델 정보

`scratchpad/config.txt`에서 확인된 무료/유료 모델들:

### ✅ 무료 모델들
- **Kimi-K2** (Groq) - 현재 완전 무료, 속도 매우 빠름
- **LLaMA 3** (Groq/Ollama) - 고품질 LLM, 오픈소스  
- **Gemma** (Groq/Ollama) - 구글 오픈모델, 빠른 응답
- **DeepSeek Coder** (Ollama) - 코드용 특화 모델
- **Mixtral** (Ollama/Groq) - 균형잡힌 성능

### 🔧 설정 예시
```json
{
  "Providers": [
    {
      "name": "groq",
      "baseUrl": "https://api.groq.com/openai/v1",
      "apiKey": "YOUR_GROQ_API_KEY"
    }
  ],
  "Router": {
    "default": "groq,kimi",
    "think": "groq,kimi-k2", 
    "longContext": "groq,llama3-70b",
    "code": "groq,deepseek-coder"
  }
}
```

---

## 📋 설치 단계 계획

### Phase 1: 환경 준비
1. **시스템 안정화 완료 대기** - Codex의 정리 작업 완료 후
2. **Claude Code 설정 백업**
3. **MCP 공식 문서 확인** 및 최신 버전 조사

### Phase 2: MCP 설치
1. **MCP 서버 설치**
   ```bash
   npm install -g @modelcontextprotocol/server
   ```

2. **로컬 파일 접근 MCP 서버 설정**
   ```bash
   mcp-server-filesystem --root C:\Users\etlov\multi-agent-workspace
   ```

### Phase 3: Claude Code와 통합  
1. **Claude Code config 수정**
2. **MCP 서버 연결 테스트**
3. **기본 기능 검증**

### Phase 4: 고급 모델 통합
1. **Groq API 키 설정** (무료)
2. **Ollama 로컬 설치** (선택사항)  
3. **모델별 라우팅 설정**

---

## ⚠️ 주의사항

1. **시스템 안정화 우선**: 현재 진행 중인 시스템 정리 작업이 완료된 후 시작
2. **점진적 설치**: 한 번에 모든 모델을 설치하지 말고 단계적으로 진행
3. **설정 백업**: 각 단계마다 작동하는 설정을 백업
4. **보안 고려**: API 키 등 민감 정보는 `secrets/` 폴더에 안전하게 보관

---

## 📅 예상 일정

- **현재**: 시스템 안정화 대기 중
- **1단계**: 시스템 정리 완료 후 즉시 시작 (예상: 2025-08-19)  
- **2-3단계**: 설치 및 기본 설정 (1-2일)
- **4단계**: 고급 기능 테스트 (1일)

---

## 🎯 성공 기준

1. ✅ Claude Code에서 로컬 파일 접근 가능
2. ✅ 무료 모델(Kimi-K2, LLaMA3 등) 정상 작동  
3. ✅ 명령어별 모델 라우팅 작동 (`/think`, `/code` 등)
4. ✅ 기존 Claude Code 기능 유지

---

**이 계획은 시스템 안정화 작업 완료 후 사용자 요청 시 실행됩니다.**