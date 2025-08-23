# -*- coding: utf-8 -*-
import os, re, json, sys
from pathlib import Path

# Optional MCP python SDK (if installed)
try:
    from mcp import ClientSession, StdioServerParameters, stdio_client
    HAVE_MCP = True
except Exception:
    HAVE_MCP = False

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
SECRETS = REPO_ROOT / "secrets" / "my_sensitive_data.md"
CFG = PKG_DIR / "mcp_servers.json"

def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def _find(pattern: str, txt: str) -> str | None:
    import re as _re
    m = _re.search(pattern, txt, _re.IGNORECASE)
    return m.group(1).strip() if m else None

def load_secrets():
    txt = _read_text(SECRETS)
    return {
        "GROQ_API_KEY": _find(r"(gsk_[A-Za-z0-9_-]+)", txt or ""),
        "BRAVE_API_KEY": _find(r"BRAVE_API_KEY[:\s`\"=]+([A-Za-z0-9_-]{20,})", txt or ""),
        "FIRECRAWL_API_KEY": _find(r"FIRECRAWL_API_KEY[:\s`\"=]+([A-Za-z0-9_-]{20,})", txt or ""),
        "FIGMA_API_KEY": _find(r"FIGMA_API_KEY[:\s`\"=]+([A-Za-z0-9_-]{20,})", txt or ""),
        "NOTION_TOKEN": _find(r"(secret_[A-Za-z0-9]{20,})", txt or ""),
    }

def load_config():
    cfg = json.loads(_read_text(CFG) or "{}")
    proj = cfg.get("projectRoot", ".")
    cfg["projectRoot"] = str((REPO_ROOT / proj).resolve())
    return cfg

def expand_env(env_map: dict[str, str], sec: dict[str, str], project_root: str):
    out = {}
    for k, v in env_map.items():
        v = v.replace("${PROJECT_ROOT}", project_root)
        for name, val in sec.items():
            v = v.replace("${%s}" % name, val or "")
        out[k] = v
    return out

def _build_params(srv_name: str, spec: dict, sec: dict, project_root: str):
    cmd = spec["command"]
    args = [a.replace("${PROJECT_ROOT}", project_root) for a in spec.get("args", [])]
    env = os.environ.copy()
    env.update(expand_env(spec.get("env", {}), sec, project_root))
    if any("${" in v for v in spec.get("env", {}).values()):
        return None
    return cmd, args, env

async def connect_all():
    """Return dict[name] = (session, tools). Empty if MCP not installed."""
    if not HAVE_MCP:
        print("[mcp_client] 'mcp' 패키지 미설치: pip install -r requirements.txt", file=sys.stderr)
        return {}

    cfg = load_config()
    sec = load_secrets()
    project_root = cfg["projectRoot"]
    sessions = {}

    for name, spec in cfg.get("servers", {}).items():
        if not spec.get("enabled", True):
            continue
        params = _build_params(name, spec, sec, project_root)
        if params is None:
            print(f"[mcp_client] {name}: 필요한 API 키 없음 → 스킵", file=sys.stderr)
            continue
        cmd, args, env = params
        server = StdioServerParameters(command=cmd, args=args, env=env)
        try:
            # 실제 MCP 서버 연결 구현
            transport = StdioServerParameters(command=cmd, args=args, env=env)
            
            # stdio_client를 컨텍스트 매니저 없이 직접 사용
            import asyncio
            import subprocess
            
            # 프로세스 실행
            process = await asyncio.create_subprocess_exec(
                cmd, *args,
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # MCP 클라이언트 세션 생성 (올바른 방식)
            session = ClientSession(process.stdout, process.stdin)
            
            # 초기화 및 도구 목록 조회
            try:
                await asyncio.wait_for(session.initialize(), timeout=5.0)
                tools_response = await asyncio.wait_for(session.list_tools(), timeout=5.0)
                
                # 도구 목록 구성
                tools_dict = {}
                if hasattr(tools_response, 'tools'):
                    for tool in tools_response.tools:
                        tools_dict[tool.name] = {
                            "name": tool.name,
                            "description": getattr(tool, 'description', ''),
                            "schema": getattr(tool, 'inputSchema', {})
                        }
                
                sessions[name] = (session, tools_dict)
                print(f"[mcp_client] connected: {name} ({len(tools_dict)} tools)", file=sys.stderr)
                
            except asyncio.TimeoutError:
                # 타임아웃 시 프로세스 정리
                process.terminate()
                await process.wait()
                raise Exception("연결 타임아웃")
                
        except Exception as e:
            print(f"[mcp_client] {name} 연결 실패: {e}", file=sys.stderr)
    return sessions

async def call_tool(session, tool_name: str, args: dict | None = None):
    """실제 MCP 도구 호출"""
    args = args or {}
    
    if session is None:
        return "[ERROR] MCP 세션이 연결되지 않았습니다"
    
    try:
        # MCP 도구 호출
        import asyncio
        result = await asyncio.wait_for(
            session.call_tool(tool_name, arguments=args), 
            timeout=10.0
        )
        
        # 응답 처리
        if hasattr(result, 'content') and result.content:
            parts = []
            for content in result.content:
                if hasattr(content, 'text'):
                    parts.append(content.text)
                elif isinstance(content, dict) and 'text' in content:
                    parts.append(content['text'])
                elif isinstance(content, str):
                    parts.append(content)
            return "\n".join(parts) if parts else str(result)
        else:
            return str(result)
            
    except asyncio.TimeoutError:
        return "[ERROR] MCP 도구 호출 타임아웃"
    except Exception as e:
        return f"[ERROR] MCP 도구 호출 실패: {e}"

def read_file_direct(path: str) -> str:
    p = (REPO_ROOT / path).resolve()
    base = REPO_ROOT.resolve()
    if not str(p).startswith(str(base)):
        return "[deny] project root 밖 접근 금지"
    return _read_text(p) or "[empty or not found]"

