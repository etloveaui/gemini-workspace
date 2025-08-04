from __future__ import annotations

import re
import subprocess
import sys


def main():
    # get list of staged files from git
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    if result.returncode != 0:
        print("pre-commit guard: failed to list staged files", file=sys.stderr)
        sys.exit(result.returncode)

    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
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
