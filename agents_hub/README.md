에이전트 허브(파일 기반 큐)

폴더 구조
- queue/: 새 메시지·작업 대기열(JSON)
- processing/<agent>/: 에이전트가 클레임한 항목
- archive/<YYYYMMDD>/<status>/: 완료된 항목 보관

메시지 스키마(JSON)
{
  "id": "uuid",
  "from": "codex|gemini|...",
  "to": "codex|gemini|all",
  "type": "message|task",
  "title": "string",
  "body": "string",
  "tags": ["optional", "tags"],
  "created_at": "iso8601",
  "status": "queued|processing|done|failed"
}

기본 사용은 tasks.py의 invoke hub.* 를 참고하세요.

