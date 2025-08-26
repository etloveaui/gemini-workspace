#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 자동 활용 시스템
Claude Code에서 투명하게 MCP 기능을 자동으로 활용
- 토큰 관리 효율화
- 파일 작업 최적화
- 워크스페이스 상태 자동 파악
"""
import sys
import os
from pathlib import Path
import importlib

# 인코딩 및 경로 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding
setup_utf8_encoding()

class MCPAutoSystem:
    """MCP 자동 활용 시스템"""
    
    def __init__(self):
        from environment_path_manager import get_workspace_path
        self.workspace_root = get_workspace_path()
        self.mcp_available = self._check_mcp_availability()
        self._load_mcp_modules()
        
    def _check_mcp_availability(self) -> bool:
        """MCP 모듈 사용 가능성 확인"""
        try:
            sys.path.insert(0, str(self.workspace_root / "src" / "ai_integration" / "mcp_servers"))
            return True
        except Exception as e:
            print(f"⚠️ MCP 모듈 접근 불가: {e}")
            return False
    
    def _load_mcp_modules(self):
        """MCP 모듈들 로드"""
        if not self.mcp_available:
            return
            
        try:
            # MCP 서버 경로를 sys.path에 추가
            mcp_path = self.workspace_root / "src" / "ai_integration" / "mcp_servers"
            if str(mcp_path) not in sys.path:
                sys.path.insert(0, str(mcp_path))
            
            # Filesystem MCP 로드
            from filesystem_server import read_file, list_directory, find_files, write_file
            self.fs_read = read_file
            self.fs_list = list_directory
            self.fs_find = find_files
            self.fs_write = write_file
            
            # Workspace MCP 로드
            from workspace_server import get_workspace_status, get_agent_activity, search_workspace_content, get_database_stats
            self.ws_status = get_workspace_status
            self.ws_activity = get_agent_activity  
            self.ws_search = search_workspace_content
            self.ws_db_stats = get_database_stats
            
            self.mcp_available = True
            
            # MCP 함수들 등록
            self.mcp_functions = {
                'read_file': self.fs_read,
                'list_directory': self.fs_list,
                'find_files': self.fs_find,
                'write_file': self.fs_write,
                'workspace_status': self.ws_status,
                'agent_activity': self.ws_activity,
                'search_content': self.ws_search,
                'db_stats': self.ws_db_stats
            }
            
            print("✅ MCP 모듈 로드 완료")
            
        except ImportError as e:
            print(f"⚠️ MCP 모듈 임포트 실패: {e}")
            self.mcp_available = False
        except Exception as e:
            print(f"⚠️ MCP 시스템 오류: {e}")
            self.mcp_available = False
    
    # === 파일 작업 최적화 ===
    
    def smart_read_file(self, file_path: str, max_size: int = 50000) -> str:
        """스마트 파일 읽기 - MCP 우선, 토큰 효율성 고려"""
        if self.mcp_available:
            try:
                result = self.fs_read(file_path)
                if len(result) > max_size:
                    return f"파일 크기가 큼 ({len(result)}자). 요약: {result[:1000]}..."
                return result
            except:
                pass
        
        # Fallback to standard read
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > max_size:
                    return f"파일 크기가 큼 ({len(content)}자). 요약: {content[:1000]}..."
                return content
        except Exception as e:
            return f"파일 읽기 실패: {e}"
    
    def smart_list_directory(self, dir_path: str) -> list:
        """스마트 디렉터리 목록 - MCP 우선"""
        if self.mcp_available:
            try:
                return self.fs_list(dir_path)
            except:
                pass
        
        # Fallback
        try:
            return [f.name for f in Path(dir_path).iterdir()]
        except:
            return []
    
    def smart_find_files(self, pattern: str, directory: str = None) -> list:
        """스마트 파일 검색 - MCP 우선"""
        if directory is None:
            directory = str(self.workspace_root)
            
        if self.mcp_available:
            try:
                return self.fs_find(pattern, directory)
            except:
                pass
        
        # Fallback
        try:
            return [str(f) for f in Path(directory).rglob(pattern)]
        except:
            return []
    
    # === 워크스페이스 상태 자동 파악 ===
    
    def get_current_workspace_status(self) -> dict:
        """현재 워크스페이스 상태 자동 파악"""
        if self.mcp_available:
            try:
                import json
                status_json = self.ws_status()
                if isinstance(status_json, str):
                    return json.loads(status_json)
                return status_json
            except Exception as e:
                print(f"⚠️ MCP 워크스페이스 상태 조회 실패: {e}")
        
        # Fallback - 기본 정보만
        return {
            "status": "fallback_mode",
            "workspace_root": str(self.workspace_root),
            "mcp_available": self.mcp_available,
            "files_count": len(list(self.workspace_root.rglob("*"))),
        }
    
    def get_agent_activities(self) -> dict:
        """에이전트 활동 상황 파악"""
        if self.mcp_available:
            try:
                import json
                activities = {}
                for agent in ["claude", "codex", "gemini"]:
                    result = self.ws_activity(agent)
                    if isinstance(result, str) and not result.startswith("[ERROR]"):
                        activities[agent] = json.loads(result)
                    else:
                        activities[agent] = {"error": result}
                return activities
            except Exception as e:
                print(f"⚠️ MCP 에이전트 활동 조회 실패: {e}")
        
        # Fallback - communication 폴더 기반
        activities = {}
        for agent in ["claude", "codex", "gemini"]:
            comm_dir = self.workspace_root / "communication" / agent
            if comm_dir.exists():
                recent_files = sorted(comm_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
                activities[agent] = [f.name for f in recent_files]
        
        return activities
    
    def smart_search_workspace(self, query: str) -> list:
        """워크스페이스 스마트 검색"""
        if self.mcp_available:
            try:
                return self.ws_search(query)
            except:
                pass
        
        # Fallback - 간단한 파일명 검색
        results = []
        for file_path in self.workspace_root.rglob("*"):
            if query.lower() in file_path.name.lower():
                results.append(str(file_path))
                if len(results) >= 20:  # 제한
                    break
        
        return results
    
    # === 자동화 시스템 ===
    
    def auto_token_optimization(self) -> dict:
        """토큰 사용 최적화 자동 분석"""
        report = {
            "large_files": [],
            "optimization_suggestions": [],
            "token_estimate": 0
        }
        
        # 큰 파일 식별
        for file_path in self.workspace_root.rglob("*.py"):
            if file_path.stat().st_size > 10000:  # 10KB 이상
                report["large_files"].append(str(file_path))
        
        # 최적화 제안
        if len(report["large_files"]) > 20:
            report["optimization_suggestions"].append("큰 파일이 많음 - 요약 읽기 권장")
        
        report["token_estimate"] = len(report["large_files"]) * 1000  # 대략적 추정
        
        return report
    
    def auto_system_health_check(self) -> dict:
        """시스템 건강도 자동 체크"""
        health = {
            "status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        # HUB 파일 존재 확인
        hub_file = self.workspace_root / "docs" / "CORE" / "HUB_ENHANCED.md"
        if not hub_file.exists():
            health["issues"].append("HUB_ENHANCED.md 파일 없음")
            health["status"] = "warning"
        
        # Communication 폴더 정리 필요성 확인
        comm_files = 0
        for agent in ["claude", "codex", "gemini"]:
            agent_dir = self.workspace_root / "communication" / agent
            if agent_dir.exists():
                comm_files += len(list(agent_dir.glob("*.md")))
        
        if comm_files > 10:
            health["recommendations"].append("Communication 폴더 정리 권장")
        
        return health

# 전역 인스턴스
mcp_auto = MCPAutoSystem()

# 편의 함수들
def read_file_smart(file_path: str) -> str:
    """MCP 기반 스마트 파일 읽기"""
    return mcp_auto.smart_read_file(file_path)

def list_dir_smart(dir_path: str) -> list:
    """MCP 기반 스마트 디렉터리 목록"""
    return mcp_auto.smart_list_directory(dir_path)

def find_files_smart(pattern: str) -> list:
    """MCP 기반 스마트 파일 검색"""
    return mcp_auto.smart_find_files(pattern)

def get_workspace_status_auto() -> dict:
    """워크스페이스 상태 자동 파악"""
    return mcp_auto.get_current_workspace_status()

def optimize_tokens_auto() -> dict:
    """토큰 최적화 자동 분석"""
    return mcp_auto.auto_token_optimization()

def health_check_auto() -> dict:
    """시스템 건강도 자동 체크"""
    return mcp_auto.auto_system_health_check()

if __name__ == "__main__":
    print("=== MCP 자동 활용 시스템 테스트 ===")
    
    # 상태 확인
    status = get_workspace_status_auto()
    print(f"📊 워크스페이스 상태: {status}")
    
    # 토큰 최적화
    token_info = optimize_tokens_auto()
    print(f"🎯 토큰 최적화: {token_info}")
    
    # 건강도 체크
    health = health_check_auto()
    print(f"💊 시스템 건강도: {health}")
    
    print("✅ MCP 자동 시스템 준비 완료")