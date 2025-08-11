from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def ensure_inside_repo(path: Path, repo_root: Optional[Path] = None) -> Path:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    p = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if not str(p).startswith(str(root)):
        raise ValueError("Path must be inside repo root")
    return p


def exists(path: str | Path) -> bool:
    return Path(path).exists()


def make_dirs(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def move(src: str | Path, dst: str | Path) -> None:
    src_p = Path(src)
    dst_p = Path(dst)
    make_dirs(dst_p.parent)
    shutil.move(str(src_p), str(dst_p))


def copy(src: str | Path, dst: str | Path) -> None:
    src_p = Path(src)
    dst_p = Path(dst)
    make_dirs(dst_p.parent)
    if src_p.is_dir():
        if dst_p.exists():
            shutil.rmtree(dst_p)
        shutil.copytree(src_p, dst_p)
    else:
        shutil.copy2(src_p, dst_p)


def remove_file(path: str | Path, missing_ok: bool = True) -> None:
    p = Path(path)
    try:
        p.unlink()
    except FileNotFoundError:
        if not missing_ok:
            raise


def remove_dir(path: str | Path, missing_ok: bool = True) -> None:
    p = Path(path)
    try:
        shutil.rmtree(p)
    except FileNotFoundError:
        if not missing_ok:
            raise


def which(cmd: str) -> Optional[str]:
    path = shutil.which(cmd)
    return path


def run(cmd: list[str], cwd: Optional[str | Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    # Run a command without relying on OS-specific shell builtins
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check)

