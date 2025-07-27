# scripts/hub_manager.py
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import os
import time

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1F]")
_BLOCK_RE = re.compile(r"(?ms)^[ \t]*---[ \t]*\n__lastSession__:[ \t]*.*?(?=^[ \t]*---[ \t]*$|\Z)")

# --- Low-level I/O helpers -------------------------------------------------

def _read() -> str:
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write(text: str) -> None:
    # LF 고정 + 파일 끝 개행 보장 + flush + fsync + 짧은 sleep
    if text and not text.endswith("\n"):
        text += "\n"
    with open(HUB_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    time.sleep(0.05)

# --- High-level transformers ----------------------------------------------

def _normalize(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return _CONTROL_CHARS.sub("", s)

def strip_last_session_block(text: str) -> str:
    t = _normalize(text)
    t = _BLOCK_RE.sub("", t)
    return t.rstrip() + "\n"

# --- Public API ------------------------------------------------------------

def get_changed_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "HEAD"],
            capture_output=True, text=True, check=False, cwd=ROOT
        )
        return [p.strip() for p in out.stdout.splitlines() if p.strip()]
    except Exception:
        return []

def update_session_end_info(task_id: str = "general") -> None:
    hub = strip_last_session_block(_read())
    changed = get_changed_files()
    ts = datetime.now(timezone.utc).isoformat()

    lines = [
        "---",
        "__lastSession__:",
        f"  task: {task_id}",
        f"  timestamp: {ts}",
    ]
    if changed:
        lines.append("  changed_files:")
        lines.extend([f"    - {p}" for p in changed])

    hub = hub.rstrip() + "\n" + "\n".join(lines) + "\n"
    _write(hub)

def clear_last_session() -> None:
    _write(strip_last_session_block(_read()))

def handle_last_session() -> None:
    if "__lastSession__:" in _read():
        clear_last_session()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        handle_last_session()
    elif sys.argv[1] == "clear":
        clear_last_session()
    else:
        update_session_end_info(sys.argv[1])
