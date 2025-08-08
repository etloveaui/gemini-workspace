# \[P0]Debug\_19.md

> **대상 브랜치:** `debug/18` (현 상황 유지)
> **현재 테스트 결과:** 7 PASSED / 1 FAILED (`test_wip_commit_protocol`)
> **작성 언어:** 한글 고정
> **본 문서는 삭제 금지(아래 §6 방어 조치 적용)**

---

## 0. 목적

* `test_wip_commit_protocol` **단일 실패**를 해결하여 `[P0]` 단계 테스트 전부를 통과시킨다.
* 기존 시도(모의 Context, subprocess, invoke.Program 등)로 발생한 오류들을 정리·수정한다.
* 작업지시서(본 문서) 삭제 방지 장치를 구축한다.
* CLI 대화(세션 로그/임시 로그) 정리 방식을 명확히 정의한다.

---

## 1. 현황 정리

1. **브랜치 상태**: `debug/18`에서 작업 중. `test_last_session_cycle` 등 기존 오류는 해결됨.
2. **테스트 결과**: `pytest -vv` 기준 7개 PASS, 1개 FAIL. 실패 테스트는 **`tests/test_core_systems.py::test_wip_commit_protocol`**.
3. **최근 실패 로그 핵심**

   * TypeError (Context 타입 문제) → MockContext 사용으로 invoke 내부 타입 체크 실패.
   * subprocess 호출 시 `OSError: [WinError 123]` (Windows 경로/공백/인코딩 + `" ".join(args)` & `shell=True` 조합 문제).
   * NameError(`mock_ctx` 미정의) 등 중간 수정 잔여물.

---

## 2. 목표

* **테스트 관점 목표**: `test_wip_commit_protocol`이 안정적으로 통과하도록 **테스트 코드와 실행 경로**를 정비.
* **코드 관점 목표**: `scripts/runner.py` 혹은 `_runner_run_command` 계층에서 **인자 전달/경로 처리**를 안전하게 수정.
* **프로세스 관점 목표**: 문서 삭제 방지, CLI 로그 정리 절차 확립.

---

## 3. 원인 가설 & 해결 전략

### 3.1 원인 가설 요약

1. **서브프로세스 실행 인자 처리 문제**

   * `" ".join(args)`, `shell=True` 사용 → Windows에서 경로/따옴표 처리 실패.
   * `subprocess.run()`에 list 인자를 주면서 `shell=False`로 해야 안전.
2. **테스트 내 Context/CLI 호출 혼선**

   * invoke Task는 `Context` 필요. 직접 호출 시 Mocking이 불완전.
   * 반대로 subprocess로 invoke 호출 시에는 runner 내부 구현이 불안정.
3. **중간에 변경된 테스트 로직 유지 불일치**

   * `invoke_cli` 픽스처/MockContext 방식 혼재 → NameError/TypeError 유발.

### 3.2 해결 전략

* **전략 A (권장)**: **러너 계층 수정 + subprocess 방식 유지**

  * `scripts/runner.py`(또는 `tasks._runner_run_command`)에서 **shell=False, args=list**로 일관 처리.
  * 테스트는 원래 의도대로 `invoke_cli` 픽스처로 `invoke wip`를 실행 → 커밋 성공 여부를 Git 로그로 검증.

* **전략 B (차선)**: **테스트에서 직접 Task 호출**

  * `invoke.Context` 실제 객체를 생성하여 전달.
  * `_runner_run_command`를 monkeypatch하여 커밋 명령 인자만 캡처 후, Git 직접 호출 없음.
  * 하지만 이 경우 실제 Git 커밋 검증 신뢰도가 떨어질 수 있음(목표 달성만 확인시 OK).

본 문서는 **전략 A**를 기본으로 지시한다. (실제 환경과 동일 흐름 유지 & 충돌 원인 제거)

---

## 4. 작업 지시 (실행 단계)

### 4.1 러너 수정

**대상 파일**: `scripts/runner.py` (또는 동일 기능 모듈. 현재 로그상 `scripts/runner.py` 또는 `tasks._runner_run_command` 존재)

1. **현재 문제 코드 예시 (가정)**

   ```python
   cp = subprocess.run(" ".join(args), capture_output=True, text=True,
                       cwd=cwd, check=check, shell=True)
   ```

2. **수정 지시**

   ```python
   import subprocess

   def run_command(task_name: str, args: list[str], cwd, check: bool):
       # 1) args는 리스트 그대로 전달
       # 2) shell=False (기본), Windows에서도 안전
       cp = subprocess.run(
           args,
           capture_output=True,
           text=True,
           cwd=cwd,
           check=check
       )
       return cp
   ```

3. **tasks.py 내 `_runner_run_command`가 별도라면 동일하게 수정**

   * `shell=True`, `" ".join(args)` 제거
   * 오류 처리/로그 기록 로직은 유지.

### 4.2 테스트 수정 (`test_wip_commit_protocol`)

**대상 파일**: `tests/test_core_systems.py`

1. **invoke\_cli 픽스처 재사용**

   * `def test_wip_commit_protocol(invoke_cli, setup_git_repo):` 형태로 복구.
   * `cwd=repo_path` 명시 전달.
2. **테스트 로직**

   * repo에 더미 변경 → `git add .`는 wip 태스크 내에서 처리되거나 runner가 실행하므로 불필요.
   * `stdout, stderr = invoke_cli(["wip"], cwd=repo_path)`
   * 종료 코드 0 확인.
   * 이후 `git log -1 --pretty=%B` 등으로 커밋 메시지 파일(-F) 사용 여부 확인 OR 커밋 생성 여부만 확인.
3. **폴링 필요 시**

   * OS/IO 지연 문제 대비, 0.1s 간격, 최대 1초 재시도 후 실패 처리.

**예시 코드 스니펫 (핵심 부분만)**:

```python
def test_wip_commit_protocol(invoke_cli, setup_git_repo):
    repo_path = setup_git_repo
    (repo_path / "test_file.txt").write_text("updated content")
    
    # invoke wip 실행
    stdout, stderr = invoke_cli(["wip"], cwd=repo_path)
    assert "WIP" in stdout or stderr == "", f"invoke wip failed: {stderr}"

    # 커밋 실제 생성 확인
    import subprocess
    log_msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    assert "WIP" in log_msg or "auto WIP" in log_msg, \
        f"Last commit message not found or invalid: {log_msg}"
```

> ※ 커밋 메시지 패턴은 실제 wip 스크립트 메시지 규칙에 맞춰 수정.

### 4.3 테스트 헬퍼/픽스처 점검

* `invoke_cli` 픽스처 내부에서 `subprocess.run(["invoke", ...], cwd=repo_path, ...)`가 동작하도록 재확인.
* 출력 캡처 시 `text=True`, `encoding='utf-8'` 설정(Windows 인코딩 이슈 예방).

### 4.4 잔여 Mock 코드 제거

* `MockContext`, `mock_ctx`, `_runner_run_command` monkeypatch 등 이전 해결 시도 잔여물을 제거.
* 남겨야 할 모킹은 **runner 계층 수정 후엔 거의 불필요**.

---

## 5. CLI 대화/로그 정리 절차

1. **세션/대화 로그 위치 파악**

   * 예: `scratchpad/emergency_logs/`, `logs/`, `emergency_log_*` 등.
2. **정리 정책**

   * `[P0]` 완료 시점에 **불필요한 임시 로그만** 삭제.
   * 삭제 전 반드시 `logs/ARCHIVE_YYYYMMDD/`로 이동 후 git 커밋.
3. **CLI 초기화(대화 클리어) 스크립트 추가 (선택)**

   * `scripts/clear_cli_state.py`: 임시 파일/세션 캐시 폴더 삭제, but 중요한 지시서 제외.
   * `invoke clean-cli` 태스크로 실행 가능하게 추가.

---

## 6. 작업지시서(본 문서) 삭제 방지 조치

아래 3중 방어 중 최소 2개 이상 적용:

1. **Git 훅(프리커밋/프리푸시)**

   * `.githooks/pre-commit` 혹은 `scripts/check_no_delete.py` 호출:

     * `.no_delete_list` 파일에 적힌 경로(예: `docs/debug/[P0]Debug_19.md`)가 Git diff에서 삭제/이동/이름변경되면 **commit 중단**.

2. **테스트에 방어 로직 추가**

   * `tests/test_p0_rules.py`에 다음 테스트 추가:

     ```python
     def test_debug_19_doc_exists():
         from pathlib import Path
         assert Path("docs/debug/[P0]Debug_19.md").exists(), "[P0]Debug_19.md 문서가 삭제됨!"
     ```
   * CI에서 해당 테스트 실패 시 빌드/배포 중단.

3. **파일 권한/속성 설정(로컬)**

   * Windows: `attrib +R docs/debug/[P0]Debug_19.md`
   * Git: `git update-index --skip-worktree docs/debug/[P0]Debug_19.md` (편집 어렵게)
   * 단, 내용 업데이트 필요 시 일시 해제.

---

## 7. 실행 순서 (체크리스트)

1. **브랜치 확인**: `git switch debug/18`
2. **러너 수정**: `scripts/runner.py` 또는 `tasks._runner_run_command`를 §4.1대로 고침
3. **테스트 코드 정비**: `tests/test_core_systems.py::test_wip_commit_protocol`을 §4.2대로 수정
4. **불필요 모킹 제거/픽스처 정비**
5. **문서 방어 장치 추가 (§6)**
6. **로그 정리 스크립트/절차 반영 (§5)**
7. **테스트 실행**: `pytest -vv` → 8/8 PASS 확인
8. **커밋 & 푸시**:

   * 메시지 예: `"[P0]Debug_19: fix wip protocol test & add doc guard"`
9. **결과 보고**:

   * 테스트 로그 요약
   * 수정된 파일 목록
   * 방어장치 동작 확인 여부

---

## 8. 플랜 B (전략 A 실패 시)

* **전략 B 적용**: 테스트에서 직접 Task 호출 + `_runner_run_command` 모킹

  * 단, 실제 Git 커밋 검증 대신 `mock_calls`로 인자 확인
  * 이후 별도 통합 테스트에서 실제 커밋 검증

**예시 핵심**:

```python
from invoke import Context
from tasks import wip

def test_wip_commit_protocol_mock(setup_git_repo, monkeypatch):
    repo_path = setup_git_repo
    (repo_path / "test_file.txt").write_text("updated content")

    calls = []
    def fake_run(task_name, args, cwd, check):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr("tasks._runner_run_command", fake_run)

    ctx = Context()    # 실제 Context
    ctx.cwd = repo_path

    wip(ctx)

    commit_cmd = [c for c in calls if c[0]=="git" and c[1]=="commit"]
    assert commit_cmd, "git commit not called"
```

---

## 9. 마무리/보고 형식

* **보고 파일**: `scratchpad/emergency_logs/P0_Debug_19_report_<YYYYMMDD>.md` (선택)
* **포맷**:

  * 변경 파일 목록 & Diff 요약
  * 테스트 결과 (전체 PASS 스크린샷 혹은 로그 인라인)
  * 방어 장치 테스트 여부
  * 향후 TODO(예: P1로 이동)

---

## 10. 부록: 체크리스트 요약

* [ ] runner에서 shell=True / " ".join(args) 제거
* [ ] test\_wip\_commit\_protocol, invoke\_cli 픽스처 경로/cwd 확인
* [ ] Git 로그로 커밋 메시지 검증
* [ ] 문서 삭제 방지 훅/테스트 추가
* [ ] CLI 로그 정리 스크립트 작성
* [ ] 8/8 PASS 확인 및 커밋

---

**끝.**
(이 문서는 프로젝트 루트 내 `docs/debug/[P0]Debug_19.md`로 저장하고, §6의 방어 조치 적용을 즉시 수행하라.)
