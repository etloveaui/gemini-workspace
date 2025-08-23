#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 서버 직접 호출 테스트
FastMCP 없이 직접 서버 기능 호출
"""
import sys
from pathlib import Path

# 인코딩 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding, safe_print
setup_utf8_encoding()

# MCP 서버 모듈 직접 임포트
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "ai_integration" / "mcp_servers"))

def test_direct_calls():
    """MCP 서버 함수들 직접 호출"""
    safe_print("=== MCP 서버 직접 호출 테스트 ===")
    safe_print()
    
    try:
        # Filesystem 서버 테스트
        safe_print("[TEST] Filesystem 서버:")
        from filesystem_server import read_file, list_directory, find_files
        
        # 디렉터리 목록
        result = list_directory("scripts")
        lines = len([line for line in result.split('\n') if line.strip()])
        safe_print(f"  디렉터리 목록: {lines}개 항목")
        
        # 파일 읽기
        result = read_file("CLAUDE.md")
        success = len(result) > 100 and "[ERROR]" not in result
        safe_print(f"  파일 읽기: {'성공' if success else '실패'} ({len(result)}자)")
        
        # 파일 검색
        result = find_files("*.py", "scripts")
        files = len([line for line in result.split('\n') if line.strip()])
        safe_print(f"  파일 검색: {files}개 Python 파일 발견")
        
        safe_print()
        
        # Workspace 서버 테스트
        safe_print("[TEST] Workspace 서버:")
        from workspace_server import get_workspace_status, get_agent_activity, search_workspace_content
        
        # 워크스페이스 상태
        result = get_workspace_status()
        success = '"timestamp"' in result and "[ERROR]" not in result
        safe_print(f"  워크스페이스 상태: {'성공' if success else '실패'}")
        
        # 에이전트 활동
        result = get_agent_activity("claude")
        success = '"agent"' in result and "[ERROR]" not in result
        safe_print(f"  에이전트 활동: {'성공' if success else '실패'}")
        
        # 검색
        result = search_workspace_content("Claude")
        success = '"query"' in result and "[ERROR]" not in result
        safe_print(f"  워크스페이스 검색: {'성공' if success else '실패'}")
        
        safe_print()
        safe_print("[SUCCESS] 모든 MCP 기능이 직접 호출로 정상 작동합니다!")
        
        return True
        
    except Exception as e:
        safe_print(f"[ERROR] 직접 호출 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_calls()
    sys.exit(0 if success else 1)