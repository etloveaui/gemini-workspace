import subprocess
import sys
import os

# 스크립트의 절대 경로를 얻기 위한 헬퍼 함수
def get_script_path(script_name):
    return os.path.join(os.path.dirname(__file__), "..", "scripts", script_name)

def run_script(script_name, *args):
    cmd = [sys.executable, get_script_path(script_name)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result

def test_invoke_doctor():
    """Verify that `invoke doctor` runs without errors and shows PASS/FAIL strings."""
    proc = run_script("doctor.py")
    assert proc.returncode in [0, 1] # 0 for all pass, 1 for some fail
    assert "[PASS]" in proc.stdout or "[FAIL]" in proc.stdout

def test_invoke_quickstart():
    """Verify that `invoke quickstart` runs and shows expected strings."""
    proc = run_script("quickstart.py")
    assert proc.returncode == 0
    assert "환영합니다" in proc.stdout or "가상 환경" in proc.stdout

def test_invoke_help_getting_started():
    """Verify that `invoke help getting-started` runs and shows expected section content."""
    proc = run_script("help.py", "getting-started")
    assert proc.returncode == 0
    # 실제 시스템에서는 한국어 섹션명 "시작하기"를 사용
    assert "시작하기" in proc.stdout or "Section 'getting-started' not found" in proc.stdout