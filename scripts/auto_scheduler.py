#!/usr/bin/env python3
"""
자동 스케줄러 v1.0 - 사용자가 신경쓰지 않아도 되는 자동화
"""
import schedule
import time
import subprocess
from pathlib import Path
import threading

def run_auto_update():
    """자동 상태 업데이트 실행"""
    try:
        root = Path("C:/Users/etlov/multi-agent-workspace")
        subprocess.run([
            'python', 
            str(root / 'scripts' / 'auto_status_updater.py')
        ], cwd=root)
        print("✅ 자동 업데이트 완료")
    except Exception as e:
        print(f"❌ 자동 업데이트 실패: {e}")

def run_performance_check():
    """성능 체크 실행"""
    try:
        root = Path("C:/Users/etlov/multi-agent-workspace")  
        subprocess.run([
            'python',
            str(root / 'scripts' / 'performance_optimizer.py')
        ], cwd=root)
        print("✅ 성능 최적화 완료")
    except Exception as e:
        print(f"❌ 성능 최적화 실패: {e}")

def setup_scheduler():
    """스케줄러 설정"""
    # 10분마다 상태 업데이트
    schedule.every(10).minutes.do(run_auto_update)
    
    # 1시간마다 성능 체크
    schedule.every().hour.do(run_performance_check)
    
    print("📅 자동 스케줄러 시작됨")
    print("- 10분마다: 상태 업데이트")
    print("- 1시간마다: 성능 최적화")

def run_scheduler():
    """스케줄러 실행"""
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    setup_scheduler()
    run_scheduler()