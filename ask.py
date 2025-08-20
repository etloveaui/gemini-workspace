#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎯 통합 에이전트 인터페이스 - 가장 간단한 사용법"""

import sys
import subprocess
from pathlib import Path

def main():
    """통합 에이전트 호출"""
    if len(sys.argv) < 2:
        print("🎯 통합 에이전트 인터페이스")
        print("작업을 입력하면 최적의 에이전트가 자동으로 처리합니다")
        print()
        print("사용법: python ask.py \"작업 내용\"")
        print()
        print("예시:")
        print("  python ask.py \"버그 수정해줘\"")
        print("  python ask.py \"파일 정리해줘\"") 
        print("  python ask.py \"시스템 설계해줘\"")
        return
    
    task = " ".join(sys.argv[1:])
    
    # 스마트 디스패처로 자동 라우팅
    try:
        result = subprocess.run([
            'python', 'scripts/smart_dispatcher.py', task
        ], cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"\n✅ 작업이 적절한 에이전트로 라우팅되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("대신 Claude가 직접 처리하겠습니다...")
        # 폴백: Claude가 직접 처리
        print(f"📝 작업: {task}")

if __name__ == "__main__":
    main()