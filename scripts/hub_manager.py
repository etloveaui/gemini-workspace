from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

def _read():
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

import os

def _write(text: str):
    if text and not text.endswith(os.linesep):
        text += os.linesep
    HUB_PATH.write_text(text, encoding="utf-8", newline='')

def strip_last_session_block(text: str) -> str:
    lines = text.replace('\r\n','\n').replace('\r','\n').split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == '---' and i + 1 < len(lines) and lines[i+1].strip().startswith('__lastSession__:'):
            i += 2
            while i < len(lines):
                if lines[i].strip() == '---':
                    i += 1
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"

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
    block = ["---", "__lastSession__:", f"  task: {task_id}", f"  timestamp: {ts}"]
    if changed:
        block.append("  changed_files:")
        block.extend([f"    - {p}" for p in changed])
    hub = hub.rstrip() + "\n" + "\n".join(block) + "\n"
    _write(hub)

def clear_last_session() -> None:
    _write(strip_last_session_block(_read()))

def handle_last_session() -> None:
    txt = _read()
    if "__lastSession__:" in txt:
        clear_last_session()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        handle_last_session()
    elif sys.argv[1] == "clear":
        clear_last_session()
    else:
        update_session_end_info(sys.argv[1])