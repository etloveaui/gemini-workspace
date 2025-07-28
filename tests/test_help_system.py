import pytest
from invoke import Program
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tasks import ns

def run_invoke(*args):
    cmd = [sys.executable, "-m", "invoke", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', shell=False, cwd=ROOT)
    return proc

def test_invoke_help():
    """Verify that `invoke help` runs without errors and shows key sections."""
    proc = run_invoke("help")
    assert proc.returncode == 0
    assert "Commands Overview" in proc.stdout
    assert "Troubleshooting" in proc.stdout
    assert "invoke doctor" in proc.stdout
