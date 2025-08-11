from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = ROOT / "context"
INBOX_DIR = ROOT / ".agents" / "inbox"
MESSAGES_PATH = CONTEXT_DIR / "messages.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime:
    try:
        # Python 3.11: fromisoformat handles offsets
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.now(timezone.utc) - timedelta(days=365*50)


def _ensure_dirs():
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)


def _default_sender() -> str:
    name = os.getenv("ACTIVE_AGENT")
    if name:
        return name.lower().strip()
    # Fallback to config if available
    try:
        from scripts import agent_manager  # lazy import

        return agent_manager.get_active_agent()
    except Exception:
        return "unknown"


@dataclass
class Message:
    ts: str
    sender: str
    to: str
    body: str
    tags: List[str]

    @staticmethod
    def from_dict(d: dict) -> Optional["Message"]:
        try:
            ts = str(d.get("ts") or d.get("time") or _utc_now_iso())
            sender = str(d.get("from") or d.get("sender") or "unknown")
            to = str(d.get("to") or "all")
            body = str(d.get("body") or "")
            tags = d.get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            return Message(ts=ts, sender=sender, to=to, body=body, tags=list(tags))
        except Exception:
            return None

    def to_dict(self) -> dict:
        return {
            "ts": self.ts,
            "from": self.sender,
            "to": self.to,
            "body": self.body,
            "tags": self.tags,
        }


def append_message(to: str, body: str, tags: Optional[Iterable[str]] = None, sender: Optional[str] = None) -> Message:
    _ensure_dirs()
    msg = Message(
        ts=_utc_now_iso(),
        sender=(sender or _default_sender()),
        to=str(to).lower().strip(),
        body=str(body),
        tags=[t.strip() for t in (tags or []) if t and str(t).strip()],
    )
    with MESSAGES_PATH.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")
    return msg


def _iter_messages() -> Iterable[Message]:
    if not MESSAGES_PATH.exists():
        return []
    out: List[Message] = []
    for line in MESSAGES_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except Exception:
            continue
        m = Message.from_dict(data)
        if m:
            out.append(m)
    return out


def _read_pointer(agent: str) -> datetime:
    _ensure_dirs()
    ptr = INBOX_DIR / f".{agent}.read_at"
    if not ptr.exists():
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        return _parse_iso(ptr.read_text(encoding="utf-8").strip())
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _write_pointer(agent: str, ts: Optional[str] = None) -> str:
    _ensure_dirs()
    ts = ts or _utc_now_iso()
    ptr = INBOX_DIR / f".{agent}.read_at"
    ptr.write_text(ts, encoding="utf-8")
    return ts


def list_inbox(agent: str, since: Optional[str] = None, unread_only: bool = False, limit: int = 20) -> List[Message]:
    agent = agent.lower().strip()
    since_dt: datetime
    if since:
        s = since.strip().lower()
        now = datetime.now(timezone.utc)
        try:
            if s.endswith("h"):
                since_dt = now - timedelta(hours=int(s[:-1]))
            elif s.endswith("d"):
                since_dt = now - timedelta(days=int(s[:-1]))
            else:
                since_dt = _parse_iso(s)
        except Exception:
            since_dt = _read_pointer(agent) if unread_only else datetime.fromtimestamp(0, tz=timezone.utc)
    else:
        since_dt = _read_pointer(agent) if unread_only else datetime.fromtimestamp(0, tz=timezone.utc)

    msgs = [m for m in _iter_messages() if (m.to in (agent, "all"))]
    msgs.sort(key=lambda m: m.ts, reverse=True)

    def _ts(m: Message) -> datetime:
        return _parse_iso(m.ts)

    filtered = [m for m in msgs if _ts(m) >= since_dt]
    return filtered[: max(0, int(limit)) or 20]


def unread_count(agent: str) -> int:
    rp = _read_pointer(agent)
    msgs = [m for m in _iter_messages() if (m.to in (agent, "all") and _parse_iso(m.ts) > rp)]
    return len(msgs)


def mark_read(agent: str) -> str:
    return _write_pointer(agent)


def write_inbox_markdown(agent: str, messages: List[Message]) -> Path:
    _ensure_dirs()
    md_path = INBOX_DIR / f"{agent}.md"
    lines: List[str] = [
        f"# Inbox for {agent}",
        "",
    ]
    for m in messages:
        tags = (", ".join(m.tags)) if m.tags else ""
        tag_str = f" [{tags}]" if tags else ""
        lines.append(f"- {m.ts} | from:{m.sender} -> {m.to}{tag_str}\n  - {m.body}")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


__all__ = [
    "append_message",
    "list_inbox",
    "mark_read",
    "unread_count",
    "write_inbox_markdown",
]

