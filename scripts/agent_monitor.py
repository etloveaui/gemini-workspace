#!/usr/bin/env python3
"""
실시간 에이전트 모니터링 시스템
- 파일 변경 실시간 감지
- 에이전트별 작업 진행도 추적
- 충돌 방지 알림
- 자동 상태 업데이트
"""
import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AgentFileHandler(FileSystemEventHandler):
    """에이전트 파일 변경 핸들러"""
    
    def __init__(self, monitor):
        self.monitor = monitor
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # communication 폴더 내 파일만 모니터링
        if "communication" in str(file_path):
            self.monitor.handle_file_change(file_path)

class AgentMonitor:
    """실시간 에이전트 모니터링"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.comm_dir = self.root / "communication"
        self.status_file = self.root / ".agents" / "monitor_status.json"
        self.log_file = self.root / ".agents" / "monitor.log"
        
        self.agents = ["claude", "gemini", "codex"]
        self.agent_status = {}
        self.file_observer = None
        
        self._init_monitoring()
    
    def _init_monitoring(self):
        """모니터링 초기화"""
        self.status_file.parent.mkdir(exist_ok=True, parents=True)
        
        # 에이전트별 상태 초기화
        for agent in self.agents:
            self.agent_status[agent] = {
                "last_activity": None,
                "current_task": "unknown",
                "files_modified": 0,
                "status": "inactive"
            }
        
        self._save_status()
    
    def start_monitoring(self):
        """모니터링 시작"""
        print("🔍 실시간 에이전트 모니터링 시작...")
        
        # 파일 시스템 모니터링 설정
        event_handler = AgentFileHandler(self)
        self.file_observer = Observer()
        self.file_observer.schedule(event_handler, str(self.comm_dir), recursive=True)
        self.file_observer.start()
        
        # 주기적 상태 체크
        monitor_thread = threading.Thread(target=self._periodic_check, daemon=True)
        monitor_thread.start()
        
        print(f"   📁 모니터링 폴더: {self.comm_dir}")
        print(f"   🤖 대상 에이전트: {', '.join(self.agents)}")
    
    def handle_file_change(self, file_path: Path):
        """파일 변경 처리"""
        try:
            # 에이전트 식별
            agent = self._identify_agent(file_path)
            if not agent:
                return
            
            # 상태 업데이트
            self.agent_status[agent].update({
                "last_activity": datetime.now().isoformat(),
                "files_modified": self.agent_status[agent]["files_modified"] + 1,
                "status": "active",
                "last_file": str(file_path.name)
            })
            
            # 작업 내용 분석
            task_info = self._analyze_file_content(file_path)
            if task_info:
                self.agent_status[agent]["current_task"] = task_info
            
            # 로그 기록
            self._log_activity(agent, "file_modified", file_path.name)
            
            # 충돌 체크
            self._check_conflicts(agent, file_path)
            
            # 상태 저장
            self._save_status()
            
            print(f"🔄 {agent.upper()} 활동 감지: {file_path.name}")
            
        except Exception as e:
            self._log_activity("system", "error", f"모니터링 오류: {e}")
    
    def _identify_agent(self, file_path: Path) -> Optional[str]:
        """파일 경로로 에이전트 식별"""
        path_str = str(file_path).lower()
        
        for agent in self.agents:
            if f"communication/{agent}/" in path_str or f"communication\\{agent}\\" in path_str:
                return agent
        
        return None
    
    def _analyze_file_content(self, file_path: Path) -> Optional[str]:
        """파일 내용 분석하여 작업 파악"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # 키워드 기반 작업 분석
            if "pytest" in content or "test" in content:
                return "테스트 수정"
            elif "폴더 정리" in content or "cleanup" in content:
                return "폴더 정리"
            elif "doctor" in content or "진단" in content:
                return "시스템 진단"
            elif "최적화" in content or "optimize" in content:
                return "시스템 최적화"
            elif "완료" in content or "completed" in content:
                return "작업 완료"
            else:
                return "일반 작업"
                
        except:
            return None
    
    def _check_conflicts(self, agent: str, file_path: Path):
        """작업 충돌 체크"""
        current_task = self.agent_status[agent].get("current_task", "")
        
        # pytest 작업 중복 체크
        if "테스트" in current_task:
            other_agents = [a for a in self.agents if a != agent]
            for other_agent in other_agents:
                other_task = self.agent_status[other_agent].get("current_task", "")
                if "테스트" in other_task and self.agent_status[other_agent]["status"] == "active":
                    self._log_activity("system", "conflict", f"{agent}와 {other_agent} 테스트 작업 중복")
                    print(f"⚠️  충돌 감지: {agent}와 {other_agent}가 동시에 테스트 작업 중")
    
    def _periodic_check(self):
        """주기적 상태 체크"""
        while True:
            time.sleep(30)  # 30초마다
            
            try:
                # 비활성 에이전트 체크
                current_time = datetime.now()
                for agent in self.agents:
                    last_activity = self.agent_status[agent]["last_activity"]
                    if last_activity:
                        last_time = datetime.fromisoformat(last_activity)
                        if (current_time - last_time).seconds > 300:  # 5분 이상 비활성
                            if self.agent_status[agent]["status"] == "active":
                                self.agent_status[agent]["status"] = "inactive"
                                self._log_activity(agent, "status_change", "inactive")
                
                self._save_status()
                
            except Exception as e:
                self._log_activity("system", "error", f"주기적 체크 오류: {e}")
    
    def _log_activity(self, agent: str, activity_type: str, details: str):
        """활동 로그 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {agent.upper()}: {activity_type} - {details}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def _save_status(self):
        """상태 파일 저장"""
        status_data = {
            "last_updated": datetime.now().isoformat(),
            "agents": self.agent_status,
            "monitoring": True
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
    
    def get_status_summary(self) -> str:
        """상태 요약 반환"""
        lines = []
        lines.append("🔍 실시간 에이전트 모니터링 상태")
        lines.append("=" * 40)
        
        for agent in self.agents:
            status = self.agent_status[agent]
            status_icon = "🟢" if status["status"] == "active" else "⚪"
            
            lines.append(f"{status_icon} {agent.upper()}")
            lines.append(f"   상태: {status['status']}")
            lines.append(f"   작업: {status['current_task']}")
            lines.append(f"   파일 수정: {status['files_modified']}개")
            
            if status["last_activity"]:
                last_time = datetime.fromisoformat(status["last_activity"])
                time_diff = datetime.now() - last_time
                lines.append(f"   마지막 활동: {time_diff.seconds//60}분 전")
            lines.append("")
        
        return "\n".join(lines)
    
    def stop_monitoring(self):
        """모니터링 중지"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        print("🔍 모니터링 중지됨")

def start_agent_monitoring(root_path: str = "C:/Users/eunta/multi-agent-workspace"):
    """에이전트 모니터링 시작"""
    try:
        monitor = AgentMonitor(root_path)
        monitor.start_monitoring()
        return monitor
    except ImportError:
        print("⚠️ watchdog 모듈이 필요합니다: pip install watchdog")
        return None
    except Exception as e:
        print(f"❌ 모니터링 시작 실패: {e}")
        return None

if __name__ == "__main__":
    # 간단한 모니터링 실행
    monitor = start_agent_monitoring()
    
    if monitor:
        try:
            # 현재 상태 출력
            print(monitor.get_status_summary())
            
            # 계속 실행 (Ctrl+C로 중지)
            while True:
                time.sleep(10)
                print("\n" + monitor.get_status_summary())
                
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    else:
        # watchdog 없이 간단한 모니터링
        print("📁 간단 모니터링 모드 (파일 존재 확인)")
        
        comm_dir = Path("C:/Users/eunta/multi-agent-workspace/communication")
        while True:
            for agent in ["claude", "gemini", "codex"]:
                agent_dir = comm_dir / agent
                if agent_dir.exists():
                    files = list(agent_dir.glob("*.md"))
                    latest_file = max(files, key=lambda f: f.stat().st_mtime) if files else None
                    if latest_file:
                        mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
                        time_diff = datetime.now() - mtime
                        if time_diff.seconds < 300:  # 5분 이내
                            print(f"🟢 {agent.upper()}: 최근 활동 ({latest_file.name})")
                        else:
                            print(f"⚪ {agent.upper()}: 비활성")
            
            time.sleep(30)