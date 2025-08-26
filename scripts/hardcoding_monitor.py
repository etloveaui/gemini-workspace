#!/usr/bin/env python3
"""
하드코딩 실시간 모니터링 서비스
파일 변경 감지 시 자동으로 하드코딩 검사 수행
"""
import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 워크스페이스 경로 설정
sys.path.append(str(Path(__file__).parent))
from hardcoding_prevention_system import HardcodingPrevention
from environment_path_manager import get_workspace_path

class HardcodingWatcher(FileSystemEventHandler):
    def __init__(self):
        self.prevention = HardcodingPrevention()
        self.last_check = {}  # 파일별 마지막 검사 시간
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        if not self.prevention.should_scan_file(file_path):
            return
        
        # 너무 자주 검사하지 않기 위한 쿨다운 (5초)
        now = time.time()
        if file_path in self.last_check:
            if now - self.last_check[file_path] < 5:
                return
        
        self.last_check[file_path] = now
        
        # 하드코딩 검사
        violations = self.prevention.scan_file_for_hardcoding(file_path)
        
        if violations:
            print(f"🚨 하드코딩 발견: {file_path.name}")
            print(f"    {len(violations)}개 위반사항")
            
            # 자동 수정 시도
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 
                    get_workspace_path("scripts", "fix_hardcoded_paths.py"),
                    str(file_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 자동 수정 완료: {file_path.name}")
                else:
                    print(f"⚠️ 자동 수정 실패: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ 자동 수정 오류: {e}")

def start_monitoring():
    """모니터링 시작"""
    workspace_root = get_workspace_path()
    
    event_handler = HardcodingWatcher()
    observer = Observer()
    observer.schedule(event_handler, str(workspace_root), recursive=True)
    
    print(f"🔍 하드코딩 실시간 모니터링 시작: {workspace_root}")
    print("📁 감시 중인 디렉터리: scripts/, communication/, docs/")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⏹️  모니터링 종료")
    
    observer.join()

if __name__ == "__main__":
    start_monitoring()
