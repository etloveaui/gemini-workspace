import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import json

# 환경 변수 또는 기본 경로를 사용하여 DB 경로 설정
DEFAULT_DB_PATH = Path(os.getenv("GEMINI_USAGE_DB_PATH", Path(__file__).parent.parent / "usage.db"))
ROOT = Path(__file__).resolve().parents[1]

def _ensure_db(db_path: Path = DEFAULT_DB_PATH):
    """지정된 경로에 DB와 'usage' 테이블이 있는지 확인하고 없으면 생성합니다."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
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
            returncode INTEGER
        )
    """)
    conn.commit()
    conn.close()

def _log_event(task_name: str, event_type: str, command: str, stdout: str, stderr: str, returncode: int = None, db_path: Path = DEFAULT_DB_PATH):
    """이벤트(특히 오류)를 DB에 기록합니다."""
    _ensure_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usage (timestamp, task_name, event_type, command, stdout, stderr, returncode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now(timezone.utc).isoformat(), task_name, event_type, command, stdout, stderr, returncode))
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
    
    print(f"[RUN:{task_name}] args={args!r}, cwd={str(effective_cwd)!r}")

    try:
        cp = subprocess.run(
            args,
            cwd=str(effective_cwd),
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=check,
            shell=False  # 보안을 위해 shell=False 유지
        )
        return cp
    except subprocess.CalledProcessError as e:
        # 실패 시 로그 기록
        _log_event(
            task_name=task_name,
            event_type="command_error",
            command=" ".join(args),
            stdout=e.stdout,
            stderr=e.stderr,
            returncode=e.returncode,
            db_path=db_path
        )
        raise
    except FileNotFoundError as e:
        # 명령어 자체를 찾지 못한 경우
        _log_event(
            task_name=task_name,
            event_type="file_not_found_error",
            command=" ".join(args),
            stdout="",
            stderr=str(e),
            returncode=-1, # 임의의 에러 코드
            db_path=db_path
        )
        raise

