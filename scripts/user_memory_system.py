"""
사용자 요구사항 자동 기억 시스템
사용자가 한 번 말한 중요한 지시사항을 자동으로 기억하고 적용
"""
import json
import re
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line

ROOT = Path(__file__).resolve().parent.parent
MEMORY_FILE = ROOT / ".agents" / "user_memory.json"

class UserMemorySystem:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memory_file.parent.mkdir(exist_ok=True)
        self.memory = self.load_memory()
    
    def load_memory(self):
        """기억 데이터 로드"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.create_default_memory()
        return self.create_default_memory()
    
    def create_default_memory(self):
        """기본 메모리 구조 생성"""
        return {
            "user_preferences": {
                "work_style": "즉시 실행 중심, 계획보다 구현 우선",
                "naming_convention": "yyyymmdd_01_xxx 방식",
                "task_assignment": "Claude 작업 전에 다른 에이전트들 먼저 작업 배정",
                "documentation": "중요 결정사항은 즉시 HUB_ENHANCED.md, AGENTS.md, GEMINI.md 등록"
            },
            "repeated_instructions": {
                "구현의 의미": "모든 것이 실행 가능한 상태까지 완성",
                "작업 전달 방식": "사용자가 직접 전달, 자동 전달 아님",
                "걱정 해소": "실제 동작하는 결과물로 안심시키기"
            },
            "agent_coordination": {
                "priority_order": ["codex_easy_tasks", "gemini_research", "claude_implementation"],
                "communication_method": "파일 기반 비동기 시스템"
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def save_memory(self):
        """메모리 저장"""
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def add_user_preference(self, category, key, value):
        """사용자 선호도 추가/업데이트"""
        if category not in self.memory:
            self.memory[category] = {}
        self.memory[category][key] = value
        self.save_memory()
    
    def get_user_preference(self, category, key=None):
        """사용자 선호도 조회"""
        if key:
            return self.memory.get(category, {}).get(key)
        return self.memory.get(category, {})
    
    def analyze_user_input(self, user_input):
        """사용자 입력에서 중요한 패턴 추출"""
        patterns = {
            "urgency": ["빨리", "즉시", "재깍재깍", "바로"],
            "implementation": ["구현", "구축", "실행가능", "동작하는"],
            "worry": ["걱정", "불안", "문제", "실패"],
            "task_assignment": ["작업 시켜", "시키면", "배정"],
            "memory_request": ["기억", "알아서", "자동으로"]
        }
        
        found_patterns = {}
        for pattern_type, keywords in patterns.items():
            matches = []
            for keyword in keywords:
                if keyword in user_input:
                    matches.append(keyword)
            if matches:
                found_patterns[pattern_type] = matches
        
        return found_patterns
    
    def update_from_user_input(self, user_input):
        """사용자 입력으로부터 메모리 업데이트"""
        patterns = self.analyze_user_input(user_input)
        
        if "urgency" in patterns:
            self.add_user_preference("user_preferences", "response_speed", "즉시 반응 선호")
        
        if "implementation" in patterns:
            self.add_user_preference("repeated_instructions", "구현 강조", "실행 가능한 결과물 필수")
        
        if "worry" in patterns:
            self.add_user_preference("user_preferences", "reassurance_needed", "구체적 결과물로 안심시키기")
        
        if "task_assignment" in patterns:
            self.add_user_preference("agent_coordination", "assignment_preference", "사용자 직접 전달")
        
        if "memory_request" in patterns:
            self.add_user_preference("user_preferences", "auto_memory", "중요 지시사항 자동 기억")
    
    def get_work_guidelines(self):
        """현재 작업 가이드라인 반환"""
        return {
            "파일 네이밍": self.get_user_preference("user_preferences", "naming_convention"),
            "작업 스타일": self.get_user_preference("user_preferences", "work_style"),
            "우선순위": self.get_user_preference("agent_coordination", "priority_order"),
            "구현 정의": self.get_user_preference("repeated_instructions", "구현의 의미")
        }
    
    def display_memory_status(self):
        """현재 기억 상태 출력"""
        print(header("사용자 요구사항 기억 시스템"))
        
        guidelines = self.get_work_guidelines()
        for key, value in guidelines.items():
            if value:
                print(kv(key, value))
        
        print(status_line(1, "OK", "메모리 시스템", f"활성화됨 - {MEMORY_FILE.name}"))

def main():
    """메인 실행 함수"""
    import argparse
    parser = argparse.ArgumentParser(description='사용자 기억 시스템')
    parser.add_argument('--status', action='store_true', help='현재 상태 확인')
    parser.add_argument('--input', help='사용자 입력 분석')
    
    args = parser.parse_args()
    
    memory_system = UserMemorySystem()
    
    if args.status:
        memory_system.display_memory_status()
    elif args.input:
        memory_system.update_from_user_input(args.input)
        print("사용자 입력이 메모리에 반영되었습니다.")
    else:
        memory_system.display_memory_status()

if __name__ == "__main__":
    main()