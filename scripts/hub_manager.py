import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def get_active_task_id_from_hub():
    """HUB.md 파일에서 활성 태스크 ID를 읽어옵니다."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        return None

    content = hub_path.read_text(encoding="utf-8")
    match = re.search(r"- \[xX]\]\s+`([^`]+)`", content)
    if match:
        return match.group(1)
    return None

def update_hub_file(task_id: str):
    """HUB.md 파일의 태스크를 완료 처리하고, __lastSession__ 블록을 업데이트합니다."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        print(f"Error: {hub_path} not found.")
        return

    content = hub_path.read_text(encoding="utf-8")
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # __lastSession__ 블록 업데이트 또는 추가
    last_session_block = f"""__lastSession__:
  task: {task_id}
  timestamp: {now_utc.isoformat()}"""

    if "__lastSession__:" in content:
        content = re.sub(r"__lastSession__:.*?(\n|$)", f"{last_session_block}\1", content, flags=re.DOTALL)
    else:
        content = f"{content.rstrip()}\n\n{last_session_block}"

    hub_path.write_text(content, encoding="utf-8")
    print(f"Updated HUB.md for task {task_id}")

def clear_last_session():
    """HUB.md 파일에서 __lastSession__ 블록을 제거합니다."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        print(f"Error: {hub_path} not found.")
        return

    content = hub_path.read_text(encoding="utf-8")
    content = re.sub(r"\n---\n__lastSession__:.*?(\n|$)", "\n", content, flags=re.DOTALL)
    hub_path.write_text(content.strip() + "\n", encoding="utf-8")
    print("Cleared __lastSession__ block from HUB.md")

def handle_last_session():
    """HUB.md 파일에서 __lastSession__ 블록을 확인하고 사용자에게 복구 여부를 묻습니다."""
    hub_path = ROOT / "docs" / "HUB.md"
    if not hub_path.exists():
        print(f"Error: {hub_path} not found.")
        return

    content = hub_path.read_text(encoding="utf-8")
    match = re.search(r"__lastSession__:\n(?:  active_task_id: (.*)\n)?(?:  changed_files:\n((?:(?:    - .*\n)*)))?  timestamp: (.*)\n", content)
    
    if match:
        active_task_id = match.group(1) if match.group(1) else "N/A"
        changed_files_str = match.group(2) if match.group(2) else "N/A"
        timestamp = match.group(3) if match.group(3) else "N/A"

        print(f"\n__lastSession__ block found in HUB.md:\n")
        print(f"  Active Task ID: {active_task_id}")
        print(f"  Changed Files:\n{changed_files_str}")
        print(f"  Timestamp: {timestamp}")
        print("\nShould I restore this session (e.g., by checking out the relevant branch/commit) or clear it? (restore/clear)")
        # Note: In a real CLI, you would prompt the user for input here.
        # For now, we'll assume 'clear' for automated execution.
        clear_last_session()
    else:
        print("No __lastSession__ block found in HUB.md.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "clear_session":
            clear_last_session()
        elif command == "handle_session":
            handle_last_session()
        else:
            task_id = command
            update_hub_file(task_id)
    else:
        print("Usage: python scripts/hub_manager.py <task_id> | clear_session | handle_session")