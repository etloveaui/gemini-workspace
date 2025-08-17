import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import ai, agent_manager


def patch_config(monkeypatch, tmp_path):
    config_dir = tmp_path
    config_path = config_dir / "config.json"
    monkeypatch.setattr(agent_manager, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(agent_manager, "CONFIG_PATH", config_path)
    return config_path


def test_interactive_updates_provider(monkeypatch, tmp_path):
    config_path = patch_config(monkeypatch, tmp_path)

    inputs = iter(["/p gemini", "/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    ai.interactive("claude")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data["provider"] == "gemini"


def test_main_reads_provider(monkeypatch, tmp_path):
    config_path = patch_config(monkeypatch, tmp_path)
    config_path.write_text(json.dumps({"provider": "gemini"}), encoding="utf-8")

    captured = {}

    def fake_interactive(provider):
        captured["provider"] = provider
        return []

    monkeypatch.setattr(ai, "interactive", fake_interactive)
    monkeypatch.setattr(sys, "argv", ["ai"])

    ai.main()

    assert captured["provider"] == "gemini"
