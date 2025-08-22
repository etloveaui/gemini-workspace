"""
VS Code 시작시 자동 검증
"""
import time
from datetime import datetime
from pathlib import Path

def log_startup():
    """시작 로그 기록"""
    log_file = Path('.agents/startup_logs.txt')
    log_file.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - VS Code 자동 시작 확인\n")
    
    print(f"[{timestamp}] VS Code 자동 시작 시스템 활성화됨")

if __name__ == "__main__":
    log_startup()
