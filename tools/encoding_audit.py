#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encoding audit against a known bad commit:
- Collect files changed in the bad commit
- For each file present in the working tree, detect mojibake or non-UTF8
- Optionally attempt restore from known-good commits

Usage:
  python tools/encoding_audit.py                 # audit only (bad-commit set)
  python tools/encoding_audit.py --restore       # audit + restore (bad-commit set)
  python tools/encoding_audit.py --full          # audit all tracked files
"""

from __future__ import annotations
import subprocess
from pathlib import Path
import sys
import json

BAD_COMMIT = "d4f6efe"
GOOD_COMMITS = [
    "26bb83d",
    "95dd94b",
    "69400fa",
    "6fa2776",
]

TEXT_EXTS = {'.md','.py','.txt','.json','.yml','.yaml','.ini','.cfg','.toml','.ps1'}
BROKEN_PATTERNS = [
    "?쒖뒪?쒖뿉", "硫붿씤 泥댁젣", "筌ㅼ뮇", "獄?", "揶쏆뮇", "餓?",
    "?뀒?뒪?듃", "?쒗븘?듃", "CUserseuntamulti-agent-workspace",
]

# Allow-list: files that intentionally contain demo patterns or tooling code
ALLOW_PATHS = {
    'bulk_recovery.py',
    'tools/encoding_audit.py',
    'docs/tasks/URGENT_CODEX_인코딩_대량_복구_지시서.md',
}
ALLOW_PREFIXES = {
    'scratchpad/',  # scratch files may intentionally include examples
}

def sh(args:list[str]) -> tuple[int, str, str]:
    p = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    return p.returncode, p.stdout, p.stderr

def get_changed_paths(commit:str) -> list[str]:
    code, out, err = sh(["git","diff-tree","--no-commit-id","--name-only","-r",commit])
    if code != 0:
        raise RuntimeError(f"git diff-tree failed: {err}")
    return [line.strip() for line in out.splitlines() if line.strip()]

def is_text_file(path:Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS

def detect_issue(data:bytes) -> str|None:
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return 'non_utf8'
    for pat in BROKEN_PATTERNS:
        if pat in text:
            return 'mojibake'
    return None

def git_show(commit:str, rel:str) -> bytes|None:
    p = subprocess.run(["git","show",f"{commit}:{rel}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return None
    return p.stdout

def try_restore(rel:str) -> str|None:
    for c in GOOD_COMMITS:
        data = git_show(c, rel)
        if data is None:
            continue
        if detect_issue(data) is None:
            Path(rel).parent.mkdir(parents=True, exist_ok=True)
            Path(rel).write_bytes(data)
            return c
    return None

def main():
    restore = '--restore' in sys.argv
    full = '--full' in sys.argv
    report = []
    suspects = 0

    if full:
        # Audit all tracked files
        code, out, err = sh(["git","ls-files"])
        if code != 0:
            raise RuntimeError(f"git ls-files failed: {err}")
        candidates = [line.strip() for line in out.splitlines() if line.strip()]
        print(f"Tracking audit across {len(candidates)} files...")
    else:
        changed = get_changed_paths(BAD_COMMIT)
        candidates = changed
        print(f"Changed files in bad commit: {len(changed)}")

    for rel in candidates:
        if rel in ALLOW_PATHS or any(rel.startswith(pfx) for pfx in ALLOW_PREFIXES):
            continue
        p = Path(rel)
        if not p.exists():
            continue
        if not is_text_file(p):
            continue
        try:
            data = p.read_bytes()
        except Exception:
            continue
        issue = detect_issue(data)
        if issue:
            suspects += 1
            entry = {'path': rel, 'issue': issue}
            if restore:
                src = try_restore(rel)
                entry['restored_from'] = src
            report.append(entry)

    Path('encoding_audit_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Suspects found: {suspects}")
    print("Report written to encoding_audit_report.json")
    if restore and suspects:
        subprocess.run(["git","add","."], check=False)
        print("Staged restored files.")

if __name__ == '__main__':
    main()
