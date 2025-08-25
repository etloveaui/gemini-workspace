"""
에이전트 상태 실시간 동기화 시스템
HUB_ENHANCED.md 자동 업데이트 및 에이전트 간 작업 충돌 방지
"""
import time
import threading
from pathlib import Path
from datetime import datetime
import json
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line
try:
    from usage_logging import record_event
except Exception:
    def record_event(*args, **kwargs):
        pass

ROOT = Path(__file__).resolve().parent.parent
HUB_FILE = ROOT / "docs" / "HUB_ENHANCED.md"
AGENTS_DIR = ROOT / "communication"

class RealtimeAgentSync:
    def __init__(self):
        self.running = False
        self.last_sync = {}
        self.agent_status = {}
        
    def watch_agent_files(self):
        """에이전트 파일 변경 감지"""
        agents = ['claude', 'codex', 'gemini']
        
        while self.running:
            for agent in agents:
                agent_dir = AGENTS_DIR / agent
                if not agent_dir.exists():
                    continue
                
                # 최근 파일 찾기
                recent_files = []
                for file_path in agent_dir.glob('*.md'):
                    if file_path.name.startswith('20250822_'):
                        mtime = file_path.stat().st_mtime
                        recent_files.append((file_path, mtime))
                
                if recent_files:
                    # 가장 최근 파일
                    latest_file, latest_time = max(recent_files, key=lambda x: x[1])
                    
                    # 변경 감지
                    if agent not in self.last_sync or latest_time > self.last_sync[agent]:
                        self.last_sync[agent] = latest_time
                        self.update_agent_status(agent, latest_file)
            
            time.sleep(10)  # 10초마다 체크
    
    def update_agent_status(self, agent, file_path):
        """에이전트 상태 업데이트"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 상태 파싱
            status = "active"
            if "status: completed" in content:
                status = "completed"
            elif "status: in_progress" in content:
                status = "in_progress"
            elif "status: pending" in content:
                status = "pending"
            
            # 우선순위 파싱
            priority = "P2"
            if "priority: P0" in content:
                priority = "P0"
            elif "priority: P1" in content:
                priority = "P1"
            
            self.agent_status[agent] = {
                "status": status,
                "priority": priority,
                "file": file_path.name,
                "last_activity": datetime.now().strftime('%H:%M'),
                "updated": True
            }
            
            print(f"📝 {agent.upper()} 상태 업데이트: {status} ({priority})")
            
        except Exception as e:
            print(f"❌ {agent} 상태 업데이트 실패: {e}")
    
    def update_hub_realtime(self):
        """HUB_ENHANCED.md 실시간 업데이트"""
        while self.running:
            if any(agent.get('updated', False) for agent in self.agent_status.values()):
                self.sync_hub_file()
                # 업데이트 플래그 리셋
                for agent in self.agent_status:
                    self.agent_status[agent]['updated'] = False
            
            time.sleep(30)  # 30초마다 HUB 업데이트
    
    def sync_hub_file(self):
        """HUB_ENHANCED.md 파일 동기화"""
        try:
            if not HUB_FILE.exists():
                return
            
            content = HUB_FILE.read_text(encoding='utf-8')
            
            # 자동 상태 업데이트 섹션 찾기
            auto_section_start = "## 🤖 자동 상태 업데이트"
            auto_section_end = "## Active Tasks"
            
            start_idx = content.find(auto_section_start)
            if start_idx == -1:
                # 섹션이 없으면 추가
                active_tasks_idx = content.find("## Active Tasks")
                if active_tasks_idx != -1:
                    new_section = self.generate_auto_section()
                    content = content[:active_tasks_idx] + new_section + content[active_tasks_idx:]
            else:
                # 기존 섹션 업데이트
                end_idx = content.find(auto_section_end, start_idx)
                if end_idx != -1:
                    new_section = self.generate_auto_section()
                    content = content[:start_idx] + new_section + content[end_idx:]
            
            # 파일 저장
            HUB_FILE.write_text(content, encoding='utf-8')
            print(f"📋 HUB_ENHANCED.md 자동 업데이트 완료 ({datetime.now().strftime('%H:%M')})")
            
        except Exception as e:
            print(f"❌ HUB_ENHANCED.md 업데이트 실패: {e}")
    
    def generate_auto_section(self):
        """자동 상태 업데이트 섹션 생성"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        section = f"## 🤖 자동 상태 업데이트 (마지막 업데이트: {now})\n\n"
        section += "### 에이전트 활동 현황\n"
        
        for agent, info in self.agent_status.items():
            section += f"- **{agent.upper()}**: {info['status']} (마지막 활동: {info['last_activity']})\n"
            section += f"  └─ {info['file']} ({info['status']})\n"
        
        section += "\n"
        return section
    
    def check_conflicts(self):
        """작업 충돌 감지"""
        conflicts = []
        
        # P0 우선순위 작업이 여러 에이전트에 있는지 체크
        p0_agents = [agent for agent, info in self.agent_status.items() 
                    if info.get('priority') == 'P0' and info.get('status') in ['pending', 'in_progress']]
        
        if len(p0_agents) > 1:
            conflicts.append(f"P0 우선순위 충돌: {', '.join(p0_agents)}")
        
        # 같은 파일에 접근하는 작업 체크 (추후 구현)
        
        return conflicts
    
    def start_realtime_sync(self):
        """실시간 동기화 시작"""
        print(header("에이전트 실시간 동기화 시작"))
        print("Ctrl+C로 중단할 수 있습니다.")

        self.running = True
        try:
            record_event(task_name="realtime_agent_sync", event_type="start", command="start_realtime_sync")
        except Exception:
            pass
        
        # 백그라운드 스레드 시작
        file_watcher = threading.Thread(target=self.watch_agent_files)
        hub_updater = threading.Thread(target=self.update_hub_realtime)
        
        file_watcher.daemon = True
        hub_updater.daemon = True
        
        file_watcher.start()
        hub_updater.start()
        
        try:
            while True:
                conflicts = self.check_conflicts()
                if conflicts:
                    for conflict in conflicts:
                        print(status_line(1, "WARN", "충돌 감지", conflict))
                
                time.sleep(60)  # 1분마다 충돌 체크
                
        except KeyboardInterrupt:
            print("\n🛑 실시간 동기화를 중단합니다.")
            self.running = False
            try:
                record_event(task_name="realtime_agent_sync", event_type="stopped", command="start_realtime_sync")
            except Exception:
                pass

def main():
    """메인 실행"""
    import argparse
    parser = argparse.ArgumentParser(description='실시간 에이전트 동기화')
    parser.add_argument('--start', action='store_true', help='실시간 동기화 시작')
    parser.add_argument('--status', action='store_true', help='현재 상태 확인')
    
    args = parser.parse_args()
    
    sync = RealtimeAgentSync()
    
    if args.start:
        sync.start_realtime_sync()
    elif args.status:
        print(header("에이전트 상태 확인"))
        # 일회성 상태 체크
        agents = ['claude', 'codex', 'gemini']
        for agent in agents:
            agent_dir = AGENTS_DIR / agent
            if agent_dir.exists():
                files = list(agent_dir.glob('20250822_*.md'))
                print(kv(agent.upper(), f"{len(files)} 개 활성 파일"))
    else:
        # 한번만 동기화
        sync.sync_hub_file()
        try:
            record_event(task_name="realtime_agent_sync", event_type="one_shot", command="sync_hub_file")
        except Exception:
            pass

if __name__ == "__main__":
    main()
