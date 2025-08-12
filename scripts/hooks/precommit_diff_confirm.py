from __future__ import annotations

import os
import subprocess
import sys
import json
from pathlib import Path


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, text=True, capture_output=True, encoding="utf-8", errors="replace")


def main():
    # Skip in CI or when explicitly disabled or config flag off
    if os.getenv("SKIP_DIFF_CONFIRM") in {"1", "true", "True"}:
        sys.exit(0)
    try:
        root = Path(__file__).resolve().parents[2]
        cfg = root / ".agents" / "config.json"
        if cfg.exists():
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if not data.get("diff_confirm", True):
                sys.exit(0)
    except Exception:
        pass

    # Global toggle from .agents/config.json (hooks.enabled=false)
    try:
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        cfg = root / ".agents" / "config.json"
        if cfg.exists():
            import json as _json
            data = _json.loads(cfg.read_text(encoding="utf-8"))
            hooks_cfg = data.get("hooks", {}) if isinstance(data, dict) else {}
            if not hooks_cfg.get("enabled", True):
                sys.exit(0)
    except Exception:
        pass

    # Show staged diff
    files = run(["git", "diff", "--cached", "--name-only"]).stdout.strip()
    if not files:
        sys.exit(0)

    diff = run(["git", "--no-pager", "diff", "--cached", "--stat", "--patch"]).stdout
    print("\n[pre-commit] Staged changes preview:\n")
    try:
        # On Windows + codepage issues, printing may error; ignore
        print(diff)
    except Exception:
        pass

    # Ask for confirmation
    prompt = os.getenv("DIFF_CONFIRM_PROMPT", "Apply this commit? [y/N]: ")
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        # Non-interactive environment: default deny
        ans = "n"
    if ans not in {"y", "yes"}:
        print("Commit aborted by user.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
