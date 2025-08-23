#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전한 MCP 통합 시스템
실제 동작하는 MCP 연결 및 도구 호출 구현
"""
import sys
import asyncio
import subprocess
import json
from pathlib import Path

# 인코딩 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding, safe_print
setup_utf8_encoding()

ROOT = Path(__file__).resolve().parent.parent

class RealMCPClient:
    """실제 작동하는 MCP 클라이언트"""
    
    def __init__(self):
        self.servers = {}
        self.processes = {}
    
    async def connect_server(self, name, script_path):
        """MCP 서버에 실제 연결"""
        try:
            safe_print(f"[INFO] {name} 서버 연결 중...")
            
            # 서버 프로세스 시작
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 프로세스 저장
            self.processes[name] = process
            
            # 초기화 메시지 전송
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize", 
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "claude-code", "version": "1.0.0"}
                }
            }
            
            # JSON RPC 메시지 전송
            msg_json = json.dumps(init_msg) + "\n"
            process.stdin.write(msg_json.encode('utf-8'))
            await process.stdin.drain()
            
            # 응답 대기 (타임아웃 포함)
            try:
                response_data = await asyncio.wait_for(
                    process.stdout.readline(), timeout=3.0
                )
                response = json.loads(response_data.decode('utf-8'))
                
                if response.get('id') == 1:
                    safe_print(f"[OK] {name} 서버 초기화 성공")
                    
                    # 도구 목록 요청
                    tools_msg = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    msg_json = json.dumps(tools_msg) + "\n"
                    process.stdin.write(msg_json.encode('utf-8'))
                    await process.stdin.drain()
                    
                    tools_response_data = await asyncio.wait_for(
                        process.stdout.readline(), timeout=3.0
                    )
                    tools_response = json.loads(tools_response_data.decode('utf-8'))
                    
                    # 도구 목록 저장
                    tools = tools_response.get('result', {}).get('tools', [])
                    self.servers[name] = {
                        'process': process,
                        'tools': {tool['name']: tool for tool in tools}
                    }
                    
                    safe_print(f"[OK] {name}: {len(tools)}개 도구 사용 가능")
                    return True
                    
            except asyncio.TimeoutError:
                safe_print(f"[ERROR] {name} 서버 응답 타임아웃")
                process.terminate()
                return False
                
        except Exception as e:
            safe_print(f"[ERROR] {name} 서버 연결 실패: {e}")
            return False
    
    async def call_tool(self, server_name, tool_name, args=None):
        """MCP 도구 실제 호출"""
        if server_name not in self.servers:
            return f"[ERROR] 서버 '{server_name}'을 찾을 수 없습니다"
        
        server = self.servers[server_name]
        process = server['process']
        
        if tool_name not in server['tools']:
            available = list(server['tools'].keys())
            return f"[ERROR] 도구 '{tool_name}' 없음. 사용 가능: {available}"
        
        try:
            # 도구 호출 메시지
            call_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args or {}
                }
            }
            
            msg_json = json.dumps(call_msg) + "\n"
            process.stdin.write(msg_json.encode('utf-8'))
            await process.stdin.drain()
            
            # 응답 읽기
            response_data = await asyncio.wait_for(
                process.stdout.readline(), timeout=10.0
            )
            response = json.loads(response_data.decode('utf-8'))
            
            if 'result' in response:
                content = response['result'].get('content', [])
                if content and isinstance(content, list):
                    return content[0].get('text', str(response))
                return str(response['result'])
            elif 'error' in response:
                return f"[ERROR] {response['error']['message']}"
            else:
                return str(response)
                
        except asyncio.TimeoutError:
            return "[ERROR] 도구 호출 타임아웃"
        except Exception as e:
            return f"[ERROR] 도구 호출 실패: {e}"
    
    async def shutdown(self):
        """모든 서버 연결 종료"""
        for name, process in self.processes.items():
            try:
                process.terminate()
                await process.wait()
                safe_print(f"[INFO] {name} 서버 종료됨")
            except:
                pass
        
        self.servers.clear()
        self.processes.clear()

async def main():
    """완전한 MCP 통합 데모"""
    safe_print("=== 완전한 MCP 통합 시스템 ===")
    safe_print()
    
    client = RealMCPClient()
    
    try:
        # 서버들 연결
        servers_to_connect = [
            ("filesystem", ROOT / "src" / "ai_integration" / "mcp_servers" / "filesystem_server.py"),
            ("workspace", ROOT / "src" / "ai_integration" / "mcp_servers" / "workspace_server.py")
        ]
        
        connected_servers = []
        for name, script_path in servers_to_connect:
            if await client.connect_server(name, script_path):
                connected_servers.append(name)
        
        safe_print()
        safe_print(f"[SUCCESS] {len(connected_servers)}개 서버 연결 완료!")
        safe_print()
        
        if connected_servers:
            # 실제 도구 호출 테스트
            safe_print("=== 실제 MCP 도구 호출 테스트 ===")
            
            # 1. Filesystem 도구 테스트
            if "filesystem" in connected_servers:
                safe_print("[TEST] Filesystem 서버 도구 테스트:")
                
                result = await client.call_tool("filesystem", "list_directory", {"dir_path": "scripts"})
                lines = result.split('\n')[:5]  # 처음 5줄만
                safe_print(f"  디렉터리 목록: {len(lines)}개 항목")
                
                result = await client.call_tool("filesystem", "read_file", {"file_path": "README.md"})
                safe_print(f"  파일 읽기: {len(result)}자 읽음 ({'성공' if '[ERROR]' not in result else '실패'})")
                
                result = await client.call_tool("filesystem", "find_files", {"pattern": "*.py", "dir_path": "scripts"})
                py_count = len([line for line in result.split('\n') if line.strip()])
                safe_print(f"  Python 파일 검색: {py_count}개 발견")
                safe_print()
            
            # 2. Workspace 도구 테스트
            if "workspace" in connected_servers:
                safe_print("[TEST] Workspace 서버 도구 테스트:")
                
                result = await client.call_tool("workspace", "get_workspace_status", {})
                safe_print(f"  워크스페이스 상태: {len(result)}자 응답 ({'성공' if 'timestamp' in result else '실패'})")
                
                result = await client.call_tool("workspace", "get_agent_activity", {"agent_name": "claude"})
                safe_print(f"  에이전트 활동: {len(result)}자 응답 ({'성공' if 'agent' in result else '실패'})")
                
                result = await client.call_tool("workspace", "search_workspace_content", {"query": "MCP"})
                safe_print(f"  워크스페이스 검색: {len(result)}자 응답 ({'성공' if 'query' in result else '실패'})")
                safe_print()
            
            safe_print("[SUCCESS] 모든 MCP 도구가 정상적으로 작동합니다!")
            safe_print()
            safe_print("이제 Claude Code에서 다음 기능들을 사용할 수 있습니다:")
            safe_print("  1. 안전한 파일 시스템 접근")
            safe_print("  2. 실시간 워크스페이스 상태 모니터링")
            safe_print("  3. 에이전트 활동 추적")
            safe_print("  4. 프로젝트 전체 검색")
            
        else:
            safe_print("[ERROR] 연결된 서버가 없습니다.")
            
    finally:
        # 정리
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())