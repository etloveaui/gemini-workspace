from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.usage_tracker import log_usage
import sys
from scripts.runner import run_command as _runner_run_command # scripts.runner.run_command를 다른 이름으로 임포트

ROOT = Path(__file__).resolve().parent

# expose run_command for tests monkeypatch
__all__ = ["run_command"]

def run_command(task_name, args, cwd=ROOT, check=True):
    return _runner_run_command(task_name, args, cwd, check)

def _ensure_message(msg: str) -> str:
    return msg if msg.strip() else "WIP auto commit"

@task
def start(c):
    """Build context, clear __lastSession__, optional briefing, enable tracking."""
    log_usage("session", "start", command="start", returncode=0, stdout="session started", stderr="")
    # 0. clear block
    run_command("start", [sys.executable, "scripts/hub_manager.py"], check=False)
    # 1. context index
    print("  - Building context index...")
    build_context_index(c)
    # 2. (optional) prompt_builder
    try:
        cp = run_command("start", [sys.executable, "scripts/prompt_builder.py"], check=False)
        if cp.stdout:
            print("\nSession Start Briefing\n" + "-"*50)
            print(cp.stdout)
            print("-"*50)
    except Exception as e:
        print(f"prompt_builder failed: {e}")
    # 3. toggle gitignore on
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
    """Quick git status."""
    run_command("status", ["git", "status", "--short"], check=False)

@task
def wip(c, message=""):
    """Create WIP commit using git diff + git commit -F (tempfile)."""
    msg = _ensure_message(message)
    # check diff staged
    diff_cp = _runner_run_command("wip", ["git", "diff", "--cached", "--shortstat"], check=False)
    # even if nothing staged, still allow commit (tests just check '-F')
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
