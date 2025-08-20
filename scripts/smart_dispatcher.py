#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🎯 스마트 디스패처 v1.0 - 자연어 작업을 적절한 에이전트로 자동 라우팅"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.stdout.reconfigure(encoding='utf-8')

# 🧠 에이전트별 특화 키워드 (간단하고 효율적)
AGENT_PATTERNS = {
    'claude': {
        'keywords': [
            # 총괄 및 조율
            '총감독', '조율', '통합', '관리', '계획', '설계', '아키텍처',
            # 분석 및 문서화  
            '분석', '검토', '평가', '진단', '문서', '가이드', '매뉴얼',
            # 복잡한 작업
            '복잡한', '고도화', '시스템', '전략', '로드맵', '청사진'
        ],
        'anti_keywords': ['코딩', '프로그래밍', '버그', '함수'],
        'weight': 1.0,
        'description': '전략기획, 시스템설계, 문서화, 프로젝트 관리'
    },
    'codex': {
        'keywords': [
            # 코딩 관련
            '코딩', '프로그래밍', '함수', '클래스', '버그', '디버깅',
            '최적화', '성능', '알고리즘', 'api', '테스트', 'pytest',
            # 기술적 구현
            'python', 'javascript', 'git', '커밋', '리팩토링', '코드'
        ],
        'anti_keywords': ['문서', '가이드', '분석만'],
        'weight': 1.0,
        'description': '코딩, 디버깅, 성능최적화, 기술구현'
    },
    'gemini': {
        'keywords': [
            # 대량 작업
            '대량', '반복', '일괄', '정리', '변환', '수집',
            # 빠른 작업
            '빠른', '간단한', '목록', '정리', '아카이브', '폴더',
            # 데이터 처리
            '데이터', '파일', '검색', '찾기', '탐색', '스캔'
        ],
        'anti_keywords': ['복잡한', '설계', '아키텍처'],
        'weight': 1.0,
        'description': '대량처리, 파일정리, 데이터수집, 빠른작업'
    }
}

# 🎯 작업 유형별 우선순위 (비즈니스 로직)
TASK_PRIORITIES = {
    'urgent': ['긴급', '즉시', 'asap', '빨리', '문제', '오류', '실패'],
    'maintenance': ['정리', '청소', '아카이브', '삭제', '정비'],
    'development': ['개발', '구현', '추가', '생성', '만들기'],
    'analysis': ['분석', '검토', '조사', '파악', '확인']
}

class SmartDispatcher:
    """토큰 효율적인 스마트 디스패처"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.history_file = workspace_root / 'reports' / 'dispatcher_history.json'
        self.load_history()
    
    def load_history(self):
        """과거 디스패칭 기록 로드 (학습용)"""
        self.history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
    
    def save_history(self, task: str, selected_agent: str, confidence: float, reason: str):
        """디스패칭 결정 기록 저장"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'selected_agent': selected_agent,
            'confidence': confidence,
            'reason': reason
        }
        
        self.history.append(record)
        
        # 최근 100개만 유지 (메모리 효율성)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # 저장
        self.history_file.parent.mkdir(exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def analyze_task(self, task: str) -> Dict[str, float]:
        """작업 분석 - 각 에이전트별 적합도 점수 계산"""
        task_lower = task.lower()
        scores = {}
        
        for agent, pattern in AGENT_PATTERNS.items():
            score = 0.0
            
            # 긍정 키워드 점수
            for keyword in pattern['keywords']:
                if keyword in task_lower:
                    score += 1.0
            
            # 부정 키워드 점수 차감
            for anti_keyword in pattern['anti_keywords']:
                if anti_keyword in task_lower:
                    score -= 0.5
            
            # 가중치 적용
            score *= pattern['weight']
            
            # 정규화 (0-1 범위)
            scores[agent] = max(0, score)
        
        return scores
    
    def get_task_priority(self, task: str) -> str:
        """작업 우선순위 판단"""
        task_lower = task.lower()
        
        for priority, keywords in TASK_PRIORITIES.items():
            if any(keyword in task_lower for keyword in keywords):
                return priority
        
        return 'normal'
    
    def select_best_agent(self, task: str) -> Tuple[str, float, str]:
        """최적 에이전트 선택"""
        scores = self.analyze_task(task)
        
        # 최고 점수 에이전트 선택
        if not scores or all(score == 0 for score in scores.values()):
            # 모든 점수가 0이면 Claude가 총감독으로 처리
            return 'claude', 0.5, '기본값: 총감독관이 판단 필요'
        
        best_agent = max(scores, key=scores.get)
        best_score = scores[best_agent]
        confidence = min(best_score / 3.0, 1.0)  # 최대 신뢰도 제한
        
        # 이유 생성
        reasons = []
        pattern = AGENT_PATTERNS[best_agent]
        
        for keyword in pattern['keywords']:
            if keyword in task.lower():
                reasons.append(f"'{keyword}' 키워드 매치")
        
        if not reasons:
            reasons = ['기본 할당']
        
        reason = f"{pattern['description']} 특화 ({', '.join(reasons[:3])})"
        
        return best_agent, confidence, reason
    
    def dispatch(self, task: str, save_to_history: bool = True) -> Dict:
        """작업 디스패칭 실행"""
        agent, confidence, reason = self.select_best_agent(task)
        priority = self.get_task_priority(task)
        
        result = {
            'task': task,
            'selected_agent': agent,
            'confidence': confidence,
            'reason': reason,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'all_scores': self.analyze_task(task)
        }
        
        if save_to_history:
            self.save_history(task, agent, confidence, reason)
        
        return result

def main():
    """메인 디스패처 인터페이스"""
    workspace_root = Path(__file__).parent.parent
    dispatcher = SmartDispatcher(workspace_root)
    
    if len(sys.argv) < 2:
        print("🎯 스마트 디스패처 v1.0")
        print("사용법: python scripts/smart_dispatcher.py \"작업 내용\"")
        print("\n예시:")
        print("  python scripts/smart_dispatcher.py \"Python 코드 버그 수정\"")
        print("  python scripts/smart_dispatcher.py \"시스템 아키텍처 설계\"")
        print("  python scripts/smart_dispatcher.py \"대량 파일 정리\"")
        return
    
    task = " ".join(sys.argv[1:])
    result = dispatcher.dispatch(task)
    
    # 결과 출력
    print(f"🎯 작업: {result['task']}")
    print(f"🤖 선택된 에이전트: {result['selected_agent'].upper()}")
    print(f"📊 신뢰도: {result['confidence']:.1%}")
    print(f"💡 선택 이유: {result['reason']}")
    print(f"⚡ 우선순위: {result['priority']}")
    
    # 상세 점수 (디버깅용)
    if '--verbose' in sys.argv:
        print(f"\n📈 상세 점수:")
        for agent, score in result['all_scores'].items():
            print(f"  {agent}: {score:.1f}")
    
    # 실행 명령어 제안
    agent_commands = {
        'claude': f'claude.py "{task}"',
        'codex': f'ma.py codex "{task}"',  
        'gemini': f'ma.py gemini "{task}"'
    }
    
    print(f"\n🚀 실행 명령어:")
    print(f"  python {agent_commands.get(result['selected_agent'], 'claude.py')} ")

if __name__ == "__main__":
    main()