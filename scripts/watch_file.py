"""
Lightweight polling-based watcher for communication directories.
Platform: Windows/Linux, Python 3.x, UTF-8.

Usage:
  venv/Scripts/python.exe scripts/watch_file.py --path communication --interval 1.0
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def snapshot_paths(root: Path) -> dict[str, float]:
    files: dict[str, float] = {}
    if root.is_file():
        try:
            files[str(root)] = root.stat().st_mtime
        except OSError:
            pass
        return files

    for p in root.rglob("*"):
        if p.is_file():
            try:
                files[str(p)] = p.stat().st_mtime
            except OSError:
                continue
    return files


def watch(path: Path, interval: float = 1.0) -> None:
    path = path.resolve()
    if not path.exists():
        print(f"[watch] path not found: {path}")
        sys.exit(1)
    target_desc = "file" if path.is_file() else "dir"
    print(f"[watch] watching {target_desc}: {path} (interval {interval}s)")
    before = snapshot_paths(path)
    try:
        while True:
            time.sleep(interval)
            after = snapshot_paths(path)

            # created
            for f in after.keys() - before.keys():
                print(f"[watch][created] {f}")

            # deleted
            for f in before.keys() - after.keys():
                print(f"[watch][deleted] {f}")

            # modified
            for f in before.keys() & after.keys():
                if after[f] != before[f]:
                    print(f"[watch][modified] {f}")

            before = after
    except KeyboardInterrupt:
        print("[watch] stopped")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="communication", help="root path to watch")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args(argv)

    watch(Path(args.path), args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
