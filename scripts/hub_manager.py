# /scripts/hub_manager.py
import sys
import datetime
import subprocess
import re
from pathlib import Path

HUB_PATH = Path("docs/HUB.md")

def get_changed_files_from_last_commit():
    """Returns a list of changed files from the last commit."""
    try:
        cmd = ["git", "diff", "HEAD~1", "--name-only"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ["N/A - Could not determine changed files."]

def update_last_session(task_id="general"):
    """Atomically reads HUB.md, removes the old session block, and appends a new one."""
    if not HUB_PATH.exists():
        print(f"Error: HUB file not found at {HUB_PATH}")
        return

    # 1. Read content with guaranteed UTF-8 encoding
    hub_content = HUB_PATH.read_text(encoding="utf-8")

    # 2. Reliably remove the old block using a regular expression
    pattern = re.compile(r"^\s*---\s*\n__lastSession__:.*$", re.MULTILINE | re.DOTALL)
    content_without_session = pattern.sub("", hub_content).rstrip()

    # 3. Create the new session block safely
    timestamp = datetime.datetime.now().isoformat(timespec='seconds') + '+09:00'
    changed_files = get_changed_files_from_last_commit()
    
    # Safely build the YAML string for changed files
    changed_files_yaml = "\n".join([f"    - {f}" for f in changed_files])

    last_session_block = (
        f"\n\n---\n"
        f"__lastSession__:\n"
        f"  active_task_id: {task_id}\n"
        f"  changed_files:\n"
        f"{changed_files_yaml}\n"
        f"  timestamp: {timestamp}\n"
    )

    # 4. Write the new content back with guaranteed UTF-8 encoding
    final_content = content_without_session + last_session_block
    HUB_PATH.write_text(final_content, encoding="utf-8")
    print(f"Successfully updated __lastSession__ in {HUB_PATH}")

if __name__ == "__main__":
    task_id_arg = sys.argv[1] if len(sys.argv) > 1 else "general"
    update_last_session(task_id_arg)
