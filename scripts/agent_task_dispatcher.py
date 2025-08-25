#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에이전트별 작업 배정 자동화 시스템
Claude (총사령관) -> Codex (구현) -> Gemini (분석) 자동 조율
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class AgentTaskDispatcher:
    """에이전트 작업 자동 배정 시스템"""
    
    def __init__(self):
        self.workspace = Path("C:/Users/eunta/multi-agent-workspace")
        self.agents = {
            "claude": {
                "role": "총사령관-실무형",
                "strengths": ["시스템 통합", "아키텍처 설계", "의사결정", "품질 관리"],
                "comm_folder": self.workspace / "communication" / "claude"
            },
            "codex": {
                "role": "구현 전문가",
                "strengths": ["코드 작성", "디버깅", "자동화 도구", "시스템 파일 수정"],
                "comm_folder": self.workspace / "communication" / "codex"
            },
            "gemini": {
                "role": "연구-분석가",
                "strengths": ["대량 데이터 분석", "패턴 인식", "문서 정리", "시스템 모니터링"],
                "comm_folder": self.workspace / "communication" / "gemini"
            }
        }
        
        # 사용자 개입 vs 자동화 영역 구분
        self.user_decision_areas = [
            "새로운 프로젝트 방향성",
            "중요한 아키텍처 변경", 
            "외부 시스템 연동",
            "보안 정책 변경",
            "예산/리소스 할당"
        ]
        
        self.automation_areas = [
            "파일 정리 및 아카이브",
            "경로 수정 및 통일",
            "코드 포맷팅 및 스타일",
            "문서 동기화",
            "로그 분석 및 보고",
            "성능 모니터링"
        ]
    
    def analyze_task_type(self, task_description: str) -> Dict:
        """작업 유형 분석 및 적합한 에이전트 결정"""
        
        # 키워드 기반 분류
        implementation_keywords = ["코드", "구현", "버그", "디버그", "스크립트", "자동화"]
        research_keywords = ["분석", "조사", "패턴", "데이터", "문서", "보고서"] 
        architecture_keywords = ["설계", "통합", "시스템", "아키텍처", "계획", "전략"]
        
        task_lower = task_description.lower()
        
        scores = {
            "claude": 0,
            "codex": 0,
            "gemini": 0
        }
        
        # 점수 계산
        for keyword in implementation_keywords:
            if keyword in task_lower:
                scores["codex"] += 2
        
        for keyword in research_keywords:
            if keyword in task_lower:
                scores["gemini"] += 2
                
        for keyword in architecture_keywords:
            if keyword in task_lower:
                scores["claude"] += 2
        
        # 복잡도 분석
        if any(word in task_lower for word in ["전체", "시스템", "모든", "통합"]):
            scores["claude"] += 3  # 총사령관 역할
        
        if any(word in task_lower for word in ["급히", "즉시", "빠르게"]):
            scores["codex"] += 1  # 구현이 빠름
            
        primary_agent = max(scores.items(), key=lambda x: x[1])[0]
        
        return {
            "primary_agent": primary_agent,
            "scores": scores,
            "task_type": self._categorize_task_type(task_description),
            "urgency": self._assess_urgency(task_description)
        }
    
    def _categorize_task_type(self, task: str) -> str:
        """작업 카테고리 분류"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["mcp", "통합", "시스템"]):
            return "system_integration"
        elif any(word in task_lower for word in ["정리", "아카이브", "폴더"]):
            return "maintenance"
        elif any(word in task_lower for word in ["분석", "보고서", "조사"]):
            return "analysis"
        elif any(word in task_lower for word in ["구현", "코드", "개발"]):
            return "development"
        else:
            return "general"
    
    def _assess_urgency(self, task: str) -> str:
        """긴급도 평가"""
        urgent_words = ["긴급", "급히", "즉시", "중요"]
        if any(word in task for word in urgent_words):
            return "high"
        elif any(word in task for word in ["빠르게", "우선"]):
            return "medium"
        else:
            return "low"
    
    def create_task_assignment(self, task_description: str, requestor: str = "사용자") -> Dict:
        """작업 배정 생성"""
        analysis = self.analyze_task_type(task_description)
        
        assignment = {
            "task_id": f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": task_description,
            "requestor": requestor,
            "created_at": datetime.now().isoformat(),
            "analysis": analysis,
            "assignments": self._create_agent_assignments(task_description, analysis),
            "user_approval_required": self._requires_user_approval(task_description)
        }
        
        return assignment
    
    def _create_agent_assignments(self, task: str, analysis: Dict) -> Dict:
        """에이전트별 세부 작업 배정"""
        primary = analysis["primary_agent"]
        task_type = analysis["task_type"]
        
        assignments = {}
        
        if task_type == "system_integration":
            assignments = {
                "claude": {
                    "role": "총괄 기획 및 조율",
                    "tasks": ["전체 시스템 설계", "에이전트간 작업 조율", "품질 검증"],
                    "priority": "P0"
                },
                "codex": {
                    "role": "핵심 구현",  
                    "tasks": ["스크립트 작성", "시스템 파일 수정", "자동화 구현"],
                    "priority": "P1"
                },
                "gemini": {
                    "role": "분석 및 모니터링",
                    "tasks": ["시스템 상태 분석", "성능 모니터링", "문제점 식별"],
                    "priority": "P2"
                }
            }
        
        elif task_type == "development":
            assignments = {
                "codex": {
                    "role": "주 개발자",
                    "tasks": ["코드 작성", "테스트 구현", "디버깅"],
                    "priority": "P0"
                },
                "claude": {
                    "role": "아키텍처 검토",
                    "tasks": ["설계 검토", "코드 리뷰", "통합 관리"],
                    "priority": "P1"  
                },
                "gemini": {
                    "role": "품질 분석",
                    "tasks": ["성능 분석", "사용 패턴 분석", "개선점 도출"],
                    "priority": "P2"
                }
            }
            
        elif task_type == "analysis":
            assignments = {
                "gemini": {
                    "role": "주 분석가", 
                    "tasks": ["데이터 수집", "패턴 분석", "보고서 작성"],
                    "priority": "P0"
                },
                "claude": {
                    "role": "결과 검토",
                    "tasks": ["분석 결과 검토", "의사결정 지원", "다음 단계 계획"],
                    "priority": "P1"
                },
                "codex": {
                    "role": "도구 개발",
                    "tasks": ["분석 도구 개발", "데이터 처리 자동화", "시각화 구현"],
                    "priority": "P2"
                }
            }
        
        else:  # general
            assignments[primary] = {
                "role": "주 담당자",
                "tasks": [task],
                "priority": "P0"
            }
        
        return assignments
    
    def _requires_user_approval(self, task: str) -> bool:
        """사용자 승인 필요 여부"""
        return any(area in task for area in self.user_decision_areas)
    
    def dispatch_task(self, task_description: str) -> str:
        """작업 배정 실행"""
        assignment = self.create_task_assignment(task_description)
        
        # Communication 폴더에 배정 문서 생성
        task_id = assignment["task_id"]
        
        for agent, details in assignment["assignments"].items():
            comm_file = self.agents[agent]["comm_folder"] / f"{task_id}_{agent}_assignment.md"
            
            content = f"""# 작업 배정: {assignment['description']}

## 기본 정보
- **Task ID**: {task_id}
- **요청자**: {assignment['requestor']}
- **생성 시간**: {assignment['created_at']}
- **긴급도**: {assignment['analysis']['urgency']}

## 당신의 역할: {details['role']}
**우선순위**: {details['priority']}

### 할당된 작업들:
"""
            for i, task in enumerate(details['tasks'], 1):
                content += f"{i}. {task}\n"
            
            content += f"""
### 다른 에이전트와의 협업:
"""
            for other_agent, other_details in assignment["assignments"].items():
                if other_agent != agent:
                    content += f"- **{other_agent.upper()}**: {other_details['role']} ({other_details['priority']})\n"
            
            content += f"""

### 진행 상황 보고:
작업 완료 후 `{task_id}_{agent}_report.md` 파일로 결과를 보고해주세요.

---
🤖 **자동 생성됨** - Claude Agent Task Dispatcher
"""
            
            # 폴더 생성 및 파일 작성
            comm_file.parent.mkdir(parents=True, exist_ok=True)
            with open(comm_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return f"✅ 작업 배정 완료: {task_id}\n📋 배정된 에이전트: {', '.join(assignment['assignments'].keys())}"

# 전역 인스턴스
dispatcher = AgentTaskDispatcher()

def dispatch_task_auto(task_description: str) -> str:
    """작업 자동 배정"""
    return dispatcher.dispatch_task(task_description)

def analyze_task_auto(task_description: str) -> Dict:
    """작업 분석"""
    return dispatcher.analyze_task_type(task_description)

if __name__ == "__main__":
    # 테스트
    test_tasks = [
        "MCP 자동 활용 시스템을 모든 Claude Code 작업에 통합해주세요",
        "communication 폴더의 모든 파일을 날짜별로 정리해주세요", 
        "시스템 성능 분석 보고서를 작성해주세요",
        "HUB 시스템의 버그를 찾아서 수정해주세요"
    ]
    
    print("=== 에이전트 작업 배정 시스템 테스트 ===")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. 작업: {task}")
        analysis = analyze_task_auto(task)
        print(f"   주 담당자: {analysis['primary_agent'].upper()}")
        print(f"   작업 유형: {analysis['task_type']}")
        print(f"   긴급도: {analysis['urgency']}")
        
        result = dispatch_task_auto(task)
        print(f"   결과: {result}")