#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "usage.db"


def _ensure_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    cur.execute(
        """
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
        """
    )
    conn.commit()
    conn.close()


def record_event(
    task_name: str,
    event_type: str,
    command: Optional[str] = None,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    returncode: Optional[int] = None,
    db_path: Path = DB_PATH,
) -> None:
    """Record a generic event into the canonical `usage` table.

    - Non-blocking best-effort: swallows exceptions to avoid impacting caller.
    - Compatible with token_usage_report aggregation.
    """
    try:
        _ensure_db(db_path)
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO usage (timestamp, task_name, event_type, command, stdout, stderr, returncode, error_type, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                task_name,
                event_type,
                command,
                stdout,
                stderr,
                returncode,
                None,
                None,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        # Best-effort; do not raise
        pass

