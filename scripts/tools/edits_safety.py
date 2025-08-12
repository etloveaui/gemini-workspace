from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / ".agents" / "edits_state.json"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime:
    s = (ts or "").strip()
    if not s:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


@dataclass
class Entry:
    last_ts: str
    last_status: str
    fail_count: int

    @staticmethod
    def from_dict(d: dict) -> "Entry":
        return Entry(
            last_ts=str(d.get("last_ts") or _utcnow_iso()),
            last_status=str(d.get("last_status") or "unknown"),
            fail_count=int(d.get("fail_count") or 0),
        )

    def to_dict(self) -> dict:
        return {"last_ts": self.last_ts, "last_status": self.last_status, "fail_count": self.fail_count}


def _load() -> Dict[str, Entry]:
    if not STATE_PATH.exists():
        return {}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: Dict[str, Entry] = {}
    for k, v in (data or {}).items():
        try:
            out[k] = Entry.from_dict(v)
        except Exception:
            continue
    return out


def _save(entries: Dict[str, Entry]):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {k: v.to_dict() for k, v in entries.items()}
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def key_for(file_rel: str, diff_hash: str) -> str:
    return f"{file_rel}::{diff_hash}"


def should_apply(file_rel: str, diff_hash: str, max_recent_success_minutes: int = 60, max_failures: int = 3, window_minutes: int = 30) -> tuple[bool, Optional[str]]:
    entries = _load()
    k = key_for(file_rel, diff_hash)
    e = entries.get(k)
    if not e:
        return True, None
    now = datetime.now(timezone.utc)
    last = _parse_iso(e.last_ts)
    # If the exact same patch was applied successfully recently, skip re-apply
    if e.last_status == "success" and (now - last) <= timedelta(minutes=max_recent_success_minutes):
        return False, "recently_applied"
    # If too many failures in the recent window, suggest backoff
    if e.fail_count >= max_failures and (now - last) <= timedelta(minutes=window_minutes):
        return False, "backoff_due_to_failures"
    return True, None


def record_result(file_rel: str, diff_hash: str, success: bool):
    entries = _load()
    k = key_for(file_rel, diff_hash)
    e = entries.get(k) or Entry(last_ts=_utcnow_iso(), last_status="unknown", fail_count=0)
    e.last_ts = _utcnow_iso()
    if success:
        e.last_status = "success"
        e.fail_count = 0
    else:
        e.last_status = "fail"
        e.fail_count = int(e.fail_count) + 1
    entries[k] = e
    _save(entries)


__all__ = [
    "should_apply",
    "record_result",
]

