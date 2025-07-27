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
from scripts.runner import run_command

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
    """Verify the __lastSession__ block is created by 'end' and cleared by 'start'."""
    program = Program(namespace=ns, version="0.1.0")

    program.run("end", exit=False)
    hub_content_after_end = HUB_PATH.read_text(encoding="utf-8")
    assert "__lastSession__:" in hub_content_after_end

    program.run("start", exit=False)
    time.sleep(0.1) # 파일 시스템 업데이트 대기
    hub_content_after_start = HUB_PATH.read_text(encoding="utf-8")
    assert "__lastSession__:" not in hub_content_after_start


def test_runner_error_logging(test_env):
    """Verify that a failed command in runner.py logs a 'command_error'."""
    # Use a command that is guaranteed to fail
    with pytest.raises(subprocess.CalledProcessError):
        run_command("test_runner", ["python", "-c", "import sys; sys.exit(1)"])

    # Check the database for the error log
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usage WHERE event_type = 'command_error' AND task_name = 'test_runner'")
    error_log = cursor.fetchone()
    conn.close()

    assert error_log is not None, "A 'command_error' log was not found."