#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 세션 시작 자동화 스크립트
- comm 폴더 정리
- 필수 파일 확인
- 환경 정보 출력
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from datetime import datetime

# 환경 경로 관리 시스템 사용
from environment_path_manager import get_workspace_path
from claude_comm_cleaner import clean_all_communications

def session_startup():
    """세션 시작 시 실행할 작업들"""
    print("🚀 Claude Code 세션 시작 자동화")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 환경 정보 출력
    workspace_root = get_workspace_path()
    print(f"📁 워크스페이스: {workspace_root}")
    
    # 2. Communication 폴더 자동 정리
    print("\n📋 Communication 폴더 자동 정리 중...")
    try:
        total_cleaned = clean_all_communications()
        if total_cleaned > 0:
            print(f"✅ {total_cleaned}개 파일이 archive로 정리되었습니다.")
        else:
            print("✅ 정리할 파일이 없습니다.")
    except Exception as e:
        print(f"❌ Comm 정리 중 오류: {e}")
    
    # 3. 필수 파일 존재 확인
    print("\n📄 필수 파일 확인 중...")
    essential_files = [
        "CLAUDE.md",
        "docs/CORE/AGENTS_CHECKLIST.md", 
        "docs/CORE/HUB_ENHANCED.md"
    ]
    
    for file_path in essential_files:
        full_path = get_workspace_path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (파일 없음)")
    
    # 4. 세션 시작 완료
    print("\n" + "=" * 50)
    print("🎯 세션 시작 준비 완료!")
    print("📝 이제 작업을 시작할 수 있습니다.")
    print("=" * 50)

if __name__ == "__main__":
    session_startup()