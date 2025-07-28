import pytest
from invoke import Program
from tasks import ns
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_invoke(*args):
    cmd = [sys.executable, "-m", "invoke", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False, cwd=ROOT)
    return proc

def test_invoke_help():
    """Verify that `invoke help` runs without errors and shows key sections."""
    proc = run_invoke("help")
    assert proc.returncode == 0
    assert "주요 명령어" in proc.stdout
    assert "문제 해결" in proc.stdout
    assert "invoke start" in proc.stdout
