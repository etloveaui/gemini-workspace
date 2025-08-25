#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Token usage aggregation (Phase 1)

- Aggregates from SQLite tables: `usage` ∪ `usage_log`
- Estimates tokens via length(command)+length(stdout)+length(stderr)
- Outputs:
  - reports/token_usage_YYYYMMDD.csv (per-agent summary for the day)
  - reports/token_usage_summary.json (health + per-agent + overall + alerts)
  - Optional session note under communication/codex/sessions
  - Optional HUB update (marker-based, no-op if markers missing)

Windows-safe, UTF-8, and failure-tolerant.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "usage.db"
REPORTS_DIR = ROOT / "reports"
SESSIONS_DIR = ROOT / "communication" / "codex" / "sessions"

# Default daily thresholds (estimated tokens)
DEFAULT_WARNING = 200_000
DEFAULT_CRITICAL = 300_000


AGENTS = ("codex", "gemini", "claude")


def _date_str(dt: Optional[datetime] = None) -> str:
    return (dt or datetime.now(timezone.utc)).astimezone().strftime("%Y%m%d")


def _iso_date(dt: Optional[datetime] = None) -> str:
    return (dt or datetime.now(timezone.utc)).astimezone().strftime("%Y-%m-%d")


def _ensure_dirs() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    try:
        cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cur.fetchone() is not None
    except Exception:
        return False


def _health_check(conn: sqlite3.Connection) -> Dict:
    cur = conn.cursor()
    exists_usage = _table_exists(cur, "usage")
    exists_log = _table_exists(cur, "usage_log")

    def stats(tbl: str) -> Dict:
        if not _table_exists(cur, tbl):
            return {"exists": False, "count": 0, "latest": None}
        try:
            cnt = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            latest = cur.execute(f"SELECT MAX(timestamp) FROM {tbl}").fetchone()[0]
            return {"exists": True, "count": int(cnt), "latest": latest}
        except Exception:
            return {"exists": True, "count": None, "latest": None}

    h_usage = stats("usage")
    h_log = stats("usage_log")

    status = "ok" if (h_usage.get("count", 0) or h_log.get("count", 0)) else "empty"
    return {"status": status, "tables": {"usage": h_usage, "usage_log": h_log}}


def _agent_of(task_name: Optional[str], command: Optional[str]) -> str:
    text = f"{task_name or ''} {command or ''}".lower()
    for a in AGENTS:
        if a in text:
            return a
    return "unknown"


def aggregate_for_date(conn: sqlite3.Connection, yyyy_mm_dd: str) -> Dict:
    cur = conn.cursor()
    parts = []
    if _table_exists(cur, "usage"):
        parts.append(
            """
            SELECT 'usage' as source,
                   timestamp,
                   task_name,
                   command,
                   stdout,
                   stderr
            FROM usage
            WHERE DATE(timestamp) = ?
            """
        )
    if _table_exists(cur, "usage_log"):
        parts.append(
            """
            SELECT 'usage_log' as source,
                   timestamp,
                   task_name,
                   command,
                   stdout,
                   stderr
            FROM usage_log
            WHERE DATE(timestamp) = ?
            """
        )

    rows: List[Tuple] = []
    if parts:
        sql = "\nUNION ALL\n".join(parts)
        # Bind yyyy-mm-dd for each SELECT
        binds = []
        for _ in parts:
            binds.append(yyyy_mm_dd)
        cur.execute(sql, binds)
        rows = cur.fetchall()

    # Aggregate
    per_agent: Dict[str, Dict[str, int]] = {a: {"events": 0, "estimated_tokens": 0} for a in AGENTS}
    per_agent["unknown"] = {"events": 0, "estimated_tokens": 0}

    for source, timestamp, task_name, command, stdout, stderr in rows:
        est = 0
        for val in (command, stdout, stderr):
            if isinstance(val, (bytes, bytearray)):
                est += len(val)
            elif val is not None:
                try:
                    est += len(str(val))
                except Exception:
                    pass
        agent = _agent_of(task_name, command)
        per_agent.setdefault(agent, {"events": 0, "estimated_tokens": 0})
        per_agent[agent]["events"] += 1
        per_agent[agent]["estimated_tokens"] += est

    overall_events = sum(v["events"] for v in per_agent.values())
    overall_tokens = sum(v["estimated_tokens"] for v in per_agent.values())

    return {
        "date": yyyy_mm_dd,
        "per_agent": per_agent,
        "overall": {"events": overall_events, "estimated_tokens": overall_tokens},
        "row_count": len(rows),
    }


def _apply_thresholds(summary: Dict, warn_tokens: int, crit_tokens: int) -> None:
    def status_for(val: int) -> str:
        if val >= crit_tokens:
            return "critical"
        if val >= warn_tokens:
            return "warning"
        return "ok"

    per_agent = summary.get("per_agent", {})
    alerts = {a: status_for(s.get("estimated_tokens", 0)) for a, s in per_agent.items()}
    overall_val = int(summary.get("overall", {}).get("estimated_tokens", 0))
    summary["alerts"] = {
        "per_agent": alerts,
        "overall": status_for(overall_val),
        "thresholds": {"warning": warn_tokens, "critical": crit_tokens},
    }


def write_reports(summary: Dict, day_str: str) -> Tuple[Path, Path]:
    _ensure_dirs()
    # CSV per-agent summary
    csv_path = REPORTS_DIR / f"token_usage_{day_str}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["agent", "events", "estimated_tokens"])
        for agent, stats in summary["per_agent"].items():
            w.writerow([agent, stats["events"], stats["estimated_tokens"]])
        w.writerow(["TOTAL", summary["overall"]["events"], summary["overall"]["estimated_tokens"]])

    # JSON full summary + health
    json_path = REPORTS_DIR / "token_usage_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return csv_path, json_path


def write_session_note(summary: Dict, seq_no: int) -> Path:
    _ensure_dirs()
    day_str = summary["date"].replace("-", "")
    seq = f"{seq_no:02d}"
    note_path = SESSIONS_DIR / f"{day_str}_{seq}_token_usage_report.md"

    lines: List[str] = []
    lines.append(f"# {day_str} 토큰 사용량 요약 보고서")
    lines.append("")
    lines.append(f"- 날짜: {summary['date']}")
    lines.append("- 에이전트: Codex")
    lines.append("- 목적: usage ∪ usage_log 일일 집계 및 건강도 점검 요약")
    lines.append("")
    lines.append("## 요약")
    lines.append(f"- 전체 이벤트: {summary['overall']['events']}")
    lines.append(f"- 추정 토큰 합계: {summary['overall']['estimated_tokens']}")
    if "alerts" in summary:
        lines.append(f"- 전체 상태: {summary['alerts']['overall']} (warn>={summary['alerts']['thresholds']['warning']:,}, critical>={summary['alerts']['thresholds']['critical']:,})")
    lines.append("- 에이전트별:")
    for agent in sorted(summary["per_agent"].keys()):
        s = summary["per_agent"][agent]
        status = summary.get("alerts", {}).get("per_agent", {}).get(agent)
        status_part = f", status={status}" if status else ""
        lines.append(f"  - {agent}: events={s['events']}, est_tokens={s['estimated_tokens']}{status_part}")
    lines.append("")
    lines.append("## 유의사항")
    lines.append("- 토큰은 문자열 길이 기반 추정치이며, 절대값은 부정확할 수 있습니다.")
    lines.append("- 테이블이 하나라도 비어도 집계는 진행됩니다.")

    with open(note_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return note_path


def find_next_seq_for_today() -> int:
    today = _date_str()
    existing = [p.name for p in SESSIONS_DIR.glob(f"{today}_*_*.md")]
    used = []
    for name in existing:
        try:
            parts = name.split("_")
            if len(parts) >= 3:
                used.append(int(parts[1]))
        except Exception:
            pass
    seq = 1
    while seq in used:
        seq += 1
    return seq


def update_hub(summary: Dict) -> Tuple[bool, Path]:
    """Marker-based safe HUB update; no-op if markers missing.

    Looks for markers in docs/CORE/HUB_ENHANCED.md:
      <!-- P1-TOKEN:BEGIN --> ... <!-- P1-TOKEN:END -->
    Replaces the block with a concise status summary.
    """
    hub_path = ROOT / "docs" / "CORE" / "HUB_ENHANCED.md"
    if not hub_path.exists():
        return (False, hub_path)

    try:
        text = hub_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return (False, hub_path)

    begin = "<!-- P1-TOKEN:BEGIN -->"
    end = "<!-- P1-TOKEN:END -->"
    if begin not in text or end not in text:
        return (False, hub_path)

    # Build replacement block
    lines: List[str] = []
    lines.append(begin)
    lines.append("")
    lines.append(f"- Date: {summary['date']}")
    lines.append(f"- Overall: {summary.get('alerts',{}).get('overall','n/a')}  ")
    lines.append(f"  (warn>={summary['alerts']['thresholds']['warning']:,}, critical>={summary['alerts']['thresholds']['critical']:,})")
    for agent, stats in sorted(summary.get("per_agent", {}).items()):
        status = summary.get("alerts", {}).get("per_agent", {}).get(agent, "n/a")
        lines.append(f"  - {agent}: events={stats['events']} est_tokens={stats['estimated_tokens']} status={status}")
    lines.append("")
    lines.append(end)

    import re
    pattern = re.compile(re.escape(begin) + r"[\s\S]*?" + re.escape(end))
    new_text = pattern.sub("\n".join(lines), text)
    if new_text == text:
        return (False, hub_path)

    try:
        hub_path.write_text(new_text, encoding="utf-8")
        return (True, hub_path)
    except Exception:
        return (False, hub_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate usage and usage_log for a given date")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)")
    parser.add_argument("--write-note", action="store_true", help="Write a session note under communication/codex/sessions")
    parser.add_argument("--warn", type=int, default=DEFAULT_WARNING, help="Daily warning threshold (estimated tokens)")
    parser.add_argument("--crit", type=int, default=DEFAULT_CRITICAL, help="Daily critical threshold (estimated tokens)")
    parser.add_argument("--update-hub", action="store_true", help="Update HUB P1-TOKEN block if markers exist")
    args = parser.parse_args()

    day_iso = args.date or _iso_date()

    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return 2

    conn = sqlite3.connect(str(DB_PATH))
    try:
        health = _health_check(conn)
        summary = aggregate_for_date(conn, day_iso)
        summary["health"] = health
        _apply_thresholds(summary, args.warn, args.crit)

        csv_path, json_path = write_reports(summary, day_iso.replace("-", ""))
        print(f"CSV: {csv_path}")
        print(f"JSON: {json_path}")

        if args.write_note:
            seq = find_next_seq_for_today()
            note_path = write_session_note(summary, seq)
            print(f"NOTE: {note_path}")
        if args.update_hub:
            updated, hub_path = update_hub(summary)
            print(f"HUB_UPDATE: {updated} path={hub_path}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
