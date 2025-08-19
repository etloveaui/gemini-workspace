from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
import json


def main():
    # Allow emergency bypass of all automation hooks
    if os.getenv("AGENTS_SKIP_HOOKS") in {"1", "true", "True"}:
        sys.exit(0)
    # Global toggle from .agents/config.json (hooks.enabled=false)
    try:
        root = Path(__file__).resolve().parents[2]
        cfg = root / ".agents" / "config.json"
        if cfg.exists():
            data = json.loads(cfg.read_text(encoding="utf-8"))
            hooks_cfg = data.get("hooks", {}) if isinstance(data, dict) else {}
            if not hooks_cfg.get("enabled", True):
                sys.exit(0)
    except Exception:
        pass
    # get list of staged files from git (Windows 인코딩 문제 해결)
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'  # 인코딩 오류 무시
        )
        if result.returncode != 0:
            print("pre-commit guard: failed to list staged files", file=sys.stderr)
            sys.exit(result.returncode)

        files = [f.strip() for f in (result.stdout or "").splitlines() if f.strip()]
    except Exception as e:
        print(f"pre-commit guard: encoding error: {e}", file=sys.stderr)
        # 인코딩 오류 시 안전하게 통과
        files = []
    blocked_patterns = [
        re.compile(r"^projects/"),
        re.compile(r"^\.gemini/.*(oauth|creds|token|secret)", re.IGNORECASE),
        re.compile(r"^\.gemini/.*\.(json|db|sqlite|pem|p12|key)$", re.IGNORECASE),
    ]

    violations = []
    for f in files:
        for pattern in blocked_patterns:
            if pattern.search(f):
                violations.append(f)
                break

    if violations:
        print("\U0001f6d1 Commit blocked by pre-commit guard. The following files are disallowed:", file=sys.stderr)
        for path in violations:
            print(f" - {path}", file=sys.stderr)
        print("\nRemove these files from the commit or adjust .gitignore before committing.", file=sys.stderr)
        sys.exit(1)

    # no violations
    sys.exit(0)


if __name__ == "__main__":
    main()
