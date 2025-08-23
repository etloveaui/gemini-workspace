#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) 매니저
Claude Code와 MCP 서버들 간의 통합을 관리합니다.
"""
import sys
import asyncio
from pathlib import Path

# 인코딩 문제 해결
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding, safe_print
setup_utf8_encoding()

# Add src to path for imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from ai_integration.claude.mcp_client import connect_all, call_tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

class MCPManager:
    def __init__(self):
        self.sessions = {}
        self.connected = False
    
    async def initialize(self):
        """MCP 서버들과 연결 초기화"""
        if not MCP_AVAILABLE:
            safe_print("[ERROR] MCP 패키지 미설치. requirements.txt에서 mcp 패키지를 확인하세요.")
            return False
            
        safe_print("[INFO] MCP 서버 연결 중...")
        try:
            self.sessions = await connect_all()
            self.connected = len(self.sessions) > 0
            
            if self.connected:
                safe_print(f"[OK] MCP 초기화 완료: {len(self.sessions)}개 서버 연결")
                for name, (session, tools) in self.sessions.items():
                    safe_print(f"  - {name}: {len(tools)} 도구 사용 가능")
            else:
                safe_print("[WARN] 연결된 MCP 서버가 없습니다.")
                
            return self.connected
            
        except Exception as e:
            safe_print(f"[ERROR] MCP 초기화 실패: {e}")
            return False
    
    async def list_available_tools(self):
        """사용 가능한 모든 MCP 도구 목록"""
        if not self.connected:
            await self.initialize()
            
        all_tools = {}
        for server_name, (session, tools) in self.sessions.items():
            all_tools[server_name] = list(tools.keys())
        
        return all_tools
    
    async def execute_tool(self, server_name: str, tool_name: str, args: dict = None):
        """특정 MCP 도구 실행"""
        if not self.connected:
            await self.initialize()
        
        if server_name not in self.sessions:
            return f"[ERROR] 서버 '{server_name}'을 찾을 수 없습니다."
        
        session, tools = self.sessions[server_name]
        if tool_name not in tools:
            available = list(tools.keys())
            return f"[ERROR] 도구 '{tool_name}'을 찾을 수 없습니다. 사용 가능: {available}"
        
        try:
            result = await call_tool(session, tool_name, args)
            return result
        except Exception as e:
            return f"[ERROR] 도구 실행 실패: {e}"
    
    async def status(self):
        """MCP 연결 상태 확인"""
        safe_print("[INFO] MCP 상태 보고서")
        safe_print("=" * 50)
        
        if not MCP_AVAILABLE:
            safe_print("[ERROR] MCP SDK 미설치")
            safe_print("   해결: pip install mcp")
            return
        
        if not self.connected:
            safe_print("[WARN] MCP 서버 미연결")
            await self.initialize()
        
        if self.sessions:
            for name, (session, tools) in self.sessions.items():
                safe_print(f"[OK] {name}")
                safe_print(f"   도구 수: {len(tools)}")
                safe_print(f"   도구 목록: {', '.join(list(tools.keys())[:3])}...")
        else:
            safe_print("[ERROR] 활성화된 MCP 서버 없음")
            safe_print("   확인: src/ai_integration/claude/mcp_servers.json")

async def main():
    """CLI 인터페이스"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP 매니저')
    parser.add_argument('--status', action='store_true', help='MCP 연결 상태 확인')
    parser.add_argument('--list-tools', action='store_true', help='사용 가능한 도구 목록')
    parser.add_argument('--test', action='store_true', help='연결 테스트')
    
    args = parser.parse_args()
    
    manager = MCPManager()
    
    if args.status:
        await manager.status()
    elif args.list_tools:
        tools = await manager.list_available_tools()
        safe_print("[INFO] 사용 가능한 MCP 도구들:")
        for server, tool_list in tools.items():
            safe_print(f"  {server}: {tool_list}")
    elif args.test:
        success = await manager.initialize()
        if success:
            safe_print("[OK] MCP 연결 테스트 성공!")
        else:
            safe_print("[ERROR] MCP 연결 테스트 실패")
    else:
        await manager.status()

if __name__ == "__main__":
    asyncio.run(main())