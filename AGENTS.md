# AGENTS.md — Multi‑Agent Workspace (Codex v0.1)

## 목적
- 동일 워크스페이스에서 여러 CLI 에이전트(Gemini, Codex, 향후 Claude)를 공존·전환 가능하게 운영하기 위한 최소 지침을 제공합니다.
- 본 문서는 GEMINI.md의 운영 원칙을 최대한 재사용합니다.

## 운영 원칙
- Windows-first, Python 직접 호출, UTF-8 고정(표준 입출력).
- 레포 내부에서만 파일 작업 수행(외부 경로는 원칙적 제한).
- 비밀·토큰은 커밋 금지(.gemini/*, secrets/* 등). 유출 시 키 회전·이력 정리 준수.

## 언어/프리뷰/구축 원칙 (Codex 확장)
- 언어: Codex는 모든 대화·로그·설명을 한국어로만 수행합니다.
- 프리뷰: 코드 변경 전/후 항상 프리뷰를 제공합니다.
  - 빠른 프리뷰: `invoke review`로 `git status`와 변경 파일 목록 확인
  - 필요 시 세부 프리뷰: `git diff <파일>`로 라인 단위 변경 확인
- 미구현 요청 처리: 사용자가 요구한 기능이 시스템에 없으면
  1) 간단 분석 → 2) 구축 계획을 문서(본 파일 또는 별도 문서)에 기록 → 3) 사용자 승인 후 구현합니다.
- 태스크 활용: 가능하면 Invoke 태스크로 작업(감시/인박스/프리뷰/허브 전송)을 일관되게 실행합니다.

## Git 훅(Pre-commit) 정책
- 전역 토글: `.agents/config.json`의 `hooks.enabled`로 전체 훅 on/off.
- 대화형 프롬프트 회피: `invoke commit_safe --skip-diff-confirm` 또는 환경변수 `SKIP_DIFF_CONFIRM=1`.
- 관리 태스크: `invoke git.set-hooks --on|--off`.

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

## HUB 작업 수명주기(자동 관리)
- 시작 전 등록: 작업을 시작하기 전에 `agents_hub/queue`에 태스크를 등록합니다(Invoke 사용 시 `invoke hub.send`).
- 클레임: 동일 에이전트가 즉시 클레임하여 `processing/<agent>/`로 이동합니다(`invoke hub.claim`).
- 완료 보고: 완료 시 `archive/<날짜>/success|failed/`로 이동하며 노트를 남깁니다(`invoke hub.complete`).
- 비대화식 환경: 인코딩/쉘 이슈가 있을 경우 브로커 스크립트 직접 호출 또는 큐/아카이브 JSON 파일을 원자적으로 기록하여 일관성 유지.

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

### 교차 에이전트 메시징(v0.1)
- 저장소: `context/messages.jsonl` (JSON Lines, UTF-8)
- 필드: `{ "ts": "UTC ISO", "from": "gemini|codex", "to": "codex|gemini|all", "tags": ["note"], "body": "..." }`
- 남기기(권장): `invoke agent.msg --to codex --body "메시지" --tags "decision,context"`
- 보기: `invoke agent.inbox --agent codex --unread --limit 20` → `.agents/inbox/codex.md` 갱신
- 읽음처리: `invoke agent.read --agent codex`

#### 실시간 감시(옵션)
- 감시 실행: `invoke agent.watch --agent codex --interval 5` (Ctrl+C로 종료)
- 자동 확인 응답: `invoke agent.watch --agent codex --interval 5 --ack`
- 비침투형: 감시는 별도 터미널에서 실행 권장. 작업 흐름은 방해받지 않습니다.

참고: Invoke 사용이 어려운 에이전트(Gemini 등)는 `context/messages.jsonl`에 위 필드를 한 줄 JSON으로 append 하면 됩니다.

### 빠른 시작(권장)
- `invoke start --fast` : 빠른 브리핑(Doctor/HUB/인덱스 스킵, Git 변경 요약, 에이전트 표시)
- 에이전트 지정 실행: `($env:ACTIVE_AGENT='codex'); invoke start --fast`
- 전체 시작 + 백그라운드 인덱싱: `invoke start` (기본값은 인덱스 백그라운드 실행)
# 업데이트 요약 (v0.1.1)

- 워처 단시간 실행: `invoke agent.watch --agent codex --interval 5 --duration 10`
  - 자동 확인 응답: `--ack` 병행. 예) `... --ack --duration 5`
- Gemini Fallback(Invoke 불가 시): `context/messages.jsonl`에 한 줄 JSON 추가로 요청 전달
  - 예: `{"ts":"2025-08-11T12:34:56Z","from":"gemini","to":"codex","tags":["task","context"],"body":"README 섹션 A 수정 요청"}`
  - Codex 확인: `invoke agent.watch --agent codex --ack --duration 5`
- MCP 통합(선택): 사용자 환경에만 설정
  - Codex CLI(예): `~/.codex/config.toml`에 MCP 서버 등록
    ```
    [mcp_servers.snyk-security]
    command = "npx"
    args = ["-y", "snyk@latest", "mcp", "-t", "stdio"]
    ```
  - Gemini CLI: MCP 지원 내장. 레포 수준에서는 메시지 허브/Invoke만 사용
  - 참고: `scratchpad/20250811_CLI_upgrade_MCP.md`
## Self-Update Protocol(자가 업데이트)
- 정책 공통 참조: `docs/SELF_UPDATE_POLICY.md`를 따른다(주기/범위/안전장치).
- 현재 범위: 자동 적용 OFF, 제안 생성만 허용(`invoke auto.scan` → `invoke auto.propose`).
- 적용 시나리오: 리뷰/미리보기 후 `invoke git.commit_safe`로 수동 적용, 훅 기본 OFF 유지.
