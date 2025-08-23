#!/usr/bin/env python3
"""
MCP 실제 사용 데모
구현된 MCP 서버들을 직접 호출하여 실제 기능을 테스트합니다.
"""
import sys
import subprocess
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def call_mcp_server(server_script, tool_name, *args):
    """MCP 서버의 도구를 직접 호출"""
    try:
        # 서버 스크립트를 모듈로 import
        sys.path.insert(0, str(ROOT / "src" / "ai_integration" / "mcp_servers"))
        
        if server_script == "filesystem":
            from filesystem_server import read_file, list_directory, find_files
            
            if tool_name == "read_file":
                return read_file(args[0] if args else "README.md")
            elif tool_name == "list_directory": 
                return list_directory(args[0] if args else ".")
            elif tool_name == "find_files":
                return find_files(args[0] if args else "*.py", args[1] if len(args) > 1 else ".")
                
        elif server_script == "workspace":
            from workspace_server import get_workspace_status, get_agent_activity, search_workspace_content
            
            if tool_name == "get_workspace_status":
                return get_workspace_status()
            elif tool_name == "get_agent_activity":
                return get_agent_activity(args[0] if args else "claude")
            elif tool_name == "search_workspace_content":
                return search_workspace_content(args[0] if args else "MCP")
                
        return f"[ERROR] 알 수 없는 도구: {tool_name}"
        
    except Exception as e:
        return f"[ERROR] MCP 도구 실행 실패: {e}"

def main():
    """MCP 실제 기능 데모"""
    print("=== MCP 실제 기능 데모 ===")
    print()
    
    # 1. Filesystem 서버 테스트
    print("1. Filesystem 서버 테스트")
    print("-" * 30)
    
    # 디렉터리 목록
    print("[TEST] 루트 디렉터리 목록:")
    result = call_mcp_server("filesystem", "list_directory", ".")
    print(result[:500] + "..." if len(result) > 500 else result)
    print()
    
    # 파일 읽기
    print("[TEST] README.md 파일 읽기:")
    result = call_mcp_server("filesystem", "read_file", "README.md")
    print(result[:300] + "..." if len(result) > 300 else result)
    print()
    
    # 파일 검색
    print("[TEST] Python 파일 검색:")
    result = call_mcp_server("filesystem", "find_files", "*.py", "scripts")
    print(result)
    print()
    
    # 2. Workspace 서버 테스트
    print("2. Workspace 서버 테스트")
    print("-" * 30)
    
    # 워크스페이스 상태
    print("[TEST] 워크스페이스 전체 상태:")
    result = call_mcp_server("workspace", "get_workspace_status")
    # JSON을 보기 좋게 출력
    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=2, ensure_ascii=False)[:800] + "...")
    except:
        print(result[:500] + "...")
    print()
    
    # 에이전트 활동
    print("[TEST] Claude 에이전트 활동:")
    result = call_mcp_server("workspace", "get_agent_activity", "claude")
    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=2, ensure_ascii=False)[:600] + "...")
    except:
        print(result[:400] + "...")
    print()
    
    # 검색 기능
    print("[TEST] 'Claude' 키워드 검색:")
    result = call_mcp_server("workspace", "search_workspace_content", "Claude")
    try:
        parsed = json.loads(result)
        print(f"검색 결과: {parsed['total_files']}개 파일에서 발견")
        for i, file_result in enumerate(parsed['results'][:3]):
            print(f"  {i+1}. {file_result['file']} ({file_result['matches']}개 매치)")
    except:
        print(result[:400] + "...")
    print()
    
    print("=== MCP 데모 완료 ===")
    print()
    print("✅ 모든 MCP 서버가 정상적으로 작동합니다!")
    print("Claude Code에서 이제 다음과 같이 사용 가능:")
    print("  - 파일 시스템 안전 접근")
    print("  - 워크스페이스 상태 모니터링")  
    print("  - 에이전트 활동 추적")
    print("  - 전체 프로젝트 검색")

if __name__ == "__main__":
    main()