# \[P0]Debug\_20.md

> **목표:** `test_wip_commit_protocol`의 지속적 실패(WinError 123) 및 부수 이슈를 “근본 원인 제거” 방식으로 해결해 `[P0]` 전 테스트 **완전 통과**.
> **브랜치:** 현재 작업 중인 `debug/18`(또는 `p0/debug_18_fix`) 유지. 머지/리베이스는 최종 PASS 후.
> **언어:** 전 구간 **한글 고정**.
> **문서 보호:** 본 지시서는 삭제 금지(§6 즉시 적용).
> **CLI 로그/대화 초기화 절차 명시(§5)**.

---

## 0. TL;DR (요약 지시)

1. **모든 `subprocess.run` 호출을 `shell=False + 리스트 인자`로 통일.**
2. **`tasks.py::wip`**: PowerShell 호출 제거(또는 테스트 모드 분기) → **순수 Python git 커밋 로직**으로 교체.
3. **`tests/invoke_cli` 픽스처와 `test_wip_commit_protocol`**: 위 규칙으로 정비, 경로는 `str(Path.resolve())`.
4. **문서 삭제 방지 훅/리스트 재확인**, **CLI 로그 정리 스크립트/태스크 완성**.
5. `pytest -vv` → **전부 PASS** 확인 후 보고.

---

## 1. 배경 & 현재 상태

* **환경**: Windows 10, Python 3.12.5, pytest 8.4.x, invoke 기반 자동화.
* **브랜치**: `debug/18` (또는 `p0/debug_18_fix`), 변경 금지.
* **테스트 현황**: 총 10개(예시) 중 8 PASS / 1 SKIP / 1 FAIL.

  * 실패: `tests/test_core_systems.py::test_wip_commit_protocol`
  * 증상: `OSError: [WinError 123] 파일 이름, 디렉터리 이름 또는 볼륨 레이블 구문이 잘못되었습니다`
* **기타 이슈**:

  * 로그 작성/삭제 관련 반복 에러 보고됨(usage.db 파일 잠금, flush 문제 등).
  * 작업지시서 삭제 방지 필요.
  * CLI 대화/임시 로그 clear 절차 요구.

---

## 2. 문제 정의

### 2.1 주요 실패 테스트

* **`test_wip_commit_protocol`**

  * `invoke wip` 호출 중 PowerShell/경로/인자 파싱 문제로 WinError 123 발생.

### 2.2 재발 원인 요약 (다른 LLM 의견 포함)

* **shell=True + 문자열 조합**( `" ".join(args)` )이 Windows에서 파싱 오류 유발.
* pytest 임시 디렉토리(길고 특수문자 포함) + PowerShell 호출 + Git 명령 중첩으로 CreateProcess가 인자를 오판.
* 리스트 인자와 shell=True 혼용, 경로 따옴표 부족, 인코딩·제어문자 등이 중첩.

### 2.3 부수 이슈

* **로그/DB**: usage.db 잠금, 로그 flush/close 미흡.
* **문서 보호**: 삭제 방지 규칙은 일부 적용되었으나 재확인 필요.
* **CLI 상태 정리(clear)**: 스크립트 존재하나 절차 고도화 필요.

---

## 3. 해결 원칙 (결론)

1. **subprocess는 “shell=False + 리스트 인자”로 통일**

   * Windows에서 가장 안전.
   * cmd/powershell 해석기 우회.
2. **PowerShell 의존 최소화**

   * 특히 테스트 경로(Temp)에서는 Python 순정 로직으로 Git 커밋.
3. **경로/인자 모두 `Path.resolve()` → `str()`로 변환**
4. **로그/DB 처리 시 flush, close, gc 고려**
5. **문서 보호 훅 + 테스트 + git 속성 3중 방어**
6. **CLI 로그/대화 정리 프로시저를 자동화 태스크로 명확히 정의**

---

## 4. 작업 항목 (상세 Step-by-Step)

### 4.1 `scripts/runner.py` (혹은 동일 역할 함수) 정비

* **목표:** 모든 외부 명령 실행을 일관된 안전 패턴으로 감싼다.

```python
# scripts/runner.py (예시)
from pathlib import Path
import subprocess
import os

def run_command(task_name: str, args: list[str], cwd=None, check=True):
    """
    안전 실행 래퍼:
    - shell=False
    - 리스트 인자만
    - cwd는 절대경로 str
    """
    abs_cwd = str(Path(cwd).resolve()) if cwd else None
    print(f"[RUN:{task_name}] args={args!r}, cwd={abs_cwd!r}")
    cp = subprocess.run(
        args,
        cwd=abs_cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
        shell=False
    )
    return cp
```

> **주의:**
>
> * PowerShell 스크립트 호출 시에도 리스트로 정확히 분리(`["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "..."]`).
> * 그러나 §4.2에서 PowerShell 자체를 제거할 예정.

### 4.2 `tasks.py::wip` 태스크 교체 (PowerShell → Python 순정 Git 로직)

```python
# tasks.py (일부)
from invoke import task
from tempfile import NamedTemporaryFile
import subprocess, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def python_wip_commit(message: str, cwd: Path):
    cwd = cwd.resolve()
    # 1) 변경사항 스테이징
    subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True, text=True)

    # 2) 임시 메시지 파일
    with NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
        tf.write(message or "auto WIP commit")
        tf.flush()
        temp_path = tf.name

    try:
        subprocess.run(["git", "commit", "-F", temp_path],
                       cwd=str(cwd), check=True, text=True)
    finally:
        os.unlink(temp_path)

@task
def wip(c, message=""):
    """
    PowerShell 호출을 제거한, 순수 Python 버전.
    테스트/실행 환경 모두 동일하게 사용 (권장).
    """
    repo_root = Path.cwd()  # 또는 프로젝트 루트로 고정 필요시 ROOT.parent 등
    python_wip_commit(message, repo_root)
```

> 기존 PowerShell 스크립트(`scripts/git-wip.ps1`)는 그대로 두되, 필요 시만 수동 호출.
> (대안) 테스트 시에만 `CI_TEST_MODE=1` 분기로 Python 로직을 실행해도 됨.

### 4.3 테스트 픽스처/테스트 코드 수정

#### 4.3.1 `invoke_cli` 픽스처

```python
# tests/conftest.py 또는 tests/test_core_systems.py
import sys, subprocess
from pathlib import Path

@pytest.fixture(scope="session")
def invoke_cli():
    def _run(command_args, cwd):
        cmd = [sys.executable, "-m", "invoke"] + command_args
        result = subprocess.run(
            cmd,
            cwd=str(Path(cwd).resolve()),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            check=True,
            shell=False
        )
        return result.stdout, result.stderr
    return _run
```

#### 4.3.2 `test_wip_commit_protocol` 본문

```python
def test_wip_commit_protocol(invoke_cli, setup_git_repo):
    repo_path = setup_git_repo

    # 더미 변경
    (repo_path / "test_file.txt").write_text("updated content", encoding="utf-8")

    # invoke wip 실행
    stdout, stderr = invoke_cli(["wip", "--message", "pytest wip commit"], cwd=repo_path)
    assert stderr.strip() == "", f"invoke wip stderr: {stderr}"

    # 실제 커밋 메시지 확인
    log_msg = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True
    ).stdout.strip()

    assert "pytest wip commit" in log_msg or "auto WIP" in log_msg
```

> **포인트**
>
> * `invoke_cli`와 동일한 규칙(shell=False + list)
> * 메시지 인자 분리: `["wip", "--message", "pytest wip commit"]`

### 4.4 pytest 임시 디렉토리 경로 단축(필요 시)

* 경로 길이 문제가 의심되면:
  `pytest --basetemp=C:\tmp\pytest` 와 같이 짧은 경로 지정.
* 또는 픽스처에서 repo 생성 경로를 명시적으로 짧은 곳으로 잡기.

### 4.5 로그/DB(usage.db) 동기화 문제 개선

* **usage\_tracker.py**: 이미 `conn.close()` 있음.
* 테스트 teardown에서 사용 후 `gc.collect()` + `time.sleep(0.1)` 정도 지연 필요 시 적용.
* `sqlite3` 잠금 문제 발생 시, WAL 모드 고려:

  ```python
  cursor.execute("PRAGMA journal_mode=WAL;")
  ```

### 4.6 문서 삭제 방지(3중 방어)

1. **.no\_delete\_list** 파일에 다음 경로 포함

   * `docs/debug/[P0]Debug_20.md`
2. **.githooks/pre-commit** 훅에서 `scripts/check_no_delete.py` 실행

   * 삭제/이동 감지 시 커밋 중단
3. **테스트 케이스 유지**

   ```python
   def test_debug20_doc_exists():
       assert Path("docs/debug/[P0]Debug_20.md").exists()
   ```
4. (선택) 로컬 보호

   * `git update-index --skip-worktree docs/debug/[P0]Debug_20.md`
   * Windows: `attrib +R docs\debug\[P0]Debug_20.md`

### 4.7 CLI 대화/로그 정리 절차 확정

* **대상**: emergency\_log\_\*.md, scratchpad/emergency\_logs/, temp run logs, old debug markdown 등
* **자동화 스크립트**: `scripts/clear_cli_state.py`

  * 삭제 전 `logs/ARCHIVE_YYYYMMDD/`로 이동
  * 이동 후 커밋(`invoke wip --message "archive logs"`)
* **태스크**: `invoke clean-cli`

  * 실행 순서 명확히 문서화(README 또는 HUB.md):

    1. `invoke clean-cli`
    2. `pytest -vv`
    3. `invoke end`

---

## 5. 검증 & 리포트

1. **수정 적용 후**

   * `pytest -vv` 실행 → 모든 테스트 PASS 확인.
   * 특히 `test_wip_commit_protocol` 성공 여부 캡처.
2. **로그 제출**

   * 변경 파일 목록(`git status -s`)
   * 마지막 테스트 결과 출력 첨부
   * 문서 보호 훅 동작 스크린샷/로그(삭제 시도 → 커밋 실패 메시지)
3. **CLI 로그 정리 실행 결과**

   * 정리된 파일 위치, 커밋 메시지 기록

---

## 6. 문서 보호 규칙 (본 문서)

* **파일명**: `docs/debug/[P0]Debug_20.md`
* **삭제 금지 규칙**:

  * `.no_delete_list`에 추가
  * pre-commit 훅에서 체크
  * 테스트로 존재 여부 검증
* **수정 정책**:

  * 내용 변경은 가능하나, 삭제는 불가
  * 변경 시 하단 “Revision” 섹션에 변경 이력 추가

---

## 7. 체크리스트

| 항목                             |  상태 | 비고    |
| ------------------------------ | :-: | ----- |
| runner.py shell=False 전환       |  ☐  |       |
| tasks.py::wip Python화          |  ☐  |       |
| invoke\_cli 픽스처 수정             |  ☐  |       |
| test\_wip\_commit\_protocol 수정 |  ☐  |       |
| pytest 경로 단축(필요 시)             |  ☐  |       |
| usage.db 동기화 점검                |  ☐  |       |
| 문서 삭제 방지 3중 방어                 |  ☐  |       |
| clean-cli 태스크/스크립트 검증          |  ☐  |       |
| 전체 테스트 PASS                    |  ☐  | 로그 첨부 |
| 결과 리포트 제출                      |  ☐  |       |

---

## 8. 부록: 빠른 디버깅 팁

* WinError 123 재발 시:

  * 실제 실행된 `args` 로그를 파일에 기록 → CMD에서 직접 붙여넣어 실행 테스트
  * `print(repr(args))`, `print(cwd)`
* PowerShell 호출이 꼭 필요하다면:

  * `["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script, "-Message", msg]` 리스트로
  * `shell=False` 유지
* 경로 길이 이슈 추정 시:

  * `os.path.getsize(cmd_str)` / `len(cmd_str)` 확인, 8.3 짧은 경로(WinAPI) 사용 고려

---

## Revision

* **v1 (YYYY-MM-DD HH\:MM)**: 최초 작성.
* 이후 변경 시 아래에 항목 추가.

---

**끝.**

> 본 문서는 즉시 `docs/debug/[P0]Debug_20.md`로 저장하고, §6의 보호 조치를 적용한다.
> 모든 테스트 PASS 후 결과를 본 문서 하단 Revision에 기록하라.
