# hub_manager.py (stable fix)
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]  # project root
HUB_PATH = ROOT / "docs" / "HUB.md"

CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F]')

_BLOCK_RE = re.compile(
    r'(?ms)^\s*---\s*\n__lastSession__:\s*.*?(?=^\s*---\s*$|\Z)'
)

def _read_hub() -> str:
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write_hub(text: str) -> None:
    # guarantee trailing newline (yaml parsers, git diffs like it)
    if text and not text.endswith("\n"):
        text += "\n"
    HUB_PATH.write_text(text, encoding="utf-8")

def strip_last_session_block(text: str) -> str:
    """Remove the YAML block starting with '---' then '__lastSession__:'.

    Works regardless of trailing control chars, duplicated timestamps, or missing
    closing '---'. Returns cleaned text (control chars removed, \n normalized).
    """
    cleaned = CONTROL_CHARS.sub('', text.replace('\r\n', '\n').replace('\r', '\n'))
    return _BLOCK_RE.sub('', cleaned).rstrip() + "\n"

def get_changed_files() -> list[str]:
    """Return list of paths changed in the current working tree (since HEAD)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "HEAD"],
            capture_output=True, text=True, check=False, cwd=ROOT
        )
        paths = [p.strip() for p in out.stdout.splitlines() if p.strip()]
        return paths
    except Exception:
        return []

def update_session_end_info(task_id: str = "general") -> None:
    """Append (after removing previous) a __lastSession__ block at file end."""
    hub = _read_hub()
    hub = strip_last_session_block(hub)
    changed = get_changed_files()
    ts = datetime.now(timezone.utc).isoformat()
    block_lines = ["---", "__lastSession__:", f"  task: {task_id}", f"  timestamp: {ts}"]
    if changed:
        block_lines.append("  changed_files:")
        block_lines.extend([f"    - {p}" for p in changed])
    hub = hub.rstrip() + "\n" + "\n".join(block_lines) + "\n"
    _write_hub(hub)

def clear_last_session() -> None:
    hub = _read_hub()
    new = strip_last_session_block(hub)
    _write_hub(new)

def handle_last_session() -> None:
    """Entry used by 'start': if block exists, strip it."""
    hub = _read_hub()
    if "__lastSession__:" in hub:
        clear_last_session()
    # else: nothing

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        handle_last_session()
    elif sys.argv[1] == "clear":
        clear_last_session()
    else:
        update_session_end_info(sys.argv[1])
