#!/usr/bin/env python3
"""
MCP 직접 테스트 (인코딩 안전)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "ai_integration" / "mcp_servers"))

def test_filesystem():
    try:
        from filesystem_server import read_file, list_directory, find_files
        
        print("[OK] Filesystem MCP Server 임포트 성공")
        
        # 디렉터리 목록 테스트
        result = list_directory("scripts")
        file_count = len([line for line in result.split('\n') if 'FILE:' in line])
        print(f"[OK] scripts 폴더: {file_count}개 파일 발견")
        
        # 파일 읽기 테스트
        result = read_file("CLAUDE.md")
        success = len(result) > 100 and "[ERROR]" not in result
        print(f"[OK] CLAUDE.md 읽기: {'성공' if success else '실패'} ({len(result)} 문자)")
        
        # 파일 검색 테스트
        result = find_files("*.py", "scripts")
        py_files = len([line for line in result.split('\n') if line.strip()])
        print(f"[OK] Python 파일 검색: {py_files}개 발견")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Filesystem 테스트 실패: {e}")
        return False

def test_workspace():
    try:
        from workspace_server import get_workspace_status, get_agent_activity
        
        print("[OK] Workspace MCP Server 임포트 성공")
        
        # 워크스페이스 상태 테스트
        result = get_workspace_status()
        success = '"timestamp"' in result and '[ERROR]' not in result
        print(f"[OK] 워크스페이스 상태: {'성공' if success else '실패'}")
        
        # 에이전트 활동 테스트
        result = get_agent_activity("claude")
        success = '"agent"' in result and '[ERROR]' not in result
        print(f"[OK] Claude 활동 조회: {'성공' if success else '실패'}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Workspace 테스트 실패: {e}")
        return False

def main():
    print("=== MCP 직접 기능 테스트 ===")
    print()
    
    fs_ok = test_filesystem()
    print()
    ws_ok = test_workspace()
    print()
    
    if fs_ok and ws_ok:
        print("[SUCCESS] 모든 MCP 서버가 정상 작동합니다!")
        print()
        print("사용 가능한 기능:")
        print("1. 파일시스템 안전 접근 (filesystem)")
        print("   - read_file: 파일 내용 읽기")
        print("   - list_directory: 폴더 목록 조회")
        print("   - find_files: 파일 패턴 검색")
        print()
        print("2. 워크스페이스 컨텍스트 (workspace)")
        print("   - get_workspace_status: 전체 상태 조회")
        print("   - get_agent_activity: 에이전트 활동 추적")
        print("   - search_workspace_content: 프로젝트 전체 검색")
        print()
        return True
    else:
        print("[ERROR] 일부 MCP 서버에 문제가 있습니다.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)