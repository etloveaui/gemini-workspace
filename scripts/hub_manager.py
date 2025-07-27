import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1F]")
_BLOCK_RE = re.compile(r"(?ms)^---\s*__lastSession__:\s*.*?(?=^---\s*$|\Z)")

def _read():
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write(text: str):
    if text and not text.endswith("\n"):
        text += "\n"
    HUB_PATH.write_text(text, encoding="utf-8")

def strip_last_session_block(text: str) -> str:
    cleaned = CONTROL_CHARS.sub('', text.replace('
', '
').replace('', '
'))
    print(f"Cleaned text before regex: {cleaned[-500:]}") # 디버그 출력 추가
    result = _BLOCK_RE.sub('', cleaned)
    print(f"Text after regex substitution: {result[-500:]}") # 디버그 출력 추가
    return result.rstrip() + "\n"

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
