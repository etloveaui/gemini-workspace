from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import agent_manager  # type: ignore


def _now_parts():
    now = datetime.now()
    return now.strftime("%Y%m%d"), now.strftime("%H%M%S")


def cmd_save(args):
    day, time = _now_parts()
    agent = args.agent or agent_manager.get_active_agent()
    logs_dir = ROOT / "logs" / "sessions" / day
    logs_dir.mkdir(parents=True, exist_ok=True)

    if args.from_file:
        content = Path(args.from_file).read_text(encoding="utf-8", errors="replace")
    else:
        content = args.content or ""

    title = args.title or "Session Summary"
    fname = f"{time}_{agent}.md"
    path = logs_dir / fname
    md = [
        f"# {title}",
        "",
        f"- Agent: {agent}",
        f"- Date: {day} {time}",
        "",
        content.strip(),
        "",
    ]
    path.write_text("\n".join(md), encoding="utf-8")
    print(str(path))


def cmd_export(args):
    day = args.day or _now_parts()[0]
    src = ROOT / "logs" / "sessions" / day
    if not src.exists():
        print("not_found")
        return
    out_dir = ROOT / "logs" / "archives"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"sessions_{day}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in src.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(src).as_posix())
    print(str(zip_path))


def main():
    parser = argparse.ArgumentParser("archive manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_save = sub.add_parser("save")
    p_save.add_argument("--title", required=True)
    p_save.add_argument("--content")
    p_save.add_argument("--from-file")
    p_save.add_argument("--agent")
    p_save.set_defaults(func=cmd_save)

    p_exp = sub.add_parser("export")
    p_exp.add_argument("--day")
    p_exp.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

