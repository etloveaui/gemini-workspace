# Multi‑Agent Workspace (Gemini + Codex)

이 워크스페이스는 Windows/Invoke 기반으로 Gemini와 Codex를 함께 사용하도록 구성되어 있습니다.

## 빠른 시작
- 의존성 설치: `venv\Scripts\pip.exe install -r requirements.txt`
- 시스템 시작: `venv\Scripts\python.exe -m invoke start`

## AI CLI
- `ai` : 인터랙티브 모드 시작
  - `/exit` 종료
  - `/p <provider>` 제공자 전환(예: claude, gemini)
  - `/save` 대화 내용 저장
- `ai "프롬프트"` : 원샷 질의

## 에이전트 전환/상태
- 상태 확인: `invoke agent.status`
- 전환: `invoke agent.set --name gemini|codex`
- 프로세스 별 라벨: PowerShell에서 `($env:ACTIVE_AGENT='codex'); invoke start`

## 출력 포맷 정책
- 기본으로 최종 출력에 한국어 "근거(요약)" 1–2줄을 덧붙입니다(체인오브소트 비공개, 휴리스틱 설명).
- 비활성화: `($env:OUTPUT_KO_RATIONALE='0'); invoke <task>`

## 문서
- 운영 표준: `GEMINI.md` (섹션 13: 멀티 에이전트)
- 멀티에이전트 가이드: `AGENTS.md`
 - 에이전트 허브: `agents_hub/README.md` (파일 기반 메시지 큐)
 - 사전 Diff 워크플로우: `.edits/` 제안/승인 편집 및 pre-commit diff 확인

## 에이전트 허브(간단)
- 보내기: `invoke hub.send --to gemini --title "작업" --body "설명" --type task`
- 대기열 보기: `invoke hub.inbox --agent gemini`
- 클레임: `invoke hub.claim --agent gemini` → 처리 중으로 이동
- 완료: `invoke hub.complete --id <ID> --status success --agent gemini`

## 사전 Diff 워크플로우(편집 제안)
- 캡처(초안 생성): `invoke edits.capture --file scripts/foo.py` → `.edits/proposals/scripts/foo.py` 생성 후 편집
- 제안 등록: `invoke edits.propose --file scripts/foo.py --from-file C:\path\tmp.txt`
- 미리보기: `invoke edits.diff [--file scripts/foo.py]`
- 적용: `invoke edits.apply [--file scripts/foo.py]`(파일별 확인 프롬프트)
- 폐기: `invoke edits.discard --file scripts/foo.py`

## 커밋 전 Diff 확인(강제)
- pre-commit 훅이 스테이징된 변경의 diff를 출력하고 승인(y/N)을 요구합니다.
- CI/자동화에서 건너뛰기: `SKIP_DIFF_CONFIRM=1`

참고: 비밀·토큰은 커밋 금지(`.gemini/*`, `secrets/*`). 모든 명령은 레포 내부 경로에서 실행하세요.
