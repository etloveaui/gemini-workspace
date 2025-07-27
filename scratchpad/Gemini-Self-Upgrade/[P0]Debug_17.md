# \[P0]Debug\_17.md – Gemini CLI 테스트 안정화 & `__lastSession__` 사이클 복구 지시서

> **목표:** `tests/test_p0_rules.py::test_last_session_cycle` 를 100% 통과시키고, 실제 워크스페이스에서도 `tasks.start/end` 실행 시 `docs/HUB.md` 내 `__lastSession__` 블록 생성/제거가 **항상** 올바르게 반영되도록 한다.

---

## 0. 성공 기준 (Success Criteria)

1. `pytest -k test_last_session_cycle -vv` 및 `invoke test` 실행 결과 **모든 테스트 통과**.
2. `invoke end` 후 HUB.md 에 `__lastSession__:` YAML 블록이 정확히 1개 생성됨.
3. `invoke start` 후 HUB.md 에 `__lastSession__:` 블록이 **완전히 제거됨**.
4. Windows 환경/pytest/invoke 병행 사용 시에도 파일 동기화 문제(race condition)가 재발하지 않음.

---

## 1. 환경 / 전제 조건

* **OS:** Windows (기본), 단 pytest/invoke 는 Python 서브프로세스에서 동작할 수 있음.
* **작업 루트:** `%USERPROFILE%/gemini-workspace` (혹은 현재 저장소 루트). 외부 경로 접근 금지.
* **테스트 파일:** `tests/test_p0_rules.py`
* **핵심 스크립트:** `scripts/hub_manager.py`, `tasks.py`, `scripts/runner.py`
* **DB 파일:** `usage.db` – 테스트 중 잠금/권한 오류 빈발. 필요 시 백업/삭제 로직 포함.

---

## 2. 전체 전략 요약

1. **파일 I/O 동기화 강화:** HUB.md 쓰기 시 `flush()` + `os.fsync()` 수행. (Windows 캐시/버퍼링 대응)
2. **`hub_manager` 직접 호출(Option A)** 또는 **서브프로세스 호출(Option B)** 중 1개로 일관화.
3. **정규식 기반 블록 제거 + 라인 파서 보완:** edge-case 줄바꿈/EOF 문제 방지.
4. **테스트/태스크 실행 직후 짧은 sleep(0.1\~0.2s)** 로 레이스 컨디션 완전 제거.
5. **실패 시 비상로깅**: emergency\_logs 에 상세 기록 후 중단.

---

## 3. 패치 세트 (필수 변경사항)

### 3.1 `scripts/hub_manager.py` 최종 버전 (권장안)

```python
# scripts/hub_manager.py
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import os
import time

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1F]")
_BLOCK_RE = re.compile(r"(?ms)^[ \t]*---[ \t]*\n__lastSession__:[ \t]*.*?(?=^[ \t]*---[ \t]*$|\Z)")

# --- Low-level I/O helpers -------------------------------------------------

def _read() -> str:
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write(text: str) -> None:
    # LF 고정 + 파일 끝 개행 보장 + flush + fsync + 짧은 sleep
    if text and not text.endswith("\n"):
        text += "\n"
    with open(HUB_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    time.sleep(0.05)

# --- High-level transformers ----------------------------------------------

def _normalize(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return _CONTROL_CHARS.sub("", s)

def strip_last_session_block(text: str) -> str:
    t = _normalize(text)
    t = _BLOCK_RE.sub("", t)
    return t.rstrip() + "\n"

# --- Public API ------------------------------------------------------------

def get_changed_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "HEAD"],
            capture_output=True, text=True, check=False, cwd=ROOT
        )
        return [p.strip() for p in out.stdout.splitlines() if p.strip()]
    except Exception:
        return []

def update_session_end_info(task_id: str = "general") -> None:
    hub = strip_last_session_block(_read())
    changed = get_changed_files()
    ts = datetime.now(timezone.utc).isoformat()

    lines = [
        "---",
        "__lastSession__:",
        f"  task: {task_id}",
        f"  timestamp: {ts}",
    ]
    if changed:
        lines.append("  changed_files:")
        lines.extend([f"    - {p}" for p in changed])

    hub = hub.rstrip() + "\n" + "\n".join(lines) + "\n"
    _write(hub)

def clear_last_session() -> None:
    _write(strip_last_session_block(_read()))

def handle_last_session() -> None:
    if "__lastSession__:" in _read():
        clear_last_session()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        handle_last_session()
    elif sys.argv[1] == "clear":
        clear_last_session()
    else:
        update_session_end_info(sys.argv[1])
```

### 3.2 `tasks.py` 핵심 변경 (Option A 권장)

* **Option A (권장):** hub\_manager 모듈 **직접 import 후 함수 호출**
* **Option B:** `python scripts/hub_manager.py ...` 형태로 **서브프로세스 호출** + 호출 직후 `sleep(0.1)`

#### Option A 예시

```python
from scripts import hub_manager

@task
def start(c):
    # 1) __lastSession__ 제거
    hub_manager.clear_last_session()
    # 2) 인덱스 빌드
    build_context_index(c)
    # 3) briefing 등...
    # 4) gitignore 토글 ON
    ...

@task
def end(c, task_id="general"):
    run_command("end", ["invoke", "wip"], check=False)
    run_command("end", ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "scripts/toggle_gitignore.ps1", "-Restore"], check=False)

    # 3) __lastSession__ 작성 (직접 호출)
    hub_manager.update_session_end_info(task_id)

    run_command("end", ["git", "add", "docs/HUB.md"], check=False)
    run_command("end", ["invoke", "wip"], check=False)
```

### 3.3 `scripts/runner.py` 점검 (선택)

* 실패 시 `command_error` 로깅이 DB에 꼭 남도록 확인.
* 이미 구현되어 있으면 변경 불필요. 없으면 아래 형태 보장:

```python
def run_command(task_name, args, cwd=ROOT, check=True):
    _log(task_name, "command_start", args)
    cp = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if cp.returncode != 0:
        _log(task_name, "command_error", args, cp.returncode, cp.stdout, cp.stderr)
        if check:
            raise subprocess.CalledProcessError(cp.returncode, args, cp.stdout, cp.stderr)
    _log(task_name, "command_end", args, cp.returncode, cp.stdout, cp.stderr)
    return cp
```

### 3.4 `tests/test_p0_rules.py` 최소 수정 (필요 시)

* **end/start 직후 파일 확인 전에 sleep 추가**

```python
import time

def test_last_session_cycle(test_env):
    program = Program(namespace=ns, version="0.1.0")

    program.run("end", exit=False)
    time.sleep(0.2)
    hub_after_end = HUB_PATH.read_text(encoding="utf-8")
    assert "__lastSession__:" in hub_after_end

    program.run("start", exit=False)
    time.sleep(0.2)
    hub_after_start = HUB_PATH.read_text(encoding="utf-8")
    assert "__lastSession__:" not in hub_after_start
```

> **주의:** 테스트 파일 변경은 가능하면 피하되, 이미 race condition 으로 불안정하다면 최소 sleep 추가 허용.

---

## 4. 실행 절차 (Step-by-Step)

### Step 0. 백업 & 정리

1. `git stash -u` 또는 별도 브랜치 생성.
2. `usage.db` 파일이 열려 있으면 이름 변경(`usage.db.bak`) 또는 삭제.
3. `docs/HUB.md` 백업.

### Step 1. 패치 반영

1. 위 3.1 \~ 3.3 패치 내용을 해당 파일에 반영.
2. (선택) 테스트 파일 sleep 추가.
3. `git add` & `git commit -m "fix: [P0]Debug_17 – stabilize last_session_cycle"` (WIP 스크립트 사용 가능)

### Step 2. 로컬 테스트

powershell
pytest tests/test_p0_rules.py::test_last_session_cycle -vv
pytest -vv
invoke test


* 모두 통과해야 함.

### Step 3. 수동 검증

```powershell
invoke end
# HUB.md 열어 __lastSession__ 확인
invoke start
# HUB.md 열어 __lastSession__ 없는지 확인
```

### Step 4. 마무리

* `.gitignore` 복원 여부 확인(`/projects/` 라인 등).
* 변경 사항 커밋/푸시.
* HUB.md/Log.md에 작업 과정 기록(사용자 승인 후).

---

## 5. 실패 시 대응 프로토콜

1. **같은 방법 3회 연속 실패** → 동일 접근 중단, 비상 로그 작성.
2. `scratchpad/emergency_logs/`에 다음을 포함한 마크다운 생성:

   * 실행한 명령/결과(stdout/stderr)
   * HUB.md before/after 스냅샷
   * timestamps, sleep 적용 여부, fsync 적용 여부
   * 시스템 정보 (Python, pytest, invoke, Windows 버전)
3. 사용자에게 즉시 보고하고 다음 대안 제안:

   * 파일 시스템 폴링(반복 read) 방식 도입
   * HUB.md 편집을 메모리→tempfile→atomic rename 방식으로 변경
   * pytest monkeypatch 재조정

---

## 6. 부록 (Appendix)

### 6.1 `__lastSession__` 블록 포맷 규약


---
__lastSession__:
  task: <task_id>
  timestamp: <ISO8601 UTC>
  changed_files:
    - path/to/file
    - ...


### 6.2 정규식 참고

* 블록 제거용:

  * `(?ms)^[ \t]*---[ \t]*\n__lastSession__:[ \t]*.*?(?=^[ \t]*---[ \t]*$|\Z)`

### 6.3 Sleep 권장값

* 기본 0.1\~0.2초 (Windows FS 캐시 경험상 충분)
* 실패 재현 시 0.5초까지 증대 후 다시 테스트

---

## 7. 변경 이력 (for this doc)

* **v1.0 (2025-07-27):** 초기 버전. 다른 LLM 제안 통합, fsync + sleep, direct call 전략 명문화.

---

