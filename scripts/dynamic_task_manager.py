#!/usr/bin/env python3
"""
동적 작업 추가 시스템
- 작업 진행 중에 새로운 요청사항을 자연스럽게 추가
- 기존 작업을 중단하지 않고 부가적으로 통합
- 우선순위 자동 조정 및 의존성 관리
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid

@dataclass
class TaskRequest:
    """작업 요청 데이터 클래스"""
    id: str
    title: str
    description: str
    priority: str  # "urgent", "high", "medium", "low"
    category: str  # "addition", "modification", "clarification"
    dependencies: List[str]  # 의존 작업 ID들
    estimated_effort: str  # "quick", "medium", "complex"
    context: str  # 추가 컨텍스트
    created_at: str
    status: str  # "pending", "integrated", "completed", "rejected"
    integration_notes: str = ""

class DynamicTaskManager:
    """동적 작업 관리자"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.requests_file = self.workspace_path / "scratchpad" / "dynamic_requests.jsonl"
        self.integration_log = self.workspace_path / "scratchpad" / "task_integration_log.md"
        self.active_session_file = self.workspace_path / "scratchpad" / "active_session.json"
        
        self.ensure_files()
    
    def ensure_files(self):
        """필요한 파일들 생성"""
        self.requests_file.parent.mkdir(exist_ok=True)
        
        if not self.requests_file.exists():
            self.requests_file.touch()
        
        if not self.integration_log.exists():
            self.create_initial_log()
    
    def create_initial_log(self):
        """초기 통합 로그 생성"""
        content = """# 동적 작업 통합 로그

이 파일은 진행 중인 작업에 추가된 새로운 요청사항들과 통합 과정을 기록합니다.

## 사용법
1. 작업 중 새로운 요청이 있으면 `scratchpad/`에 txt 또는 md 파일로 작성
2. 시스템이 자동으로 감지하여 기존 작업 계획에 통합
3. 우선순위와 의존성을 고려하여 실행 순서 조정

---

"""
        with open(self.integration_log, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def add_request(self, title: str, description: str, priority: str = "medium", 
                   category: str = "addition", context: str = "") -> str:
        """새로운 요청 추가"""
        
        request = TaskRequest(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            priority=priority,
            category=category,
            dependencies=[],
            estimated_effort=self._estimate_effort(description),
            context=context,
            created_at=datetime.now().isoformat(),
            status="pending"
        )
        
        # JSONL 형식으로 저장
        with open(self.requests_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(request), ensure_ascii=False) + '\n')
        
        # 로그에 기록
        self._log_new_request(request)
        
        return request.id
    
    def _estimate_effort(self, description: str) -> str:
        """작업 복잡도 추정"""
        description_lower = description.lower()
        
        # 복잡한 작업 키워드
        complex_keywords = [
            'architecture', 'design', 'refactor', 'migrate', 'implement',
            'integrate', 'system', 'framework', 'algorithm'
        ]
        
        # 빠른 작업 키워드
        quick_keywords = [
            'fix', 'update', 'change', 'add', 'remove', 'modify',
            'adjust', 'correct', 'simple', 'quick'
        ]
        
        if any(keyword in description_lower for keyword in complex_keywords):
            return "complex"
        elif any(keyword in description_lower for keyword in quick_keywords):
            return "quick"
        else:
            return "medium"
    
    def _log_new_request(self, request: TaskRequest):
        """새 요청을 로그에 기록"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
## 🆕 새 요청 추가 ({timestamp})

**ID**: `{request.id}`  
**제목**: {request.title}  
**우선순위**: {request.priority}  
**카테고리**: {request.category}  
**예상 복잡도**: {request.estimated_effort}  

**설명**:
{request.description}

**컨텍스트**:
{request.context if request.context else "없음"}

**상태**: {request.status}

---
"""
        
        with open(self.integration_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_pending_requests(self) -> List[TaskRequest]:
        """대기 중인 요청들 조회"""
        if not self.requests_file.exists():
            return []
        
        requests = []
        with open(self.requests_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        request = TaskRequest(**data)
                        if request.status == "pending":
                            requests.append(request)
                    except (json.JSONDecodeError, TypeError) as e:
                        continue
        
        return sorted(requests, key=lambda x: self._priority_score(x.priority), reverse=True)
    
    def _priority_score(self, priority: str) -> int:
        """우선순위 점수 계산"""
        scores = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(priority, 2)
    
    def integrate_request(self, request_id: str, integration_plan: str) -> bool:
        """요청을 기존 작업에 통합"""
        request = self._find_request(request_id)
        if not request:
            return False
        
        # 요청 상태 업데이트
        self._update_request_status(request_id, "integrated", integration_plan)
        
        # 통합 계획을 로그에 기록
        self._log_integration(request, integration_plan)
        
        return True
    
    def _find_request(self, request_id: str) -> Optional[TaskRequest]:
        """요청 ID로 요청 찾기"""
        if not self.requests_file.exists():
            return None
        
        with open(self.requests_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        if data.get('id') == request_id:
                            return TaskRequest(**data)
                    except (json.JSONDecodeError, TypeError):
                        continue
        return None
    
    def _update_request_status(self, request_id: str, status: str, notes: str = ""):
        """요청 상태 업데이트"""
        if not self.requests_file.exists():
            return
        
        lines = []
        with open(self.requests_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(self.requests_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        if data.get('id') == request_id:
                            data['status'] = status
                            data['integration_notes'] = notes
                        f.write(json.dumps(data, ensure_ascii=False) + '\n')
                    except (json.JSONDecodeError, TypeError):
                        f.write(line)
    
    def _log_integration(self, request: TaskRequest, integration_plan: str):
        """통합 과정을 로그에 기록"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
## ✅ 요청 통합 완료 ({timestamp})

**요청 ID**: `{request.id}`  
**제목**: {request.title}  

**통합 계획**:
{integration_plan}

**통합 후 상태**: {request.status}

---
"""
        
        with open(self.integration_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def scan_scratchpad_for_requests(self) -> List[str]:
        """scratchpad에서 새로운 요청 파일 스캔"""
        scratchpad_path = self.workspace_path / "scratchpad"
        new_requests = []
        
        # 최근 1시간 내 생성된 txt, md 파일 찾기
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        for file_path in scratchpad_path.glob("**/*.txt"):
            if file_path.stat().st_mtime > cutoff_time.timestamp():
                # 파일명에 특정 패턴이 있는지 확인
                if any(pattern in file_path.name.lower() for pattern in 
                      ['request', 'todo', 'task', 'additional', 'new', 'forclaude']):
                    new_requests.append(str(file_path))
        
        for file_path in scratchpad_path.glob("**/*.md"):
            if file_path.stat().st_mtime > cutoff_time.timestamp():
                if any(pattern in file_path.name.lower() for pattern in 
                      ['request', 'todo', 'task', 'additional', 'new']):
                    new_requests.append(str(file_path))
        
        return new_requests
    
    def process_file_request(self, file_path: str) -> Optional[str]:
        """파일에서 요청 내용 파싱하여 추가"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 파일명에서 제목 추출
            filename = Path(file_path).stem
            title = f"파일 요청: {filename}"
            
            # 우선순위 추정 (파일 내용 기반)
            priority = self._estimate_priority(content)
            
            # 카테고리 추정
            category = self._estimate_category(content, filename)
            
            return self.add_request(
                title=title,
                description=content[:1000],  # 처음 1000자만
                priority=priority,
                category=category,
                context=f"파일 경로: {file_path}"
            )
            
        except Exception as e:
            print(f"파일 처리 오류 ({file_path}): {e}")
            return None
    
    def _estimate_priority(self, content: str) -> str:
        """내용 기반 우선순위 추정"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['urgent', '긴급', 'critical', 'asap']):
            return "urgent"
        elif any(word in content_lower for word in ['important', '중요', 'high', '우선']):
            return "high"
        elif any(word in content_lower for word in ['later', '나중', 'low', '낮은']):
            return "low"
        else:
            return "medium"
    
    def _estimate_category(self, content: str, filename: str) -> str:
        """내용 기반 카테고리 추정"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        if any(word in content_lower + filename_lower for word in 
              ['clarify', '설명', 'explain', 'question', '질문']):
            return "clarification"
        elif any(word in content_lower + filename_lower for word in 
                ['modify', '수정', 'change', 'update', 'fix']):
            return "modification"
        else:
            return "addition"
    
    def generate_integration_report(self) -> str:
        """통합 가능한 요청들의 보고서 생성"""
        pending_requests = self.get_pending_requests()
        
        if not pending_requests:
            return "현재 대기 중인 요청이 없습니다."
        
        report = f"""# 🔄 동적 작업 통합 보고서

**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**대기 중인 요청**: {len(pending_requests)}개

## 📋 요청 목록 (우선순위순)

"""
        
        for i, request in enumerate(pending_requests, 1):
            effort_emoji = {"quick": "⚡", "medium": "🔧", "complex": "🏗️"}
            priority_emoji = {"urgent": "🚨", "high": "❗", "medium": "➡️", "low": "💤"}
            
            report += f"""### {i}. {request.title}

- **ID**: `{request.id}`
- **우선순위**: {priority_emoji.get(request.priority, '➡️')} {request.priority}
- **복잡도**: {effort_emoji.get(request.estimated_effort, '🔧')} {request.estimated_effort}
- **카테고리**: {request.category}
- **생성 시각**: {request.created_at}

**설명**: {request.description[:200]}{'...' if len(request.description) > 200 else ''}

"""
        
        report += """
## 🎯 권장 통합 전략

1. **긴급(urgent)** 요청들을 현재 작업에 즉시 통합
2. **빠른(quick)** 작업들을 우선적으로 처리
3. **복잡한(complex)** 작업들은 별도 계획 수립 후 통합
4. **설명(clarification)** 요청들은 현재 작업 맥락에서 즉시 해결

---
*이 보고서는 동적 작업 관리 시스템에 의해 자동 생성되었습니다.*
"""
        
        return report

# CLI 실행을 위한 메인 함수
if __name__ == "__main__":
    import sys
    
    manager = DynamicTaskManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            # 새로운 요청 파일 스캔
            new_files = manager.scan_scratchpad_for_requests()
            if new_files:
                print(f"🔍 새로운 요청 파일 {len(new_files)}개 발견:")
                for file_path in new_files:
                    request_id = manager.process_file_request(file_path)
                    if request_id:
                        print(f"✅ {file_path} → 요청 ID: {request_id}")
                    else:
                        print(f"❌ {file_path} → 처리 실패")
            else:
                print("📭 새로운 요청 파일이 없습니다.")
        
        elif command == "list":
            # 대기 중인 요청 목록
            requests = manager.get_pending_requests()
            if requests:
                print(f"📋 대기 중인 요청 {len(requests)}개:")
                for request in requests:
                    print(f"- [{request.priority}] {request.title} (ID: {request.id})")
            else:
                print("📭 대기 중인 요청이 없습니다.")
        
        elif command == "report":
            # 통합 보고서 생성
            report = manager.generate_integration_report()
            print(report)
        
        elif command == "add" and len(sys.argv) > 3:
            # 수동으로 요청 추가
            title = sys.argv[2]
            description = sys.argv[3]
            priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
            
            request_id = manager.add_request(title, description, priority)
            print(f"✅ 새 요청 추가됨: {title} (ID: {request_id})")
        
        else:
            print("사용법: python dynamic_task_manager.py [scan|list|report|add <title> <description> [priority]]")
    else:
        # 기본: 보고서 출력
        report = manager.generate_integration_report()
        print(report)