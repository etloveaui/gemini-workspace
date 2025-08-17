#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple multi-provider chat CLI.

Usage:
    ai                 # interactive mode
    ai "prompt"        # one-shot query

Interactive commands:
    /exit              # exit session
    /p <provider>      # switch provider (e.g. claude, gemini)
    /save              # save transcript to file

Currently provider calls are mocked and simply echo back the prompt
with the provider tag. This keeps the CLI usable without requiring
network access or API keys.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

DEFAULT_PROVIDER = "claude"

TranscriptEntry = Tuple[str, str, str]  # provider, prompt, response


def call_provider(provider: str, prompt: str) -> str:
    """Return a pseudo response for the given provider.

    Real provider integrations can replace this logic. For now, the
    prompt is echoed back to keep the CLI self-contained.
    """
    return f"[{provider}] {prompt}"


def one_shot(provider: str, prompt: str) -> List[TranscriptEntry]:
    response = call_provider(provider, prompt)
    print(response)
    return [(provider, prompt, response)]


def interactive(provider: str) -> List[TranscriptEntry]:
    transcript: List[TranscriptEntry] = []
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
            print(f"[system] provider set to {current}")
            continue
        if line == "/save":
            save_transcript(transcript)
            continue
        response = call_provider(current, line)
        print(response)
        transcript.append((current, line, response))
    return transcript


def save_transcript(entries: List[TranscriptEntry]) -> Path | None:
    if not entries:
        print("[system] nothing to save")
        return None
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(f"ai_session_{ts}.txt")
    with path.open("w", encoding="utf-8") as f:
        for provider, prompt, response in entries:
            f.write(f"provider: {provider}\n")
            f.write(f"user: {prompt}\n")
            f.write(f"assistant: {response}\n\n")
    print(f"[system] transcript saved to {path}")
    return path


def main() -> None:
    provider = DEFAULT_PROVIDER
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        one_shot(provider, prompt)
    else:
        interactive(provider)


if __name__ == "__main__":
    main()
