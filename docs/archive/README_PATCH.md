# Patch Notes — Multi‑Agent Enablement (v0.1)

핵심 변경
- `AGENTS.md` 추가: 멀티에이전트 운영 지침.
- `scripts/agent_manager.py` 추가: 에이전트 상태 조회/설정 (+ `ACTIVE_AGENT` 환경변수 우선).
- `tasks.py` 갱신: `invoke agent.status`, `invoke agent.set` 태스크 추가.
- `scripts/runner.py` 갱신: `[agent=...]` 표기 및 SQLite WAL 설정.
- `scripts/usage_tracker.py` 갱신: SQLite WAL 설정.
- `GEMINI.md` 갱신: 섹션 13 멀티 에이전트 호환 추가.
- `README.md` 갱신: 멀티에이전트 빠른 시작/전환 안내.

사용 방법
- 상태: `invoke agent.status`
- 전환: `invoke agent.set --name gemini|codex`
- 프로세스 전용 라벨: `($env:ACTIVE_AGENT='codex'); invoke start`

주의
- 두 터미널에서 병렬 작업 가능하나, 동일 파일 동시 수정은 피하세요.
- 데이터베이스는 WAL 모드로 완화했지만, 대량 병렬 쓰기는 피하는 것을 권장합니다.
