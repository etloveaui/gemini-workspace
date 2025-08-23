#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lightweight file watcher for the communication workspace.

- Polling-based (stdlib only), no external deps
- Detects created / modified / deleted files
- Recursive directory scan optional

Usage example:
  python scripts/watch_file.py --path communication --recursive --interval 1.0 \
         --logfile communication/logs/codex_watcher.log --pidfile communication/logs/codex_watcher.pid
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class FileInfo:
    size: int
    mtime_ns: int


def _normalize_patterns(raw: Optional[str]) -> List[str]:
    if not raw:
        return ["*"]
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def _should_include(path: str, includes: List[str], excludes: List[str]) -> bool:
    base = os.path.basename(path)
    # Exclude takes precedence
    for pat in excludes:
        if fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(path, pat):
            return False
    for pat in includes:
        if fnmatch.fnmatch(base, pat) or fnmatch.fnmatch(path, pat):
            return True
    return False


def snapshot(root: str, recursive: bool, includes: List[str], excludes: List[str]) -> Dict[str, FileInfo]:
    result: Dict[str, FileInfo] = {}
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        return result

    def add_file(fpath: str) -> None:
        if not _should_include(fpath, includes, excludes):
            return
        try:
            st = os.stat(fpath)
            if not os.path.isfile(fpath):
                return
            result[fpath] = FileInfo(size=st.st_size, mtime_ns=int(st.st_mtime_ns))
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    if recursive:
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip excluded directories by name
            dirnames[:] = [d for d in dirnames if _should_include(os.path.join(dirpath, d), ["*"], excludes) or d == ""]
            for name in filenames:
                add_file(os.path.join(dirpath, name))
    else:
        try:
            for name in os.listdir(root):
                fpath = os.path.join(root, name)
                if os.path.isfile(fpath):
                    add_file(fpath)
        except FileNotFoundError:
            pass

    return result


def fmt_ts(ts: Optional[float] = None) -> str:
    return datetime.utcfromtimestamp(ts or time.time()).strftime("%Y-%m-%d %H:%M:%S")


def log(line: str, logfile: Optional[str]) -> None:
    msg = f"[{fmt_ts()}] {line}"
    try:
        print(msg, flush=True)
    except Exception:
        # Best-effort stdout
        pass
    if logfile:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(logfile)), exist_ok=True)
            with open(logfile, "a", encoding="utf-8", errors="replace") as f:
                f.write(msg + "\n")
        except Exception:
            # Avoid crashing on logging errors
            pass


def write_pid(pidfile: Optional[str]) -> None:
    if not pidfile:
        return
    try:
        os.makedirs(os.path.dirname(os.path.abspath(pidfile)), exist_ok=True)
        with open(pidfile, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass


def diff_events(prev: Dict[str, FileInfo], curr: Dict[str, FileInfo]) -> List[Tuple[str, str]]:
    events: List[Tuple[str, str]] = []
    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())

    created = curr_keys - prev_keys
    deleted = prev_keys - curr_keys
    common = prev_keys & curr_keys

    for p in sorted(created):
        events.append(("CREATED", p))
    for p in sorted(deleted):
        events.append(("DELETED", p))
    for p in sorted(common):
        if prev[p] != curr[p]:
            events.append(("MODIFIED", p))
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Polling-based file watcher (stdlib)")
    parser.add_argument("--path", default="communication", help="Root directory to watch (default: communication)")
    parser.add_argument("--recursive", action="store_true", help="Watch directories recursively")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds (default: 1.0)")
    parser.add_argument("--include", default="*", help="Comma-separated glob patterns to include (default: *)")
    parser.add_argument("--exclude", default=".git,*.tmp,*.swp,~*", help="Comma-separated glob patterns to exclude")
    parser.add_argument("--logfile", default=None, help="Optional logfile path to append events")
    parser.add_argument("--pidfile", default=None, help="Optional pidfile path to write PID")

    args = parser.parse_args()

    watch_root = os.path.abspath(args.path)
    includes = _normalize_patterns(args.include)
    excludes = _normalize_patterns(args.exclude)

    if not os.path.isdir(watch_root):
        log(f"WATCH_START: root not found: {watch_root}", args.logfile)
        return 2

    write_pid(args.pidfile)
    log(f"WATCH_START: root={watch_root} recursive={args.recursive} interval={args.interval}", args.logfile)

    prev = snapshot(watch_root, args.recursive, includes, excludes)
    try:
        while True:
            time.sleep(max(0.05, args.interval))
            curr = snapshot(watch_root, args.recursive, includes, excludes)
            for evt, path in diff_events(prev, curr):
                rel = os.path.relpath(path, watch_root)
                log(f"{evt}: {rel}", args.logfile)
            prev = curr
    except KeyboardInterrupt:
        log("WATCH_STOP: KeyboardInterrupt", args.logfile)
        return 0
    except Exception as e:
        log(f"WATCH_ERROR: {e.__class__.__name__}: {e}", args.logfile)
        return 1


if __name__ == "__main__":
    sys.exit(main())

