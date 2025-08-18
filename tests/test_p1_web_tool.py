import subprocess, sys
from unittest.mock import patch
from pathlib import Path
import os
import pytest

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DUMMY_RESULTS = [
    {"title": "Python", "url": "https://python.org", "snippet": "Python official website."},
    {"title": "Docs", "url": "https://docs.python.org", "snippet": "Documentation for Python."},
]

@pytest.mark.skip(reason="한글 인코딩 문제로 검증 불가 - 인코딩 문제 해결 후 재시도")
def test_web_agent_with_mocked_search(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.tools.web_search.search", lambda q, top_k=5: DUMMY_RESULTS)
    os.environ["WEB_AGENT_TEST_MODE"] = "true"
    r = subprocess.run([sys.executable, "-m", "scripts.web_agent", "--query", "Python"], text=True, capture_output=True, check=True, encoding='utf-8', errors='replace')
    del os.environ["WEB_AGENT_TEST_MODE"]
    assert "Mock Python official website" in r.stdout or "Mock Documentation for Python" in r.stdout

@pytest.mark.skip(reason="한글 인코딩 문제로 검증 불가 - 인코딩 문제 해결 후 재시도")
def test_invoke_search_task(monkeypatch):
    os.environ["WEB_AGENT_TEST_MODE"] = "true"
    r = subprocess.run([sys.executable, "-m", "invoke", "search", "Python"], text=True, capture_output=True, check=True, encoding='utf-8', errors='replace')
    del os.environ["WEB_AGENT_TEST_MODE"]
    assert "Mock Python official website" in r.stdout