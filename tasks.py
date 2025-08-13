from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys
from scripts import hub_manager
from scripts.organizer import organize_scratchpad
from scripts import agent_manager
from scripts.agents import messages as agent_messages
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

@task(
    help={
        'fast': "빠른 시작 모드(검사/인덱스 생략)",
        'skip_doctor': "Doctor 검사를 건너뜀",
        'skip_index': "컨텍스트 인덱스 생성을 건너뜀",
        'bg_index': "인덱스를 백그라운드로 실행(기본 True)",
    }
)
def start(c, fast=False, skip_doctor=False, skip_index=False, bg_index=True):
    """System check, status briefing, and session initialization."""
    log_usage('session', 'start', command='start')

    def _print_quick_status():
        console.print("[bold blue]--- Quick Status ---[/bold blue]")
        active = agent_manager.get_active_agent()
        console.print(f"Active Agent: [bold]{active}[/bold]")
        git_status_result = run_command('start.git_status', ['git', 'status', '--porcelain'], check=False)
        changed = bool(git_status_result.stdout.strip())
        console.print("Changes: " + ("YES" if changed else "NO"))
        if changed:
            console.print(git_status_result.stdout)
        # Inbox summary
        try:
            ucnt = agent_messages.unread_count(active)
            console.print(f"Inbox: {ucnt} unread for {active}")
            if ucnt:
                msgs = agent_messages.list_inbox(active, unread_only=True, limit=5)
                for m in msgs:
                    tags = (", ".join(m.tags)) if m.tags else ""
                    tag_str = f" [{tags}]" if tags else ""
                    console.print(f"- {m.ts} from:{m.sender}{tag_str} :: {m.body[:120]}")
        except Exception:
            pass
        console.print("Hint: invoke help | invoke test | invoke search \"query\" | invoke agent.inbox --unread")

    if fast:
        _print_quick_status()
        console.print("[dim]Fast mode: doctor/HUB/index 생략[/dim]")
    else:
        console.print("[bold blue]--- System Status Check ---[/bold blue]")
        if not skip_doctor:
            doctor_result = run_command('start.doctor', [VENV_PYTHON, 'scripts/doctor.py'], check=False)
            console.print(doctor_result.stdout)
        else:
            console.print("[dim]Skip doctor[/dim]")

        console.print("[bold blue]--- Task Status ---[/bold blue]")
        try:
            with open('docs/HUB.md', 'r', encoding='utf-8') as f:
                hub_content = f.read()

            staging_tasks = hub_manager.parse_tasks(hub_content, 'Staging Tasks')
            active_tasks = hub_manager.parse_tasks(hub_content, 'Active Tasks')
            planned_tasks = hub_manager.parse_tasks(hub_content, 'Planned Tasks')
            paused_tasks = hub_manager.parse_tasks(hub_content, 'Paused Tasks')

            table = Table(title="Task Status")
            table.add_column("Status", style="cyan", no_wrap=True)
            table.add_column("Task", style="magenta")

            if staging_tasks:
                for task_name in staging_tasks:
                    table.add_row(" Staging ", task_name)
            if active_tasks:
                for task_name in active_tasks:
                    table.add_row(" Active ", task_name)
            if planned_tasks:
                for task_name in planned_tasks:
                    table.add_row(" Planned ", task_name)
            if paused_tasks:
                for task_name in paused_tasks:
                    table.add_row(" Paused ", task_name)

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
        if skip_index:
            console.print("[dim]Skip context index build[/dim]")
        else:
            if bg_index:
                # 백그라운드 인덱싱
                subprocess.Popen([VENV_PYTHON, 'scripts/build_context_index.py'])
                console.print("Context index building in background...")
            else:
                build_context_index(c)

        console.print("[bold green]\nMore help: invoke help[/bold green]")
        console.print("[bold green]Next: invoke test / search \"query\"[/bold green]")

    # Fast 모드에서도 마지막 안내는 공통 제공
    active = agent_manager.get_active_agent()
    console.print(f"[dim]Agent=[{active}] Ready. What next?[/dim]")

@task(name='start_fast')
def start_fast(c):
    """Alias for fast start: invoke start --fast"""
    start(c, fast=True)


# --- Agent messaging tasks ---
from invoke import Argument  # noqa: F401 (kept for potential future CLI arg specs)


@task(
    help={
        'to': "수신 에이전트명(codex|gemini|all)",
        'body': "메시지 본문",
        'tags': "쉼표구분 태그들(선택)",
        'sender': "발신자 지정(기본: ACTIVE_AGENT)"
    }
)
def agent_msg(c, to, body, tags='', sender=None):
    """다른 에이전트에게 메시지를 남깁니다."""
    tag_list = [t.strip() for t in (tags or '').split(',') if t.strip()]
    msg = agent_messages.append_message(to=to, body=body, tags=tag_list, sender=sender)
    console.print(f"[green]Message queued[/green] ts={msg.ts} from={msg.sender} -> {msg.to}")


@task(
    help={
        'agent': "인박스를 조회할 에이전트(기본: active)",
        'since': "조회 기준 시각(예: 24h, 7d, ISO)",
        'unread': "읽지 않은 항목만",
        'limit': "표시 개수(기본 20)",
        'write_md': ".agents/inbox/<agent>.md 파일 업데이트"
    }
)
def agent_inbox(c, agent=None, since='', unread=False, limit=20, write_md=True):
    """에이전트 인박스를 조회합니다."""
    target = agent or agent_manager.get_active_agent()
    msgs = agent_messages.list_inbox(target, since=since or None, unread_only=bool(unread), limit=int(limit))
    if write_md:
        path = agent_messages.write_inbox_markdown(target, msgs)
        console.print(f"Updated inbox markdown: {path}")
    if not msgs:
        console.print("No messages.")
    else:
        console.print(f"Showing {len(msgs)} messages for {target}:")
        for m in msgs:
            tags = (", ".join(m.tags)) if m.tags else ""
            tag_str = f" [{tags}]" if tags else ""
            console.print(f"- {m.ts} from:{m.sender}{tag_str}\n  - {m.body}")


@task(
    help={'agent': "읽음 처리할 에이전트(기본: active)"}
)
def agent_read(c, agent=None):
    """인박스를 읽음 처리합니다."""
    target = agent or agent_manager.get_active_agent()
    ts = agent_messages.mark_read(target)
    console.print(f"Marked inbox as read for {target} at {ts}")

@task
def end(c, task_id='general'):
    """WIP commit, write __lastSession__ block, ensure HUB.md is committed."""
    # General WIP commit first
    run_command('end', ['invoke', 'wip'], check=False)
    # Update HUB session info synchronously
    try:
        hub_manager.update_session_end_info(task_id)
    except Exception as e:
        console.print(f"[red]HUB update failed: {e}[/red]")
    # Explicitly stage and commit HUB.md if changed
    try:
        subprocess.run(['git', 'add', 'docs/HUB.md'], check=False, text=True)
        res = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, check=False)
        if 'docs/HUB.md' in (res.stdout or ''):
            with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8') as tf:
                tf.write(f"chore(hub): update session info for {task_id}\n")
                tf.flush()
                temp_path = tf.name
            try:
                subprocess.run(['git', 'commit', '-F', temp_path], check=True, text=True)
            finally:
                os.unlink(temp_path)
    except Exception as e:
        console.print(f"[yellow]HUB auto-commit skipped/failed: {e}[/yellow]")
    # Log usage asynchronously
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
    run_command('test', [VENV_PYTHON, '-m', 'pytest', 'tests/', '-q'], check=False)

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
    # 에이전트별 분기: scripts/agents/<agent>/web_agent.py 가 있으면 사용, 없으면 기본
    agent = agent_manager.get_active_agent()
    agent_script = ROOT / 'scripts' / 'agents' / agent / 'web_agent.py'
    if agent_script.exists():
        cmd = [VENV_PYTHON, str(agent_script), '--query', q]
    else:
        cmd = [VENV_PYTHON, 'scripts/web_agent.py', '--query', q]
    run_command('search', cmd, check=False)

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

@task
def auto_scan(c):
    c.run(f"{sys.executable} scripts/auto_update/scanner.py", pty=False)

@task
def auto_propose(c):
    c.run(f"{sys.executable} scripts/auto_update/proposer.py", pty=False)

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
ns.add_task(organize_scratchpad)

auto_ns = Collection('auto')
auto_ns.add_task(auto_scan, name='scan')
auto_ns.add_task(auto_propose, name='propose')
ns.add_collection(auto_ns)

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

# Agent messaging namespace
agent_ns = Collection('agent')
agent_ns.add_task(agent_msg, name='msg')
agent_ns.add_task(agent_inbox, name='inbox')
agent_ns.add_task(agent_read, name='read')
ns.add_collection(agent_ns)

# --- Claude tasks ---
from invoke import task as _task

@_task
def claude_help(c):
    """Show Claude router help."""
    run_command('claude.help', [VENV_PYTHON, 'claude.py', '/help'], check=False)


@_task(help={'q': 'Query, e.g., "/think <q>" or plain text.'})
def claude_run(c, q):
    """Run Claude router with a query string."""
    run_command('claude.run', [VENV_PYTHON, 'claude.py', q], check=False)

claude_ns = Collection('claude')
claude_ns.add_task(claude_help, name='help')
claude_ns.add_task(claude_run, name='run')
ns.add_collection(claude_ns)


@task(
    help={
        'agent': "감시할 에이전트(기본: active)",
        'interval': "폴링 간격(초, 기본 5)",
        'ack': "새 메시지에 자동 확인 응답(ACK) 남김",
        'mark_read': "처리 후 읽음 처리(기본 True)"
    }
)
def agent_watch(c, agent=None, interval=5, ack=False, mark_read=True, duration=None):
    """새 메시지를 주기적으로 감시합니다(Ctrl+C로 종료)."""
    import time
    # optional bounded run
    end_ts = None
    if duration is not None:
        try:
            d = int(duration)
            if d > 0:
                end_ts = time.time() + d
        except Exception:
            end_ts = None

    target = agent or agent_manager.get_active_agent()
    console.print(f"[bold blue]Watching inbox for {target}[/bold blue] every {interval}s...")
    try:
        while True:
            msgs = agent_messages.list_inbox(target, unread_only=True, limit=100)
            if msgs:
                console.print(f"[yellow]New messages: {len(msgs)}[/yellow]")
                for m in reversed(msgs):  # 시간순 출력
                    tags = (", ".join(m.tags)) if m.tags else ""
                    tag_str = f" [{tags}]" if tags else ""
                    console.print(f"- {m.ts} from:{m.sender}{tag_str}\n  - {m.body}")
                    # 자동 ACK (무한 루프 방지: ack 태그에는 응답하지 않음)
                    if ack and m.sender and m.sender != target and ("ack" not in (m.tags or [])):
                        try:
                            agent_messages.append_message(
                                to=m.sender,
                                body=f"ACK: {m.body[:200]}",
                                tags=["ack"],
                                sender=target,
                            )
                            console.print(f"  [dim]ACK sent to {m.sender}[/dim]")
                        except Exception as e:
                            console.print(f"  [red]ACK failed:[/red] {e}")
                if mark_read:
                    # Advance read pointer to the newest processed message
                    try:
                        latest_ts = msgs[0].ts
                    except Exception:
                        latest_ts = None
                    agent_messages.mark_read(target, ts=latest_ts)
            # stop after duration if requested
            if end_ts is not None and time.time() >= end_ts:
                break
            time.sleep(int(interval))
    except KeyboardInterrupt:
        console.print("\n[dim]Watcher stopped[/dim]")
    finally:
        if end_ts is not None:
            console.print("[dim]Watcher finished (duration reached)[/dim]")

# Register watch task under agent namespace as well
agent_ns.add_task(agent_watch, name='watch')

# --- Agent management tasks ---
from invoke import task as _task_alias  # avoid shadowing

@_task_alias
def agent_status(c):
    """Shows the currently active agent."""
    name = agent_manager.get_active_agent()
    print(f"Active agent: {name}")


@_task_alias
def agent_set(c, name):
    """Sets the active agent (gemini|codex)."""
    updated = agent_manager.set_active_agent(name)
    print(f"Active agent set to: {updated}")


# Reuse existing 'agent' namespace defined above; just add tasks
agent_ns.add_task(agent_status, name='status')
agent_ns.add_task(agent_set, name='set')
program = Program(namespace=ns)

# --- Hub (agents_hub) tasks ---
@task
def hub_send(c, to, title, body, type='message', tags=''):
    """Send a message/task to another agent via hub."""
    tag_list = [t for t in tags.split(',') if t.strip()]
    run_command('hub.send', [VENV_PYTHON, 'scripts/agents/broker.py', 'send', '--to', to, '--title', title, '--body', body, '--type', type, '--tags', *tag_list], check=False)


@task
def hub_inbox(c, agent=None):
    """List pending items for agent (default: active agent)."""
    agent = agent or agent_manager.get_active_agent()
    run_command('hub.list', [VENV_PYTHON, 'scripts/agents/broker.py', 'list', '--for', agent], check=False)


@task
def hub_claim(c, agent=None):
    """Claim one pending item for agent and move to processing."""
    agent = agent or agent_manager.get_active_agent()
    run_command('hub.claim', [VENV_PYTHON, 'scripts/agents/broker.py', 'claim', '--agent', agent], check=False)


@task
def hub_complete(c, id, status='success', note='', agent=None):
    """Complete a processing item and archive it."""
    agent = agent or agent_manager.get_active_agent()
    args = [VENV_PYTHON, 'scripts/agents/broker.py', 'complete', '--agent', agent, '--id', id, '--status', status]
    if note:
        args += ['--note', note]
    run_command('hub.complete', args, check=False)


hub_ns = Collection('hub')
hub_ns.add_task(hub_send, name='send')
hub_ns.add_task(hub_inbox, name='inbox')
hub_ns.add_task(hub_claim, name='claim')
hub_ns.add_task(hub_complete, name='complete')
ns.add_collection(hub_ns)

# --- Review / Git helpers ---
@task
def review(c):
    """Show a quick preview of changes (status + diff summary)."""
    console.print("[bold blue]--- Git Status ---[/bold blue]")
    res = run_command('review.status', ['git', 'status', '--porcelain'], check=False)
    console.print(res.stdout or 'Clean')
    console.print("[bold blue]--- Diff (names) ---[/bold blue]")
    res2 = run_command('review.diffnames', ['git', 'diff', '--name-only'], check=False)
    console.print(res2.stdout or '(no unstaged diffs)')
    # Optional short patch at the end for quick glance
    run_command('review.diff', ['git', '--no-pager', 'diff', '--stat'], check=False)


@task
def review_staged(c):
    """Show staged changes (diff --cached)."""
    run_command('review.staged', ['git', '--no-pager', 'diff', '--cached'], check=False)


@task
def review_last(c, n=1):
    """Show last commit patch (HEAD~n..HEAD)."""
    rng = f'HEAD~{int(n)}..HEAD'
    run_command('review.last', ['git', '--no-pager', 'show', rng, '--stat', '--patch'], check=False)


@task
def commit_safe(c, message, no_verify=False, skip_add=False, skip_diff_confirm=False):
    """Commit via Python helper to avoid quoting/guard issues."""
    args = [VENV_PYTHON, 'scripts/commit_helper.py', '--message', message]
    if no_verify:
        args.append('--no-verify')
    if skip_add:
        args.append('--skip-add')
    if skip_diff_confirm:
        args.append('--skip-diff-confirm')
    run_command('commit.safe', args, check=False)


@task
def git_push(c):
    """Push current branch to origin (safe with rebase retry)."""
    run_command('git.push', [VENV_PYTHON, 'scripts/git_safe.py'], check=False)


@task
def git_untrack_projects(c):
    """Remove projects/* from git index (keep files on disk) and commit."""
    run_command('git.rm_cached', ['git', 'rm', '-r', '--cached', 'projects'], check=False)
    # Commit with allow-projects to include the index removal
    run_command('git.commit_untrack', [VENV_PYTHON, 'scripts/commit_helper.py', '--message', 'chore(git): untrack projects/* from repo index', '--no-verify', '--allow-projects'], check=False)


# --- OS tools ---
@task
def os_audit(c):
    """OS 명령 일관성 감사 리포트를 생성합니다."""
    log_usage('os', 'audit', command='os.audit')
    run_command('os.audit', [VENV_PYTHON, 'scripts/tools/os_command_audit.py'], check=False)

os_ns = Collection('os')
os_ns.add_task(os_audit, name='audit')
ns.add_collection(os_ns)
ns.add_task(review, name='review')
ns.add_task(review_staged, name='review_staged')
ns.add_task(review_last, name='review_last')

git_ns = Collection('git')
git_ns.add_task(commit_safe, name='commit_safe')
git_ns.add_task(git_push, name='push')
git_ns.add_task(git_untrack_projects, name='untrack-projects')
ns.add_collection(git_ns)

# --- Git hooks toggle ---
@task(help={"on": "true/false to enable or disable hooks"})
def set_hooks(c, on='false'):
    """Enable/disable pre-commit hooks via .agents/config.json."""
    import json
    cfg_path = ROOT / '.agents' / 'config.json'
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "hooks": {
            "enabled": str(on).lower() in {"1", "true", "yes", "on"},
            "diff_confirm": True,
        }
    }
    cfg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    console.print(f"Hooks enabled={data['hooks']['enabled']}. Updated {cfg_path}")

git_ns.add_task(set_hooks, name='set-hooks')

# --- Edits (pre-edit diff workflow) ---
@task
def edits_capture(c, file):
    run_command('edits.capture', [VENV_PYTHON, 'scripts/edits_manager.py', 'capture', '--file', file], check=False)


@task
def edits_propose(c, file, from_file=None, content=None):
    args = [VENV_PYTHON, 'scripts/edits_manager.py', 'propose', '--file', file]
    if from_file:
        args += ['--from-file', from_file]
    if content:
        args += ['--content', content]
    run_command('edits.propose', args, check=False)


@task
def edits_list(c):
    run_command('edits.list', [VENV_PYTHON, 'scripts/edits_manager.py', 'list'], check=False)


@task
def edits_diff(c, file=None):
    args = [VENV_PYTHON, 'scripts/edits_manager.py', 'diff']
    if file:
        args += ['--file', file]
    run_command('edits.diff', args, check=False)


@task
def edits_apply(c, file=None, keep=False):
    args = [VENV_PYTHON, 'scripts/edits_manager.py', 'apply']
    if file:
        args += ['--file', file]
    if keep:
        args.append('--keep')
    run_command('edits.apply', args, check=False)


@task
def edits_discard(c, file):
    run_command('edits.discard', [VENV_PYTHON, 'scripts/edits_manager.py', 'discard', '--file', file], check=False)


edits_ns = Collection('edits')
edits_ns.add_task(edits_capture, name='capture')
edits_ns.add_task(edits_propose, name='propose')
edits_ns.add_task(edits_list, name='list')
edits_ns.add_task(edits_diff, name='diff')
edits_ns.add_task(edits_apply, name='apply')
edits_ns.add_task(edits_discard, name='discard')
ns.add_collection(edits_ns)

# --- Text utils ---
@task(help={
    'file': 'Target file path',
    'old': 'Old string',
    'new': 'New string',
    'expect': 'Expected replacements (0 ignore)',
    'dry_run': 'Preview only'
})
def text_replace(c, file, old, new, expect=0, dry_run=False):
    """Replace text with line-ending tolerance (CRLF/LF)."""
    args = [VENV_PYTHON, 'scripts/textops.py', 'replace', '--file', file, '--old', old, '--new', new]
    try:
        exp = int(expect)
    except Exception:
        exp = 0
    if exp:
        args += ['--expect', str(exp)]
    if dry_run:
        args += ['--dry-run']
    run_command('text.replace', args, check=False)

text_ns = Collection('text')
text_ns.add_task(text_replace, name='replace')
ns.add_collection(text_ns)

# --- Archive tasks ---
@task
def archive_save(c, title, content=None, from_file=None, agent=None):
    args = [VENV_PYTHON, 'scripts/archive_manager.py', 'save', '--title', title]
    if content:
        args += ['--content', content]
    if from_file:
        args += ['--from-file', from_file]
    if agent:
        args += ['--agent', agent]
    run_command('archive.save', args, check=False)


@task
def archive_export(c, day=None):
    args = [VENV_PYTHON, 'scripts/archive_manager.py', 'export']
    if day:
        args += ['--day', day]
    run_command('archive.export', args, check=False)


arch_ns = Collection('archive')
arch_ns.add_task(archive_save, name='save')
arch_ns.add_task(archive_export, name='export')
ns.add_collection(arch_ns)

# --- Hub watcher ---
@task
def hub_watch(c, agent=None, interval=5):
    agent = agent or agent_manager.get_active_agent()
    run_command('hub.watch', [VENV_PYTHON, 'scripts/agents/watcher.py', '--agent', agent, '--interval', str(interval)], check=False)

hub_ns.add_task(hub_watch, name='watch')

# --- Preferences (toggle features) ---
@task
def prefs_show(c):
    print({
        'active': agent_manager.get_active_agent(),
        'diff_confirm': agent_manager.get_flag('diff_confirm', True),
        'edits_enforce': agent_manager.get_flag('edits_enforce', True),
    })


@task
def prefs_set(c, key, value):
    # bool parsing
    v = value
    if value.lower() in {'true', '1', 'on', 'yes'}:
        v = True
    elif value.lower() in {'false', '0', 'off', 'no'}:
        v = False
    agent_manager.set_flag(key, v)
    prefs_show(c)


prefs_ns = Collection('prefs')
prefs_ns.add_task(prefs_show, name='show')
prefs_ns.add_task(prefs_set, name='set')
ns.add_collection(prefs_ns)
