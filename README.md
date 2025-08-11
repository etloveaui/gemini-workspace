# Multi‑Agent Workspace (Gemini + Codex)

이 워크스페이스는 Windows/Invoke 기반으로 Gemini와 Codex를 함께 사용하도록 구성되어 있습니다.

## 빠른 시작
- 의존성 설치: `venv\Scripts\pip.exe install -r requirements.txt`
- 시스템 시작: `venv\Scripts\python.exe -m invoke start`

## 에이전트 전환/상태
- 상태 확인: `invoke agent.status`
- 전환: `invoke agent.set --name gemini|codex`
- 프로세스 별 라벨: PowerShell에서 `($env:ACTIVE_AGENT='codex'); invoke start`

## 문서
- 운영 표준: `GEMINI.md` (섹션 13: 멀티 에이전트)
- 멀티에이전트 가이드: `AGENTS.md`

참고: 비밀·토큰은 커밋 금지(`.gemini/*`, `secrets/*`). 모든 명령은 레포 내부 경로에서 실행하세요.
