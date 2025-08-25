#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
완전 자동화 시스템 스케줄러
사용자가 신경쓸 필요 없이 모든 시스템이 자동으로 동작하도록 스케줄링
"""
import os
import sys
import time
import schedule
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread
import json

# 인코딩 및 경로 설정
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

class AutoSystemScheduler:
    def __init__(self):
        self.running = True
        self.log_file = ROOT / "logs" / "auto_scheduler.log"
        self.status_file = ROOT / "docs" / "CORE" / "auto_system_status.json"
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """필요한 디렉터리 생성"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message):
        """로그 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def _update_status(self, task_name, status, details=None):
        """시스템 상태 업데이트"""
        try:
            if self.status_file.exists():
                with open(self.status_file, "r", encoding="utf-8") as f:
                    status_data = json.load(f)
            else:
                status_data = {"tasks": {}}
            
            status_data["last_update"] = datetime.now().isoformat()
            status_data["tasks"][task_name] = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self._log(f"Status update failed: {e}")
    
    def run_token_monitoring(self):
        """토큰 모니터링 실행"""
        try:
            self._log("🔍 토큰 모니터링 시작...")
            result = subprocess.run([
                sys.executable, "scripts/token_usage_report.py", 
                "--auto"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self._log("✅ 토큰 모니터링 완료")
                self._update_status("token_monitoring", "success", "HUB 자동 업데이트 완료")
            else:
                self._log(f"❌ 토큰 모니터링 실패: {result.stderr}")
                self._update_status("token_monitoring", "failed", result.stderr)
        except Exception as e:
            self._log(f"❌ 토큰 모니터링 오류: {e}")
            self._update_status("token_monitoring", "error", str(e))
    
    def run_daily_reports(self):
        """일일 보고서 생성"""
        try:
            self._log("📊 일일 보고서 생성 시작...")
            result = subprocess.run([
                sys.executable, "scripts/daily_report_generator.py"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self._log("✅ 일일 보고서 생성 완료")
                self._update_status("daily_reports", "success", "모든 에이전트 보고서 생성")
            else:
                self._log(f"❌ 일일 보고서 실패: {result.stderr}")
                self._update_status("daily_reports", "failed", result.stderr)
        except Exception as e:
            self._log(f"❌ 일일 보고서 오류: {e}")
            self._update_status("daily_reports", "error", str(e))
    
    def run_session_startup(self):
        """세션 시작 자동화"""
        try:
            self._log("🚀 세션 시작 자동화...")
            result = subprocess.run([
                sys.executable, "scripts/session_startup.py"
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self._log("✅ 세션 시작 자동화 완료")
                self._update_status("session_startup", "success", "Communication 폴더 정리 완료")
            else:
                self._log(f"❌ 세션 시작 실패: {result.stderr}")
                self._update_status("session_startup", "failed", result.stderr)
        except Exception as e:
            self._log(f"❌ 세션 시작 오류: {e}")
            self._update_status("session_startup", "error", str(e))
    
    def run_system_health_check(self):
        """시스템 헬스 체크"""
        try:
            self._log("🏥 시스템 헬스 체크...")
            
            # MCP 시스템 확인
            mcp_result = subprocess.run([
                sys.executable, "scripts/claude_mcp_final.py"
            ], capture_output=True, text=True, encoding='utf-8')
            
            # Doctor 실행
            doctor_result = subprocess.run([
                sys.executable, "scripts/doctor.py"
            ], capture_output=True, text=True, encoding='utf-8')
            
            health_status = {
                "mcp_status": "ok" if mcp_result.returncode == 0 else "failed",
                "doctor_status": "ok" if doctor_result.returncode == 0 else "failed"
            }
            
            self._log("✅ 시스템 헬스 체크 완료")
            self._update_status("health_check", "success", health_status)
            
        except Exception as e:
            self._log(f"❌ 헬스 체크 오류: {e}")
            self._update_status("health_check", "error", str(e))
    
    def setup_scheduler(self):
        """스케줄 설정"""
        # 토큰 모니터링: 매 15분마다
        schedule.every(15).minutes.do(self.run_token_monitoring)
        
        # 세션 시작 자동화: 매 시간마다
        schedule.every().hour.do(self.run_session_startup)
        
        # 일일 보고서: 매일 오후 6시
        schedule.every().day.at("18:00").do(self.run_daily_reports)
        
        # 시스템 헬스 체크: 매 30분마다
        schedule.every(30).minutes.do(self.run_system_health_check)
        
        self._log("📋 자동 스케줄링 설정 완료:")
        self._log("  - 토큰 모니터링: 매 15분")
        self._log("  - 세션 자동화: 매 시간")
        self._log("  - 일일 보고서: 매일 18:00")
        self._log("  - 헬스 체크: 매 30분")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        self._log("🔄 자동 스케줄러 시작...")
        self.setup_scheduler()
        
        # 초기 실행
        self.run_system_health_check()
        self.run_token_monitoring()
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                self._log("🛑 자동 스케줄러 중지")
                self.running = False
                break
            except Exception as e:
                self._log(f"❌ 스케줄러 오류: {e}")
                time.sleep(60)
    
    def start_background(self):
        """백그라운드에서 스케줄러 시작"""
        scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        self._log("🚀 백그라운드 자동 스케줄러 시작!")
        return scheduler_thread

def main():
    """메인 실행"""
    scheduler = AutoSystemScheduler()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--background":
        # 백그라운드 실행
        scheduler.start_background()
        input("자동 스케줄러가 백그라운드에서 실행 중입니다. 종료하려면 Enter를 누르세요...")
    else:
        # 포그라운드 실행
        scheduler.run_scheduler()

if __name__ == "__main__":
    main()