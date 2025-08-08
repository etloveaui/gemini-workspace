from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys
from scripts import hub_manager
import subprocess, os
ROOT = Path(__file__).resolve().parent
if os.name == 'nt':
    _venv_candidate = ROOT / 'venv' / 'Scripts' / 'python.exe'
else:
    _venv_candidate = ROOT / 'venv' / 'bin' / 'python'
if _venv_candidate.exists():
    VENV_PYTHON = str(_venv_candidate)
else:
    VENV_PYTHON = sys.executable
__all__ = ['run_command']

def run_command(task_name, args, cwd=ROOT, check=True):
    '''"""TODO: Add docstring."""'''
    return _runner_run_command(task_name, args, cwd, check)

def _ensure_message(msg: str) -> str:
    '''"""TODO: Add docstring."""'''
    return msg if msg.strip() else 'WIP auto commit'

def python_wip_commit(message: str, cwd: Path):
    '''"""TODO: Add docstring."""'''
    cwd = cwd.resolve()
    subprocess.run(['git', 'add', '-A'], cwd=str(cwd), check=True, text=True)
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as tf:
        tf.write(message or 'auto WIP commit')
        tf.flush()
        temp_path = tf.name
    try:
        subprocess.run(['git', 'commit', '-F', temp_path], cwd=str(cwd), check=True, text=True)
    finally:
        os.unlink(temp_path)

from rich.console import Console
from rich.table import Table

console = Console()

@task
def start(c):
    """System check, status briefing, and session initialization."""
    log_usage('session', 'start', command='start')
    console.print("[bold blue]--- System Status Check ---[/bold blue]")
    doctor_result = run_command('start.doctor', [VENV_PYTHON, 'scripts/doctor.py'], check=False)
    console.print(doctor_result.stdout)
    console.print("[bold blue]--- Task Status ---[/bold blue]")
    try:
        with open('docs/HUB.md', 'r', encoding='utf-8') as f:
            hub_content = f.read()
        active_tasks = hub_manager.parse_tasks(hub_content, 'Active Tasks')
        paused_tasks = hub_manager.parse_tasks(hub_content, 'Paused Tasks')

        table = Table(title="Task Status")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Task", style="magenta")

        for task_name in active_tasks:
            table.add_row("Active", task_name)
        for task_name in paused_tasks:
            table.add_row("Paused", task_name)
        
        console.print(table)

    except FileNotFoundError:
        console.print("[red]docs/HUB.md not found.[/red]")
    console.print("[bold blue]--- Git Status ---[/bold blue]")
    git_status_result = run_command('start.git_status', ['git', 'status', '--porcelain'], check=False)
    if git_status_result.stdout:
        console.print(git_status_result.stdout)
    else:
        console.print("No changes in the working directory.")
    hub_manager.clear_last_session()
    console.print("[bold blue]\n--- Initializing Session ---[/bold blue]")
    build_context_index(c)
    console.print("[bold green]\nMore help is available by typing: invoke help[/bold green]")
    console.print("[bold green]What would you like to do next?[/bold green]")

@task
def end(c, task_id='general'):
    """WIP commit, write __lastSession__ block."""
    run_command('end', ['invoke', 'wip'], check=False)
    hub_manager.update_session_end_info(task_id)
    subprocess.Popen([VENV_PYTHON, "-c", f"from scripts import hub_manager; hub_manager.update_session_end_info('{task_id}')"])
    subprocess.Popen([VENV_PYTHON, "-c", f"from scripts.usage_tracker import log_usage; log_usage('{task_id}', 'session_end', command='end', returncode=0, stdout='session ended', stderr='')"])
    print('end done')

@task
def status(c):
    '''"""TODO: Add docstring."""'''
    run_command('status', ['git', 'status', '--short'], check=False)

@task
def wip(c, message=''):
    """
    PowerShell 호출을 제거한, 순수 Python 버전.
    테스트/실행 환경 모두 동일하게 사용 (권장).
    """
    repo_root = Path.cwd()
    python_wip_commit(message, repo_root)

@task(name='build')
def build_context_index(c):
    '''"""TODO: Add docstring."""'''
    run_command('context.build', [VENV_PYTHON, 'scripts/build_context_index.py'], check=False)

@task(name='query')
def query_context(c, query):
    '''"""TODO: Add docstring."""'''
    run_command('context.query', [VENV_PYTHON, 'scripts/context_store.py', query], check=False)

@task
def test(c):
    '''"""TODO: Add docstring."""'''
    run_command('test', ['pytest', 'tests/', '-q'], check=False)

@task
def clean_cli(c):
    """Clears temporary files and session cache directories."""
    run_command('clean_cli', [VENV_PYTHON, 'scripts/clear_cli_state.py'], check=False)

@task
def doctor(c):
    '''"""TODO: Add docstring."""'''
    run_command('doctor', [VENV_PYTHON, 'scripts/doctor.py'], check=False)

@task
def quickstart(c):
    '''"""TODO: Add docstring."""'''
    run_command('quickstart', [VENV_PYTHON, 'scripts/quickstart.py'], check=False)

@task
def help(c, section='all'):
    '''"""TODO: Add docstring."""'''
    run_command('help', [VENV_PYTHON, 'scripts/help.py', section], check=False)

@task
def search(c, q):
    """invoke search "<query>" : web search + summarize"""
    run_command('search', [VENV_PYTHON, 'scripts/web_agent.py', '--query', q], check=False)

@task(help={'file': 'The file to refactor or inspect.', 'rule': 'The refactoring rule to apply.', 'dry_run': 'Show changes without applying them.', 'yes': 'Apply changes without confirmation.', 'list_rules': 'List all available refactoring rules.', 'explain': 'Explain a specific refactoring rule.'})
def refactor(c, file=None, rule=None, dry_run=False, yes=False, list_rules=False, explain=None):
    """Refactors a file using a plugin-driven rule system."""
    command = [VENV_PYTHON, 'scripts/agents/file_agent.py']
    
    if list_rules:
        command.append('--list')
    elif explain:
        command.append(f'--explain={explain}')
    elif file and rule:
        command.append(f'--file={file}')
        command.append(f'--rule={rule}')
        if dry_run:
            command.append('--dry-run')
        if yes:
            command.append('--yes')
    else:
        # 사용자가 아무 인자도 없이 invoke refactor를 호출했을 때 도움말을 보여주기 위함
        run_command('refactor.help', [VENV_PYTHON, 'scripts/agents/file_agent.py', '--help'], check=False)
        return

    run_command('refactor', command, check=False)
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
ns.add_task(refactor)

@task
def analyze_image(c, image):
    """Analyzes an image file and returns a text description."""
    run_command('analyze_image', [VENV_PYTHON, 'scripts/multimodal_agent.py', '--image', image], check=False)

ns.add_task(analyze_image)

@task
def benchmark(c):
    """Runs performance benchmarks for key functionalities."""
    run_command('benchmark', [VENV_PYTHON, 'scripts/benchmark.py'], check=False)

ns.add_task(benchmark)

@task
def config(c, lang):
    """Sets the CLI language (e.g., 'en', 'ko')."""
    run_command('config', [VENV_PYTHON, 'scripts/config_manager.py', '--lang', lang], check=False)

ns.add_task(config)

# New task for managing task status in HUB.md
@task
def complete_task(c, task_name):
    """Moves a task from Active to Completed in HUB.md."""
    hub_manager.move_task_to_completed(task_name)
    print(f"Task '{task_name}' moved to Completed in HUB.md.")

task_ns = Collection('task')
task_ns.add_task(complete_task, name='complete')
ns.add_collection(task_ns)

ctx_ns = Collection('context')
ctx_ns.add_task(build_context_index, name='build')
ctx_ns.add_task(query_context, name='query')
ns.add_collection(ctx_ns)
program = Program(namespace=ns)