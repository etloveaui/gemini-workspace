import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from . import agent_manager

console = Console()

def confirm_action(message: str, choices: list[str], default: str = None) -> str:
    """
    Presents an interactive prompt to the user for confirmation.
    """
    completer = WordCompleter(choices, ignore_case=True)
    while True:
        try:
            answer = prompt(f"{message} ({'/'.join(choices)}) ", completer=completer, default=default).strip()
            if answer in choices:
                return answer
            else:
                print(f"Invalid choice. Please select one of: {', '.join(choices)}")
        except EOFError:
            # User pressed Ctrl+D
            print("Operation cancelled by user.")
            return None
        except KeyboardInterrupt:
            # User pressed Ctrl+C
            print("Operation cancelled by user.")
            return None

# 환경 변수 또는 기본 경로를 사용하여 DB 경로 설정
DEFAULT_DB_PATH = Path(os.getenv("GEMINI_USAGE_DB_PATH", Path(__file__).parent.parent / "usage.db"))
ROOT = Path(__file__).resolve().parents[1]

def _ensure_db(db_path: Path = DEFAULT_DB_PATH):
    """지정된 경로에 DB와 'usage' 테이블이 있는지 확인하고 없으면 생성합니다."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 동시 실행 안정화: WAL 모드 및 합리적 동기화 레벨 설정
    try:
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    # 스키마를 Debug_21.md에 명시된 내용과 유사하게, 하지만 기존 컬럼 유지
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            command TEXT,
            stdout TEXT,
            stderr TEXT,
            returncode INTEGER,
            error_type TEXT,
            error_message TEXT
        )
    """)
    # 마이그레이션: 누락된 컬럼이 있으면 추가
    cur.execute("PRAGMA table_info(usage);")
    cols = {row[1] for row in cur.fetchall()}
    migrations = []
    if "stdout" not in cols:
        migrations.append("ALTER TABLE usage ADD COLUMN stdout TEXT;")
    if "stderr" not in cols:
        migrations.append("ALTER TABLE usage ADD COLUMN stderr TEXT;")
    if "returncode" not in cols:
        migrations.append("ALTER TABLE usage ADD COLUMN returncode INTEGER;")
    if "error_type" not in cols:
        migrations.append("ALTER TABLE usage ADD COLUMN error_type TEXT;")
    if "error_message" not in cols:
        migrations.append("ALTER TABLE usage ADD COLUMN error_message TEXT;")
    for sql in migrations:
        try:
            cur.execute(sql)
        except Exception:
            pass
    conn.commit()
    conn.close()

def _log_event(task_name: str, event_type: str, command: str, stdout: str, stderr: str, returncode: int = None, error_type: str = None, error_message: str = None, db_path: Path = DEFAULT_DB_PATH):
    """이벤트(특히 오류)를 DB에 기록합니다."""
    _ensure_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usage (timestamp, task_name, event_type, command, stdout, stderr, returncode, error_type, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now(timezone.utc).isoformat(), task_name, event_type, command, stdout, stderr, returncode, error_type, error_message))
    conn.commit()
    conn.close()

def run_command(task_name: str, args: list[str], cwd=None, check=True, db_path: Path = DEFAULT_DB_PATH):
    """
    명령어를 실행하고, 실패 시 오류를 DB에 로깅합니다.
    - shell=False 원칙 유지
    - cwd는 Path 객체 또는 str로 받을 수 있음
    """
    _ensure_db(db_path)
    
    # cwd가 None일 경우, 프로젝트 루트를 기본값으로 사용
    effective_cwd = Path(cwd).resolve() if cwd else ROOT
    
    # 자식 프로세스에 전달할 환경 변수 설정
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    agent = agent_manager.get_active_agent()
    console.print(f"[bold green][RUN:{task_name}][agent={agent}][/bold green] args={args!r}, cwd={str(effective_cwd)!r}")

    try:
        cp = subprocess.run(
            args,
            cwd=str(effective_cwd),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=check,
            shell=False,  # 보안을 위해 shell=False 유지
            env=env
        )
        return cp
    except subprocess.CalledProcessError as e:
        error_type = "CalledProcessError"
        error_message = str(e)
        _log_event(
            task_name=task_name,
            event_type="command_error",
            command=f"AGENT={agent} " + " ".join(args),
            stdout=e.stdout,
            stderr=e.stderr,
            returncode=e.returncode,
            error_type=error_type,
            error_message=error_message,
            db_path=db_path
        )
        console.print(Panel(
            Text(f"Command failed with exit code {e.returncode}.\n\n[bold red]Stderr:[/bold red]\n{e.stderr}\n\n[bold yellow]Stdout:[/bold yellow]\n{e.stdout}", style="red"),
            title=f"[bold red]Error in {task_name}[/bold red]",
            border_style="red"
        ))
        console.print(Panel(
            Text("Possible solutions: Check the command syntax, ensure all dependencies are installed, or verify file paths.", style="cyan"),
            title="[bold cyan]Suggested Solutions[/bold cyan]",
            border_style="cyan"
        ))
        raise
    except FileNotFoundError as e:
        error_type = "FileNotFoundError"
        error_message = str(e)
        _log_event(
            task_name=task_name,
            event_type="file_not_found_error",
            command=f"AGENT={agent} " + " ".join(args),
            stdout="",
            stderr=str(e),
            returncode=-1,
            error_type=error_type,
            error_message=error_message,
            db_path=db_path
        )
        console.print(Panel(
            Text(f"Command not found: {e.strerror}.\n\n[bold red]Error Message:[/bold red]\n{e.strerror}", style="red"),
            title=f"[bold red]Error in {task_name}[/bold red]",
            border_style="red"
        ))
        console.print(Panel(
            Text("Possible solutions: Ensure the command is correctly spelled and is in your system's PATH. If it's a script, verify its existence and permissions.", style="cyan"),
            title="[bold cyan]Suggested Solutions[/bold cyan]",
            border_style="cyan"
        ))
        raise
