from __future__ import annotations

import subprocess
from pathlib import Path
import sys


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, encoding="utf-8", errors="replace")


def main():
    cwd = Path.cwd()
    # Try simple push
    cp = _run(["git", "push"], cwd)
    if cp.returncode == 0:
        print(cp.stdout.strip())
        return

    out = (cp.stdout or "") + (cp.stderr or "")
    # Non-fast-forward or rejected
    if "rejected" in out or "non-fast-forward" in out:
        # detect branch
        br = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
        branch = (br.stdout or "main").strip()
        # rebase and push
        pr = _run(["git", "pull", "--rebase", "origin", branch], cwd)
        if pr.returncode != 0:
            sys.stderr.write(pr.stderr)
            sys.exit(pr.returncode)
        cp2 = _run(["git", "push"], cwd)
        print((cp2.stdout or cp2.stderr).strip())
        sys.exit(cp2.returncode)

    # Fallback: print original error
    sys.stderr.write(cp.stderr)
    sys.exit(cp.returncode or 1)


if __name__ == "__main__":
    main()

