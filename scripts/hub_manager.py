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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        update_hub_file(task_id)
    else:
        print("Usage: python scripts/hub_manager.py <task_id>")