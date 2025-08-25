#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 개입 영역 명확 구분 시스템
자동화 가능 영역 vs 사용자 결정 필요 영역을 명확히 구분하고 관리
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import json
import re

# 인코딩 및 경로 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding
setup_utf8_encoding()

class UserInterventionSystem:
    """사용자 개입 영역 관리 시스템"""
    
    def __init__(self):
        self.workspace_root = Path("C:/Users/eunta/multi-agent-workspace")
        self.decisions_log = self.workspace_root / "cache" / "user_decisions.json"
        self.decisions_log.parent.mkdir(exist_ok=True)
        
        # 자동화 가능 영역 정의
        self.automation_areas = {
            "file_management": {
                "description": "파일 정리, 이동, 삭제, 백업",
                "confidence": "high",
                "examples": [
                    "Communication 폴더 정리",
                    "임시 파일 삭제", 
                    "Archive 이동",
                    "경로 통일 작업",
                    "파일명 표준화"
                ],
                "auto_approval": True
            },
            
            "system_integration": {
                "description": "새로운 도구/모듈의 기술적 통합",
                "confidence": "high", 
                "examples": [
                    "MCP 서버 자동 로드",
                    "스크립트 경로 추가",
                    "의존성 자동 설치",
                    "설정 파일 업데이트"
                ],
                "auto_approval": True
            },
            
            "code_maintenance": {
                "description": "코드 품질 및 유지보수",
                "confidence": "medium",
                "examples": [
                    "코드 포맷팅",
                    "주석 추가/수정",
                    "타입 힌트 추가",
                    "리팩토링 (기능 변경 없음)"
                ],
                "auto_approval": True
            },
            
            "monitoring_reporting": {
                "description": "시스템 모니터링 및 보고",
                "confidence": "high",
                "examples": [
                    "상태 체크",
                    "성능 모니터링",
                    "오류 로깅",
                    "사용량 추적"
                ],
                "auto_approval": True
            }
        }
        
        # 사용자 개입 필수 영역
        self.user_decision_areas = {
            "project_direction": {
                "description": "프로젝트 방향성 및 전략 결정",
                "confidence": "requires_user",
                "examples": [
                    "새로운 기능 추가 여부",
                    "아키텍처 대규모 변경",
                    "외부 서비스 연동",
                    "데이터 스키마 변경"
                ],
                "approval_required": True,
                "escalation_time": "immediate"
            },
            
            "security_privacy": {
                "description": "보안 및 개인정보 관련 결정",
                "confidence": "requires_user",
                "examples": [
                    "API 키 설정",
                    "민감 정보 처리 방식",
                    "접근 권한 변경",
                    "외부 통신 설정"
                ],
                "approval_required": True,
                "escalation_time": "immediate"
            },
            
            "resource_allocation": {
                "description": "리소스 사용 및 비용 관련 결정",
                "confidence": "requires_user",
                "examples": [
                    "대용량 다운로드",
                    "장시간 실행 작업",
                    "토큰 대량 사용",
                    "스토리지 확장"
                ],
                "approval_required": True,
                "escalation_time": "before_action"
            },
            
            "user_preference": {
                "description": "사용자 개인 취향 및 워크플로우",
                "confidence": "requires_user",
                "examples": [
                    "UI/UX 변경",
                    "개인화 설정",
                    "워크플로우 순서",
                    "알림 방식"
                ],
                "approval_required": True,
                "escalation_time": "when_convenient"
            }
        }
        
        # 기존 사용자 결정 로드
        self._load_previous_decisions()
    
    def _load_previous_decisions(self) -> None:
        """이전 사용자 결정사항 로드"""
        if self.decisions_log.exists():
            try:
                with open(self.decisions_log, 'r', encoding='utf-8') as f:
                    self.previous_decisions = json.load(f)
            except:
                self.previous_decisions = {}
        else:
            self.previous_decisions = {}
    
    def _save_decision(self, decision_data: Dict) -> None:
        """사용자 결정사항 저장"""
        decision_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{decision_data.get('category', 'unknown')}"
        self.previous_decisions[decision_id] = {
            **decision_data,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.decisions_log, 'w', encoding='utf-8') as f:
            json.dump(self.previous_decisions, f, indent=2, ensure_ascii=False)
    
    # === 작업 분류 및 승인 시스템 ===
    
    def classify_task_intervention_level(self, task_description: str) -> Dict[str, Any]:
        """작업의 사용자 개입 필요도 분류"""
        task_lower = task_description.lower()
        
        classification = {
            "task": task_description,
            "intervention_level": "unknown",
            "confidence": 0.0,
            "reasoning": [],
            "auto_approvable": False,
            "user_approval_required": False,
            "escalation_timing": "immediate"
        }
        
        # 자동화 가능 영역 체크
        automation_score = 0
        automation_matches = []
        
        for area_name, area_info in self.automation_areas.items():
            for keyword in area_info["examples"]:
                if any(word in task_lower for word in keyword.lower().split()):
                    automation_score += 1
                    automation_matches.append(f"{area_name}: {keyword}")
        
        # 사용자 개입 필수 영역 체크  
        intervention_score = 0
        intervention_matches = []
        
        for area_name, area_info in self.user_decision_areas.items():
            for keyword in area_info["examples"]:
                if any(word in task_lower for word in keyword.lower().split()):
                    intervention_score += 2  # 더 높은 가중치
                    intervention_matches.append(f"{area_name}: {keyword}")
        
        # 분류 결정
        if intervention_score > automation_score:
            classification.update({
                "intervention_level": "user_required",
                "confidence": min(intervention_score * 0.2, 1.0),
                "reasoning": intervention_matches,
                "auto_approvable": False,
                "user_approval_required": True
            })
        elif automation_score > 0:
            classification.update({
                "intervention_level": "automated",
                "confidence": min(automation_score * 0.3, 1.0),
                "reasoning": automation_matches,
                "auto_approvable": True,
                "user_approval_required": False
            })
        else:
            # 애매한 경우 - 사용자에게 문의
            classification.update({
                "intervention_level": "unclear",
                "confidence": 0.1,
                "reasoning": ["키워드 매칭 결과 없음"],
                "auto_approvable": False,
                "user_approval_required": True,
                "escalation_timing": "when_convenient"
            })
        
        return classification
    
    def check_previous_similar_decision(self, task_description: str) -> Optional[Dict]:
        """유사한 이전 결정 확인"""
        task_words = set(task_description.lower().split())
        
        best_match = None
        best_similarity = 0
        
        for decision_id, decision_data in self.previous_decisions.items():
            if "task" in decision_data:
                decision_words = set(decision_data["task"].lower().split())
                similarity = len(task_words & decision_words) / len(task_words | decision_words)
                
                if similarity > 0.5 and similarity > best_similarity:
                    best_match = decision_data
                    best_similarity = similarity
        
        return best_match
    
    # === 승인 요청 시스템 ===
    
    def request_user_approval(self, task_description: str, auto_execute: bool = False) -> Dict[str, Any]:
        """사용자 승인 요청"""
        classification = self.classify_task_intervention_level(task_description)
        
        # 이전 유사 결정 확인
        previous_decision = self.check_previous_similar_decision(task_description)
        
        approval_request = {
            "task": task_description,
            "classification": classification,
            "previous_decision": previous_decision,
            "timestamp": datetime.now().isoformat(),
            "auto_executed": False
        }
        
        # 자동 승인 가능한 경우
        if classification["auto_approvable"] and auto_execute:
            approval_request["status"] = "auto_approved"
            approval_request["auto_executed"] = True
            approval_request["reasoning"] = "자동화 가능 영역으로 분류됨"
            
        # 이전 결정 기반 자동 승인
        elif previous_decision and previous_decision.get("auto_approve_similar", False):
            approval_request["status"] = "auto_approved_by_precedent"
            approval_request["auto_executed"] = auto_execute
            approval_request["reasoning"] = f"이전 유사 결정 기반 ({previous_decision.get('timestamp', 'unknown')})"
            
        # 사용자 승인 필요
        else:
            approval_request["status"] = "user_approval_required"
            approval_request["approval_message"] = self._generate_approval_message(classification)
        
        return approval_request
    
    def _generate_approval_message(self, classification: Dict) -> str:
        """사용자 승인 요청 메시지 생성"""
        task = classification["task"]
        level = classification["intervention_level"]
        confidence = classification["confidence"]
        
        message = f"""
🤖 사용자 승인 요청

**작업**: {task}

**분류**: {level} (신뢰도: {confidence:.1%})
**추론**: {', '.join(classification['reasoning'][:3])}

**승인이 필요한 이유**:
{self._get_approval_reason(classification)}

**옵션**:
1. ✅ 승인하고 실행
2. ❌ 거부
3. 🔄 수정 후 재요청
4. ⚙️ 향후 유사 작업 자동 승인 설정

**회신**: 번호를 선택해 주세요.
"""
        return message.strip()
    
    def _get_approval_reason(self, classification: Dict) -> str:
        """승인이 필요한 이유 설명"""
        level = classification["intervention_level"]
        
        if level == "user_required":
            return "• 사용자 결정이 필요한 영역으로 분류됨\n• 시스템 설정이나 개인 선호도에 영향을 줄 수 있음"
        elif level == "unclear":
            return "• 자동/수동 분류가 명확하지 않음\n• 안전을 위해 사용자 확인 요청"
        else:
            return "• 예상치 못한 분류 결과\n• 시스템 오류 가능성"
    
    # === 자동화 규칙 학습 ===
    
    def learn_from_user_decision(self, task: str, user_choice: str, reasoning: str = "") -> None:
        """사용자 결정으로부터 학습"""
        decision_data = {
            "task": task,
            "user_choice": user_choice,
            "reasoning": reasoning,
            "classification": self.classify_task_intervention_level(task)
        }
        
        # 자동 승인 패턴 학습
        if user_choice == "approve_and_auto_future":
            decision_data["auto_approve_similar"] = True
            decision_data["learned_pattern"] = self._extract_decision_pattern(task)
        
        self._save_decision(decision_data)
    
    def _extract_decision_pattern(self, task: str) -> List[str]:
        """작업에서 결정 패턴 추출"""
        # 간단한 키워드 추출
        keywords = []
        task_lower = task.lower()
        
        # 동작 키워드
        actions = ["생성", "수정", "삭제", "이동", "정리", "통합", "업데이트"]
        for action in actions:
            if action in task_lower:
                keywords.append(f"action:{action}")
        
        # 대상 키워드
        targets = ["파일", "폴더", "스크립트", "시스템", "설정", "문서"]
        for target in targets:
            if target in task_lower:
                keywords.append(f"target:{target}")
        
        return keywords
    
    # === 시스템 상태 관리 ===
    
    def get_automation_status(self) -> Dict[str, Any]:
        """현재 자동화 상태 조회"""
        total_decisions = len(self.previous_decisions)
        auto_approved = sum(1 for d in self.previous_decisions.values() 
                          if d.get("user_choice") in ["approve", "approve_and_auto_future"])
        
        return {
            "total_decisions": total_decisions,
            "auto_approved_rate": auto_approved / total_decisions if total_decisions > 0 else 0,
            "automation_areas_count": len(self.automation_areas),
            "user_decision_areas_count": len(self.user_decision_areas),
            "learned_patterns": sum(1 for d in self.previous_decisions.values() 
                                  if d.get("auto_approve_similar", False))
        }
    
    def generate_automation_report(self) -> str:
        """자동화 상태 보고서 생성"""
        status = self.get_automation_status()
        
        report = f"""
🤖 사용자 개입 시스템 상태 보고서

## 자동화 현황
- **전체 결정**: {status['total_decisions']}건
- **자동 승인률**: {status['auto_approved_rate']:.1%}
- **학습된 패턴**: {status['learned_patterns']}개

## 영역별 분류
### ✅ 자동화 가능 영역 ({status['automation_areas_count']}개)
"""
        
        for area_name, area_info in self.automation_areas.items():
            report += f"- **{area_name}**: {area_info['description']}\n"
        
        report += f"\n### 🙋 사용자 개입 필요 영역 ({status['user_decision_areas_count']}개)\n"
        
        for area_name, area_info in self.user_decision_areas.items():
            report += f"- **{area_name}**: {area_info['description']}\n"
        
        report += "\n## 권장사항\n"
        
        if status['auto_approved_rate'] < 0.5:
            report += "• 자동 승인률이 낮습니다. 더 많은 작업을 자동화할 수 있는지 검토해보세요.\n"
        
        if status['learned_patterns'] < 5:
            report += "• 학습된 패턴이 적습니다. 반복 작업에 대해 '향후 자동 승인' 옵션을 활용해보세요.\n"
        
        return report

# 전역 인스턴스
intervention_system = UserInterventionSystem()

# 편의 함수들
def classify_task(task_description: str) -> Dict[str, Any]:
    """작업 분류"""
    return intervention_system.classify_task_intervention_level(task_description)

def request_approval(task_description: str, auto_execute: bool = False) -> Dict[str, Any]:
    """승인 요청"""
    return intervention_system.request_user_approval(task_description, auto_execute)

def learn_decision(task: str, choice: str, reasoning: str = "") -> None:
    """사용자 결정 학습"""
    return intervention_system.learn_from_user_decision(task, choice, reasoning)

def get_system_status() -> Dict[str, Any]:
    """시스템 상태"""
    return intervention_system.get_automation_status()

def generate_report() -> str:
    """보고서 생성"""
    return intervention_system.generate_automation_report()

if __name__ == "__main__":
    print("=== 사용자 개입 시스템 테스트 ===")
    
    # 테스트 작업들
    test_tasks = [
        "Communication 폴더의 오래된 파일들을 정리해주세요",
        "새로운 AI 모델을 프로젝트에 통합해주세요", 
        "사용자 데이터베이스 스키마를 변경해주세요",
        "코드 포맷팅을 자동으로 적용해주세요",
        "외부 API 키를 설정해주세요"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. 작업: {task}")
        classification = classify_task(task)
        print(f"   분류: {classification['intervention_level']} (신뢰도: {classification['confidence']:.1%})")
        print(f"   자동 승인: {'가능' if classification['auto_approvable'] else '불가'}")
    
    print(f"\n{generate_report()}")
    
    print("\n✅ 사용자 개입 시스템 준비 완료")