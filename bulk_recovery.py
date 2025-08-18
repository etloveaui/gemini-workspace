#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk encoding recovery script.
Finds entries in damaged_files_list.txt and restores their clean versions
from known-good commits, avoiding shell redirection issues and preserving bytes.
"""

import subprocess
import sys
import os
from pathlib import Path

BROKEN_PATTERNS = [
    "?쒖뒪?쒖뿉", "硫붿씤 泥댁젣", "筌ㅼ뮇", "獄?", "揶쏆뮇", "餓?",
    "?뀒?뒪?듃", "?쒗븘?듃", "CUserseuntamulti-agent-workspace",
]

# Candidate commits from the recovery playbook (most recent to older)
COMMIT_CANDIDATES = [
    "26bb83d",
    "95dd94b",
    "69400fa",
    "6fa2776",
]

def run_git_show(commit: str, path: str):
    """Return (bytes, ok) of file contents at commit:path."""
    try:
        proc = subprocess.run(
            ["git", "show", f"{commit}:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            return b"", False
        return proc.stdout, True
    except Exception:
        return b"", False

def looks_broken(data: bytes) -> bool:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        # If it isn't valid UTF-8, treat as broken for this recovery task
        return True
    return any(pat in text for pat in BROKEN_PATTERNS)

def restore_file_from_commits(path: str) -> tuple[bool, str|None]:
    for commit in COMMIT_CANDIDATES:
        data, ok = run_git_show(commit, path)
        if not ok:
            continue
        if looks_broken(data):
            continue
        # Write bytes as-is to preserve encoding/content
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        return True, commit
    return False, None

def main() -> int:
    lst = Path("damaged_files_list.txt")
    if not lst.exists():
        print("❌ damaged_files_list.txt not found. Run the scanner first.")
        return 1

    targets = [line.strip() for line in lst.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Targets: {len(targets)} files")

    success = 0
    failed: list[str] = []
    for rel in targets:
        # Normalize to repo-relative forward slashes
        rel = rel.replace("\\", "/")
        print(f"Restoring: {rel}")
        ok, src = restore_file_from_commits(rel)
        if ok:
            print(f"Restored from {src}: {rel}")
            success += 1
        else:
            print(f"No clean version found in candidates: {rel}")
            failed.append(rel)

    print("\nSummary")
    print(f"   Success: {success}")
    print(f"   Failed: {len(failed)}")
    if failed:
        print("   First few failures:")
        for f in failed[:10]:
            print(f"   - {f}")

    # Stage changes if any
    if success > 0:
        try:
            subprocess.run(["git", "add", "."], check=False)
            print("Staged recovered files.")
        except Exception as e:
            print(f"⚠️ Staging failed: {e}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
