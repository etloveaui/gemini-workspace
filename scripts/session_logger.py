from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

if os.name == "nt":  # pragma: no cover - tested via interface
    import msvcrt
    _LOCK_SIZE = 0x7FFFFFFF

    def _lock_file(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, _LOCK_SIZE)

    def _unlock_file(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, _LOCK_SIZE)
else:  # POSIX
    import fcntl

    def _lock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

    def _unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = ROOT / "docs" / "sessions"


def append_session_tldr(summary: str, *, when: datetime | None = None, root: Path | None = None) -> Path:
    """Append a session TL;DR to the daily markdown file.

    Parameters
    ----------
    summary: str
        Three-line summary text.
    when: datetime | None
        Timestamp for the entry; defaults to ``datetime.now()``.
    root: Path | None
        Repository root; mainly for testing.
    Returns
    -------
    Path
        Path to the file written.
    """

    when = when or datetime.now()
    root = Path(root) if root is not None else ROOT
    day_file = root / "docs" / "sessions" / f"{when:%Y-%m-%d}.md"
    day_file.parent.mkdir(parents=True, exist_ok=True)
    entry = f"### {when:%H:%M:%S}\n{summary.rstrip()}\n\n"
    with open(day_file, "a", encoding="utf-8") as f:
        _lock_file(f)
        try:
            f.write(entry)
            f.flush()
        finally:
            _unlock_file(f)
    return day_file
