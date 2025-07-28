from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys
from scripts import hub_manager
import subprocess, os

ROOT = Path(__file__).resolve().parent

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
    """Build context, clear __lastSession__, optional briefing, enable tracking."""
    log_usage("session", "start", command="start", returncode=0, stdout="session started", stderr="")

    hub_manager.clear_last_session()
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
    repo_root = Path.cwd()  # 또는 프로젝트 루트로 고정 필요시 ROOT.parent 등
    python_wip_commit(message, repo_root)

@task(name="build")
def build_context_index(c):
    run_command("context.build", [sys.executable, "scripts/build_context_index.py"], check=False)

@task(name="query")
def query_context(c, query):
    run_command("context.query", [sys.executable, "scripts/context_store.py", query], check=False)

@task
def test(c):
    run_command("test", ["pytest", "tests/", "-v"], check=False)

@task
def clean_cli(c):
    """Clears temporary files and session cache directories."""
    run_command("clean_cli", [sys.executable, "scripts/clear_cli_state.py"], check=False)

@task
def doctor(c):
    c.run(f"powershell.exe -ExecutionPolicy Bypass -Command \"& '{sys.executable}' 'scripts/doctor.py'\"", pty=False)

@task
def quickstart(c):
    c.run(f"powershell.exe -ExecutionPolicy Bypass -Command \"& '{sys.executable}' 'scripts/quickstart.py'\"", pty=False)

@task
def help(c, section="all"):
    c.run(f"powershell.exe -ExecutionPolicy Bypass -Command \"& '{sys.executable}' 'scripts/help.py' {section}\"", pty=False)

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

ctx_ns = Collection('context')
ctx_ns.add_task(build_context_index, name='build')
ctx_ns.add_task(query_context, name='query')

ns.add_collection(ctx_ns)
program = Program(namespace=ns)
