# System Rework Plan — Slim + Automation (v0.2)

## Goals
- 대화: 한 번 실행→연속 대화(프리픽스 없이), Provider 전환은 옵션.
- 녹화: 항상 ON, PowerShell 기본 Transcript, 중복 감지, 부하 0에 가깝게.
- 자동화: 세션 시작/종료 1회 훅으로 HUB 동기화·승격만 수행(상시 데몬 없음).
- 슬림: 래퍼/워처 기본 OFF, 필요 시 수동 실행.

## Phase 1 — Automation Tasks (우선순위 1)
- `invoke hub.sync`: docs/CORE/HUB_ENHANCED.md ↔ agents_hub/queue,processing 동기화.
- `invoke task.autopromote`: 규칙 기반 Planned→Active 승격(화이트리스트·태그 기반).
- 훅: `agent.start`(세션 진입 시 1회), `agent.end`(세션 종료 시 1회)에서 위 태스크 호출.
- DoD:
  - 수동 개입 없이 시작/종료 시 HUB가 큐와 일치.
  - 로그에 TL;DR 3줄 자동 반영.

## Phase 2 — Slim Mode Transition (우선순위 2)
- 기본값: `.agents/emergency.json: enabled=false`, `AI_REC_AUTO=0`.
- PS7 프로필 유지(UTF-8/CRLF) + 래퍼·워처 비활성.
- Transcript는 대화 CLI에서만 제어(중복 시작 방지).

## Phase 3 — Conversation CLI (무마찰)
- `scripts/ai.ps1`: `ai`만 실행→인터랙티브, `ai "첫 질문"`도 지원.
- 세션 명령: 일반 텍스트=질의, `/exit` 종료, `/p claude|gemini` Provider 전환, `/save` 메모(선택).
- 기본 Provider: `claude`(변경은 `.agents/config.json`에 저장, 세션 간 유지).
- 구현: `src/cli/ai_session.py`(스트리밍, 세션 요약 3줄 생성, messages.jsonl 옵션 기록).
- Transcript: 세션 시작 시 자동 `Start-Transcript`, 종료 시 `Stop-Transcript`(이미 켜져 있으면 스킵).

## Phase 4 — Logging & Memory
- 세션 요약 저장: `docs/sessions/YYYY-MM-DD.md`에 3줄 요약 append.
- 선택: 핵심 결정만 `context/messages.jsonl`에 append.
- 규칙: 기능 실패 접근은 태스크 로그에 즉시 기록(재시도 금지 사항 포함).

## Phase 5 — Cleanup & Deprecation
- 폐기: 프리픽스 전용 라우터/고부하 래퍼/워처 스크립트 목록화 후 제거.
- 유지: `invoke start --fast`, `invoke review`, 헬스체크.
- 문서: AGENTS.md에 "슬림+자동" 흐름으로 일원화, 사용법 1페이지.

## Guardrails
- 앱 코드(프로젝트 폴더) 직접 수정 금지 → 오버레이/제안 우선.
- 정규식 대량 치환 금지, 컨텍스트 패치만 사용.
- 모든 변경 전 프리뷰(run: review), 끝나면 TL;DR 3줄 로그.

## Risks & Rollback
- 자동 승격 오작동 → 훅 일시 비활성, 수동 모드 회귀.
- 녹화 충돌 → Transcript 중복 감지로 완화, 실패 시 수동 안내.

## Ownership & Timeline
- P1(Automation) 0.5일, P2(Slim) 0.5일, P3(CLI) 0.5~1일, P4~P5 각 0.5일.
- 진행 중 변경은 모두 문서화하고 승인 후 단계 전환.

