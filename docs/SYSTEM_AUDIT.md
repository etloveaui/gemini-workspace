# SYSTEM_AUDIT — 시스템 점검/유지 가이드

## 목적
- 레포가 비대해졌을 때의 체감 속도 저하, 레이트 리밋 관련 장애를 사전에 탐지하고 점검합니다.
- 모든 절차는 비파괴적이며(읽기 위주), 유지 스크립트는 명시적 `--Fix` 시에만 적용됩니다.

## 빠른 점검
1) 감사 리포트 생성
```
pwsh -ExecutionPolicy Bypass -File tools/sys_audit.ps1
```
- 결과: `reports/sys_audit_YYYYMMDD_HHMMSS.txt`(+ 선택적 JSON)

2) JSON도 원하면
```
pwsh -ExecutionPolicy Bypass -File tools/sys_audit.ps1 -Json
```

## 보고서 해석 포인트
- Top directories: `.git / venv / node_modules / terminal_logs / context`의 급성장 여부 확인
- Largest files: 100MB 이상 파일 상주 여부 체크
- Heavy paths: `context/messages.jsonl`, `usage.db`, `terminal_logs` 용량 추적
- Ignore checks: `.gemini/`, `secrets/`, `projects/` 등 Git 무시 규칙 적용 여부
- Emergency config: `tools/codex_emergency.ps1`과 `.agents/emergency.json` 존재 확인

## 유지/정리(선택)
Dry-run(기본):
```
pwsh -ExecutionPolicy Bypass -File tools/sys_maint.ps1
```
적용 실행:
```
pwsh -ExecutionPolicy Bypass -File tools/sys_maint.ps1 --Fix
```
- 수행 내용(기본):
  - `terminal_logs/`에서 최근 X일(`TrimLogsDays`, 기본 14) 이전 로그를 `archive/terminal_logs/<timestamp>/`로 이동
  - `context/messages.jsonl`이 50MB 초과 시 분할 권고만 표시(자동 변경 없음)
  - `usage.db`는 Vacuum 권고만 표시(외부 도구 필요)

## 레이트 리밋/폭주 대응(요약)
- 이머전시 실행 래퍼 사용:
```
pwsh -ExecutionPolicy Bypass -File tools/codex_emergency.ps1 -- codex <기존_인자들>
```
- 권장 설정: `CODEX_RPS=0.3`, `CODEX_MAX_TOKENS=2500`, 재시도 8회(지수 백오프)

## 프리뷰/검증
- 변경 프리뷰: `invoke review` 또는 `git status && git diff`로 확인
- 점검 완료 후 원상복구는 불필요(본 스크립트는 추가-only, 기본 읽기 전용)

