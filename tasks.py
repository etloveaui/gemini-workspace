from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys
from scripts import hub_manager
import subprocess, os

ROOT = Path(__file__).resolve().parent
# Determine the path to the Python executable within the virtual environment.
# Prefer a venv-managed interpreter when present (cross‑platform), otherwise
# fall back to the interpreter running this script. This avoids hard‑coding
# Windows‑specific paths and makes the CLI portable across platforms.
if os.name == "nt":
    _venv_candidate = ROOT / "venv" / "Scripts" / "python.exe"
else:
    _venv_candidate = ROOT / "venv" / "bin" / "python"
if _venv_candidate.exists():
    VENV_PYTHON = str(_venv_candidate)
else:
    VENV_PYTHON = sys.executable

__all__ = ["run_command"]

def run_command(task_name, args, cwd=ROOT, check=True):
    return _runner_run_command(task_name, args, cwd, check)

def _ensure_message(msg: str) -> str:
    return msg if msg.strip() else "WIP auto commit"

def python_wip_commit(message: str, cwd: Path):
    cwd = cwd.resolve()
    # 1) 변경사항 스테이징
    subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True, text=True)

    # 2) 임시 메시지 파일
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
        tf.write(message or "auto WIP commit")
        tf.flush()
        temp_path = tf.name

    try:
        subprocess.run(["git", "commit", "-F", temp_path],
                       cwd=str(cwd), check=True, text=True)
    finally:
        os.unlink(temp_path)

@task
def start(c):
    """System check, status briefing, and session initialization."""
    log_usage("session", "start", command="start")

    # 1. 시스템 환경 점검
    print("--- System Status Check ---")
    doctor_result = run_command("start.doctor", [VENV_PYTHON, "scripts/doctor.py"], check=False)
    print(doctor_result.stdout)

    # 2. HUB.md에서 작업 현황 브리핑
    print("--- Task Status ---")
    try:
        with open("docs/HUB.md", "r", encoding="utf-8") as f:
            hub_content = f.read()
        active_tasks = hub_manager.parse_tasks(hub_content, "Active Tasks")
        paused_tasks = hub_manager.parse_tasks(hub_content, "Paused Tasks")
        print(f"Active Tasks: {active_tasks}")
        print(f"Paused Tasks: {paused_tasks}")
    except FileNotFoundError:
        print("docs/HUB.md not found.")

    # 3. Git 변경 사항 요약
    print("--- Git Status ---")
    git_status_result = run_command("start.git_status", ["git", "status", "--porcelain"], check=False)
    if git_status_result.stdout:
        print(git_status_result.stdout)
    else:
        print("No changes in the working directory.")

    # 4. 이전 세션 정보 정리 및 컨텍스트 빌드
    hub_manager.clear_last_session()
    print("\n--- Initializing Session ---")
    build_context_index(c)

    # 5. 도움말 및 다음 행동 제안
    print("\nMore help is available by typing: invoke help")
    print("What would you like to do next?")

@task
def end(c, task_id="general"):
    """WIP commit, restore gitignore, write __lastSession__ block."""
    run_command("end", ["invoke", "wip"], check=False)
    # Use cross‑platform PowerShell Core (`pwsh`) instead of the Windows‑only
    # `powershell.exe`. This avoids quoting issues on non‑Windows platforms.
    # Run the PowerShell script using pwsh when available; fall back to Windows PowerShell.
    try:
        run_command(
            "end",
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/toggle_gitignore.ps1",
                "-Restore",
            ],
            check=True,
        )
    except FileNotFoundError:
        # Fallback to Windows built-in PowerShell (common on Windows)
        run_command(
            "end",
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/toggle_gitignore.ps1",
                "-Restore",
            ],
            check=False,
        )
    hub_manager.update_session_end_info(task_id)
    
    run_command("end", ["git", "add", "docs/HUB.md"], check=False)
    run_command("end", ["invoke", "wip"], check=False)
    log_usage(task_id, "session_end", command="end", returncode=0, stdout="session ended", stderr="")
    print("end done")

@task
def status(c):
    run_command("status", ["git", "status", "--short"], check=False)

@task
def wip(c, message=""):
    """
    PowerShell 호출을 제거한, 순수 Python 버전.
    테스트/실행 환경 모두 동일하게 사용 (권장).
    """
    repo_root = Path.cwd()
    python_wip_commit(message, repo_root)

@task(name="build")
def build_context_index(c):
    run_command("context.build", [VENV_PYTHON, "scripts/build_context_index.py"], check=False)

@task(name="query")
def query_context(c, query):
    run_command("context.query", [VENV_PYTHON, "scripts/context_store.py", query], check=False)

@task
def test(c):
    run_command("test", ["pytest", "tests/", "-q"], check=False)

@task
def clean_cli(c):
    """Clears temporary files and session cache directories."""
    run_command("clean_cli", [VENV_PYTHON, "scripts/clear_cli_state.py"], check=False)

@task
def doctor(c):
    run_command("doctor", [VENV_PYTHON, "scripts/doctor.py"], check=False)

@task
def quickstart(c):
    run_command("quickstart", [VENV_PYTHON, "scripts/quickstart.py"], check=False)

@task
def help(c, section="all"):
    run_command("help", [VENV_PYTHON, "scripts/help.py", section], check=False)

@task
def search(c, q):
    """invoke search \"<query>\" : web search + summarize"""
    run_command("search", [VENV_PYTHON, "scripts/web_agent.py", "--query", q], check=False)

ns = Collection()
ns.add_task(start)
ns.add_task(end)
ns.add_task(status)
ns.add_task(wip)
ns.add_task(test)
ns.add_task(clean_cli)
ns.add_task(doctor)
ns.add_task(quickstart)
ns.add_task(help)
ns.add_task(search)

ctx_ns = Collection('context')
ctx_ns.add_task(build_context_index, name='build')
ctx_ns.add_task(query_context, name='query')

ns.add_collection(ctx_ns)
program = Program(namespace=ns)
