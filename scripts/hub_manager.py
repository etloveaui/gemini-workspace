# scripts/hub_manager.py
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import os
import time

ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "docs" / "HUB.md"

def _read() -> str:
    return HUB_PATH.read_text(encoding="utf-8", errors="replace")

def _write_atomic(text: str) -> None:
    if text and not text.endswith('\n'):
        text += '\n'
    tmp_path = HUB_PATH.with_suffix(".tmp")

    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_path, HUB_PATH)  # atomic
    time.sleep(0.05)  # 보수적 대기 (윈도우/AV 캐시 대비)

CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F]')  # ,  제외


def strip_last_session_block(text: str) -> str:
    """
    __lastSession__ YAML 블록(위의 --- 포함) 제거.
    라인 스캔 + 정규식 하이브리드로 안전 제거.
    """
    cleaned = CONTROL_CHARS.sub('', text)
    lines = cleaned.splitlines()

    start_idx = -1
    # 뒤에서부터 __lastSession__ 라인 탐색
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith('__lastSession__'):
            # 위쪽에서 가장 가까운 '---' 찾기
            for j in range(i - 1, -1, -1):
                if lines[j].strip() == '---':
                    start_idx = j
                    break
            break

    if start_idx == -1:
        return text  # 블록 없음

    new_lines = lines[:start_idx]
    result = '\n'.join(new_lines).rstrip()
    return (result + '\n') if result else ''

# --- Public API ------------------------------------------------------------

def parse_tasks(content: str, section_title: str) -> list[str]:
    """지정된 섹션 아래의 작업 목록을 파싱합니다."""
    try:
        # 섹션 제목과 그 다음 섹션 제목 사이의 내용을 추출
        pattern = re.compile(rf"## {re.escape(section_title)}\n(.*?)\n## ", re.DOTALL)
        match = pattern.search(content)
        if not match:
            # 파일 끝까지의 내용을 처리하기 위한 대체 패턴
            pattern = re.compile(rf"## {re.escape(section_title)}\n(.*?)$", re.DOTALL)
            match = pattern.search(content)

        if match:
            section_content = match.group(1)
            # "- "로 시작하는 라인 아이템을 추출
            tasks = re.findall(r"^\s*-\s*(.+?)\s*$", section_content, re.MULTILINE)
            return [task.strip() for task in tasks]
        return []
    except Exception:
        return []

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
    _write_atomic(hub)

def clear_last_session() -> None:
    _write_atomic(strip_last_session_block(_read()))

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
