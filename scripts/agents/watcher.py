from __future__ import annotations

import argparse
import os
import sys
import time
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUB = ROOT / "agents_hub" / "queue"


def main():
    parser = argparse.ArgumentParser("agents hub watcher")
    parser.add_argument("--agent", default=os.getenv("ACTIVE_AGENT", "codex"))
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    seen: set[str] = set()
    (ROOT / "agents_hub" / "queue").mkdir(parents=True, exist_ok=True)
    try:
        while True:
            for p in HUB.glob("*.json"):
                if p.name in seen:
                    continue
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                to = str(data.get("to", "")).lower()
                if to in {args.agent.lower(), "all"}:
                    print(json.dumps({"id": data.get("id"), "title": data.get("title"), "type": data.get("type")}, ensure_ascii=False))
                    seen.add(p.name)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

