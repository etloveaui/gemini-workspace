#!/usr/bin/env python3
"""
Claude Communication Folder Auto-Cleaner
자동으로 오래된 파일들을 archive로 이동하는 스크립트
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def clean_claude_communication():
    """Claude communication 폴더 정리"""
    base_path = Path("C:/Users/eunta/multi-agent-workspace/communication/claude")
    archive_path = base_path / "archive"
    
    # Archive 폴더 생성
    archive_path.mkdir(exist_ok=True)
    
    # 3일 이상 된 파일들을 archive로 이동
    cutoff_date = datetime.now() - timedelta(days=3)
    
    moved_files = []
    for file_path in base_path.glob("*.md"):
        if file_path.name.startswith("prompt_template") or file_path.name.startswith("claude_session_limit_template"):
            continue  # 템플릿 파일은 유지
            
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
    
    print(f"✅ {len(moved_files)}개 파일을 archive로 이동했습니다:")
    for file in moved_files:
        print(f"  - {file}")
    
    return moved_files

if __name__ == "__main__":
    clean_claude_communication()