import sqlite3
from pathlib import Path
import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "usage.db"

def log_usage(task_name: str, event_type: str, command: str = None, returncode: int = None, stdout: str = None, stderr: str = None):
    """태스크 사용 로그를 기록합니다."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # usage_tracker.py가 runner.py의 스키마를 따르도록 수정
        cursor.execute("""
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
        cursor.execute("""
        INSERT INTO usage (timestamp, task_name, event_type, command, returncode, stdout, stderr)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, task_name, event_type, command, returncode, stdout, stderr))
        conn.commit()