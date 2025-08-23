#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code용 MCP 통합 도구
Claude Code에서 직접 사용할 수 있는 MCP 기능 제공
"""
import sys
import asyncio
from pathlib import Path

# 인코딩 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding, safe_print
setup_utf8_encoding()

# MCP 통합 클라이언트 임포트
from mcp_integration_complete import RealMCPClient

ROOT = Path(__file__).resolve().parent.parent

class ClaudeMCPIntegration:
    """Claude Code용 MCP 통합 클래스"""
    
    def __init__(self):
        self.client = None
        self.connected = False
    
    async def initialize(self):
        """MCP 연결 초기화"""
        if self.connected:
            return True
        
        try:
            self.client = RealMCPClient()
            
            # 서버들 연결
            servers = [
                ("filesystem", ROOT / "src" / "ai_integration" / "mcp_servers" / "filesystem_server.py"),
                ("workspace", ROOT / "src" / "ai_integration" / "mcp_servers" / "workspace_server.py")
            ]
            
            connected_count = 0
            for name, script_path in servers:
                if await self.client.connect_server(name, script_path):
                    connected_count += 1
            
            self.connected = connected_count > 0
            return self.connected
            
        except Exception as e:
            safe_print(f"[ERROR] MCP 초기화 실패: {e}")
            return False
    
    async def read_project_file(self, file_path: str) -> str:
        """프로젝트 파일 안전 읽기"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("filesystem", "read_file", {"file_path": file_path})
    
    async def list_project_directory(self, dir_path: str = ".") -> str:
        """프로젝트 디렉터리 목록 조회"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("filesystem", "list_directory", {"dir_path": dir_path})
    
    async def find_project_files(self, pattern: str, dir_path: str = ".") -> str:
        """프로젝트 파일 패턴 검색"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("filesystem", "find_files", {
            "pattern": pattern, 
            "dir_path": dir_path
        })
    
    async def get_workspace_status(self) -> str:
        """워크스페이스 전체 상태 조회"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("workspace", "get_workspace_status", {})
    
    async def get_agent_activity(self, agent_name: str = "claude") -> str:
        """에이전트 활동 내역 조회"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("workspace", "get_agent_activity", {"agent_name": agent_name})
    
    async def search_workspace(self, query: str) -> str:
        """워크스페이스 전체 검색"""
        if not self.connected:
            await self.initialize()
        
        if not self.connected:
            return "[ERROR] MCP 연결되지 않음"
        
        return await self.client.call_tool("workspace", "search_workspace_content", {"query": query})
    
    async def cleanup(self):
        """리소스 정리"""
        if self.client:
            await self.client.shutdown()
        self.connected = False

# 전역 인스턴스 (Claude Code용)
_claude_mcp = None

def get_mcp_client():
    """Claude Code용 MCP 클라이언트 인스턴스 반환"""
    global _claude_mcp
    if _claude_mcp is None:
        _claude_mcp = ClaudeMCPIntegration()
    return _claude_mcp

# 동기 래퍼 함수들 (Claude Code에서 쉽게 사용)
def mcp_read_file(file_path: str) -> str:
    """파일 읽기 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.read_project_file(file_path))

def mcp_list_directory(dir_path: str = ".") -> str:
    """디렉터리 목록 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.list_project_directory(dir_path))

def mcp_find_files(pattern: str, dir_path: str = ".") -> str:
    """파일 검색 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.find_project_files(pattern, dir_path))

def mcp_workspace_status() -> str:
    """워크스페이스 상태 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.get_workspace_status())

def mcp_agent_activity(agent_name: str = "claude") -> str:
    """에이전트 활동 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.get_agent_activity(agent_name))

def mcp_search_workspace(query: str) -> str:
    """워크스페이스 검색 (동기 버전)"""
    client = get_mcp_client()
    return asyncio.run(client.search_workspace(query))

# 테스트용 메인 함수
async def test_claude_integration():
    """Claude MCP 통합 테스트"""
    safe_print("=== Claude Code MCP 통합 테스트 ===")
    safe_print()
    
    client = ClaudeMCPIntegration()
    
    try:
        # 초기화
        if await client.initialize():
            safe_print("[OK] MCP 초기화 성공")
            
            # 테스트들
            safe_print("\n[TEST] 파일 읽기:")
            result = await client.read_project_file("CLAUDE.md")
            safe_print(f"  결과: {len(result)}자 ({'성공' if len(result) > 100 else '실패'})")
            
            safe_print("\n[TEST] 디렉터리 목록:")
            result = await client.list_project_directory("scripts")
            lines = len(result.split('\n'))
            safe_print(f"  결과: {lines}줄 ({'성공' if lines > 5 else '실패'})")
            
            safe_print("\n[TEST] 워크스페이스 상태:")
            result = await client.get_workspace_status()
            safe_print(f"  결과: {len(result)}자 ({'성공' if 'timestamp' in result else '실패'})")
            
            safe_print("\n[SUCCESS] Claude Code MCP 통합 완료!")
            safe_print("\n사용법:")
            safe_print("  from scripts.claude_mcp_integration import mcp_read_file")
            safe_print("  content = mcp_read_file('README.md')")
            
        else:
            safe_print("[ERROR] MCP 초기화 실패")
            
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_claude_integration())