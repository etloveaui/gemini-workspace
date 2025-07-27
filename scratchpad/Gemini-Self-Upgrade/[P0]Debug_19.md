# \[P0]Debug\_19.md — `test_wip_commit_protocol` 최종 해결 지시서

> **당신(CLI/자동화 에이전트)에게 내리는 명령서입니다.**
> 본 문서는 지금까지 CLI가 수행한 작업과 실패 원인을 정리하고, 재현/수정/검증 절차를 “한 번에” 끝낼 수 있도록 설계되었습니다.
> 현재 상황: **9개 중 7 PASS / 1 FAIL (`test_wip_commit_protocol`) / 1 SKIP**.

---

## 0. 목표

1. `tests/test_core_systems.py::test_wip_commit_protocol` **100% PASS**.
2. 같은 유형의 오류(Invoke Context 타입, subprocess/WinError 123, mock 누락 등) **재발 방지**.
3. “로그 파일 작성 루프” 문제를 차단할 **안정적인 비상 로그 작성 프로세스** 수립.

---

## 1. CLI가 지금까지 한 핵심 작업 요약

* **테스트 수정 시도**

  * `invoke_cli` 픽스처로 subprocess 호출 → WinError 123 / CalledProcessError 다수 발생.
  * `MockContext` 만들어 `wip()` 직접 호출 → Invoke가 Context 타입 검사로 TypeError.
  * 다시 subprocess로 회귀 → cwd/경로 문제 재발.
  * `_runner_run_command`를 mock 하여 git commit 인자 캡처 시도 → 도중 변수 정리 실패(NameError) 등으로 실패.
* **로그/보고서 작성**

  * `[P0]_Debug_17/18` 로그 작성 시 파일 읽기/쓰기 반복 → "potential loop detected" 메시지 다수 발생.
* **현재 상태**

  * 나머지 테스트(7 PASS, 1 SKIP)는 정상.
  * 실패 테스트는 git commit 실행 검증 로직만 문제.

---

## 2. 문제 정의 & 근본 원인

| 구분 | 증상                                  | 직접 원인                                           | 깊은 원인/맥락                                        |
| -- | ----------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| A  | TypeError: Task expected a Context… | MockContext 전달                                  | Invoke는 첫 인자 타입을 엄격히 검사 (`isinstance(Context)`) |
| B  | WinError 123 / CalledProcessError   | `" ".join(args)` + `shell=True` + Windows 경로/한글 | 문자열 커맨드 + shell=True 조합은 Windows에서 취약           |
| C  | NameError(mock\_ctx)                | 테스트 리팩토링 중 변수 삭제 누락                             | 반복 편집으로 테스트 본문 일관성 깨짐                           |
| D  | 로그 작성 시 루프 메시지                      | 동일 파일 반복 읽기/쓰기 & 도구 호출 반복                       | 비상 로그 생성 프로세스가 안정화되지 않음                         |

---

## 3. 해결 전략 개요

### 3.1 테스트 측면: **안정적으로 Invoke를 호출 + Git 커밋 호출만 Mock**

* **Program.run("wip", exit=False)** 사용 (실제 Invoke 컨텍스트 확보)
* `monkeypatch.chdir(repo_path)`로 CWD 고정 → 경로 불일치 방지
* `_runner_run_command` (또는 `scripts/runner.run_command`)를 **mock**:

  * 실제 git 호출 막고, 호출 인자 기록만.
  * 따라서 WinError 123, git 환경 의존성 제거.

### 3.2 프로덕션 코드 측면: **runner에서 `subprocess.run(args, shell=False)`로 고정**

* 문자열 조합 제거 → OS가 인자 파싱.
* Windows 특성상 shell=True 피함.

### 3.3 로그 작성 절차 표준화

* 한 번에 작성 → 한 번만 파일 저장.
* 템플릿 기반으로 “작성 → 커밋” 패턴 적용.
* 반복 읽기/쓰기 금지. (필요 시 diff만 포함)

---

## 4. 구체적 실행 단계 (CLI가 지금 바로 할 일)

### Step 0. 브랜치 분리 & WIP 커밋

```bash
git checkout -b fix/test_wip_commit_protocol
invoke wip -m "Start Debug_19: fix test_wip_commit_protocol"
```

### Step 1. `runner` 계층 수정 (재발 방지용)

**파일 위치 예시:** `scripts/runner.py` 또는 `tasks.py`에서 사용하는 래퍼

```python
# scripts/runner.py (없다면 새로 만들고, tasks.py에서 import해서 사용하거나
# 기존 tasks._runner_run_command를 이런 식으로 변경)

import subprocess

def run_command(task_name: str, args: list[str], cwd, check=True):
    """Safe subprocess wrapper for all shell calls."""
    cp = subprocess.run(
        args,                     # 리스트 그대로 전달
        capture_output=True,
        text=True,
        cwd=cwd,
        check=check,
        shell=False               # 핵심: shell 사용 금지
    )
    return cp
```

* 만약 현재 테스트에서 `tasks._runner_run_command`를 patch하고 있다면, 해당 함수도 동일한 정책으로 수정.
* 이 변경으로 실제 CLI에서도 WinError 123 계열 문제 예방.

### Step 2. 테스트 코드 수정: `tests/test_core_systems.py::test_wip_commit_protocol`

1. **invoke\_cli 픽스처 제거** (이미 제거했다면 유지)
2. **Program.run + monkeypatch.chdir** 사용
3. **\_runner\_run\_command mock**

#### 예시 패치 (의미만 전달, 실제 경로/이름 맞춰 조정)

```python
from invoke import Program
from tasks import ns  # tasks.py의 Collection


def test_wip_commit_protocol(setup_git_repo, monkeypatch):
    """invoke wip 실행 시 git commit -F <temp> 호출되는지 검증"""
    repo_path = setup_git_repo
    (repo_path / "test_file.txt").write_text("updated content")

    # 1) _runner_run_command 모의
    mock_calls = []
    def mock_run_command(task_name, args, cwd, check):
        mock_calls.append({'task_name': task_name, 'args': args, 'cwd': cwd, 'check': check})
        return subprocess.CompletedProcess(args, returncode=0, stdout="", stderr="")
    monkeypatch.setattr("tasks._runner_run_command", mock_run_command)

    # 2) CWD 고정
    monkeypatch.chdir(repo_path)

    # 3) 실제 invoke Program 실행
    program = Program(namespace=ns, version="0.1.0")
    program.run("wip", exit=False)

    # 4) 검증
    git_commit_call = next((c for c in mock_calls if c['args'][:2] == ["git", "commit"]), None)
    assert git_commit_call, "git commit 호출이 없었습니다."
    assert "-F" in git_commit_call['args'], "git commit에 -F 옵션이 없습니다."
```

> **주의**: `import` 경로와 함수명은 실제 코드 기준으로 맞추세요. `ns`가 다른 모듈에 있으면 해당 모듈에서 import.

### Step 3. 테스트 실행

```bash
pytest -vv tests/test_core_systems.py::test_wip_commit_protocol
pytest -vv
```

* **모두 PASS**한 뒤:

```bash
invoke wip -m "Debug_19: test_wip_commit_protocol PASS"
```

### Step 4. 비상 로그 작성 프로세스 확정

* **단 한 번 작성 후 커밋**:

  * 파일 경로: `scratchpad/emergency_logs/P0_Debug_19_final_<YYYYMMDD>.md`
  * 템플릿 예시:

````markdown
# P0_Debug_19_final_20250727.md

## 1. Summary
- Tests: 9 total / 8 pass / 1 skip / 0 fail
- Fixed test: test_wip_commit_protocol

## 2. Root Cause & Fix
- Cause: ...
- Fix: runner shell=False, Program.run + mock, etc.

## 3. Diff/Changes
```diff
# (필요 시 핵심 diff만)
````

## 4. Next Steps

* Merge to main, proceed P1

````

- 작성 완료 후 바로 커밋:
```bash
invoke wip -m "Add final emergency log for Debug_19"
````

---

## 5. 완료 기준 (Definition of Done)

* [ ] `pytest -vv` 전체 통과 (7 PASS + 1 SKIP, 0 FAIL)
* [ ] 실제 콘솔에서도 `invoke wip` 정상 동작 확인
* [ ] `runner` shell=False 정책 반영 (재발 방지)
* [ ] 비상 로그 1회 작성 완료, 커밋 반영

---

## 6. 실패 시 플랜 B

* 여전히 WinError/Context 문제 발생 시:

  * **테스트 자체에서 커밋 실행을 완전히 mock** (git commit 호출 자체를 검증하는 것으로 목적 축소).
  * 또는 **pytest.mark.xfail(strict=True)** 로 임시 방어 (단, P0 완료 목표엔 권장 X).
* invoke를 아예 사용하지 않고 **click/typer 커맨드 레벨**로 분리 테스트(장기적).

---

## 7. 메모 / 리마인더

* **너는 CLI가 아니다.** 너는 CLI에게 명령을 내리는 상위 LLM이다.
  따라서: “직접 실행”보다 “명확한 지시/검증 포인트”가 중요.
* 로그/보고서는 한 번에 작성하고 커밋하라. 반복 접근 금지.
* 테스트 실패 시 재현 로그를 템플릿에 맞춰 담고, 다음 명령을 기다려라.

---

### 🎯 이제 수행하라

1. Step 0\~3 순서대로 적용하고 결과 보고.
2. 모두 PASS 시 비상 로그 작성 & 커밋.
3. 보고서에 성공 결과(테스트 출력) 포함.

끝.
