import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "usage.db"

def _ensure_db():
    conn = sqlite3.connect(DB_PATH)
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
    """)
    conn.commit()
    conn.close()

def _log(task_name, event_type, command, returncode=None, stdout="", stderr=""):
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO usage (timestamp, task_name, event_type, command, returncode, stdout, stderr) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ts, task_name, event_type, " ".join(command) if isinstance(command, (list, tuple)) else str(command),
         returncode if returncode is not None else None, stdout, stderr)
    )
    conn.commit()
    conn.close()

def run_command(task_name: str, args: list[str], cwd=ROOT, check=True):
    """
    안전 실행 래퍼:
    - shell=False
    - 리스트 인자만
    - cwd는 절대경로 str
    """
    abs_cwd = str(Path(cwd).resolve()) if cwd else None
    print(f"[RUN:{task_name}] args={args!r}, cwd={abs_cwd!r}")
    cp = subprocess.run(
        args,
        cwd=abs_cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
        shell=False
    )
    return cp
