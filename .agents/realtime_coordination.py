#!/usr/bin/env python3
"""
실시간 에이전트 협업 시스템 v2.0
- 에이전트 간 실시간 상태 공유
- 작업 충돌 방지 메커니즘
- 우선순위 자동 조율
- 진행상황 실시간 모니터링
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
import sqlite3

class AgentCoordinator:
    """에이전트 간 실시간 협업 조율자"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.status_file = self.root / ".agents" / "realtime_status.json"
        self.conflict_db = self.root / ".agents" / "conflicts.db"
        self.lock_dir = self.root / ".agents" / "locks"
        
        # 디렉토리 생성
        self.status_file.parent.mkdir(exist_ok=True, parents=True)
        self.lock_dir.mkdir(exist_ok=True, parents=True)
        
        self._init_database()
        self._start_monitoring()
    
    def _init_database(self):
        """충돌 추적 데이터베이스 초기화"""
        with sqlite3.connect(self.conflict_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conflicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent1 TEXT NOT NULL,
                    agent2 TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    resolution TEXT,
                    resolved_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_status (
                    agent TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    current_task TEXT,
                    started_at TEXT,
                    last_heartbeat TEXT,
                    priority INTEGER DEFAULT 2
                )
            """)
    
    def register_agent(self, agent_name: str, status: str = "idle", task: str = None, priority: int = 2):
        """에이전트 등록 및 상태 업데이트"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.conflict_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agent_status 
                (agent, status, current_task, started_at, last_heartbeat, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (agent_name, status, task, timestamp, timestamp, priority))
        
        self._update_realtime_status()
        return True
    
    def request_resource_lock(self, agent_name: str, resource_path: str, priority: int = 2) -> bool:
        """리소스 잠금 요청 (충돌 방지)"""
        lock_file = self.lock_dir / f"{self._safe_filename(resource_path)}.lock"
        
        # 기존 잠금 확인
        if lock_file.exists():
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                # 잠금 만료 확인 (30분)
                lock_time = datetime.fromisoformat(lock_data['timestamp'])
                if datetime.now() - lock_time > timedelta(minutes=30):
                    lock_file.unlink()  # 만료된 잠금 제거
                else:
                    # 우선순위 비교
                    if priority <= lock_data.get('priority', 2):
                        self._log_conflict(agent_name, lock_data['agent'], resource_path)
                        return False
                    else:
                        # 높은 우선순위면 강제 해제
                        self._log_conflict(agent_name, lock_data['agent'], resource_path, "priority_override")
                        lock_file.unlink()
            except:
                lock_file.unlink()  # 손상된 잠금 파일 제거
        
        # 새 잠금 생성
        lock_data = {
            "agent": agent_name,
            "resource": resource_path,
            "timestamp": datetime.now().isoformat(),
            "priority": priority
        }
        
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f)
        
        return True
    
    def release_resource_lock(self, agent_name: str, resource_path: str):
        """리소스 잠금 해제"""
        lock_file = self.lock_dir / f"{self._safe_filename(resource_path)}.lock"
        
        if lock_file.exists():
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data['agent'] == agent_name:
                    lock_file.unlink()
                    return True
            except:
                lock_file.unlink()  # 손상된 파일 제거
        
        return False
    
    def get_agent_status(self, agent_name: str = None) -> Dict:
        """에이전트 상태 조회"""
        with sqlite3.connect(self.conflict_db) as conn:
            if agent_name:
                cursor = conn.execute(
                    "SELECT * FROM agent_status WHERE agent = ?", (agent_name,)
                )
            else:
                cursor = conn.execute("SELECT * FROM agent_status")
            
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in results]
    
    def suggest_task_assignment(self, task_priority: int, estimated_time: int) -> str:
        """최적 에이전트 추천"""
        agents_status = self.get_agent_status()
        
        # 우선순위별 에이전트 점수 계산
        scores = {}
        for agent in agents_status:
            score = 0
            
            # 상태별 점수
            if agent['status'] == 'idle':
                score += 100
            elif agent['status'] == 'working':
                score += 20
            elif agent['status'] == 'busy':
                score += 0
            
            # 최근 활동 점수
            if agent['last_heartbeat']:
                last_beat = datetime.fromisoformat(agent['last_heartbeat'])
                if datetime.now() - last_beat < timedelta(minutes=5):
                    score += 50
            
            # 우선순위 적합성
            if agent['priority'] <= task_priority:
                score += 30
            
            scores[agent['agent']] = score
        
        # 최고 점수 에이전트 반환
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "claude"  # 기본값
    
    def _log_conflict(self, agent1: str, agent2: str, resource: str, resolution: str = None):
        """충돌 기록"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.conflict_db) as conn:
            conn.execute("""
                INSERT INTO conflicts (timestamp, agent1, agent2, resource, resolution)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, agent1, agent2, resource, resolution))
    
    def _safe_filename(self, path: str) -> str:
        """파일명 안전화"""
        return path.replace("/", "_").replace("\\", "_").replace(":", "_")
    
    def _update_realtime_status(self):
        """실시간 상태 파일 업데이트"""
        status_data = {
            "last_updated": datetime.now().isoformat(),
            "agents": self.get_agent_status(),
            "active_locks": self._get_active_locks()
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def _get_active_locks(self) -> List[Dict]:
        """활성 잠금 목록"""
        locks = []
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                locks.append(lock_data)
            except:
                pass
        return locks
    
    def _start_monitoring(self):
        """백그라운드 모니터링 시작"""
        def monitor():
            while True:
                self._update_realtime_status()
                self._cleanup_expired_locks()
                time.sleep(30)  # 30초마다 업데이트
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _cleanup_expired_locks(self):
        """만료된 잠금 정리"""
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                lock_time = datetime.fromisoformat(lock_data['timestamp'])
                if datetime.now() - lock_time > timedelta(minutes=30):
                    lock_file.unlink()
            except:
                lock_file.unlink()

# 전역 인스턴스
coordinator = None

def get_coordinator(root_path: str = "C:/Users/eunta/multi-agent-workspace") -> AgentCoordinator:
    """싱글톤 코디네이터 인스턴스 반환"""
    global coordinator
    if coordinator is None:
        coordinator = AgentCoordinator(root_path)
    return coordinator

if __name__ == "__main__":
    # 테스트
    coord = get_coordinator()
    
    # Claude 등록
    coord.register_agent("claude", "working", "system_optimization", priority=0)
    
    # 리소스 잠금 테스트
    if coord.request_resource_lock("claude", "docs/CORE/HUB_ENHANCED.md", priority=0):
        print("✅ HUB_ENHANCED.md 잠금 성공")
    
    # 상태 확인
    status = coord.get_agent_status("claude")
    print(f"📊 Claude 상태: {status}")
    
    # 작업 추천
    recommended = coord.suggest_task_assignment(task_priority=1, estimated_time=60)
    print(f"🤖 추천 에이전트: {recommended}")