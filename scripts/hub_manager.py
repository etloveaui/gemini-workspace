import datetime
import re
from pathlib import Path
import subprocess
import os

ROOT = Path(__file__).resolve().parent.parent

def get_changed_files():
    """Runs 'git status --porcelain' to get a list of changed files."""
    try:
        # Ensure we are in the project root for the git command
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
            encoding='utf-8'
        )
        # The output needs to be split by newline characters
        return [line.strip().split(" ", 1)[1] for line in result.stdout.strip().splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Could not get changed files: {e}")
        return []

def update_session_end_info(task_id: str):
    """Updates HUB.md with a __lastSession__ block containing changed files."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        print(f"Error: HUB.md not found at {hub_path}")
        return

    content = hub_path.read_text(encoding="utf-8")
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    changed_files = get_changed_files()

    # First, robustly clear any existing __lastSession__ block and its separator
    content = re.sub(r"\n---\n__lastSession__:\n.*?\n(?=^---\n|\Z)", "\n", content, flags=re.DOTALL | re.MULTILINE).strip()

    # Create the YAML-formatted string for the changed files
    changed_files_yaml = "\n".join([f"    - {f}" for f in changed_files]) if changed_files else "    (No uncommitted changes)"

    # Create the new __lastSession__ block
    last_session_block = f"""
---
__lastSession__:
  active_task_id: {task_id}
  changed_files:
{changed_files_yaml}
  timestamp: {now_utc.isoformat()}
"""

    # Append the new block to the content
    hub_path.write_text(f"{content}{last_session_block}\n", encoding="utf-8")
    print(f"Updated HUB.md with session state for task: {task_id}")

def clear_last_session():
    """Removes the __lastSession__ block and its separator from HUB.md."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        return

    content = hub_path.read_text(encoding="utf-8")
    # This regex finds the --- separator and everything after it
    content = re.sub(r"\n---\n__lastSession__:\n.*?\n(?=^---\n|\Z)", "\n", content, flags=re.DOTALL | re.MULTILINE).strip()
    hub_path.write_text(content + "\n", encoding="utf-8")
    print("Previous session state has been cleared from HUB.md.")

def handle_last_session():
    """Checks for a __lastSession__ block, briefs the user, and then clears it."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        return

    content = hub_path.read_text(encoding="utf-8")
    session_match = re.search(r"__lastSession__:(.*)", content, re.DOTALL)
    
    if session_match:
        session_block = session_match.group(1).strip()
        
        task_id_match = re.search(r"active_task_id:\s*(.*)", session_block)
        timestamp_match = re.search(r"timestamp:\s*(.*)", session_block)
        files_match = re.search(r"changed_files:\n(.*)", session_block, re.DOTALL)

        task_id = task_id_match.group(1).strip() if task_id_match else "N/A"
        timestamp = timestamp_match.group(1).strip() if timestamp_match else "N/A"
        
        print("\n[Resuming Session] Previous session state found:")
        print(f"  - Active Task: {task_id}")
        print(f"  - Last Modified: {timestamp}")

        if files_match:
            files_list = files_match.group(1).strip()
            if "(No uncommitted changes)" not in files_list:
                print("  - Uncommitted Changes:")
                # Indent the files for better display
                for f in files_list.split('\n'):
                    print(f"    {f.strip()}")
        
        clear_last_session()
    else:
        print("No previous session state found. Starting a clean session.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "handle_session":
            handle_last_session()
        elif command == "update_session":
            if len(sys.argv) > 2:
                task_id = sys.argv[2]
                update_session_end_info(task_id)
            else:
                print("Usage: python scripts/hub_manager.py update_session <task_id>")
        else:
            print(f"Unknown command: {command}. Use 'handle_session' or 'update_session'.")
    else:
        print("Usage: python scripts/hub_manager.py <command> [args]")
