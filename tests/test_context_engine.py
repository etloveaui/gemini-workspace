# tests/test_context_engine.py
import pytest
import json
from pathlib import Path
import sys
import datetime
import subprocess

# 스크립트 경로를 sys.path에 추가하여 모듈 임포트 가능하게 함
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from context_store import ContextStore
from summarizer import summarize_text
from prompt_builder import build_prompt_context

# 테스트를 위한 임시 디렉토리 설정
@pytest.fixture
def temp_context_dir(tmp_path):
    # context/index.json 생성
    context_dir = tmp_path / "context"
    context_dir.mkdir()
    index_file = context_dir / "index.json"
    index_data = {
        "updated_at_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "docs": [
            {"path": "docs/HUB.md", "lines": 100, "sha1": "abc", "tags": ["Active Tasks", "Paused Tasks"]},
            {"path": "docs/tasks/gemini-self-upgrade/log.md", "lines": 200, "sha1": "def", "tags": ["System"]},
            {"path": "scripts/context_store.py", "lines": 50, "sha1": "ghi", "tags": ["Script"]},
            {"path": "long_document.md", "lines": 500, "sha1": "jkl", "tags": []}
        ]
    }
    index_file.write_text(json.dumps(index_data))

    # mock_policy.yaml 생성
    gemini_dir = tmp_path / ".gemini"
    gemini_dir.mkdir()
    policy_file = gemini_dir / "context_policy.yaml"
    policy_file.write_text("""
session_start_briefing:
  sources:
    - doc_tag: "Active Tasks"
    - doc_tag: "Paused Tasks"
  max_tokens: 1500

code_refactor:
  sources:
    - changed_files
    - file_extension: ".py"
  max_tokens: 4000
""")

    # 테스트용 문서 내용 생성
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "HUB.md").write_text("This is the HUB.md content with Active Tasks and Paused Tasks.")
    (tmp_path / "docs" / "tasks").mkdir()
    (tmp_path / "docs" / "tasks" / "gemini-self-upgrade").mkdir()
    (tmp_path / "docs" / "tasks" / "gemini-self-upgrade" / "log.md").write_text("This is a system log with some important information.")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "context_store.py").write_text("Python script content.")
    (tmp_path / "long_document.md").write_text("""
This is a very long document. It contains multiple sentences.
Goal: Summarize this document effectively.
Error: An error occurred during processing.
Conclusion: The main point is summarization.
""")

    return tmp_path

# test_retrieval_accuracy
def test_retrieval_accuracy(temp_context_dir, monkeypatch):
    monkeypatch.setattr('context_store.INDEX_PATH', temp_context_dir / "context" / "index.json")
    monkeypatch.setattr('context_store.ROOT', temp_context_dir)
    
    store = ContextStore()
    results = store.retrieve({"doc_tag": "Active Tasks"})
    assert len(results) > 0
    assert any("HUB.md" in doc['path'] for doc in results)
    assert results[0]['path'] == "docs/HUB.md" # HUB.md가 최우선으로 와야 함

# test_summarization
def test_summarization():
    long_text = """
    This is a very long document. It contains multiple sentences.
    Goal: Summarize this document effectively.
    Error: An error occurred during processing.
    Conclusion: The main point is summarization.
    """
    summary = summarize_text(long_text, max_sentences=2)
    assert "Goal: Summarize this document effectively." in summary or "Conclusion: The main point is summarization." in summary
    assert len(summary) < len(long_text) # 요약된 내용이 원본보다 짧아야 함
    assert "..." in summary # 요약되었음을 나타내는 ...이 포함되어야 함

# test_prompt_assembly
def test_prompt_assembly(temp_context_dir, monkeypatch):
    # sys.path에 scripts 디렉토리 추가 (테스트 환경에서 모듈을 찾을 수 있도록)
    import sys
    from pathlib import Path
    import importlib # importlib 추가
    
    scripts_path = str(Path(__file__).parent.parent / "scripts")
    if scripts_path not in sys.path:
        sys.path.append(scripts_path)

    # 모듈을 다시 로드하여 변경된 sys.path를 반영
    import prompt_builder
    import context_store
    importlib.reload(prompt_builder) # 모듈 강제 재로드
    importlib.reload(context_store) # 모듈 강제 재로드

    monkeypatch.setattr(prompt_builder, 'POLICY_PATH', temp_context_dir / ".gemini" / "context_policy.yaml")
    monkeypatch.setattr(prompt_builder, 'ROOT', temp_context_dir)
    monkeypatch.setattr(context_store, 'INDEX_PATH', temp_context_dir / "context" / "index.json")
    monkeypatch.setattr(context_store, 'ROOT', temp_context_dir)

    # build_prompt_context 함수가 직접 파일 내용을 읽도록 mock
    def mock_read_text(file_path, encoding='utf-8', errors='replace'):
        if "HUB.md" in str(file_path):
            return "This is the HUB.md content with Active Tasks and Paused Tasks."
        elif "log.md" in str(file_path):
            return "This is a system log with some important information."
        return ""

    monkeypatch.setattr(Path, 'read_text', mock_read_text)

    # ContextStore 클래스 자체를 mock
    class MockContextStore:
            def retrieve(self, query):
                if query.get("doc_tag") == "Active Tasks":
                    return [{"path": "docs/HUB.md", "content": "This is the HUB.md content with Active Tasks and Paused Tasks."}]
                elif query.get("doc_tag") == "Paused Tasks":
                    return [{"path": "docs/tasks/100xfenok-generator-date-title-input-fix/log.md", "content": "This is a log for a paused task."}]
                return []

    monkeypatch.setattr(prompt_builder, 'ContextStore', MockContextStore)

    prompt_context = prompt_builder.build_prompt_context("session_start_briefing")
    assert "# Context for: session_start_briefing (Assembled by Engine)" in prompt_context
    assert "## Content from: docs/HUB.md" in prompt_context
    assert "Active Tasks and Paused Tasks" in prompt_context
    assert "system log" not in prompt_context # 정책에 따라 포함되지 않아야 함

    # 추가적인 assert 문: final_context_parts에 내용이 제대로 추가되었는지 확인
    assert "## Content from: docs/HUB.md\nThis is the HUB.md content with Active Tasks and Paused Tasks.\n" in prompt_context
    assert "## Content from: docs/tasks/100xfenok-generator-date-title-input-fix/log.md\nThis is a log for a paused task.\n" in prompt_context
