# AGENTS.md — Multi‑Agent Workspace (Codex v0.1)

## 목적
- 동일 워크스페이스에서 여러 CLI 에이전트(Gemini, Codex, 향후 Claude)를 공존·전환 가능하게 운영하기 위한 최소 지침을 제공합니다.
- 본 문서는 GEMINI.md의 운영 원칙을 최대한 재사용합니다.

## 운영 원칙
- Windows-first, Python 직접 호출, UTF-8 고정(표준 입출력).
- 레포 내부에서만 파일 작업 수행(외부 경로는 원칙적 제한).
- 비밀·토큰은 커밋 금지(.gemini/*, secrets/* 등). 유출 시 키 회전·이력 정리 준수.

## Codex 사용 지침 (VS Code PowerShell 7)
- 워크스페이스 루트에서 Codex CLI를 실행해 파일을 읽고 수정합니다.
- 출력이 길 때
  - 스크롤백 확장: VS Code Settings → Terminal: Integrated: Scrollback (예: 50000).
  - 로그 저장: `Start-Transcript .\transcript.txt` → 작업 후 `Stop-Transcript`.
  - 파이프 저장: `invoke <task> | Tee-Object .\last_run.log`.

### 동시 실행 팁
- 두 터미널에서 병렬 실행 가능. 같은 파일 동시 수정은 피하세요.
- 에이전트 라벨링: 프로세스 단위로 `ACTIVE_AGENT=codex`(또는 `gemini`) 환경변수를 설정하면 전역 스위치를 건드리지 않고 라벨만 분리됩니다.
  - 예: PowerShell `($env:ACTIVE_AGENT='codex'); invoke start`
- 내부 DB(SQLite)는 WAL 모드로 설정되어 동시 기록 안정성이 향상되었습니다.

## 파이썬/경로 규칙
- venv가 있으면 `venv/Scripts/python.exe`, 없으면 `sys.executable` 사용(Windows 기준).
- PowerShell 래핑을 피하고 Python 프로세스를 직접 호출합니다.

## 공존 전략(초기)
- 현 단계(v0.1): 문서화 중심. Codex는 이 레포 내에서 독립적으로 작업하며, 기존 Invoke 태스크는 그대로 사용합니다.
- 예정(v0.2): 에이전트 전환 스위처 추가(`.agents/config.json`, `scripts/agent_manager.py`, `invoke agent.status/set`).
- 예정(v0.3): 태스크 분기(예: search/refactor/multimodal를 에이전트별 Provider로 선택) — 사용자 승인 후 단계적 적용.

## 로깅
- 기본: `scripts/runner.py`를 통해 실행된 Invoke 태스크는 `usage.db`에 기록됩니다.
- Codex 단독 작업을 별도 기록하려면 필요 시 수동 로깅을 사용할 수 있습니다.
  - 예: 파이썬 원라이너로 요약 기록하기
    - `python -c "from scripts.usage_tracker import log_usage; log_usage('codex-note','manual','AGENT=codex')"`

## 디렉터리/보안 합의
- `.gemini/` 내 자격증명·토큰류는 항상 로컬 전용, 커밋 금지.
- `projects/`는 로컬 전용 작업 공간으로 유지(커밋 금지).

## 확장 가이드
- 새 에이전트(예: Claude) 추가 시
  - 운영 원칙 상속(GEMINI.md의 Windows/UTF-8/보안 규칙).
  - `.agents/config.json`의 `active` 값과 허용 리스트에 에이전트명을 추가.
  - 필요 시 전용 문서(`CLAUDE.md`)로 세부 지침 분리.

## 현재 상태 요약
- 구현됨: 문서(이 파일), 기존 태스크·로깅 체계 유지.
- 미구현(예정): 에이전트 스위처, 태스크 분기, DB에 에이전트 컬럼 추가 마이그레이션(선택).

## 참고
- 상세 운영 표준과 절차는 `GEMINI.md`를 따릅니다. Codex 관련 차이점은 본 문서에서만 최소 표기합니다.
