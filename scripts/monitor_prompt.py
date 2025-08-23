"""
Monitor a designated prompt file for changes and echo contents.
Writes a simple event log under communication/codex.

Usage (Windows PowerShell):
  .\\venv\\Scripts\\python.exe scripts\\monitor_prompt.py --file communication\\codex\\prompt.md --debounce 0.5
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


def _try_decodings(path: Path) -> str:
    # Heuristic decoding: prefer fewer replacement chars and more Hangul coverage
    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp949",
        "euc-kr",
        "utf-16",
        "utf-16le",
        "utf-16be",
    ]
    best_text = ""
    best_score = float("-inf")
    for enc in encodings:
        try:
            text = path.read_text(encoding=enc)
        except Exception:
            continue

        # score: fewer replacement chars + proportion of Hangul letters
        repl = text.count("\ufffd")
        hangul = sum(0xAC00 <= ord(ch) <= 0xD7A3 for ch in text)
        total = max(len(text), 1)
        score = -repl + (hangul / total)
        if score > best_score:
            best_score = score
            best_text = text
    if best_text:
        return best_text
    # fallback with replacement
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"<read error: {e}>"


def read_text_safe(path: Path) -> str:
    try:
        return _try_decodings(path)
    except OSError as e:
        return f"<read error: {e}>"


def ensure_log_dir() -> Path:
    log_dir = Path("communication/codex").resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def append_event(log_dir: Path, event: str, file_path: Path, preview: str) -> None:
    day = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"{day}_prompt_events.log"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"[{ts}] {event}: {file_path}"
    body = "\n".join([header, "---", preview[:2000], "", ""])  # cap preview
    with log_file.open("a", encoding="utf-8") as f:
        f.write(body)


def watch_file(file_path: Path, interval: float, debounce: float) -> int:
    log_dir = ensure_log_dir()
    file_path = file_path.resolve()
    last_seen_mtime: float | None = None
    last_event_time = 0.0

    print(f"[prompt] monitoring file: {file_path} (interval {interval}s, debounce {debounce}s)")
    try:
        while True:
            exists = file_path.exists()
            mtime = file_path.stat().st_mtime if exists else None

            now = time.time()
            event = None

            if last_seen_mtime is None:
                if exists:
                    event = "created"
            else:
                if not exists:
                    event = "deleted"
                elif mtime != last_seen_mtime:
                    event = "modified"

            if event and (now - last_event_time) >= debounce:
                content = read_text_safe(file_path) if exists else "<no file>"
                print(f"[prompt][{event}] {file_path}")
                print("[prompt][content]\n" + content)
                append_event(log_dir, event, file_path, content)
                last_event_time = now

            last_seen_mtime = mtime
            time.sleep(interval)
    except KeyboardInterrupt:
        print("[prompt] stopped")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="Path to prompt file to monitor")
    p.add_argument("--interval", type=float, default=0.5)
    p.add_argument("--debounce", type=float, default=0.5)
    args = p.parse_args(argv)

    return watch_file(Path(args.file), args.interval, args.debounce)


if __name__ == "__main__":
    raise SystemExit(main())
