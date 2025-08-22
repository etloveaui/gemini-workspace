#!/usr/bin/env python3
"""
스마트 디스패처 에이전트 v2.0 - 빠릿빠릿 버전
이전 실패를 교훈삼아 단순하고 확실한 방식으로 재설계
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from realtime_coordination import get_coordinator

class SmartDispatcher:
    """빠릿빠릿 작업 분배 시스템"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.coordinator = get_coordinator(root_path)
        self.task_queue = self.root / ".agents" / "task_queue.json"
        
        # 에이전트별 전문 분야
        self.agent_specialties = {
            "claude": ["system_management", "coordination", "documentation", "analysis"],
            "gemini": ["file_operations", "data_processing", "monitoring", "debugging"],
            "codex": ["coding", "testing", "optimization", "implementation"]
        }
        
        # 우선순위별 처리 시간 (분)
        self.priority_timeouts = {
            0: 30,   # P0: 30분
            1: 120,  # P1: 2시간 
            2: 480,  # P2: 8시간
            3: 1440  # P3: 24시간
        }
    
    def dispatch_task(self, task: Dict) -> str:
        """작업을 최적 에이전트에 할당"""
        
        # 1. 작업 유형 분석
        task_type = self._analyze_task_type(task)
        
        # 2. 적합한 에이전트 찾기
        suitable_agents = self._find_suitable_agents(task_type, task.get('priority', 2))
        
        # 3. 가장 적합한 에이전트 선택
        best_agent = self._select_best_agent(suitable_agents, task)
        
        # 4. 작업 할당
        if self._assign_task_to_agent(best_agent, task):
            return best_agent
        
        # 5. 실패 시 Claude가 처리 (총감독관)
        return "claude"
    
    def _analyze_task_type(self, task: Dict) -> str:
        """작업 유형 자동 분석"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        text = f"{title} {description}"
        
        # 키워드 기반 분류
        if any(keyword in text for keyword in ['test', 'pytest', 'debug', 'fix', 'error']):
            return "coding"
        elif any(keyword in text for keyword in ['file', 'folder', 'clean', 'organize']):
            return "file_operations"
        elif any(keyword in text for keyword in ['monitor', 'track', 'analyze', 'report']):
            return "monitoring"
        elif any(keyword in text for keyword in ['system', 'config', 'setup', 'install']):
            return "system_management"
        else:
            return "analysis"  # 기본값
    
    def _find_suitable_agents(self, task_type: str, priority: int) -> List[str]:
        """작업에 적합한 에이전트 목록 반환"""
        suitable = []
        
        for agent, specialties in self.agent_specialties.items():
            if task_type in specialties:
                # 에이전트 상태 확인
                status = self.coordinator.get_agent_status(agent)
                if status and len(status) > 0:
                    agent_info = status[0]
                    # 우선순위가 맞고 너무 바쁘지 않으면 추가
                    if (agent_info['priority'] >= priority and 
                        agent_info['status'] in ['idle', 'working']):
                        suitable.append(agent)
        
        return suitable if suitable else ["claude"]  # 기본값
    
    def _select_best_agent(self, candidates: List[str], task: Dict) -> str:
        """후보 중 최고 에이전트 선택"""
        if len(candidates) == 1:
            return candidates[0]
        
        # 점수 기반 선택
        scores = {}
        for agent in candidates:
            score = 0
            
            status = self.coordinator.get_agent_status(agent)
            if status and len(status) > 0:
                agent_info = status[0]
                
                # 상태별 점수
                if agent_info['status'] == 'idle':
                    score += 100
                elif agent_info['status'] == 'working':
                    score += 50
                
                # 우선순위 점수
                score += (4 - agent_info['priority']) * 10
                
                # 최근 활동 점수
                try:
                    last_beat = datetime.fromisoformat(agent_info['last_heartbeat'])
                    minutes_since = (datetime.now() - last_beat).total_seconds() / 60
                    if minutes_since < 5:
                        score += 30
                except:
                    pass
            
            scores[agent] = score
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _assign_task_to_agent(self, agent: str, task: Dict) -> bool:
        """에이전트에게 작업 할당"""
        
        # 통신 폴더에 작업 파일 생성
        comm_dir = self.root / "communication" / agent
        comm_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_file = comm_dir / f"{timestamp}_dispatched_task.md"
        
        # 작업 파일 내용 생성
        task_content = self._generate_task_content(task, agent)
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task_content)
            
            # 코디네이터에 상태 업데이트
            self.coordinator.register_agent(
                agent, 
                "assigned", 
                task.get('title', 'dispatched_task'),
                task.get('priority', 2)
            )
            
            return True
        except Exception as e:
            print(f"❌ 작업 할당 실패 ({agent}): {e}")
            return False
    
    def _generate_task_content(self, task: Dict, agent: str) -> str:
        """작업 파일 내용 생성"""
        priority_names = {0: "P0-긴급", 1: "P1-높음", 2: "P2-일반", 3: "P3-낮음"}
        priority = task.get('priority', 2)
        
        return f"""---
agent: {agent}
priority: {priority_names.get(priority, 'P2-일반')}
status: pending
created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
dispatched_by: SmartDispatcher
---

# 🤖 {agent.upper()} 자동 할당 작업

## 📋 작업 개요
- **작업명**: {task.get('title', '자동 할당된 작업')}
- **우선순위**: {priority_names.get(priority, 'P2-일반')}
- **할당 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **담당자**: {agent.capitalize()}

## 🎯 작업 상세

### 요청 내용
{task.get('description', '작업 설명이 제공되지 않았습니다.')}

### 배경 정보
- **자동 할당 이유**: {self._get_assignment_reason(agent, task)}
- **예상 소요시간**: {self.priority_timeouts.get(priority, 480)}분 이내
- **제약 조건**: 시스템 안정성 유지, 기존 기능 손상 금지

## 🚀 즉시 실행 지시사항

**SmartDispatcher의 명령**:
1. 이 파일을 확인하는 즉시 작업 시작
2. 우선순위 {priority_names.get(priority)} 작업임을 인지
3. 진행상황을 실시간으로 업데이트
4. 완료 시 결과를 communication 폴더에 보고

**⚡ 지금 바로 시작하세요!**

---

## 💬 {agent.upper()} 응답 구간

### [응답 시간] 작업 분석 및 계획

[{agent.capitalize()}의 분석 및 실행 계획을 여기에 작성]

### [완료 시간] ✅ 작업 완료

[최종 결과 및 산출물 요약을 여기에 작성]
"""
    
    def _get_assignment_reason(self, agent: str, task: Dict) -> str:
        """할당 이유 설명"""
        specialties = self.agent_specialties.get(agent, [])
        task_type = self._analyze_task_type(task)
        
        if task_type in specialties:
            return f"{agent.capitalize()}의 전문분야({task_type})와 일치"
        else:
            return f"{agent.capitalize()}이 현재 가장 적합한 상태"

# 편의 함수들
def quick_dispatch(title: str, description: str, priority: int = 2) -> str:
    """빠른 작업 할당"""
    dispatcher = SmartDispatcher("C:/Users/etlov/multi-agent-workspace")
    
    task = {
        "title": title,
        "description": description,
        "priority": priority,
        "created_at": datetime.now().isoformat()
    }
    
    assigned_agent = dispatcher.dispatch_task(task)
    print(f"✅ 작업 '{title}' → {assigned_agent.upper()}에게 할당됨")
    return assigned_agent

if __name__ == "__main__":
    # 테스트
    print("🤖 SmartDispatcher v2.0 테스트")
    
    # 테스트 작업들
    test_tasks = [
        {"title": "pytest 실패 수정", "description": "15개 실패 테스트 해결", "priority": 0},
        {"title": "폴더 정리", "description": "communication 폴더 정리", "priority": 1},
        {"title": "시스템 모니터링", "description": "토큰 사용량 추적", "priority": 2}
    ]
    
    dispatcher = SmartDispatcher("C:/Users/etlov/multi-agent-workspace")
    
    for task in test_tasks:
        agent = dispatcher.dispatch_task(task)
        print(f"📋 '{task['title']}' → {agent}")