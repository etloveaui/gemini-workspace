from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.agents import messages


def test_append_decision(tmp_path, monkeypatch):
    inbox_dir = tmp_path / ".agents" / "inbox"
    monkeypatch.setattr(messages, "CONTEXT_DIR", tmp_path)
    monkeypatch.setattr(messages, "INBOX_DIR", inbox_dir)
    msg_path = tmp_path / "messages.jsonl"
    monkeypatch.setattr(messages, "MESSAGES_PATH", msg_path)

    msg = messages.append_decision("upgrade kernel", sender="codex")

    assert msg_path.exists()
    data = [json.loads(line) for line in msg_path.read_text(encoding="utf-8").splitlines()]
    assert data[-1]["body"] == "upgrade kernel"
    assert data[-1]["from"] == "codex"
    assert data[-1]["to"] == "all"
    assert "decision" in data[-1]["tags"]
    assert "critical" in data[-1]["tags"]
    assert "ts" in data[-1]
    assert msg.body == "upgrade kernel"
