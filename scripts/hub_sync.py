import json
import re
from datetime import datetime, timezone
from pathlib import Path
import hub_manager

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = get_workspace_path("docs", "CORE", "HUB_ENHANCED.md")
QUEUE_DIR = ROOT / "agents_hub" / "queue"
PROCESSING_DIR = ROOT / "agents_hub" / "processing"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug or "task"


def _parse_section(content: str, title: str) -> list[str]:
    pattern = re.compile(rf"^## {re.escape(title)}\n", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return []
    start = match.end()
    lines = []
    for line in content[start:].splitlines():
        if line.startswith('## '):
            break
        if line.strip().startswith('- '):
            lines.append(line.strip()[2:].strip())
    return lines


def _update_section(content: str, title: str, tasks: list[str]) -> str:
    pattern = re.compile(rf"(## {re.escape(title)}\n)(.*?)(\n## |\Z)", re.DOTALL)
    block = ''.join(f"- {t}\n" for t in tasks)
    def repl(match):
        return f"{match.group(1)}{block}{match.group(3)}"
    if pattern.search(content):
        return pattern.sub(repl, content, count=1)
    return content.rstrip() + f"\n## {title}\n{block}\n"


def _queue_titles() -> list[str]:
    titles = []
    for f in QUEUE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            title = data.get("title")
            if title:
                titles.append(title)
        except Exception:
            pass
    return titles


def _processing_titles() -> list[str]:
    titles = []
    for f in PROCESSING_DIR.glob("*/*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            title = data.get("title")
            if title:
                titles.append(title)
        except Exception:
            pass
    return titles


def _ensure_queue_file(title: str) -> None:
    slug = _slugify(title)
    path = QUEUE_DIR / f"{slug}.json"
    if path.exists():
        return
    data = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent": "codex",
        "title": title,
        "tasks": [],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ensure_processing_file(title: str) -> None:
    slug = _slugify(title)
    agent_dir = PROCESSING_DIR / "codex"
    agent_dir.mkdir(parents=True, exist_ok=True)
    path = agent_dir / f"{slug}.json"
    if path.exists():
        return
    ts = datetime.now(timezone.utc).isoformat()
    data = {
        "id": slug,
        "from": "codex",
        "to": "codex",
        "type": "task",
        "title": title,
        "created_at": ts,
        "status": "processing",
        "claimed_at": ts,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sync() -> None:
    content = HUB_PATH.read_text(encoding="utf-8")
    staging_tasks = _parse_section(content, "Staging Tasks")
    active_tasks = _parse_section(content, "Active Tasks")

    queue_titles = _queue_titles()
    processing_titles = _processing_titles()

    changed = False

    for t in queue_titles:
        if t not in staging_tasks:
            staging_tasks.append(t)
            changed = True
    for t in staging_tasks:
        if t not in queue_titles:
            _ensure_queue_file(t)
            changed = True

    for t in processing_titles:
        if t not in active_tasks:
            active_tasks.append(t)
            changed = True
    for t in active_tasks:
        if t not in processing_titles:
            _ensure_processing_file(t)
            changed = True

    if changed:
        today = datetime.now().strftime("%Y-%m-%d")
        content = _update_section(content, "Staging Tasks", staging_tasks)
        content = _update_section(content, "Active Tasks", active_tasks)
        content = re.sub(r"\*Last Updated: .*", f"*Last Updated: {today}", content)
        hub_manager._write_atomic(content)

    summary = {"staging": staging_tasks, "active": active_tasks}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sync()
