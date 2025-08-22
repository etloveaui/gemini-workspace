#!/usr/bin/env python3
"""
간단한 에이전트 모니터링 시스템 (watchdog 불필요)
"""
import os
import time
import json
from datetime import datetime
from pathlib import Path

class SimpleAgentMonitor:
    """간단한 에이전트 모니터링"""
    
    def __init__(self):
        self.root = Path("C:/Users/etlov/multi-agent-workspace")
        self.comm_dir = self.root / "communication"
        self.agents = ["claude", "gemini", "codex"]
        self.last_check = {}
    
    def check_agent_activity(self):
        """에이전트 활동 체크"""
        from cli_style import header, item
        print(header("Agent Activity Check"))
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print("===")
        
        for agent in self.agents:
            agent_dir = self.comm_dir / agent
            if not agent_dir.exists():
                print(item(1, f"{agent.upper()}: communication folder missing"))
                continue
            
            # 최근 파일 찾기
            files = list(agent_dir.glob("*.md"))
            if not files:
                print(item(1, f"{agent.upper()}: no files"))
                continue
            
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
            time_diff = datetime.now() - mtime
            
            # 작업 내용 추측
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                task_hint = ""
                if "pytest" in content.lower():
                    task_hint = "(pytest 작업)"
                elif "최적화" in content:
                    task_hint = "(시스템 최적화)"
                elif "완료" in content:
                    task_hint = "(작업 완료)"
                elif "진행" in content:
                    task_hint = "(작업 진행 중)"
                    
            except:
                task_hint = ""
            
            if time_diff.seconds < 300:  # 5분 이내
                print(item(1, f"{agent.upper()}: recent activity {task_hint}"))
                print(f"   - file={latest_file.name}, minutes_ago={time_diff.seconds//60}")
            elif time_diff.seconds < 3600:  # 1시간 이내
                print(item(1, f"{agent.upper()}: activity detected {task_hint}"))
                print(f"   - file={latest_file.name}, minutes_ago={time_diff.seconds//60}")
            else:
                print(item(1, f"{agent.upper()}: inactive"))
                print(f"   - file={latest_file.name}, hours_ago={time_diff.seconds//3600}")
        
        print()

def monitor_once():
    """한 번만 모니터링"""
    monitor = SimpleAgentMonitor()
    monitor.check_agent_activity()

if __name__ == "__main__":
    monitor_once()
