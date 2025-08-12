오케이, 이해했어. **Claude Desktop 말고, 네 프로젝트에 MCP를 박아 넣어 같이 쓰는 걸**로 갈게.
핵심은 “MCP 서버들을 우리 코드가 직접 띄우고, 필요할 때 툴 호출 → 결과를 붙여서 Groq LLM에 넘기는” 흐름이야.

# 최소 통합 계획 (프로젝트 내)

* **전제**: Node.js 설치(서버 실행용), Python 환경 유지, Groq API는 지금처럼 `secrets/my_sensitive_data.md`.
* **패키지**: `pip install mcp anyio trio` (공식 Python MCP 클라이언트)

## 새 파일/수정 요약

1. `scripts/mcp_servers.json`

   * 어떤 MCP 서버를 쓸지 정의(커맨드·args·env). 예:
   * `filesystem`(필수), `desktop-commander`(옵션), `brave-search`/`firecrawl-mcp`(옵션)

2. `mcp_client.py`

   * JSON 설정 읽고 **서버 프로세스(StdIO)** 띄우기
   * `call_tool(server, tool, params)` 공용 함수 제공 (Python에서 MCP 툴 호출)

3. `router.py`

   * **슬래시 커맨드 라우팅**(CC Router 느낌):

     * `/think …` → (옵션) `brave-search`로 3\~5개 결과 요약 붙이고 → `ask_groq.py`에 프롬프트 증강해서 호출
     * `/code …` → (옵션) `filesystem.read`로 대상 파일 읽어 컨텍스트 추가 → Groq에 전달
     * `/run …` → `desktop-commander.run` 같은 툴 실행 후 로그 요약 붙여 Groq 호출
     * `/open path` → `filesystem.read`로 내용 반환
   * 기본 텍스트는 그대로 `ask_groq.py`로 패스

4. `ask_groq.py` (기존 파일 **가벼운 수정**)

   * 입력이 `/`로 시작하면 `router.py`를 통해 **사전-도구 호출 & 컨텍스트 증강** → 그 결과를 최종 프롬프트로 LLM 호출
   * 모델 라우팅은 우리가 정한 기본값 유지:

     * `/think` → **kimi-k2**(가능 시) 또는 **llama-3.3-70b**
     * `/code` → **qwen/qwen3-32b**
     * `/long` → **llama-3.3-70b**
     * `/fast` → **llama-3.1-8b-instant**

## 사용 예

* `python router.py "/open docs/HUB.md"` → 파일 내용 반환
* `python router.py "/think RAG 인덱스 설계 포인트 5개"` → (옵션 검색+요약)→ Groq 답변
* `python router.py '/run "python scripts/build.py"'` → 실행 로그 요약 + 후속 질문 가능
* 일반 질문은 그대로: `python ask_groq.py "이번 주 할 일 정리해줘"`

## 보안/가드레일

* `filesystem` 서버는 **프로젝트 루트만** 노출.
* 민감키는 기존처럼 `secrets/my_sensitive_data.md` (Git ignore).
* 웹/크롤 툴 키 없으면 해당 서버 블록만 설정에서 생략.

---

원하면 지금 바로 다음 파일들을 **생성**해줄게:

* `scripts/mcp_servers.json` (윈도우 경로 포함)
* `mcp_client.py` (서버 스폰+툴 호출 유틸)
* `router.py` (슬래시 라우팅 → MCP → Groq 연동)
* `requirements.txt` 업데이트

진행할까? (옵션 MCP: `filesystem`만 먼저, 나중에 `desktop-commander`/`brave-search` 붙이는 방식도 가능)
