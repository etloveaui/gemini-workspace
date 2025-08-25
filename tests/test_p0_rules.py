import os
import subprocess
import pytest
from invoke import Program
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tasks import ns
import shutil
from pathlib import Path
import sqlite3
import time
import importlib

# run_command는 runner에서 직접 가져오지 않고, runner 모듈을 통해 접근합니다.
from scripts import runner

import time
import re

# --- Constants and Test Setup ---
ROOT = Path(__file__).resolve().parent.parent
HUB_PATH = get_workspace_path("docs", "CORE", "HUB_ENHANCED.md")

# 전역 DB_PATH는 이제 사용하지 않음
# DB_PATH = ROOT / "usage.db"

@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """테스트마다 격리된 임시 데이터베이스를 생성하고 경로를 반환합니다."""
    db_path = tmp_path / "test_usage.db"
    # 환경 변수를 설정하여 runner 모듈이 이 DB를 사용하도록 합니다.
    monkeypatch.setenv("GEMINI_USAGE_DB_PATH", str(db_path))
    
    # runner 모듈을 리로드하여 변경된 환경 변수를 적용합니다.
    importlib.reload(runner)
    
    yield db_path
    
    # 테스트 종료 후 임시 DB 파일이 삭제되도록 보장 (tmp_path가 자동으로 처리)

@pytest.fixture(scope="function")
def test_env(isolated_db):
    # --- Setup ---
    initial_hub_content = """# Workspace HUB

*Last Updated: 2025-07-22*

## Projects

## Active Tasks

## Paused Tasks

## Completed Tasks
"""
    if HUB_PATH.exists():
        HUB_PATH.write_text(initial_hub_content, encoding="utf-8", newline='')

    yield

    # --- Teardown ---
    if HUB_PATH.exists():
        HUB_PATH.write_text(initial_hub_content, encoding="utf-8", newline='')

# --- Test Cases ---

def test_runner_error_logging(isolated_db):
    """runner.run_command 실패 시, 지정된 DB에 command_error가 기록되는지 검증합니다."""
    # 실패가 보장된 명령어 실행
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_command(
            "test_error_task", 
            ["python", "-c", "import sys; sys.exit(1)"],
            db_path=isolated_db  # 격리된 DB 경로를 명시적으로 전달
        )

    # 검증: 격리된 DB에 오류 로그가 기록되었는지 확인
    conn = sqlite3.connect(isolated_db)
    cur = conn.cursor()
    cur.execute("SELECT task_name, event_type, command, stderr, returncode FROM usage ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    assert row is not None, "usage 테이블에 기록이 없습니다."
    assert row[0] == "test_error_task"
    assert row[1] == "command_error"
    assert "sys.exit(1)" in (row[2] or "")
    assert row[4] == 1 # stderr

def test_debug_19_doc_exists():
    from pathlib import Path
    assert Path("scratchpad/Gemini-Self-Upgrade/[P0]Debug_19.md").exists(), "[P0]Debug_19.md 문서가 삭제됨!"


def test_debug20_doc_exists():
    from pathlib import Path
    assert Path("docs/debug/[P0]Debug_20.md").exists(), "[P0]Debug_20.md 문서가 삭제됨!"