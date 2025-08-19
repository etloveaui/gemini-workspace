#!/usr/bin/env python3
"""
멀티 에이전트 워크스페이스 관리자
- 동시실행 가능한 에이전트 관리
- 작업 큐 및 우선순위 시스템
- 충돌 방지 및 리소스 모니터링
"""

import json
import time
import psutil
import os
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class MultiAgentManager:
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.agents_dir = self.workspace / ".agents"
        self.locks_dir = self.agents_dir / "locks"
        self.queue_dir = self.agents_dir / "queue"
        self.config_file = self.agents_dir / "config.json"
        
        # 디렉토리 생성
        for dir_path in [self.locks_dir, self.queue_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.load_config()
        self.init_database()
        
    def load_config(self):
        """설정 파일 로드"""
        default_config = {
            "active": ["claude", "gemini", "codex"],
            "concurrent_limit": 3,
            "mcp": {
                "context7": {"enabled": True, "cache_duration": 3600}
            },
            "priority_system": {
                "auto_assign": True,
                "load_balancing": True
            },
            "monitoring": {"enabled": True, "interval": 1}
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """설정 파일 저장"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def init_database(self):
        """모니터링 데이터베이스 초기화"""
        db_path = self.workspace / "usage.db"
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # 에이전트 상태 테이블
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                cpu_percent REAL,
                memory_mb REAL,
                tasks_active INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 작업 이력 테이블
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                priority INTEGER,
                status TEXT NOT NULL,
                start_time DATETIME,
                end_time DATETIME,
                duration_seconds REAL
            )
        """)
        
        self.conn.commit()
    
    def acquire_lock(self, agent_name: str) -> bool:
        """에이전트 잠금 획득"""
        lock_file = self.locks_dir / f"{agent_name}.lock"
        
        if lock_file.exists():
            # 기존 잠금 파일의 타임스탬프 확인 (60초 타임아웃)
            if time.time() - lock_file.stat().st_mtime > 60:
                lock_file.unlink()  # 오래된 잠금 제거
            else:
                return False
        
        # 잠금 파일 생성
        lock_data = {
            "agent": agent_name,
            "pid": os.getpid(),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f)
        
        return True
    
    def release_lock(self, agent_name: str):
        """에이전트 잠금 해제"""
        lock_file = self.locks_dir / f"{agent_name}.lock"
        if lock_file.exists():
            lock_file.unlink()
    
    def add_task(self, task_id: str, priority: int = 2, 
                 agent: Optional[str] = None, data: Dict = None) -> bool:
        """작업 큐에 태스크 추가"""
        task_data = {
            "id": task_id,
            "priority": priority,
            "assigned_agent": agent,
            "created_at": datetime.now().isoformat(),
            "status": "queued",
            "data": data or {}
        }
        
        # 우선순위별 디렉토리 생성
        priority_dir = self.queue_dir / f"P{priority}"
        priority_dir.mkdir(exist_ok=True)
        
        task_file = priority_dir / f"{task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_next_task(self, agent_name: str) -> Optional[Dict]:
        """에이전트를 위한 다음 작업 가져오기"""
        # 우선순위 순으로 검색 (P0 → P1 → P2 → P3)
        for priority in range(4):
            priority_dir = self.queue_dir / f"P{priority}"
            if not priority_dir.exists():
                continue
            
            for task_file in priority_dir.glob("*.json"):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # 이미 할당된 작업이거나 완료된 작업 건너뛰기
                    if task_data.get("status") != "queued":
                        continue
                    
                    # 특정 에이전트 지정된 경우 확인
                    assigned_agent = task_data.get("assigned_agent")
                    if assigned_agent and assigned_agent != agent_name:
                        continue
                    
                    # 작업 할당
                    task_data["assigned_agent"] = agent_name
                    task_data["status"] = "running"
                    task_data["started_at"] = datetime.now().isoformat()
                    
                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, indent=2, ensure_ascii=False)
                    
                    return task_data
                    
                except (json.JSONDecodeError, IOError):
                    continue
        
        return None
    
    def complete_task(self, task_id: str, agent_name: str, 
                     success: bool = True, result: Dict = None):
        """작업 완료 처리"""
        # 모든 우선순위 디렉토리에서 태스크 파일 찾기
        for priority in range(4):
            priority_dir = self.queue_dir / f"P{priority}"
            task_file = priority_dir / f"{task_id}.json"
            
            if task_file.exists():
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                # 완료 상태 업데이트
                task_data["status"] = "completed" if success else "failed"
                task_data["completed_at"] = datetime.now().isoformat()
                task_data["result"] = result or {}
                
                # 완료된 작업은 archive로 이동
                archive_dir = self.agents_dir / "archive" / "completed"
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                archive_file = archive_dir / f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(task_data, f, indent=2, ensure_ascii=False)
                
                # 원본 파일 삭제
                task_file.unlink()
                
                # 데이터베이스에 기록
                self.log_task_completion(task_data)
                break
    
    def get_agent_status(self) -> Dict:
        """모든 에이전트 상태 조회"""
        status = {}
        
        for agent in self.config.get("active_agents", ["claude", "gemini", "codex"]):
            lock_file = self.locks_dir / f"{agent}.lock"
            is_active = lock_file.exists()
            
            # 활성 작업 수 계산
            active_tasks = 0
            for priority in range(4):
                priority_dir = self.queue_dir / f"P{priority}"
                if priority_dir.exists():
                    for task_file in priority_dir.glob("*.json"):
                        try:
                            with open(task_file, 'r') as f:
                                task_data = json.load(f)
                            if (task_data.get("assigned_agent") == agent and 
                                task_data.get("status") == "running"):
                                active_tasks += 1
                        except:
                            continue
            
            status[agent] = {
                "active": is_active,
                "tasks_active": active_tasks,
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_mb": psutil.virtual_memory().used / 1024 / 1024
            }
        
        return status
    
    def log_task_completion(self, task_data: Dict):
        """작업 완료를 데이터베이스에 기록"""
        start_time = task_data.get("started_at")
        end_time = task_data.get("completed_at")
        
        duration = 0
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
        
        self.conn.execute("""
            INSERT INTO task_history 
            (task_id, agent_name, priority, status, start_time, end_time, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data["id"],
            task_data.get("assigned_agent", "unknown"),
            task_data.get("priority", 2),
            task_data.get("status", "unknown"),
            start_time,
            end_time,
            duration
        ))
        self.conn.commit()
    
    def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        if not self.config.get("monitoring", {}).get("enabled", True):
            return
        
        def monitor_loop():
            while True:
                try:
                    # 에이전트 상태 모니터링
                    status = self.get_agent_status()
                    
                    for agent, info in status.items():
                        self.conn.execute("""
                            INSERT INTO agent_status 
                            (agent_name, status, cpu_percent, memory_mb, tasks_active)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            agent,
                            "active" if info["active"] else "idle",
                            info["cpu_percent"],
                            info["memory_mb"],
                            info["tasks_active"]
                        ))
                    
                    self.conn.commit()
                    
                    # 오래된 잠금 파일 정리
                    current_time = time.time()
                    for lock_file in self.locks_dir.glob("*.lock"):
                        if current_time - lock_file.stat().st_mtime > 300:  # 5분 타임아웃
                            lock_file.unlink()
                    
                    time.sleep(self.config.get("monitoring", {}).get("interval", 10))
                    
                except Exception as e:
                    print(f"모니터링 오류: {e}")
                    time.sleep(60)  # 오류 시 1분 대기
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def get_performance_stats(self, hours: int = 24) -> Dict:
        """성능 통계 조회"""
        cursor = self.conn.cursor()
        
        # 최근 N시간 동안의 통계
        cursor.execute("""
            SELECT 
                agent_name,
                COUNT(*) as task_count,
                AVG(duration_seconds) as avg_duration,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count
            FROM task_history 
            WHERE start_time > datetime('now', '-{} hours')
            GROUP BY agent_name
        """.format(hours))
        
        stats = {}
        for row in cursor.fetchall():
            agent, task_count, avg_duration, success_count = row
            stats[agent] = {
                "task_count": task_count,
                "avg_duration_seconds": avg_duration or 0,
                "success_rate": (success_count / task_count * 100) if task_count > 0 else 0
            }
        
        return stats

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    manager = MultiAgentManager()
    
    if len(sys.argv) < 2:
        print("사용법: python multi_agent_manager.py <command> [args...]")
        print("명령어:")
        print("  status          - 에이전트 상태 조회")
        print("  add-task <id>   - 작업 추가")
        print("  stats           - 성능 통계")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        status = manager.get_agent_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif command == "add-task":
        if len(sys.argv) < 3:
            print("사용법: add-task <task_id> [priority] [agent]")
            sys.exit(1)
        
        task_id = sys.argv[2]
        priority = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        agent = sys.argv[4] if len(sys.argv) > 4 else None
        
        manager.add_task(task_id, priority, agent)
        print(f"작업 {task_id} 추가됨 (우선순위: P{priority})")
    
    elif command == "stats":
        stats = manager.get_performance_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)