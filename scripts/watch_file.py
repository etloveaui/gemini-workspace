#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lightweight file change watcher (polling, stdlib-only).

Usage (Windows, venv recommended):
  venv\\Scripts\\python.exe scripts\\watch_file.py <path> [--recursive] [--interval 1.0]
                                            [--include *.py --exclude *.log]
                                            [--log-file logs\\watch_file.log]

Notes:
  - Uses polling (no external deps). Checks mtime/size; hashes only on mtime change.
  - Treats renames as delete+create events.
  - UTF-8 I/O, Windows paths supported.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
from pathlib import Path
import sys
import time
from typing import Dict, Iterable, List, Optional, Tuple


Event = Tuple[str, Path]


def sha256_of_file(path: Path) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:  # type: ignore[call-arg]
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def list_files(base: Path, recursive: bool) -> List[Path]:
    if base.is_file():
        return [base]
    files: List[Path] = []
    if recursive:
        for root, _, filenames in os.walk(base):
            root_p = Path(root)
            for name in filenames:
                files.append(root_p / name)
    else:
        for p in base.iterdir():
            if p.is_file():
                files.append(p)
    return files


def apply_patterns(paths: Iterable[Path], includes: List[str], excludes: List[str]) -> List[Path]:
    def match_any(name: str, patterns: List[str]) -> bool:
        return any(fnmatch.fnmatch(name, pat) for pat in patterns)

    result: List[Path] = []
    for p in paths:
        name = p.name
        if includes and not match_any(name, includes):
            continue
        if excludes and match_any(name, excludes):
            continue
        result.append(p)
    return result


class FileSnapshot:
    __slots__ = ("size", "mtime", "hash")

    def __init__(self, size: int, mtime: float, content_hash: Optional[str]):
        self.size = size
        self.mtime = mtime
        self.hash = content_hash


def take_snapshot(paths: Iterable[Path]) -> Dict[Path, FileSnapshot]:
    snap: Dict[Path, FileSnapshot] = {}
    for p in paths:
        try:
            st = p.stat()
        except (FileNotFoundError, PermissionError, OSError):
            continue
        # Hash lazily only when needed; first snapshot includes hash to allow accurate diffs.
        h = sha256_of_file(p)
        snap[p] = FileSnapshot(size=st.st_size, mtime=st.st_mtime, content_hash=h)
    return snap


def diff_snapshots(old: Dict[Path, FileSnapshot], new: Dict[Path, FileSnapshot]) -> List[Event]:
    events: List[Event] = []
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    for p in sorted(new_keys - old_keys):
        events.append(("CREATED", p))
    for p in sorted(old_keys - new_keys):
        events.append(("DELETED", p))

    for p in sorted(new_keys & old_keys):
        o = old[p]
        n = new[p]
        # Compare by size/mtime first, then hash to confirm actual content change.
        if o.size != n.size or o.mtime != n.mtime:
            # If we don't have a content hash yet in 'new', compute now.
            if n.hash is None:
                n.hash = sha256_of_file(p)
            if o.hash != n.hash:
                events.append(("MODIFIED", p))
    return events


def ensure_log_dir(log_file: Optional[Path]) -> None:
    if log_file is None:
        return
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def log(line: str, log_file: Optional[Path]) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    out = f"[{ts}] {line}"
    print(out, flush=True)
    if log_file is not None:
        try:
            with log_file.open("a", encoding="utf-8") as f:
                f.write(out + os.linesep)
        except Exception:
            # Best-effort logging; ignore failures.
            pass


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll-based file change watcher (stdlib-only)")
    parser.add_argument("path", help="Target file or directory to watch")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subdirectories when path is a directory")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds (default: 1.0)")
    parser.add_argument("--include", action="append", default=[], help="Include glob (can repeat), e.g., --include *.py")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude glob (can repeat), e.g., --exclude *.log")
    parser.add_argument("--log-file", default=str(Path("logs") / "watch_file.log"), help="Log file path (default: logs/watch_file.log). Use '-' to disable file logging")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    target = Path(args.path).expanduser().resolve()
    if not target.exists():
        print(f"Error: path not found: {target}", file=sys.stderr)
        return 2

    includes: List[str] = list(args.include)
    excludes: List[str] = list(args.exclude)

    log_path: Optional[Path]
    if args.log_file == "-":
        log_path = None
    else:
        log_path = Path(args.log_file).expanduser().resolve()
        ensure_log_dir(log_path)

    log(f"Watching: {target} (recursive={args.recursive}, interval={args.interval}s)", log_path)
    if includes:
        log(f"Includes: {includes}", log_path)
    if excludes:
        log(f"Excludes: {excludes}", log_path)

    # Initial scan
    current_files = apply_patterns(list_files(target, args.recursive), includes, excludes)
    snapshot = take_snapshot(current_files)
    log(f"Initial files: {len(snapshot)}", log_path)

    try:
        while True:
            time.sleep(max(0.05, float(args.interval)))
            try:
                files_now = apply_patterns(list_files(target, args.recursive), includes, excludes)
            except Exception as e:
                log(f"Scan error: {e}", log_path)
                continue

            new_snapshot = take_snapshot(files_now)
            events = diff_snapshots(snapshot, new_snapshot)
            for kind, path in events:
                log(f"{kind}: {path}", log_path)
            snapshot = new_snapshot
    except KeyboardInterrupt:
        log("Stopped by user (Ctrl+C)", log_path)
        return 0


if __name__ == "__main__":
    sys.exit(main())

