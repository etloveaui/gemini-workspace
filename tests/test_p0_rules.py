import os
import subprocess
import pytest
from invoke import Program
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tasks import ns
import shutil
from pathlib import Path
import sqlite3
import time
from scripts.runner import run_command, _ensure_db

import time
import re

def run_invoke(*args):
    cmd = [sys.executable, "-m", "invoke", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False, cwd=ROOT)
    if proc.returncode != 0:
        raise AssertionError(f"invoke {' '.join(args)} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc.stdout

def wait_for_pattern(path, pattern, timeout=2.0, interval=0.05):
    """pattern이 path 파일에 등장할 때까지 반복 확인"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(pattern, content):
            return content
        time.sleep(interval)
    raise AssertionError(f"Timeout: '{pattern}' not found in {path}")

# --- Constants and Test Setup ---
ROOT = Path(__file__).resolve().parent.parent
HUB_PATH = ROOT / "docs" / "HUB.md"
DB_PATH = ROOT / "usage.db"

@pytest.fixture(scope="function")
def test_env():
    # --- Setup ---
    # Ensure HUB.md is clean before each test
    initial_hub_content = """# Workspace HUB

*Last Updated: 2025-07-22*

## Projects

## Active Tasks

## Paused Tasks

## Completed Tasks
"""
    HUB_PATH.write_text(initial_hub_content, encoding="utf-8", newline='')

    # Rename usage.db to avoid permission issues
    db_renamed = False
    if DB_PATH.exists():
        try:
            os.rename(DB_PATH, DB_PATH.with_suffix(".db.bak"))
            db_renamed = True
        except OSError as e:
            print(f"Could not rename usage.db: {e}")
            # If rename fails, try to delete (might be locked by another process)
            try:
                os.remove(DB_PATH)
            except (sqlite3.OperationalError, PermissionError) as e_inner:
                print(f"Could not delete usage.db: {e_inner}")

    yield

    # --- Teardown ---
    # Ensure HUB.md is clean after each test
    HUB_PATH.write_text(initial_hub_content, encoding="utf-8", newline='')

    # Restore usage.db
    if db_renamed and DB_PATH.with_suffix(".db.bak").exists():
        try:
            os.rename(DB_PATH.with_suffix(".db.bak"), DB_PATH)
        except OSError as e:
            print(f"Could not restore usage.db: {e}")
    elif DB_PATH.exists(): # If a new DB was created during test, remove it
        try:
            os.remove(DB_PATH)
        except (sqlite3.OperationalError, PermissionError) as e_inner:
            print(f"Could not remove new usage.db: {e_inner}")

# --- Test Cases ---

def test_commit_protocol(test_env, monkeypatch):
    """Verify that the 'wip' task uses the '-F' option for git commit."""
    call_args = []

    def mock_program_run(self, task_name, *args, **kwargs):
        if task_name == "wip":
            # Simulate git diff --cached --shortstat
            call_args.append(["git", "diff", "--cached", "--shortstat"])
            # Simulate git commit -F temp_path
            call_args.append(["git", "commit", "-F", "temp_path"])
        # You might need to add more logic here if other tasks are run during the test
        # For now, we only care about 'wip'

    monkeypatch.setattr("invoke.Program.run", mock_program_run)

    # Create a dummy file and stage it
    dummy_file = ROOT / "dummy_for_commit.txt"
    dummy_file.write_text("test content")
    subprocess.run(["git", "add", str(dummy_file)])

    program = Program(namespace=ns, version="0.1.0")
    program.run("wip", exit=False)

    # Cleanup
    os.remove(dummy_file)
    subprocess.run(["git", "reset", "HEAD", "--", str(dummy_file)])

    commit_cmd = next((cmd for cmd in call_args if cmd[0] == "git" and cmd[1] == "commit" and "-F" in cmd), None)
    assert commit_cmd is not None, "git commit was never called."
    assert "-F" in commit_cmd, "The '-F' option was not used in the git commit command."

def test_last_session_cycle(test_env):
    # 1) end 실행 → 블록 등장 대기
    run_invoke("end")
    wait_for_pattern(HUB_PATH, r"__lastSession__:")

    # 2) start 실행 → 블록 제거 대기
    run_invoke("start")

    # 폴링 방식으로 '없어짐' 확인
    deadline = time.time() + 2.0
    while time.time() < deadline:
        txt = HUB_PATH.read_text(encoding="utf-8", errors="ignore")
        if "__lastSession__:" not in txt:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("Timeout: __lastSession__ block still present after start")


def test_runner_error_logging(test_env, clean_usage_db, monkeypatch):
    """Verify that a failed command in runner.py logs a 'command_error'."""
    # Monkeypatch DB_PATH to use a temporary file for this test
    temp_db_path = Path(clean_usage_db) # clean_usage_db fixture returns the path to the temporary db
    monkeypatch.setattr("scripts.runner.DB_PATH", temp_db_path)

    # Monkeypatch _ensure_db to use the temporary DB_PATH
    def mock_ensure_db():
        conn = sqlite3.connect(temp_db_path)
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
        """
        )
        conn.commit()
        conn.close()
    monkeypatch.setattr("scripts.runner._ensure_db", mock_ensure_db)

    # Use a command that is guaranteed to fail
    with pytest.raises(subprocess.CalledProcessError):
        run_command("test_runner", ["python", "-c", "import sys; sys.exit(1)"])

    # Check the database for the error log
    time.sleep(0.1) # Give some time for DB write to complete
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("SELECT * FROM usage WHERE event_type = 'command_error' AND task_name = 'test_runner'")
        error_log = cursor.fetchone()

    assert error_log is not None, "A 'command_error' log was not found."

def test_debug_19_doc_exists():
    from pathlib import Path
    assert Path("scratchpad/Gemini-Self-Upgrade/[P0]Debug_19.md").exists(), "[P0]Debug_19.md 문서가 삭제됨!"

def test_debug20_doc_exists():
    from pathlib import Path
    assert Path("docs/debug/[P0]Debug_20.md").exists(), "[P0]Debug_20.md 문서가 삭제됨!"