#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interactive AI session with streaming and optional logging.

This module offers a simple conversational loop that streams
provider responses token-by-token, generates a three-line session
summary on exit, and can append that summary to ``context/messages.jsonl``.
It also triggers transcript start/stop PowerShell scripts when the
session begins and ends.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

from scripts.agent_manager import get_flag, set_flag

ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPT_START = ROOT / "ai-rec-start.ps1"
TRANSCRIPT_STOP = ROOT / "ai-rec-stop.ps1"
MESSAGES_LOG = ROOT / "context" / "messages.jsonl"
DEFAULT_PROVIDER = "claude"

TranscriptEntry = Tuple[str, str, str]  # provider, prompt, response


def call_provider(provider: str, prompt: str) -> str:
    """Return a pseudo response for the given provider.

    This placeholder mirrors ``scripts.ai`` and simply echoes the prompt
    with the provider tag. Real integrations can replace this logic.
    """

    return f"[{provider}] {prompt}"


def stream_response(provider: str, prompt: str) -> Iterable[str]:
    """Yield tokens from the provider response to simulate streaming."""

    resp = call_provider(provider, prompt)
    for token in resp.split():
        yield token + " "


def try_start_transcript() -> None:
    """Invoke transcript start script if available."""

    ps = shutil.which("pwsh") or shutil.which("powershell")
    if ps and TRANSCRIPT_START.exists():
        subprocess.run([ps, "-NoLogo", "-File", str(TRANSCRIPT_START)], check=False)


def try_stop_transcript() -> None:
    """Invoke transcript stop script if available."""

    ps = shutil.which("pwsh") or shutil.which("powershell")
    if ps and TRANSCRIPT_STOP.exists():
        subprocess.run([ps, "-NoLogo", "-File", str(TRANSCRIPT_STOP)], check=False)


def append_messages_log(text: str, sender: str) -> None:
    """Append a message to ``context/messages.jsonl``."""

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "from": sender,
        "to": "all",
        "tags": ["session", "summary"],
        "body": text,
    }
    MESSAGES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MESSAGES_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def summarize_session(entries: List[TranscriptEntry]) -> str:
    """Generate a simple three-line summary of the session."""

    if not entries:
        return "(no conversation)"
    lines = []
    for idx, (_, prompt, response) in enumerate(entries[:3], 1):
        lines.append(f"{idx}. {prompt[:60]} -> {response[:60]}")
    while len(lines) < 3:
        lines.append("")
    return "\n".join(lines[:3])


def interactive(provider: str, log_summary: bool) -> None:
    transcript: List[TranscriptEntry] = []
    try_start_transcript()
    try:
        current = provider
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                continue
            if line == "/exit":
                break
            if line.startswith("/p "):
                current = line.split(maxsplit=1)[1].strip() or current
                set_flag("provider", current)
                print(f"[system] provider set to {current}")
                continue
            parts: List[str] = []
            for token in stream_response(current, line):
                print(token, end="", flush=True)
                parts.append(token)
            print()
            resp = "".join(parts).strip()
            transcript.append((current, line, resp))
        summary = summarize_session(transcript)
        print("[summary]\n" + summary)
        if log_summary:
            append_messages_log(summary, current)
    finally:
        try_stop_transcript()


def one_shot(provider: str, prompt: str, log_summary: bool) -> None:
    try_start_transcript()
    try:
        parts: List[str] = []
        for token in stream_response(provider, prompt):
            print(token, end="", flush=True)
            parts.append(token)
        print()
        resp = "".join(parts).strip()
        summary = summarize_session([(provider, prompt, resp)])
        print("[summary]\n" + summary)
        if log_summary:
            append_messages_log(summary, provider)
    finally:
        try_stop_transcript()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="*")
    ap.add_argument("--log", action="store_true", help="append summary to context/messages.jsonl")
    args = ap.parse_args()
    provider = get_flag("provider", DEFAULT_PROVIDER)
    if args.prompt:
        one_shot(provider, " ".join(args.prompt), args.log)
    else:
        interactive(provider, args.log)


if __name__ == "__main__":
    main()
