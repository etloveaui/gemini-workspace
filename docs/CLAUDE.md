Claude CLI (Groq 라우팅)

- 실행: `./claude.ps1 /think "테스트"`
- 명령: `/think`, `/code`, `/long`, `/fast`, `/help`
- 키: 레포 루트 `secrets/my_sensitive_data.md`의 `gsk_...` 또는 환경변수 `GROQ_API_KEY`
- 모듈 경로: `src/ai_integration/claude/*`
- 선택 기능: `src/ai_integration/claude/mcp_servers.json`에서 MCP 서버를 `enabled:true`로 활성화

빠른 테스트
- 도움말: `./claude.ps1 --help`
- 라우팅 테스트: `./claude.ps1 /fast "간단 테스트"`

주의: 네트워크/키는 사용자 환경 의존. 키가 없으면 에러 메시지로 안내됩니다.

