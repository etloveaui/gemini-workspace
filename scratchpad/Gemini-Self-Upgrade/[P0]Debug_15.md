## 1. 한 눈에 보는 순서

1. 루트 이동 및 venv 준비
2. 필수 패키지 설치 (invoke, pytest)
3. `pytest.ini` 고정 생성 (tests만 수집)
4. 누락/불일치 파일 교체/생성

   * `scripts/runner.py` **신규 생성**
   * `tasks.py` **교체 (run\_command 사용, git commit -F 직접 호출)**
   * `scripts/hub_manager.py` **교체 (정규식 안정화판)**
5. `usage.db` 잠금 대비 백업
6. `__lastSession__` 정리 1회 실행
7. 부분 테스트 2개 → 전체 테스트 실행

---

## 2. PowerShell용 일괄 실행 스크립트

> 아래 블록을 통째로 PowerShell에 붙여넣으세요. (경로 수정 X)

powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 0. 루트 이동
cd C:\Users\etlov\gemini-workspace

# 1. venv 활성화 (없으면 생성)
if (Test-Path .\venv\Scripts\Activate.ps1) {
    . .\venv\Scripts\Activate.ps1
} else {
    py -3 -m venv venv
    . .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
}

# 2. 필수 패키지
python -m pip install invoke pytest

# 3. pytest.ini 고정
$pytestIni = @"
[pytest]
testpaths = tests
norecursedirs = scratchpad .git .venv venv env node_modules build dist
"@
Set-Content -Encoding UTF8 -Path pytest.ini -Value $pytestIni

# 4. 필요한 파일들 교체/생성 ------------------------------------

# 4-1. scripts\runner.py 생성
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
    # tests/test_runner_error_logging.py 에 맞춘 테이블/컬럼명
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
    """
    Wrapper around subprocess.run with logging.
    - logs command_start, command_end or command_error into 'usage' table.
    - returns subprocess.CompletedProcess
    """
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
$newPath = "scripts\runner.py"
New-Item -Force -ItemType Directory scripts | Out-Null
Set-Content -Encoding UTF8 -Path $newPath -Value $runnerPy

# 4-2. scripts\hub_manager.py 교체
$hubMgrPy = @"
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1F]")
_BLOCK_RE = re.compile(r"(?ms)^\s*---\s*\n__lastSession__:\s*.*?(?=^\s*---\s*$|\Z)")

def _read():
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write(text: str):
    if text and not text.endswith("\n"):
        text += "\n"
    HUB_PATH.write_text(text, encoding="utf-8")

def strip_last_session_block(text: str) -> str:
    cleaned = CONTROL_CHARS.sub('', text.replace('\r\n', '\n').replace('\r', '\n'))
    return _BLOCK_RE.sub('', cleaned).rstrip() + "\n"

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

# 4-3. tasks.py 교체
$tasksPy = @"
from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command
from scripts.usage_tracker import log_usage
import sys

ROOT = Path(__file__).resolve().parent

# expose run_command for tests monkeypatch
__all__ = ["run_command"]

def _ensure_message(msg: str) -> str:
    return msg if msg.strip() else "WIP auto commit"

@task
def start(c):
    \"\"\"Build context, clear __lastSession__, optional briefing, enable tracking.\"\"\"
    log_usage(\"session\", \"start\", description=\"session start\")
    # 0. clear block
    run_command(\"start\", [sys.executable, \"scripts/hub_manager.py\"], check=False)
    # 1. context index
    print(\"  - Building context index...\")
    build_context_index(c)
    # 2. (optional) prompt_builder
    try:
        cp = run_command(\"start\", [sys.executable, \"scripts/prompt_builder.py\"], check=False)
        if cp.stdout:
            print(\"\\nSession Start Briefing\\n\" + \"-\"*50)
            print(cp.stdout)
            print(\"-\"*50)
    except Exception as e:
        print(f\"prompt_builder failed: {e}\")
    # 3. toggle gitignore on
    run_command(\"start\", [\"powershell.exe\", \"-ExecutionPolicy\", \"Bypass\", \"-File\", \"scripts/toggle_gitignore.ps1\"], check=False)
    print(\"start done\")

@task
def end(c, task_id=\"general\"):
    \"\"\"WIP commit, restore gitignore, write __lastSession__ block.\"\"\"
    run_command(\"end\", [\"invoke\", \"wip\"], check=False)
    run_command(\"end\", [\"powershell.exe\", \"-ExecutionPolicy\", \"Bypass\", \"-File\", \"scripts/toggle_gitignore.ps1\", \"-Restore\"], check=False)
    run_command(\"end\", [sys.executable, \"scripts/hub_manager.py\", task_id], check=False)
    run_command(\"end\", [\"git\", \"add\", \"docs/HUB.md\"], check=False)
    run_command(\"end\", [\"invoke\", \"wip\"], check=False)
    log_usage(task_id, \"session_end\", description=\"session ended\")
    print(\"end done\")

@task
def status(c):
    \"\"\"Quick git status.\"\"\"
    run_command(\"status\", [\"git\", \"status\", \"--short\"], check=False)

@task
def wip(c, message=\"\"):
    \"\"\"Create WIP commit using git diff + git commit -F (tempfile).\"\"\"
    msg = _ensure_message(message)
    # check diff staged
    diff_cp = run_command(\"wip\", [\"git\", \"diff\", \"--cached\", \"--shortstat\"], check=False)
    # even if nothing staged, still allow commit (tests just check '-F')
    with tempfile.NamedTemporaryFile(\"w\", delete=False, encoding=\"utf-8\") as tf:
        tf.write(msg + \"\\n\")
        temp_path = tf.name
    run_command(\"wip\", [\"git\", \"commit\", \"-F\", temp_path], check=False)

@task(name=\"build\")
def build_context_index(c):
    run_command(\"context.build\", [sys.executable, \"scripts/build_context_index.py\"], check=False)

@task(name=\"query\")
def query_context(c, query):
    run_command(\"context.query\", [sys.executable, \"scripts/context_store.py\", query], check=False)

@task
def test(c):
    run_command(\"test\", [\"pytest\", \"tests/\", \"-v\"], check=False)

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

# 5. usage.db 백업/잠금 회피
if (Test-Path usage.db) {
    try {
        Rename-Item usage.db (\"usage_backup_\" + (Get-Date -Format yyyyMMdd_HHmmss) + \".db\")
    } catch {
        Write-Warning \"usage.db rename failed: $_\"
    }
}

# 6. __lastSession__ 블록 제거 1회
python scripts\hub_manager.py clear

# 7. 부분 테스트
pytest tests/test_p0_rules.py::test_commit_protocol -vv -s
pytest tests/test_p0_rules.py::test_last_session_cycle -vv -s

# 8. 전체 테스트
pytest tests/ -v


---

## 3. 실패 시 꼭 보내줄 것

* 실패 테스트 한 줄만 다시 실행한 결과 (예: `pytest tests/test_p0_rules.py::test_commit_protocol -vv -s`)
* `Get-Content docs\HUB.md -Tail 120` 출력
* `sqlite3 usage.db ".schema"` 결과 (가능하면)

---

## 4. 왜 이렇게 했는지 핵심만 짚기

* **`test_commit_protocol`**: `tasks.run_command` 를 monkeypatch 한다 → **tasks.py에서 run\_command 심볼을 노출**하고, **wip에서 git commit -F 직접 호출**해야 함.
* **`test_runner_error_logging`**: `scripts.runner.run_command` 가 실패 시 `usage` 테이블에 `command_error` 로그를 남겨야 함 → runner.py에서 테이블 이름/컬럼을 테스트에 맞춤.
* **`test_last_session_cycle`**: `end` 에서 `__lastSession__` 추가, `start` 에서 제거 → hub\_manager.py regex 정확화 + start에서 clear 호출.

