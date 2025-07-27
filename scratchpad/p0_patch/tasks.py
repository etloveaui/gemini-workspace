# tasks.py (patched for P0 completion)
from invoke import task, Collection, Program
import subprocess
from scripts.usage_tracker import log_usage
import sys

# --- helper -------------------------------------------------
def run_logged(task_name, c, cmd, **kwargs):
    log_usage(task_name, "command_start", description=f"run: {cmd}")
    result = c.run(cmd, **kwargs)
    log_usage(task_name, "command_end", description=f"done: {cmd}")
    return result

# --- core tasks ---------------------------------------------
@task
def start(c):
    """[Intelligent Engine Start] Build context, clear __lastSession__, brief, activate tracking."""
    log_usage("session", "start", description="session start")
    # 0. clear previous __lastSession__ block if any
    subprocess.run([sys.executable, "scripts/hub_manager.py"], check=False)
    # 1. build context index
    print("  - Building context index...")
    build_context_index(c)
    # 2. assemble prompt context (optional)
    try:
        res = subprocess.run([sys.executable, "scripts/prompt_builder.py"],
                             capture_output=True, check=True)
        print("\nSession Start Briefing\n" + "-"*50)
        print(res.stdout.decode('utf-8', errors='ignore'))
        print("-"*50)
    except Exception as e:
        print(f"prompt_builder failed: {e}")
    # 3. toggle .gitignore tracking on
    run_logged(c.task.name, c, r"powershell.exe -ExecutionPolicy Bypass -File .\scripts\toggle_gitignore.ps1")
    print("✅ start done")

@task
def end(c, task_id="general"):
    """[Session End] WIP commit, restore gitignore, write __lastSession__ block.""" 
    print("⏹️ Ending session...")
    run_logged(c.task.name, c, "invoke wip")
    run_logged(c.task.name, c, r"powershell.exe -ExecutionPolicy Bypass -File .\scripts\toggle_gitignore.ps1 -Restore")
    # update HUB.md
    subprocess.run([sys.executable, "scripts/hub_manager.py", task_id], check=False)
    run_logged(c.task.name, c, "git add docs/HUB.md")
    run_logged(c.task.name, c, "invoke wip")
    log_usage(task_id, "session_end", description="session ended")
    print("✅ end done")

@task
def status(c):
    """[Status Check] Quick git status.""" 
    run_logged(c.task.name, c, "git status --short")

@task
def wip(c, message=""):
    """Create WIP commit using git-wip.ps1 (uses -F tempfile protocol).""" 
    cmd = f'powershell.exe -ExecutionPolicy Bypass -File "scripts/git-wip.ps1" -Message "{message}"'
    run_logged(c.task.name, c, cmd)

# ---- context namespace -------------------------------------
@task(name="build")
def build_context_index(c):
    run_logged(c.task.name, c, r"python .\scripts\build_context_index.py")

@task(name="query")
def query_context(c, query):
    print(f"Query: {query}")
    run_logged(c.task.name, c, f'python scripts/context_store.py "{query}"')

# ---- tests -------------------------------------------------
@task
def test(c):
    """Run all pytest cases in tests/""" 
    run_logged(c.task.name, c, "pytest tests/ -v")

# namespace
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
