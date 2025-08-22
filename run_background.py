#!/usr/bin/env python3
"""
백그라운드 자동화 실행기
터미널 하나 켜두면 자동으로 모든 것이 관리됩니다.
"""
import time
import subprocess
from pathlib import Path
import threading

def run_periodic_update():
    """주기적 업데이트 (10분마다)"""
    while True:
        try:
            print("🔄 자동 상태 업데이트 실행...")
            subprocess.run(['python', 'scripts/auto_status_updater.py'], 
                         capture_output=True, text=True, encoding='utf-8', errors='ignore')
            print("✅ 상태 업데이트 완료")
        except Exception as e:
            print(f"❌ 상태 업데이트 오류: {e}")
        
        time.sleep(600)  # 10분 대기

def run_periodic_optimization():
    """주기적 성능 최적화 (1시간마다)"""
    while True:
        time.sleep(3600)  # 1시간 대기
        try:
            print("⚡ 성능 최적화 실행...")
            subprocess.run(['python', 'scripts/performance_optimizer.py'], 
                         capture_output=True, text=True, encoding='utf-8', errors='ignore')
            print("✅ 성능 최적화 완료")
        except Exception as e:
            print(f"❌ 성능 최적화 오류: {e}")

def main():
    print("🤖 멀티 에이전트 백그라운드 자동화 시작")
    print("=" * 50)
    print("이 터미널을 켜둔 채로 작업하세요.")
    print("10분마다 상태 업데이트, 1시간마다 성능 최적화됩니다.")
    print("Ctrl+C로 종료 가능합니다.")
    print("=" * 50)
    
    # 즉시 한 번 실행
    print("🔄 초기 상태 업데이트...")
    try:
        result = subprocess.run(['python', 'scripts/auto_status_updater.py'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("✅ 초기 업데이트 완료")
        else:
            print("⚠️ 초기 업데이트 경고")
    except:
        print("❌ 초기 업데이트 실패")
    
    # 백그라운드 스레드 시작
    update_thread = threading.Thread(target=run_periodic_update, daemon=True)
    optimization_thread = threading.Thread(target=run_periodic_optimization, daemon=True)
    
    update_thread.start()
    optimization_thread.start()
    
    print("\n🎉 자동화 시스템 활성화!")
    print("이제 신경쓰지 마세요. 백그라운드에서 자동 관리됩니다.")
    
    try:
        while True:
            time.sleep(60)  # 1분마다 체크
            current_time = time.strftime("%H:%M:%S")
            print(f"🤖 [{current_time}] 자동화 시스템 정상 동작중...")
    except KeyboardInterrupt:
        print("\n👋 자동화 시스템을 종료합니다.")

if __name__ == "__main__":
    main()