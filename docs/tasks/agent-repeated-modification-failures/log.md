# [P-AGENT] Repeated Modification Failures (for GEMINI)

## Context
- 증상: 2.5 Pro 한도 소진 후 Flash 전환 시 반복 수정 시도/실패 빈발.
- 범위: GEMINI CLI 내부 재시도/모델 전환 로직은 외부 요인(실구현: GEMINI). 레포 차원에서의 완화책을 우선 도입.

## Mitigations (Repo-level)
- Edits Deduplication: 동일 파일+패치 해시 재적용 방지
  - 구현: `scripts/tools/edits_safety.py` + `scripts/edits_manager.py` 적용 경로에 통합
  - 정책: 최근 성공 패치(기본 60분) 재적용 스킵, 연속 실패(기본 3회/30분) 시 백오프
- Backoff/Max Attempts: 실패 누적 시 일시 스킵하며 상태 기록(`.agents/edits_state.json`)
- Line-ending Tolerance: `scripts/textops.py`의 CRLF/LF 내성 유지, 호출부에서 활용 권장

## Handoff to GEMINI (Implementation-required)
- 재시도 로직 정교화: 동일 요청/패치에 대한 중복 시도 방지 및 백오프 공유
- 모델 전환 시 컨텍스트/파일 상태 동기화 규칙 수립
- 실패 보고 파이프라인을 HUB/메시지로 통합

## Status
- Repo-level 완화: 구현/커밋 완료.
- GEMINI 측 실구현: 이 문서와 HUB 항목을 참조하여 적용 필요.

