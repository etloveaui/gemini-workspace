# -*- coding: utf-8 -*-
import sys, asyncio, json, re
from pathlib import Path
from mcp_client import connect_all, call_tool, read_file_direct
from ask_groq import main as groq_main  # reuse LLM call

ROOT = Path(__file__).resolve().parent

ROUTES = {
    "think": {"model": "auto-kimi-or-llama", "pre": ["search?optional"]},
    "code":  {"model": "qwen/qwen3-32b", "pre": ["filesystem?optional"]},
    "long":  {"model": "llama-3.3-70b-versatile", "pre": []},
    "fast":  {"model": "llama-3.1-8b-instant", "pre": []},
}

HELP = """\
/open <path>            프로젝트 파일 읽기
/run "<cmd>"            데스크탑 명령 실행
/think <q>              고정밀 추론 (Kimi 있으면 우선)
/code <q>               코드/리팩터링 친화 (Qwen3-32B)
/long <q>               장문 컨텍스트 분석 (L3.3-70B)
/fast <q>               저지연 응답 (L3.1-8B)
"""

async def handle_command(text: str):
    sessions = await connect_all()
    text = text.strip()

    # /open
    m = re.match(r"^/open\s+(.+)$", text, re.I)
    if m:
        path = m.group(1).strip().strip('"')
        # prefer filesystem MCP
        if "filesystem" in sessions:
            sess, tools = sessions["filesystem"]
            tool = next((t for t in tools if "read" in t.lower()), None)
            if tool:
                try:
                    out = await call_tool(sess, tool, {"path": path})
                    return out or "[no content]"
                except Exception as e:
                    return f"[filesystem error] {e}"
        return read_file_direct(path)

    # /run
    m = re.match(r'^/run\s+"(.+)"\s*$', text, re.I)
    if m:
        cmd = m.group(1)
        if "desktop-commander" not in sessions:
            return "[desktop-commander 미연결] scripts/mcp_servers.json에서 활성화 및 키 확인"
        sess, tools = sessions["desktop-commander"]
        # server tool name heuristic
        tname = next((t for t in tools if "run" in t.lower() or "exec" in t.lower()), None)
        if not tname:
            return "[desktop-commander] 실행 도구를 찾을 수 없음"
        try:
            out = await call_tool(sess, tname, {"command": cmd})
            return out or "[no output]"
        except Exception as e:
            return f"[run error] {e}"

    # routed LLM
    m = re.match(r"^/(think|code|long|fast)\s+(.+)$", text, re.I)
    if m:
        route, q = m.group(1).lower(), m.group(2).strip()
        model = ROUTES[route]["model"]
        ctx_chunks = []

        # optional search boosters
        if route == "think" and "brave-search" in sessions:
            try:
                sess, tools = sessions["brave-search"]
                tname = next((t for t in tools if "search" in t.lower()), None)
                if tname:
                    s = await call_tool(sess, tname, {"query": q, "count": 3})
                    if s:
                        ctx_chunks.append("## Web context\n" + s)
            except Exception:
                pass

        # optional filesystem context for /code
        if route == "code" and "filesystem" in sessions:
            try:
                # heuristic: attach README.md if exists
                s = await call_tool(sessions["filesystem"][0],
                                    next(t for t in sessions["filesystem"][1] if "read" in t.lower()),
                                    {"path": "README.md"})
                if s and not s.startswith("[deny]"):
                    ctx_chunks.append("## Project README\n" + s[:4000])
            except Exception:
                pass

        # pick final model
        if model == "auto-kimi-or-llama":
            # ask_groq supports --route mapping; reuse there:
            sys.argv = ["ask_groq.py", "--route", "think", q + ("\n\n" + "\n\n".join(ctx_chunks) if ctx_chunks else "")]
            return groq_main()  # prints & returns None; we capture by returning None
        else:
            sys.argv = ["ask_groq.py", "--model", model, q + ("\n\n" + "\n\n".join(ctx_chunks) if ctx_chunks else "")]
            return groq_main()

    if text in ("/help", "-h", "--help"):
        return HELP
    return "[unknown] 명령을 확인하려면 /help"
    
def main():
    if len(sys.argv) < 2:
        print(HELP); return
    query = " ".join(sys.argv[1:])
    out = asyncio.run(handle_command(query))
    if out is not None:
        print(out)

if __name__ == "__main__":
    main()
