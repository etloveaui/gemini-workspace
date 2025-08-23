#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spawner to run watch_file.py as a detached background process.

This avoids holding the current session while keeping the watcher alive.
"""

from __future__ import annotations

import os
import sys
import subprocess
from shutil import which


def python_executable() -> str:
    # Prefer current interpreter to ensure venv consistency
    return sys.executable or "python"


def main(argv: list[str]) -> int:
    if not os.path.isfile(os.path.join("scripts", "watch_file.py")):
        print("watch_file.py not found in scripts/", file=sys.stderr)
        return 2

    # Default args if none provided
    args = argv[1:] if len(argv) > 1 else [
        "--path", "communication",
        "--recursive",
        "--interval", "1.0",
        "--logfile", os.path.join("communication", "logs", "codex_watcher.log"),
        "--pidfile", os.path.join("communication", "logs", "codex_watcher.pid"),
    ]

    py = python_executable()
    cmd = [py, os.path.join("scripts", "watch_file.py"), *args]

    # Detach cross-platform
    kwargs: dict = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
        "cwd": os.getcwd(),
    }

    if os.name == "nt":
        # Windows detach
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        kwargs["creationflags"] = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    else:
        # POSIX detach
        kwargs["preexec_fn"] = os.setsid  # type: ignore[arg-type]

    proc = subprocess.Popen(cmd, **kwargs)  # noqa: S603
    print("WATCHER_STARTED", proc.pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

