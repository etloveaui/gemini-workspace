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
    # Backup original HUB.md
    if HUB_PATH.exists():
        shutil.copy(HUB_PATH, HUB_PATH.with_suffix(".bak"))

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
                sqlite3.connect(DB_PATH).close()
                time.sleep(0.1)
                os.remove(DB_PATH)
            except (sqlite3.OperationalError, PermissionError) as e_inner:
                print(f"Could not delete usage.db: {e_inner}")
                # If still locked, proceed without deleting/renaming, tests might fail

    yield

    # --- Teardown ---
    # Restore original HUB.md
    if HUB_PATH.with_suffix(".bak").exists():
        shutil.move(HUB_PATH.with_suffix(".bak"), HUB_PATH)

    # Restore usage.db
    if db_renamed and DB_PATH.with_suffix(".db.bak").exists():
        try:
            os.rename(DB_PATH.with_suffix(".db.bak"), DB_PATH)
        except OSError as e:
            print(f"Could not restore usage.db: {e}")
    elif DB_PATH.exists(): # If a new DB was created during test, remove it
        try:
            sqlite3.connect(DB_PATH).close()
            time.sleep(0.1)
            os.remove(DB_PATH)
        except (sqlite3.OperationalError, PermissionError) as e_inner:
            print(f"Could not remove new usage.db: {e_inner}")

# --- Test Cases ---

def test_commit_protocol(test_env, monkeypatch):
    """Verify that the 'wip' task uses the '-F' option for git commit."""
    call_args = []
    def mock_run_command(task_name, args, **kwargs):
        call_args.append(args)
        # Simulate success for git diff to allow commit to proceed
        if "diff" in args:
            return subprocess.CompletedProcess(args, 0, stdout="1 file changed")
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr("tasks.run_command", mock_run_command)

    # Create a dummy file and stage it
    dummy_file = ROOT / "dummy_for_commit.txt"
    dummy_file.write_text("test content")
    subprocess.run(["git", "add", str(dummy_file)])

    # Run the 'wip' task via subprocess to simulate CLI call
    result = subprocess.run(
        [sys.executable, "-m", "invoke", "wip", "--message='Test commit'"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False
    )
    assert result.returncode == 0, f"invoke wip failed: {result.stderr}"

    # Assert that 'git commit -F' was called (check mock_run_command calls)
    commit_cmd_found = False
    for args in call_args:
        if len(args) >= 3 and args[0] == "git" and args[1] == "commit" and args[2] == "-F":
            commit_cmd_found = True
            break
    assert commit_cmd_found, "The -F option was not used in the git commit command."

def test_last_session_cycle(test_env):
    """Verify the __lastSession__ block is created by 'end' and cleared by 'start'."""
    program = Program(namespace=ns, version="0.1.0")

    program.run("end", exit=False)
    hub_content_after_end = HUB_PATH.read_text(encoding="utf-8")
    assert "__lastSession__:" in hub_content_after_end

    program.run("start", exit=False)
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
