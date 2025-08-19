# `[P0]Debug_22.md` 지시서

## 0. 목적

* 남은 경고/잔여 리스크 정리(UTC Deprecation 등)
* 작업 브랜치(`p0/debug_18_fix`)를 **main**에 안전하게 머지
* 사용자가 쉽게 AI/시스템을 다룰 수 있는 **Help/Read 창구 구축**
* 전체 테스트/보호 장치 유지

---

## 1. 현재 상태 요약

* 테스트: **8 PASS / 1 SKIP**, 치명적 에러 없음
* 실패했던 `test_runner_error_logging` 해결 완료
* `.no_delete_list` 최신화됨

---

## 2. 해야 할 일 (To-Do)

### A. 경고 정리 (UTC Deprecation)

1. `datetime.utcnow()` → `datetime.now(timezone.utc)`로 교체
2. 관련 파일: `scripts/runner.py` (로그 타임스탬프 생성 부분)
3. 테스트 재실행하여 경고 없는지 확인

### B. 메인 머지 프로세스

1. 최신 main 동기화

   ```bash
   git checkout main
   git pull origin main
   ```
2. 브랜치 머지

   ```bash
   git checkout p0/debug_18_fix
   git pull origin p0/debug_18_fix
   git checkout main
   git merge --no-ff p0/debug_18_fix
   ```
3. 충돌 해결 → 전체 테스트 실행(`invoke test` or `pytest -vv`)
4. 성공 시 push

   ```bash
   git push origin main
   ```
5. (선택) 태그: `git tag -a p0-done -m "P0 completed"` → `git push origin p0-done`
6. (선택) 작업 브랜치 삭제: `git branch -d p0/debug_18_fix` / `git push origin --delete p0/debug_18_fix`

### C. Help / Read 시스템 구축

**목표:** “어떻게 이 AI/시스템을 쓰는지” 사용자가 즉시 알 수 있는 단일 진입점 제공

#### 1) 문서 레벨

* `docs/HELP.md` 생성 (최소 포함 항목)

  * 주요 명령어/태스크: `invoke start`, `invoke end`, `invoke wip`, `invoke context.build`, `invoke test`, etc.
  * 문제 발생 시 트러블슈팅 FAQ
  * 환경 변수 / 경로 / DB 관련 설명
  * 새 테스트/디버그 지시서 파일 목록과 위치

#### 2) CLI 레벨

* `scripts/help.py` (argparse) 작성

  * `python scripts/help.py` → 기본 도움말
  * `python scripts/help.py task wip` 등 상세 명령어 도움
* `tasks.py`에 `@task(name="help")` 추가 → 내부에서 `python scripts/help.py` 호출

  * `invoke help`로 바로 사용 가능

#### 3) 자동 안내

* `invoke start` 마지막에 HELP 경로/명령어 안내 출력
* `stderr` 발생 시 “도움말 보기: invoke help” 메시지 표준 출력

#### 4) 테스트 추가

* `tests/test_help_system.py` 작성

  * `invoke help` 실행 시 0 exit code & 핵심 섹션 포함되는지 체크

### D. 보호 장치 업데이트

* `[P0]Debug_22.md` 자체를 `.no_delete_list`에 추가
* HUB.md 업데이트(프로젝트 상태/Active tasks 반영)
* 필요 시 `docs/debug` 폴더에 이 파일 복사

---

## 3. 완료 기준 (Acceptance Criteria)

* Deprecation 경고 제거
* main 브랜치에 머지 완료 + 원격 push
* `docs/HELP.md`, `scripts/help.py`, `invoke help` 정상 동작
* 신규 테스트(`test_help_system.py`) 포함 전체 테스트 PASS
* `.no_delete_list`에 `[P0]Debug_22.md` 등록

---

## 4. 롤백 플랜

* 머지 전 태그/브랜치 백업
* HELP 시스템 도입 변경은 독립 스크립트/문서이므로 삭제 시 즉시 원복 가능
* Deprecation 수정은 git revert로 간단히 되돌릴 수 있음

---

## 5. 작업 순서 체크리스트

1. UTC 경고 수정 → 테스트
2. HELP 문서/스크립트 작성 → 테스트
3. `.no_delete_list` & HUB.md 갱신
4. main 병합 → 테스트 → push
5. 태그/브랜치 정리

---

### 추가: 사용성 향상을 위한 제안

* `invoke doctor`: 환경 점검(venv, git, sqlite 파일 유무 등)
* `invoke quickstart`: 첫 사용자를 위한 단계별 안내 출력
* `scripts/interactive_shell.py`: 간단한 질의/명령 실행 콘솔
* README 최상단에 “시작하기 빠른 링크” 제공

---

필요한 추가 세부 코드/스니펫 요청 시 바로 제공하겠습니다.
