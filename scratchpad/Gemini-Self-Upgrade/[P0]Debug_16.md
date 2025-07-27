# \[P0]Debug\_16.md — Gemini CLI 자가 업그레이드(세션 관리/테스트 통과) 최종 지시서

> **목표:** `test_last_session_cycle`, `test_commit_protocol`, `test_runner_error_logging` 포함 **모든 pytest 테스트를 한 번에 통과**시키고, 이후에도 동일 문제가 재발하지 않도록 **파일/스크립트/DB 스키마를 일관되게 정비**한다.
>
> **전제:** "Gemini CLI"는 **모든 기억이 초기화된 상태**이며, 아래 문서를 그대로 따라 하면 된다. 불필요한 추론 없이 단계별로 수행하라.

---

## 0. 작업 개요

1. **세션 블록 관리 안정화**: `docs/HUB.md` 내 `__lastSession__` 블록을

   * `end` 태스크에서 생성하고,
   * `start` 태스크에서 반드시 제거한다.
     기존 정규식 기반 제거 로직의 실패를 근본적으로 해결하기 위해 **라인 스캐닝 방식**으로 변경한다.

2. **로그/DB 스키마 통합**: `scripts/runner.py`가 생성/사용하는 `usage` 테이블(열: `task_name`, `event_type`, `command`, `returncode`, `stdout`, `stderr`)을 기준으로 통일하고, `tasks.py` 측 `log_usage` 호출 시 **runner 스키마와 충돌하지 않도록** 한다. (필수는 아님 — 테스트는 runner만 검증하지만, 혼선을 막는다.)

3. **커밋 프로토콜**: `tasks.py wip`는 **반드시 `git commit -F <tempfile>`** 을 사용해야 한다.

4. **PowerShell/Windows 대응**: 인코딩/줄바꿈/파일 잠금 이슈를 고려하여, 모든 스크립트를 UTF-8로 저장하고, 필요 시 `time.sleep(0.1)` 등 대기.

5. **이모티콘/이모지 금지**: Python/PowerShell 파일에 이모티콘 사용 금지.

---

## 1. 사전 점검(Checklist)

아래 항목을 먼저 확인하라.

* 현재 루트 디렉터리: `C:\Users\etlov\gemini-workspace`
* Git 저장소 초기화/remote 설정 완료 상태.
* Python 3.x, Git, PowerShell 사용 가능.
* 기존 `usage.db` 파일이 잠겨있지 않은지 확인.
* `scratchpad\p0_patch` 에 압축을 풀어 두었다면, 해당 내용은 참고용/백업용이며, **최종 반영은 이 문서를 따른다.**

---

## 2. 원샷 적용 스크립트 (PowerShell)

> **주의:** 아래 스크립트를 그대로 복사/붙여넣기 하여 **PowerShell에서 실행**한다. (관리자 권한 불필요)

powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 0) 루트 이동
cd C:\Users\etlov\gemini-workspace

# 1) 가상환경 준비
if (Test-Path .\venv\Scripts\Activate.ps1) {
    . .\venv\Scripts\Activate.ps1
} else {
    py -3 -m venv venv
    . .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
}

# 2) 필수 패키지 설치 (invoke, pytest)
python -m pip install invoke pytest

# 3) pytest.ini 작성/덮어쓰기
$pytestIni = @"[pytest]
testpaths = tests
norecursedirs = scratchpad .git .venv venv env node_modules build dist
"@
Set-Content -Encoding UTF8 -Path pytest.ini -Value $pytestIni

# 4) scripts 디렉터리 확보
New-Item -Force -ItemType Directory scripts | Out-Null

# 4-1) scripts/runner.py 덮어쓰기
$runnerPy = @"
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "usage.db"

def _ensure_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            command TEXT,
            returncode INTEGER,
            stdout TEXT,
            stderr TEXT
        )
    """)
    conn.commit()
    conn.close()

def _log(task_name, event_type, command, returncode=None, stdout="", stderr=""):
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO usage (timestamp, task_name, event_type, command, returncode, stdout, stderr) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ts, task_name, event_type, " ".join(command) if isinstance(command, (list, tuple)) else str(command),
         returncode if returncode is not None else None, stdout, stderr)
    )
    conn.commit()
    conn.close()

def run_command(task_name, args, cwd=ROOT, check=True):
    if not isinstance(args, (list, tuple)):
        raise TypeError("args must be list/tuple of command tokens")

    _log(task_name, "command_start", args)
    try:
        cp = subprocess.run(args, capture_output=True, text=True, cwd=cwd, check=check)
        _log(task_name, "command_end", args, cp.returncode, cp.stdout, cp.stderr)
        return cp
    except subprocess.CalledProcessError as e:
        _log(task_name, "command_error", args, e.returncode, e.stdout, e.stderr)
        raise
"@
Set-Content -Encoding UTF8 -Path scripts\runner.py -Value $runnerPy

# 4-2) scripts/hub_manager.py 덮어쓰기 (라인 스캔 방식)
$hubMgrPy = @"
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

def _read():
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write(text: str):
    if text and not text.endswith("\n"):
        text += "\n"
    HUB_PATH.write_text(text, encoding="utf-8")

def strip_last_session_block(text: str) -> str:
    lines = text.replace('\r\n','\n').replace('\r','\n').split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == '---' and i + 1 < len(lines) and lines[i+1].strip().startswith('__lastSession__:'):
            i += 2
            while i < len(lines):
                if lines[i].strip() == '---':
                    i += 1
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"

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
    block = ["---", "__lastSession__:", f"  task: {task_id}", f"  timestamp: {ts}"]
    if changed:
        block.append("  changed_files:")
        block.extend([f"    - {p}" for p in changed])
    hub = hub.rstrip() + "\n" + "\n".join(block) + "\n"
    _write(hub)

def clear_last_session() -> None:
    _write(strip_last_session_block(_read()))

def handle_last_session() -> None:
    txt = _read()
    if "__lastSession__:" in txt:
        clear_last_session()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        handle_last_session()
    elif sys.argv[1] == "clear":
        clear_last_session()
    else:
        update_session_end_info(sys.argv[1])
"@
Set-Content -Encoding UTF8 -Path scripts\hub_manager.py -Value $hubMgrPy

# 4-3) tasks.py 덮어쓰기 (run_command 노출 & -F commit)
$tasksPy = @"
from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys

ROOT = Path(__file__).resolve().parent

__all__ = ["run_command"]

def run_command(task_name, args, cwd=ROOT, check=True):
    return _runner_run_command(task_name, args, cwd, check)

def _ensure_message(msg: str) -> str:
    return msg if msg.strip() else "WIP auto commit"

@task
def start(c):
    """Build context, clear __lastSession__, optional briefing, enable tracking."""
    log_usage("session", "start", command="start", returncode=0, stdout="session started", stderr="")
    run_command("start", [sys.executable, "scripts/hub_manager.py"], check=False)
    print("  - Building context index...")
    build_context_index(c)
    try:
        cp = run_command("start", [sys.executable, "scripts/prompt_builder.py"], check=False)
        if cp.stdout:
            print("\nSession Start Briefing\n" + "-"*50)
            print(cp.stdout)
            print("-"*50)
    except Exception as e:
        print(f"prompt_builder failed: {e}")
    run_command("start", ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "scripts/toggle_gitignore.ps1"], check=False)
    print("start done")

@task
def end(c, task_id="general"):
    """WIP commit, restore gitignore, write __lastSession__ block."""
    run_command("end", ["invoke", "wip"], check=False)
    run_command("end", ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", "scripts/toggle_gitignore.ps1", "-Restore"], check=False)
    run_command("end", [sys.executable, "scripts/hub_manager.py", task_id], check=False)
    run_command("end", ["git", "add", "docs/HUB.md"], check=False)
    run_command("end", ["invoke", "wip"], check=False)
    log_usage(task_id, "session_end", command="end", returncode=0, stdout="session ended", stderr="")
    print("end done")

@task
def status(c):
    run_command("status", ["git", "status", "--short"], check=False)

@task
def wip(c, message=""):
    msg = _ensure_message(message)
    _runner_run_command("wip", ["git", "diff", "--cached", "--shortstat"], check=False)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
        tf.write(msg + "\n")
        temp_path = tf.name
    _runner_run_command("wip", ["git", "commit", "-F", temp_path], check=False)

@task(name="build")
def build_context_index(c):
    run_command("context.build", [sys.executable, "scripts/build_context_index.py"], check=False)

@task(name="query")
def query_context(c, query):
    run_command("context.query", [sys.executable, "scripts/context_store.py", query], check=False)

@task
def test(c):
    run_command("test", ["pytest", "tests/", "-v"], check=False)

ns = Collection()
ns.add_task(start)
ns.add_task(end)
ns.add_task(status)
ns.add_task(wip)
ns.add_task(test)

ctx_ns = Collection('context')
ctx_ns.add_task(build_context_index, name='build')
ctx_ns.add_task(query_context, name='query')

ns.add_collection(ctx_ns)
program = Program(namespace=ns)
"@
Set-Content -Encoding UTF8 -Path tasks.py -Value $tasksPy

# 5) usage.db 충돌/잠금 방지: 기존 파일 백업 시도
if (Test-Path usage.db) {
    try {
        Rename-Item usage.db ("usage_backup_" + (Get-Date -Format yyyyMMdd_HHmmss) + ".db")
    } catch {
        Write-Warning "usage.db rename failed: $_"
    }
}

# 6) __lastSession__ 블록 제거 1회
python scripts\hub_manager.py clear

# 7) 핵심 테스트만 먼저 수행
pytest tests/test_p0_rules.py::test_commit_protocol -vv -s
pytest tests/test_p0_rules.py::test_last_session_cycle -vv -s
pytest tests/test_p0_rules.py::test_runner_error_logging -vv -s

# 8) 전체 테스트
pytest tests/ -v


---

## 3. 테스트 실패 시 보고 형식

아래 3가지를 **그대로 출력**해서 상위 LLM(또는 담당자)에게 전달하라.

1. **실패한 테스트 단건 재실행 로그** (예:)

   powershell
   pytest tests/test_p0_rules.py::test_last_session_cycle -vv -s
   

2. **HUB.md 마지막 120줄**

   powershell
   Get-Content docs\HUB.md -Tail 120
   

3. **usage 테이블 스키마/로그 확인**

   powershell
   python - <<'PY'
   

import sqlite3
con = sqlite3.connect('usage.db')
print(con.execute('SELECT sql FROM sqlite\_master WHERE type="table" AND name="usage"').fetchall())
print('--- last 10 rows ---')
for r in con.execute('SELECT \* FROM usage ORDER BY id DESC LIMIT 10'):
print(r)
PY



---

## 4. 문제 재발 방지 체크리스트

- `scripts/hub_manager.py`에 **print 디버그 코드가 남아있지 않은지** 확인했다.
- `tasks.py` 의 `wip` 구현이 항상 `-F` 옵션 사용을 유지하는지 점검했다.
- DB 스키마를 수정할 때 `runner.py`의 `_ensure_db()` 내용과 맞췄는지 확인했다.
- `start` 실행 직후 `docs/HUB.md` 내 `__lastSession__:` 문자열이 없는지 직접 확인했다.
- Windows 줄바꿈(
) 변환이 strip 로직에서 안정적으로 처리되는지 검증했다.

---

## 5. 수동 점검 절차 (필요 시)

1. `invoke end` 실행 후 HUB.md를 열어 `---` 블록이 생성되었는지 확인.
2. `invoke start` 실행 후 HUB.md를 다시 확인하여 블록이 제거되었는지 확인.
3. `pytest -v` 를 통해 전체 테스트 반복.
4. `sqlite3 usage.db ".schema usage"` 로 테이블 구조 확인.

---

## 6. 롤백/복구 가이드

- 실수로 파일을 덮어썼다면 Git 로그에서 복구 가능: `git checkout HEAD~1 -- <path>`
- `usage.db` 가 손상되면 삭제 후 테스트 재실행 시 자동 재생성된다.
- `docs/HUB.md` 가 깨졌다면 `.bak` 백업이 있는지 확인 후 복원.

---

## 7. 이후 단계(선택)

- `context_store.py`, `prompt_builder.py` 개선(요약기 교체, BM25 검색 고도화 등)은 P0 범위를 넘는다. 이후 P1~P2에서 진행.
- Git hooks 의 Windows 호환 자동화는 추후 재도전(현재는 PowerShell 직접 호출로 우회 성공).

---

## 8. 참고: 현재 HUB.md 요약

- Active Tasks: 없음.
- Paused/Completed 항목은 그대로 두되, 테스트와 직접적 연관은 없다. 본 지시서 범위에서는 **편집하지 말 것**.

---

## 9. 마무리

위 스크립트와 지시를 **순서대로** 수행하면, `test_last_session_cycle` 포함 모든 테스트가 통과해야 한다.
만약 통과하지 못하면, **3. 테스트 실패 시 보고 형식**을 그대로 지켜 로그/출력을 전달하라.

끝.

```
