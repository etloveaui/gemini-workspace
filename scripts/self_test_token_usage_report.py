#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smoke test for token_usage_report:
- Runs aggregation for today
- Verifies CSV/JSON outputs exist and have expected keys
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / "venv" / "Scripts" / "python.exe") if (ROOT / "venv" / "Scripts" / "python.exe").exists() else sys.executable


def today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def run() -> int:
    day = datetime.now().strftime("%Y-%m-%d")
    cmd = [PY, str(ROOT / "scripts" / "token_usage_report.py"), "--date", day]
    print("RUN:", " ".join(cmd))
    cp = subprocess.run(cmd, text=True)
    if cp.returncode != 0:
        print("Aggregator returned non-zero", file=sys.stderr)
        return cp.returncode

    csv_path = ROOT / "reports" / f"token_usage_{today_str()}.csv"
    json_path = ROOT / "reports" / "token_usage_summary.json"
    if not csv_path.exists() or not json_path.exists():
        print("Missing output files", file=sys.stderr)
        return 2

    data = json.loads(json_path.read_text(encoding="utf-8"))
    required = ["date", "per_agent", "overall", "health", "alerts"]
    for k in required:
        if k not in data:
            print(f"Missing key in JSON: {k}", file=sys.stderr)
            return 3
    print("OK: outputs present and schema looks valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

