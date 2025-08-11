from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import uuid
import shutil

ROOT = Path(__file__).resolve().parents[2]
HUB = ROOT / "agents_hub"
Q_DIR = HUB / "queue"
P_DIR = HUB / "processing"
A_DIR = HUB / "archive"

ALLOWED_TYPES = {"message", "task"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs():
    Q_DIR.mkdir(parents=True, exist_ok=True)
    P_DIR.mkdir(parents=True, exist_ok=True)
    A_DIR.mkdir(parents=True, exist_ok=True)


def _write_atomic(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def cmd_send(args):
    _ensure_dirs()
    msg_id = str(uuid.uuid4())
    msg = {
        "id": msg_id,
        "from": args.sender,
        "to": args.to,
        "type": args.type,
        "title": args.title,
        "body": args.body,
        "tags": [t for t in (args.tags or []) if t],
        "created_at": _now_iso(),
        "status": "queued",
    }
    path = Q_DIR / f"{msg_id}.json"
    _write_atomic(path, msg)
    print(msg_id)


def _iter_queue_for(agent: str):
    _ensure_dirs()
    for p in sorted(Q_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        to = str(data.get("to", "")).lower()
        if to in {agent.lower(), "all"}:
            yield p, data


def cmd_list(args):
    for p, data in _iter_queue_for(args.for_agent):
        print(json.dumps({"id": data.get("id"), "title": data.get("title"), "type": data.get("type")}, ensure_ascii=False))


def cmd_claim(args):
    agent = args.agent
    for p, data in _iter_queue_for(agent):
        # move to processing/<agent>/<id>.json
        dest_dir = P_DIR / agent
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / p.name
        # update status
        data["status"] = "processing"
        data["claimed_at"] = _now_iso()
        _write_atomic(dest, data)
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        print(data.get("id"))
        return
    print("")  # nothing to claim


def cmd_complete(args):
    agent = args.agent
    pid = args.id
    proc_path = P_DIR / agent / f"{pid}.json"
    if not proc_path.exists():
        print("not_found")
        return
    try:
        data = json.loads(proc_path.read_text(encoding="utf-8"))
    except Exception:
        print("read_error")
        return
    data["status"] = "done" if args.status == "success" else "failed"
    if args.note:
        data["note"] = args.note
    data["completed_at"] = _now_iso()
    # archive path
    day = datetime.now().strftime("%Y%m%d")
    dest = A_DIR / day / data["status"] / proc_path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    _write_atomic(dest, data)
    try:
        proc_path.unlink(missing_ok=True)
    except Exception:
        pass
    print("ok")


def main():
    parser = argparse.ArgumentParser("agents hub broker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--sender", default=os.getenv("ACTIVE_AGENT", "codex"))
    p_send.add_argument("--type", default="message", choices=sorted(ALLOWED_TYPES))
    p_send.add_argument("--title", required=True)
    p_send.add_argument("--body", required=True)
    p_send.add_argument("--tags", nargs="*", default=[])
    p_send.set_defaults(func=cmd_send)

    p_list = sub.add_parser("list")
    p_list.add_argument("--for", dest="for_agent", required=True)
    p_list.set_defaults(func=cmd_list)

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("--agent", required=True)
    p_claim.set_defaults(func=cmd_claim)

    p_complete = sub.add_parser("complete")
    p_complete.add_argument("--agent", required=True)
    p_complete.add_argument("--id", required=True)
    p_complete.add_argument("--status", choices=["success", "failed"], default="success")
    p_complete.add_argument("--note", default=None)
    p_complete.set_defaults(func=cmd_complete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

