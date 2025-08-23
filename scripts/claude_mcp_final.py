#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 최종 MCP 통합
완전히 작동하는 MCP 기능을 Claude Code에서 바로 사용 가능
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

class ClaudeMCPFinal:
    """Claude Code용 최종 MCP 통합 클래스"""
    
    def __init__(self):
        self._filesystem_imported = False
        self._workspace_imported = False
    
    def _import_filesystem(self):
        """Filesystem 모듈 임포트"""
        if not self._filesystem_imported:
            global read_file, list_directory, find_files
            from filesystem_server import read_file, list_directory, find_files
            self._filesystem_imported = True
    
    def _import_workspace(self):
        """Workspace 모듈 임포트"""  
        if not self._workspace_imported:
            global get_workspace_status, get_agent_activity, search_workspace_content, get_database_stats
            from workspace_server import get_workspace_status, get_agent_activity, search_workspace_content, get_database_stats
            self._workspace_imported = True
    
    # === 파일 시스템 기능 ===
    def read_file(self, file_path: str) -> str:
        """프로젝트 파일을 안전하게 읽습니다"""
        self._import_filesystem()
        return read_file(file_path)
    
    def list_directory(self, dir_path: str = ".") -> str:
        """프로젝트 디렉터리 목록을 조회합니다"""
        self._import_filesystem()
        return list_directory(dir_path)
    
    def find_files(self, pattern: str, dir_path: str = ".") -> str:
        """프로젝트에서 파일을 패턴으로 검색합니다"""
        self._import_filesystem()
        return find_files(pattern, dir_path)
    
    # === 워크스페이스 기능 ===
    def workspace_status(self) -> str:
        """워크스페이스 전체 상태를 조회합니다"""
        self._import_workspace()
        return get_workspace_status()
    
    def agent_activity(self, agent_name: str = "claude") -> str:
        """특정 에이전트의 활동 내역을 조회합니다"""
        self._import_workspace()
        return get_agent_activity(agent_name)
    
    def search_workspace(self, query: str) -> str:
        """워크스페이스 전체에서 텍스트를 검색합니다"""
        self._import_workspace()
        return search_workspace_content(query)
    
    def database_stats(self) -> str:
        """usage.db 데이터베이스 통계를 조회합니다"""
        self._import_workspace()
        return get_database_stats()

# 전역 인스턴스
_claude_mcp_final = ClaudeMCPFinal()

# Claude Code에서 사용할 간편 함수들
def mcp_read_file(file_path: str) -> str:
    """파일 읽기"""
    return _claude_mcp_final.read_file(file_path)

def mcp_list_dir(dir_path: str = ".") -> str:
    """디렉터리 목록"""
    return _claude_mcp_final.list_directory(dir_path)

def mcp_find_files(pattern: str, dir_path: str = ".") -> str:
    """파일 검색"""
    return _claude_mcp_final.find_files(pattern, dir_path)

def mcp_workspace_status() -> str:
    """워크스페이스 상태"""
    return _claude_mcp_final.workspace_status()

def mcp_agent_activity(agent_name: str = "claude") -> str:
    """에이전트 활동"""
    return _claude_mcp_final.agent_activity(agent_name)

def mcp_search(query: str) -> str:
    """워크스페이스 검색"""
    return _claude_mcp_final.search_workspace(query)

def mcp_db_stats() -> str:
    """데이터베이스 통계"""
    return _claude_mcp_final.database_stats()

# 테스트 및 데모
def demo_claude_mcp():
    """Claude MCP 최종 데모"""
    safe_print("=== Claude Code MCP 최종 통합 데모 ===")
    safe_print()
    
    # 1. 파일 시스템 기능 테스트
    safe_print("1. 파일 시스템 기능:")
    
    result = mcp_read_file("README.md")
    safe_print(f"  - 파일 읽기: {len(result)}자 ({'성공' if len(result) > 100 else '실패'})")
    
    result = mcp_list_dir("scripts")
    files = len([line for line in result.split('\n') if 'FILE:' in line])
    safe_print(f"  - 디렉터리 목록: scripts 폴더에 {files}개 파일")
    
    result = mcp_find_files("*.py", "scripts")
    py_files = len([line for line in result.split('\n') if line.strip()])
    safe_print(f"  - 파일 검색: {py_files}개 Python 파일 발견")
    
    safe_print()
    
    # 2. 워크스페이스 기능 테스트
    safe_print("2. 워크스페이스 기능:")
    
    result = mcp_workspace_status()
    safe_print(f"  - 워크스페이스 상태: {'성공' if 'timestamp' in result else '실패'}")
    
    result = mcp_agent_activity("claude")
    safe_print(f"  - Claude 활동: {'성공' if 'agent' in result else '실패'}")
    
    result = mcp_search("MCP")
    import json
    try:
        parsed = json.loads(result)
        safe_print(f"  - 검색 결과: {parsed.get('total_files', 0)}개 파일에서 'MCP' 발견")
    except:
        safe_print(f"  - 검색 결과: {'성공' if 'query' in result else '실패'}")
    
    result = mcp_db_stats()
    safe_print(f"  - DB 통계: {'성공' if 'database' in result else '실패'}")
    
    safe_print()
    safe_print("[SUCCESS] Claude Code MCP 통합 완료!")
    safe_print()
    safe_print("Claude Code에서 사용 가능한 MCP 함수들:")
    safe_print("  - mcp_read_file(path)      # 파일 읽기")
    safe_print("  - mcp_list_dir(path)       # 디렉터리 목록")  
    safe_print("  - mcp_find_files(pattern)  # 파일 검색")
    safe_print("  - mcp_workspace_status()   # 워크스페이스 상태")
    safe_print("  - mcp_agent_activity(name) # 에이전트 활동")
    safe_print("  - mcp_search(query)        # 전체 검색")
    safe_print("  - mcp_db_stats()           # 데이터베이스 통계")

if __name__ == "__main__":
    demo_claude_mcp()