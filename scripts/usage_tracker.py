import sqlite3
from pathlib import Path
import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "usage.db"

def setup_database():
    """데이터베이스와 테이블을 생성합니다."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_name TEXT NOT NULL,
            event_type TEXT NOT NULL, -- e.g., 'start', 'end', 'error'
            details TEXT
        )
        """)
        conn.commit()

def log_usage(task_name: str, event_type: str, details: str = None):
    """태스크 사용 로그를 기록합니다."""
    setup_database()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO usage (timestamp, task_name, event_type, details)
        VALUES (?, ?, ?, ?)
        """, (timestamp, task_name, event_type, details))
        conn.commit()