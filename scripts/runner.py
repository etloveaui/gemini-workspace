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

def run_command(task_name, args, cwd=ROOT, check=True):
    if not isinstance(args, (list, tuple)):
        raise TypeError("args must be list/tuple of command tokens")

    _log(task_name, "command_start", args)
    try:
        cp = subprocess.run(args, capture_output=True, text=True, cwd=cwd, check=check)
        _log(task_name, "command_end", args, cp.returncode, cp.stdout, cp.stderr)
        return cp
    except subprocess.CalledProcessError as e:
        _log(task_name, "command_error", args, e.returncode, e.stdout, e.stderr)
        raise
