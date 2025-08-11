from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / ".agents"
CONFIG_PATH = CONFIG_DIR / "config.json"

ALLOWED = {"gemini", "codex"}  # 향후: "claude" 등 확장
DEFAULT_AGENT = "gemini"


def _read_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {"active": DEFAULT_AGENT}


def get_active_agent() -> str:
    # 프로세스 우선: 환경변수 ACTIVE_AGENT 가 있으면 전역 설정보다 우선한다.
    env_name = os.getenv("ACTIVE_AGENT")
    if env_name:
        env_name = env_name.strip().lower()
        if env_name in ALLOWED:
            return env_name
    # 전역 설정 파일
    data = _read_config()
    name = str(data.get("active", DEFAULT_AGENT)).lower()
    return name if name in ALLOWED else DEFAULT_AGENT


def set_active_agent(name: str) -> str:
    name = str(name).lower()
    if name not in ALLOWED:
        raise ValueError(f"Unsupported agent: {name}. Allowed: {sorted(ALLOWED)}")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"active": name}, ensure_ascii=False, indent=2), encoding="utf-8")
    return name


def get_flag(key: str, default=None):
    data = _read_config()
    return data.get(key, default)


def set_flag(key: str, value):
    data = _read_config()
    data[key] = value
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return value
