# /scripts/usage_tracker.py
import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "usage.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            tokens INTEGER,
            cost REAL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_usage(task_id: str, event_type: str, tokens: int = 0, cost: float = 0.0, description: str = ""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO usage_logs (timestamp, task_id, event_type, tokens, cost, description) VALUES (?, ?, ?, ?, ?, ?)",
                   (timestamp, task_id, event_type, tokens, cost, description))
    conn.commit()
    conn.close()

def get_session_summary(task_id: str = None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT SUM(tokens), SUM(cost) FROM usage_logs"
    params = []
    if task_id:
        query += " WHERE task_id = ?"
        params.append(task_id)

    cursor.execute(query, params)
    tokens, cost = cursor.fetchone()
    conn.close()
    return {"total_tokens": tokens if tokens else 0, "total_cost": cost if cost else 0.0}

if __name__ == "__main__":
    # 테스트용
    init_db()
    log_usage("test_task", "start", description="Test session start")
    log_usage("test_task", "tool_call", tokens=100, cost=0.001, description="Tool call example")
    log_usage("test_task", "end", description="Test session end")
    summary = get_session_summary("test_task")
    print(f"Test Task Summary: {summary}")
