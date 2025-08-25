# Codex → Claude 핸드오프: 초기 운영 골격 검증 요청
- 날짜: 2025-08-23
- 작성: Codex
- 수신: Claude
- 목적: 파일 기반 커뮤니케이션/워처/로깅 골격의 타당성 검증과 개선 제안 요청

## 배경/컨텍스트
- 본 워크스페이스는 에이전트 간 **파일 기반 비동기 커뮤니케이션**을 표준으로 함.
- `projects/`는 각각 독립 Git 저장소로 간주되며, 루트 Git에 포함 금지(AGENTS.md 규칙).
- 운영 OS: Windows 우선, Python 3.x, UTF-8 기본.
- 프롬프트 채널: `communication/codex/20250823_01_prompt.md` (사용자 ↔ Codex 지시용)

## 현재 구현 요약(스캐폴딩)
- 문서/가이드
  - `docs/CODEX_CHECKLIST.md`: 세션 시작/작업 전·중·후 체크리스트
  - `docs/CORE/HUB_ENHANCED.md`: 중앙 허브(우선순위/작업 로그)
  - `docs/AGENT_COMMUNICATION_SYSTEM.md`: 파일 기반 커뮤니케이션 시스템 개요
  - `communication/shared/COMMUNICATION_GUIDE.md`: 빠른 시작/템플릿/인코딩 트러블슈팅
  - `docs/USAGE.md`: 실행/테스트/로그 경로 안내
  - `.vscode/settings.json`: UTF-8 고정, 자동 추정 활성화
- 워처/모니터
  - `scripts/watch_file.py`: 디렉터리/단일 파일 모두 폴링 감시(생성/수정/삭제 이벤트)
  - `scripts/monitor_prompt.py`: 지정 프롬프트 파일 전용 모니터(자동 디코딩 휴리스틱 포함: utf-8, cp949, euc-kr, utf-16*)
  - `scripts/start_watchers.ps1`: 두 워처를 백그라운드로 실행, PID/로그 기록
    - 로그: `logs/watch_comm.out`, `logs/prompt_monitor.out`, `logs/watchers.pid`
    - 이벤트 로그: `communication/codex/YYYYMMDD_prompt_events.log`
- 실행 환경
  - `scripts/setup_venv.ps1`, `scripts/setup_venv.sh`: venv 생성/업데이트
- 로깅/트레이스
  - `utils/logging.py`: JSON 라인 로깅, `correlation_id` ContextVar, `@trace` 데코레이터
  - `scripts/demo_task.py`: 메시지 처리 데모(트레이싱 시연)
  - `scripts/smoke_test.py`: JSON 라인 포맷 간단 검증

## 의도된 운영 흐름
1) 운영자는 PowerShell에서 venv 준비 → `scripts/start_watchers.ps1 -PromptFile <지정경로>` 실행(숨김 가능)
2) 사용자(또는 타 에이전트)가 프롬프트 파일에 지시사항 저장
3) `monitor_prompt.py`가 이벤트/본문을 로그로 기록, Codex가 이를 기준으로 작업 수행
4) 결과/결정은 `communication/codex/YYYYMMDD_xx_*.md`와 `docs/CORE/HUB_ENHANCED.md`에 반영

## 현재 상태
- 코드/문서/스크립트 모두 루트 워크스페이스에 배치 완료.
- 워처는 사용자가 시작 스크립트 실행 시 동작(기본은 수동 시작). 현재 세션에서는 미실행 상태로 확인됨.
- 프롬프트 파일에 한글 인코딩 깨짐 현상 존재 → 모니터에 다중 인코딩 디코딩 휴리스틱 추가로 완화.

## 검증 요청 항목(Claude)
- 설계 타당성
  - 폴링 워처(1s/0.5s)로 충분한가? OS 이벤트 기반(Watchdog/ReadDirectoryChangesW) 전환 필요성 평가
  - 파일 기반 커뮤니케이션의 메시지 스키마/라이프사이클(초안 필요): status, owner, due, checksum, ack
  - Windows 우선 환경에서 PowerShell 스크립트/권한 모델의 안정성(ExecutionPolicy, UAC) 검토
- 신뢰성/내고장성
  - 워처 장애/중복 실행/재시작 전략(PID 파일 → 헬스체크/락/싱글턴 보장) 제안
  - 로그 로테이션/보존 정책(현재 없음) 설계 제안
  - 깨진 인코딩 복구 한계 및 예방책(편집기 표준화/PR 템플릿/사전 검증 훅) 제안
- 보안/운영
  - 민감정보 유출 방지(레드랙션/스크럽) 로깅 정책
  - 경로/입력 검증 강화, 허용된 경로 화이트리스트
- 테스트 전략
  - 워처/모니터 E2E 테스트 방법(파일 쓰기 시뮬레이션, 타임아웃, 윈도우 전용 케이스)
  - 유닛테스트 추가 위치(로깅/디코딩/trace)

## 알려진 이슈/리스크
- 워처 자동 시작 없음 → 수동 실행 의존. 재부팅 시 자동화 미구현.
- Windows 인코딩 이슈 빈발 가능 → VS Code 설정 배포로 완화, 완전 방지는 어려움.
- 폴링 기반으로 매우 짧은 순간의 생성/삭제 이벤트 손실 가능.
- 로그 무한 증가 위험(로테이션 미구현).
- `projects/` 독립성은 문서로 강제 중이나, 툴링으로 보강 필요(가드 스크립트/프리훅).

## 실행/재현 가이드
- venv: `powershell -ExecutionPolicy Bypass -File scripts/setup_venv.ps1`
- 백그라운드 실행: `./scripts/start_watchers.ps1 -PromptFile "C:\\Users\\etlov\\multi-agent-workspace\\communication\\codex\\20250823_01_prompt.md" -Hidden`
- 단독 실행(디버그):
  - `./venv/Scripts/python.exe scripts/watch_file.py --path communication --interval 1.0`
  - `./venv/Scripts/python.exe scripts/monitor_prompt.py --file communication\\codex\\20250823_01_prompt.md --interval 0.5 --debounce 0.5`
- 데모: `./venv/Scripts/python.exe scripts/demo_task.py --message "hello" --repeat 2 --log-level DEBUG`
- 스모크: `./venv/Scripts/python.exe scripts/smoke_test.py`

## 향후 개선 제안(초안)
- 워처 서비스화: Windows 서비스/작업 스케줄러 등록 스크립트 제공(자동 시작/재시작)
- 메시지 스키마: `communication/shared/schema.json`(예: type, id, status, owner, created_at, due)
- 로테이션: `logs/` 및 `communication/codex/*_prompt_events.log`에 보존/압축 정책
- 헬스체크: 워처 하트비트 파일 갱신 + Codex가 상태판 노출
- 안전장치: 편집 시 인코딩 검증 프리훅/에디터 설정 배포

## 요청
- 상기 항목에 대한 아키텍처·운영·테스트 관점 검토와 변경 제안.
- 폴링→이벤트 기반 전환 로드맵, 메시지 스키마 초안, 로그 정책 제시를 우선 부탁드립니다.

