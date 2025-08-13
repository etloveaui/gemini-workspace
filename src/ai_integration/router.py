#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Forwarder module for Claude router.
- Bridges top-level claude.py to the scratchpad router implementation
- Keeps current CLI entry stable while allowing iterative development under scratchpad/
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRATCH_ROUTER = ROOT / "scratchpad" / "claude_code" / "scripts" / "router.py"


def main() -> int:
    if not SCRATCH_ROUTER.exists():
        print("[claude] scratchpad router not found:", SCRATCH_ROUTER)
        return 1
    # Execute the scratchpad router as a module by path
    # Ensures it imports its sibling files (mcp_client.py, ask_groq.py) correctly
    sys.path.insert(0, str(SCRATCH_ROUTER.parent))
    import router as scratch_router  # type: ignore
    return scratch_router.main() or 0


if __name__ == "__main__":
    raise SystemExit(main())

