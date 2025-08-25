#!/usr/bin/env python3
"""
Filesystem MCP Server
프로젝트 파일 시스템에 안전한 접근을 제공하는 MCP 서버
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.server import NotificationOptions
from mcp.types import Resource, TextContent, Tool

# 프로젝트 루트 설정
ROOT_PATH = Path(__file__).resolve().parents[3]

# MCP 서버 생성
mcp = FastMCP("ProjectFilesystem")

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    프로젝트 내의 파일을 안전하게 읽습니다.
    
    Args:
        file_path: 읽을 파일의 상대 경로
        
    Returns:
        파일 내용 (텍스트)
    """
    try:
        # 보안: 프로젝트 루트 내부로 제한
        full_path = (ROOT_PATH / file_path).resolve()
        if not str(full_path).startswith(str(ROOT_PATH.resolve())):
            return "[ERROR] 프로젝트 외부 파일 접근 금지"
        
        if not full_path.exists():
            return f"[ERROR] 파일이 존재하지 않음: {file_path}"
            
        if full_path.is_dir():
            return f"[ERROR] 디렉터리는 읽을 수 없음: {file_path}"
            
        # UTF-8으로 파일 읽기
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        return content
        
    except Exception as e:
        return f"[ERROR] 파일 읽기 실패: {e}"

@mcp.tool()  
def list_directory(dir_path: str = ".") -> str:
    """
    프로젝트 디렉터리의 파일 목록을 조회합니다.
    
    Args:
        dir_path: 조회할 디렉터리 경로 (기본: 프로젝트 루트)
        
    Returns:
        파일 및 디렉터리 목록
    """
    try:
        # 보안 검증
        full_path = (ROOT_PATH / dir_path).resolve()
        if not str(full_path).startswith(str(ROOT_PATH.resolve())):
            return "[ERROR] 프로젝트 외부 디렉터리 접근 금지"
            
        if not full_path.exists():
            return f"[ERROR] 디렉터리가 존재하지 않음: {dir_path}"
            
        if not full_path.is_dir():
            return f"[ERROR] 파일은 목록 조회 불가: {dir_path}"
            
        # 파일 목록 수집
        items = []
        for item in sorted(full_path.iterdir()):
            item_type = "DIR " if item.is_dir() else "FILE"
            size = ""
            if item.is_file():
                try:
                    size = f" ({item.stat().st_size} bytes)"
                except:
                    size = ""
            items.append(f"{item_type}: {item.name}{size}")
            
        return "\n".join(items) if items else "[EMPTY] 디렉터리가 비어있음"
        
    except Exception as e:
        return f"[ERROR] 디렉터리 조회 실패: {e}"

@mcp.tool()
def find_files(pattern: str, dir_path: str = ".") -> str:
    """
    패턴으로 파일을 검색합니다.
    
    Args:
        pattern: 검색할 파일 패턴 (예: "*.py", "test*")
        dir_path: 검색할 디렉터리 (기본: 프로젝트 루트)
        
    Returns:
        매칭되는 파일 목록
    """
    try:
        # 보안 검증
        full_path = (ROOT_PATH / dir_path).resolve()
        if not str(full_path).startswith(str(ROOT_PATH.resolve())):
            return "[ERROR] 프로젝트 외부 디렉터리 접근 금지"
            
        if not full_path.exists() or not full_path.is_dir():
            return f"[ERROR] 유효하지 않은 디렉터리: {dir_path}"
            
        # 패턴으로 파일 검색
        matches = []
        for file_path in full_path.rglob(pattern):
            if file_path.is_file():
                # 상대 경로로 변환
                relative_path = file_path.relative_to(ROOT_PATH)
                size = file_path.stat().st_size
                matches.append(f"{relative_path} ({size} bytes)")
                
        if not matches:
            return f"[EMPTY] '{pattern}' 패턴과 매칭되는 파일 없음"
            
        return "\n".join(sorted(matches))
        
    except Exception as e:
        return f"[ERROR] 파일 검색 실패: {e}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    프로젝트 내의 파일을 안전하게 생성/수정합니다.
    
    Args:
        file_path: 쓸 파일의 상대 경로
        content: 파일에 쓸 내용
        
    Returns:
        작업 결과 메시지
    """
    try:
        # 보안: 프로젝트 루트 내부로 제한
        full_path = (ROOT_PATH / file_path).resolve()
        if not str(full_path).startswith(str(ROOT_PATH.resolve())):
            return "[ERROR] 프로젝트 외부 파일 쓰기 금지"
        
        # 디렉터리 생성 (필요시)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # UTF-8으로 파일 쓰기
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"[SUCCESS] 파일 저장 완료: {file_path} ({len(content)} 문자)"
        
    except Exception as e:
        return f"[ERROR] 파일 쓰기 실패: {e}"

@mcp.resource("file://{path}")
def get_file_resource(path: str) -> str:
    """
    파일을 리소스로 제공합니다.
    """
    return read_file(path)

if __name__ == "__main__":
    # 서버 실행
    mcp.run()