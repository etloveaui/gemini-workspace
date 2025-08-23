# 2025-08-22 GitHub Desktop 커밋 인코딩 이슈 분석 및 가이드

- 작성자: Codex
- 위치: c:\\Users\\etlov\\multi-agent-workspace\\communication\\claude\\
- 주제: GitHub Desktop에서 커밋 시 메시지 깨짐/이상 출력 및 커밋 실패 체감 현상

## 요약
- 증상: 커밋 시 출력 글자가 깨지거나(모지바케) 경로만 길게 찍히고, 커밋/푸시 과정이 불안정하게 느껴짐.
- 주요 경로: `communication/codex/20250822_prompt1.md`
- 분류: Git 에러가 아니라, “훅 출력/상태 출력의 인코딩/표시 문제 + 미커밋 변경 알림”이 섞여 보이는 현상.

## 재현 조건(관측)
- GitHub Desktop 사용, Windows 로케일(cp949/CP1252 등) + UTF-8 혼용 환경.
- 리포지토리 내 커스텀 pre-commit 훅 사용: `.githooks/pre-commit`
  - 훅 내부에서 Python 스크립트 실행: `scripts/hooks/precommit_secrets_guard.py`, `scripts/check_no_delete.py`
  - guard 스크립트가 UTF-8 출력(이모지 포함) → GitHub Desktop/호출 셸이 ANSI 코드 페이지로 해석 시 글자 깨짐.
- 커뮤니케이션 프롬프트 파일이 자주 수정되나, 종종 미커밋 상태로 남음 → 상태 출력에 해당 경로가 반복 노출.

## 탐지된 사실
- `core.hooksPath` = `.githooks` (커스텀 훅 경로 활성)
- `.githooks/pre-commit`는 Bash 스크립트이며, GitHub Desktop 내부 셸/환경 변수에 따라 UTF-8 보장이 안 될 수 있음.
- `precommit_secrets_guard.py`는 내부적으로 git 호출 시 `encoding='utf-8'`로 처리하나, 최종 출력이 ANSI 환경에서 깨질 수 있음.
- 차단 규칙은 주로 `projects/`/`.gemini/` 민감 영역이며, `communication/codex/*.md`는 차단 대상이 아님(단, 훅의 일반 출력/경고가 화면에 보일 수 있음).

## 왜 글씨가 깨져 보이는가?
- Windows 기본 코드페이지(예: CP949)와 훅/파이썬이 출력하는 UTF-8/유니코드 문자열 간 인코딩 미스매치.
- 일부 메시지에 이모지(예: U+1F6D1)를 포함 → ANSI 렌더러에서 깨짐 유발.
- 결과적으로 “에러처럼 보이나” 실제로는 상태/경고 메시지 또는 단순 경로 에코에 가까움.

## 당장 쓸 수 있는 해결책(운영 절차)
1) 변경 반영(권장)
- GitHub Desktop → Changes에서 해당 파일만 체크 → 커밋 메시지: `comm: sync codex prompt1` → Commit to main → Push origin.

2) 변경 폐기(불필요 변경일 때)
- 대상 파일 우클릭 → Discard changes → Push origin.

3) 임시 보관
- 메뉴 Branch → Stash all changes → Push → 필요 시 Branch → Pop stash.

4) 훅 임시 우회(긴급 상황용)
- Windows 환경변수에 `AGENTS_SKIP_HOOKS=1` 설정 → GitHub Desktop 재시작 → 커밋/푸시 → 작업 끝나면 변수 제거.
  - 경로: 설정 앱 → 시스템 → 정보 → 고급 시스템 설정 → 환경 변수 → 사용자 변수 추가.

5) 상태 노이즈 무시
- 해당 출력이 단순 경고/상태일 수 있으므로, 실제로 push 결과만 확인. push가 성공하면 기능상 문제는 없음.

## 근본 개선안(향후 변경 제안)
- 훅 출력 표준화
  - 이모지 제거(ASCII만 사용), 메시지 최소화.
  - Python 실행에 `-X utf8` 또는 환경변수 `PYTHONUTF8=1`/`PYTHONIOENCODING=UTF-8` 강제.
  - `.githooks/pre-commit`에서 UTF-8 locale 강제(가능 시) 또는 출력을 ASCII로 제한.
- 커뮤니케이션 프롬프트 변경 정책
  - 세션 종료 시점 묶음 커밋으로 정리 → push 직전 잔여 변경 최소화.
- GitHub Desktop 전용 가이드 추가
  - “Changes에서 커뮤니케이션 파일만 선택 커밋” 단축 절차 문서화.

## 체크리스트
- [ ] push가 실제로 완료되는지(원격에 반영) 확인.
- [ ] projects/ 경로가 포함되지 않았는지 확인(독립성 규칙).
- [ ] 훅 경고가 기능을 차단하는지(Exit code) 여부 구분.
- [ ] 인코딩 이슈는 메시지 가독성 문제이지 데이터 손상은 아님(커밋 내용은 UTF-8 원문 유지).

## 결론
- 현재 문제의 본질은 “훅/상태 출력의 인코딩 호환 + 미커밋 변경 노출”입니다.
- GitHub Desktop에서는 해당 파일을 선택 커밋하거나 변경 폐기만 해도 체감 문제가 사라집니다.
- 장기적으로 훅 출력(이모지 제거/UTF-8 강제) 표준화 패치를 제안합니다. (필요 시 Codex가 안전 범위 내에서 일괄 반영 가능합니다.)

