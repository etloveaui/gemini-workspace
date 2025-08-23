#!/usr/bin/env python3
"""
Workspace Context MCP Server  
워크스페이스 컨텍스트 정보와 에이전트 상태를 제공하는 MCP 서버
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP

# 프로젝트 경로 설정
ROOT_PATH = Path(__file__).resolve().parents[3]
DB_PATH = ROOT_PATH / "usage.db"
DOCS_PATH = ROOT_PATH / "docs"

# MCP 서버 생성
mcp = FastMCP("WorkspaceContext")

@mcp.tool()
def get_workspace_status() -> str:
    """
    워크스페이스 전체 상태를 조회합니다.
    
    Returns:
        워크스페이스 상태 정보 (JSON 형식)
    """
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(ROOT_PATH),
            "agents": {},
            "tasks": {},
            "system_health": {}
        }
        
        # 에이전트 상태 확인
        comm_path = ROOT_PATH / "communication"
        if comm_path.exists():
            for agent in ["claude", "gemini", "codex"]:
                agent_path = comm_path / agent
                if agent_path.exists():
                    recent_files = list(agent_path.glob("*.md"))
                    status["agents"][agent] = {
                        "active": len(recent_files) > 0,
                        "recent_files": len(recent_files),
                        "last_activity": "unknown"
                    }
                    
                    # 최근 활동 파일 확인
                    if recent_files:
                        latest_file = max(recent_files, key=lambda f: f.stat().st_mtime)
                        status["agents"][agent]["last_activity"] = datetime.fromtimestamp(
                            latest_file.stat().st_mtime
                        ).isoformat()
        
        # Hub 상태 확인
        hub_file = DOCS_PATH / "CORE" / "HUB_ENHANCED.md"
        if hub_file.exists():
            status["hub"] = {
                "exists": True,
                "size": hub_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(hub_file.stat().st_mtime).isoformat()
            }
            
        return json.dumps(status, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"[ERROR] 워크스페이스 상태 조회 실패: {e}"

@mcp.tool()
def get_agent_activity(agent_name: str) -> str:
    """
    특정 에이전트의 활동 내역을 조회합니다.
    
    Args:
        agent_name: 에이전트 이름 (claude, gemini, codex)
        
    Returns:
        에이전트 활동 정보
    """
    try:
        agent_path = ROOT_PATH / "communication" / agent_name.lower()
        if not agent_path.exists():
            return f"[ERROR] '{agent_name}' 에이전트 폴더가 존재하지 않음"
            
        # 최근 파일들 확인
        files = list(agent_path.glob("*.md"))
        if not files:
            return f"[EMPTY] '{agent_name}' 에이전트 활동 파일 없음"
            
        # 파일 정보 수집
        file_info = []
        for file in sorted(files, key=lambda f: f.stat().st_mtime, reverse=True):
            stat = file.stat()
            file_info.append({
                "name": file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "age_hours": (datetime.now().timestamp() - stat.st_mtime) / 3600
            })
            
        result = {
            "agent": agent_name,
            "total_files": len(files),
            "recent_files": file_info[:5],  # 최근 5개만
            "oldest_file": file_info[-1] if file_info else None
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"[ERROR] 에이전트 활동 조회 실패: {e}"

@mcp.tool()
def get_database_stats() -> str:
    """
    usage.db 데이터베이스 통계를 조회합니다.
    
    Returns:
        데이터베이스 통계 정보
    """
    try:
        if not DB_PATH.exists():
            return "[WARN] usage.db 파일이 존재하지 않음"
            
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # 테이블 목록 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            stats = {
                "database": str(DB_PATH),
                "size_bytes": DB_PATH.stat().st_size,
                "tables": tables,
                "table_stats": {}
            }
            
            # 각 테이블의 행 수 확인
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats["table_stats"][table] = count
                except Exception:
                    stats["table_stats"][table] = "ERROR"
                    
            return json.dumps(stats, indent=2, ensure_ascii=False)
            
    except Exception as e:
        return f"[ERROR] 데이터베이스 조회 실패: {e}"

@mcp.tool()
def search_workspace_content(query: str) -> str:
    """
    워크스페이스 내에서 텍스트를 검색합니다.
    
    Args:
        query: 검색할 텍스트
        
    Returns:
        검색 결과
    """
    try:
        results = []
        search_patterns = [
            "*.md", "*.py", "*.txt", "*.json", "*.yml", "*.yaml"
        ]
        
        for pattern in search_patterns:
            for file_path in ROOT_PATH.rglob(pattern):
                # 제외할 경로들
                if any(exclude in str(file_path) for exclude in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            # 상대 경로로 변환
                            relative_path = file_path.relative_to(ROOT_PATH)
                            # 검색어가 포함된 라인 찾기
                            lines = content.split('\n')
                            matching_lines = []
                            for i, line in enumerate(lines, 1):
                                if query.lower() in line.lower():
                                    matching_lines.append(f"  {i}: {line.strip()}")
                                    if len(matching_lines) >= 3:  # 최대 3개 라인만
                                        break
                                        
                            results.append({
                                "file": str(relative_path),
                                "matches": len(matching_lines),
                                "sample_lines": matching_lines
                            })
                            
                except Exception:
                    continue
                    
        if not results:
            return f"[EMPTY] '{query}' 검색 결과 없음"
            
        # 결과를 매칭 수 순으로 정렬
        results.sort(key=lambda x: x["matches"], reverse=True)
        
        return json.dumps({
            "query": query,
            "total_files": len(results),
            "results": results[:10]  # 상위 10개만
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"[ERROR] 검색 실패: {e}"

@mcp.resource("workspace://status")
def get_workspace_resource() -> str:
    """워크스페이스 상태를 리소스로 제공"""
    return get_workspace_status()

@mcp.resource("agent://{name}/activity")  
def get_agent_resource(name: str) -> str:
    """에이전트 활동을 리소스로 제공"""
    return get_agent_activity(name)

if __name__ == "__main__":
    mcp.run()