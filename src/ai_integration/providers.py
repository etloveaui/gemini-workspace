# -*- coding: utf-8 -*-
"""
Providers and model routing for Groq-backed models.
Kimi first, with fallbacks to Llama/Qwen/Gemma via Groq.
"""
from __future__ import annotations

KIMI = "moonshotai/kimi-k2-instruct"
LLAMA70 = "llama-3.3-70b-versatile"
QWEN32 = "qwen/qwen3-32b"
LLAMA8 = "llama-3.1-8b-instant"
GEMMA9 = "gemma2-9b-it"

DEFAULT_ROUTE = "default"
ROUTE_PRIMARY = {
    "think": [KIMI, LLAMA70],
    "code": [QWEN32, LLAMA70],
    "long": [LLAMA70, KIMI],
    "fast": [LLAMA8, GEMMA9],
    DEFAULT_ROUTE: [KIMI, LLAMA70],
}

ROUTE_TEMP = {"think": 0.2, "code": 0.1, "long": 0.3, "fast": 0.5, DEFAULT_ROUTE: 0.3}

API_URL = "https://api.groq.com/openai/v1/chat/completions"

