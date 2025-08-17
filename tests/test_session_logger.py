from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import multiprocessing as mp
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.session_logger import append_session_tldr


def _worker(root: Path, text: str, when: datetime) -> None:
    append_session_tldr(text, when=when, root=root)


def test_concurrent_appends(tmp_path: Path) -> None:
    when = datetime(2025, 1, 1, 10, 0, 0)
    args = [
        (tmp_path, "1\n2\n3", when),
        (tmp_path, "4\n5\n6", when + timedelta(minutes=1)),
    ]
    with mp.Pool(2) as pool:
        pool.starmap(_worker, args)
    day_file = tmp_path / "docs" / "sessions" / "2025-01-01.md"
    content = day_file.read_text(encoding="utf-8")
    assert "1\n2\n3" in content
    assert "4\n5\n6" in content
