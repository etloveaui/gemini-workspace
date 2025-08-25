#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Communication Folders Auto-Cleaner
모든 에이전트(Claude, Codex, Gemini) communication 폴더 자동 정리 스크립트
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 환경 경로 관리 시스템 사용
from environment_path_manager import get_workspace_path

def clean_agent_communication(agent_name):
    """특정 에이전트 communication 폴더 정리"""
    base_path = get_workspace_path("communication", agent_name)
    if not base_path.exists():
        return []
        
    archive_path = base_path / "archive"
    
    # Archive 폴더 생성
    archive_path.mkdir(exist_ok=True)
    
    # 1일 이상 된 파일들을 archive로 이동 (어제 파일들까지)
    cutoff_date = datetime.now() - timedelta(days=1)
    
    moved_files = []
    for file_path in base_path.glob("*.md"):
        # 템플릿 파일들은 유지
        if any(template in file_path.name for template in ["template", "GUIDE", "README"]):
            continue
            
        # 파일 이름에서 날짜 추출 (20250822 형식)
        try:
            date_str = file_path.name[:8]  # 첫 8자리
            file_date = datetime.strptime(date_str, "%Y%m%d")
            
            if file_date < cutoff_date:
                # archive로 이동
                dest_path = archive_path / file_path.name
                shutil.move(str(file_path), str(dest_path))
                moved_files.append(file_path.name)
        except (ValueError, IndexError):
            # 날짜 형식이 아닌 파일은 건드리지 않음
            pass
    
    # 이미지 파일도 정리 (.PNG, .jpg 등)
    for img_file in base_path.glob("*.PNG"):
        if img_file.stat().st_mtime < cutoff_date.timestamp():
            dest_path = archive_path / img_file.name
            shutil.move(str(img_file), str(dest_path))
            moved_files.append(img_file.name)
    
    return moved_files

def clean_all_communications():
    """모든 에이전트 communication 폴더 정리"""
    agents = ["claude", "codex", "gemini"]
    total_moved = 0
    
    for agent in agents:
        moved_files = clean_agent_communication(agent)
        if moved_files:
            print(f"[{agent.upper()}] {len(moved_files)}개 파일을 archive로 이동:")
            for file in moved_files:
                print(f"  - {file}")
            total_moved += len(moved_files)
        else:
            print(f"[{agent.upper()}] 정리할 파일 없음")
    
    print(f"\n[TOTAL] 총 {total_moved}개 파일 정리 완료")
    return total_moved

if __name__ == "__main__":
    clean_all_communications()