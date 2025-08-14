# EMERGENCY_MODE — 과부하/레이트리밋 완화 가이드

## 목적
- 단시간 요청 폭주(429/Rate limit/스트림 끊김) 발생 시 즉시 적용 가능한 완화 절차를 제공합니다.
- 변경은 비파괴적(추가 파일)이며, 기존 워크플로우는 그대로 유지됩니다.

## 즉시 실행(권장)
- PowerShell 7에서 아래처럼 래퍼를 통해 실행합니다.

```
pwsh -ExecutionPolicy Bypass -File tools/codex_emergency.ps1 -- codex <기존_인자들>
```

- 또는 준비된 세션 런처를 사용합니다(환경변수 자동 설정):

```
pwsh -ExecutionPolicy Bypass -File .\codex-session-emergency.ps1 -- start --fast
```

- 기본 완화:
  - 자동 재시도: 최대 8회, 지수 백오프(200ms 기반, 최대 10s, 0–250ms 지터)
  - RPS 억제: 최소 간격 3500ms(≈0.28rps), 프로세스 간 파일 게이트로 동기화
  - 토큰 상한: `--max-tokens 2500` 자동 주입(명시 시 우선)

## 환경변수(선택 조정)
- `CODEX_RETRY_MAX`: 최대 재시도(기본 8)
- `CODEX_BACKOFF_BASE_MS`: 백오프 기본(ms, 기본 200)
- `CODEX_BACKOFF_MAX_MS`: 백오프 상한(ms, 기본 10000)
- `CODEX_EMERGENCY_MIN_DELAY_MS`: 시도 간 최소 간격(ms, 기본 3500)
- `CODEX_RPS`: RPS 목표(예: 0.3). 설정 시 최소 간격 자동 계산(상기 값보다 우선)
- `CODEX_MAX_TOKENS`: `--max-tokens` 자동 주입 값(기본 2500)

예시:
```
($env:ACTIVE_AGENT='codex')
($env:CODEX_RETRY_MAX='8'); ($env:CODEX_BACKOFF_BASE_MS='200'); ($env:CODEX_BACKOFF_MAX_MS='10000')
($env:CODEX_RPS='0.3'); ($env:CODEX_MAX_TOKENS='2500')
pwsh -ExecutionPolicy Bypass -File tools/codex_emergency.ps1 -- codex start --fast
```

## 동작 원리(요약)
- 표준출력/표준에러를 캡처하여 `Rate limit/429/Please try again in/timeout` 등의 신호를 감지하면 재시도합니다.
- `.agents/.emergency_gate` 파일을 사용해 동일 리포 내 동시 실행 간 최소 간격을 보장합니다.
- `--max-tokens`가 인자에 없으면 기본값을 자동 주입합니다.

## 롤백
- 원래대로 실행: 기존 커맨드를 그대로 사용하면 됩니다.
- 파일 제거는 불필요합니다. 본 래퍼는 선택적으로 쓸 수 있습니다.

## 참고
- 자세한 운영 원칙과 맥락은 `AGENTS.md`의 Rate-limit Hardening 섹션을 따릅니다.

## 프로필 기반 토글(v0.1.2+)
- `.agents/emergency.json`의 `enabled=true`이면 PowerShell UTF-8 프로필이 `codex`/`cx`를 `tools/codex_emergency.ps1`로 래핑합니다.
- `rps/max_tokens/retry` 설정은 환경변수(`CODEX_*`)로 자동 주입됩니다.
- 해제하려면 `enabled=false`로 바꾸고 새 세션을 시작하세요.

## Health Ops 번들
- 일괄 적용: `tools/health_check.ps1 -Apply`(로그 정리, 허브 50MB↑ 분할, DB VACUUM).
- 예약 등록: `tools/health_schedule.ps1 -Time 03:30 -Apply` (미리보기만 원하면 `-Apply` 생략).
- HUB 큐 마감: `tools/hub_complete.ps1 -Result success -Note "요약"` → `agents_hub/archive/<YYYYMMDD>/success/`로 이동.
