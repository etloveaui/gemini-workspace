#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
멀티 에이전트 협업 시스템 v2.0
Context7 MCP와 기존 communication 폴더를 연결하는 실제 작동 시스템

핵심 개념:
- 파일 기반 협업: 각 에이전트는 communication/ 폴더를 통해 소통
- Context7 MCP 활용: 실시간 정보 검색 및 캐싱
- 실제 테스트 검증: 모든 기능을 실제 테스트 후 구현
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import shutil

# Context7 MCP 임포트
import sys
sys.path.append(str(Path(__file__).parent.parent / ".agents"))
from context7_mcp import Context7MCP

class AgentCollaborator:
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.comm_dir = self.workspace / "communication"
        
        # Context7 MCP 초기화
        self.context7 = Context7MCP(workspace_path)
        
        # 에이전트 정보
        self.agents = {
            "claude": {
                "name": "Claude",
                "role": "총감독관",
                "capabilities": ["코드분석", "시스템설계", "품질관리"],
                "folder": self.comm_dir / "claude"
            },
            "gemini": {
                "name": "Gemini", 
                "role": "대량작업전문가",
                "capabilities": ["데이터분석", "일괄처리", "보고서생성"],
                "folder": self.comm_dir / "gemini"
            },
            "codex": {
                "name": "Codex",
                "role": "개발전문가", 
                "capabilities": ["코드생성", "디버깅", "테스트작성"],
                "folder": self.comm_dir / "codex"
            }
        }
        
        self.init_collaboration_system()
    
    def init_collaboration_system(self):
        """협업 시스템 초기화"""
        # communication 폴더 구조 확인/생성
        for agent_id, agent_info in self.agents.items():
            agent_folder = agent_info["folder"]
            agent_folder.mkdir(parents=True, exist_ok=True)
            
            # 각 에이전트별 하위 폴더
            (agent_folder / "tasks").mkdir(exist_ok=True)
            (agent_folder / "reports").mkdir(exist_ok=True)
            (agent_folder / "archive").mkdir(exist_ok=True)
        
        # 공유 폴더
        shared_folder = self.comm_dir / "shared"
        shared_folder.mkdir(exist_ok=True)
        (shared_folder / "handoffs").mkdir(exist_ok=True)
        (shared_folder / "resources").mkdir(exist_ok=True)
    
    def create_task_request(self, target_agent: str, task_info: Dict) -> str:
        """다른 에이전트에게 작업 요청 파일 생성"""
        if target_agent not in self.agents:
            raise ValueError(f"Unknown agent: {target_agent}")
        
        # 작업 ID 생성
        task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(task_info['title'].encode()).hexdigest()[:8]}"
        
        # 작업 요청 파일 내용
        task_content = {
            "task_id": task_id,
            "from_agent": "claude",  # Claude가 요청하는 경우
            "to_agent": target_agent,
            "created_at": datetime.now().isoformat(),
            "priority": task_info.get("priority", "P2"),
            "status": "pending",
            "title": task_info["title"],
            "description": task_info.get("description", ""),
            "requirements": task_info.get("requirements", []),
            "expected_output": task_info.get("expected_output", ""),
            "deadline": task_info.get("deadline", ""),
            "context": task_info.get("context", {}),
            "resources": task_info.get("resources", [])
        }
        
        # 파일 생성
        task_file = self.agents[target_agent]["folder"] / "tasks" / f"{task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_content, f, indent=2, ensure_ascii=False)
        
        # 알림 파일 생성 (실제 에이전트가 확인할 수 있도록)
        notification_file = self.agents[target_agent]["folder"] / f"NEW_TASK_{task_id}.md"
        notification_content = f"""---
agent: {target_agent}
priority: {task_content['priority']}
status: pending
created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
task_id: {task_id}
---

# 🚀 새로운 작업 요청

## 📋 작업 개요
- **작업명**: {task_content['title']}
- **요청자**: Claude (총감독관)
- **우선순위**: {task_content['priority']}
- **마감일**: {task_content.get('deadline', '미정')}

## 🎯 작업 상세
{task_content['description']}

## 📋 요구사항
{chr(10).join([f'- {req}' for req in task_content['requirements']])}

## 📊 기대 결과
{task_content['expected_output']}

## 📁 관련 파일
- 상세 정보: `tasks/{task_id}.json`

---

**💡 작업 시작 시**: 이 파일을 `archive/` 폴더로 이동하고 작업을 진행해주세요.
"""
        
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(notification_content)
        
        return task_id
    
    def check_task_status(self, task_id: str, agent: str) -> Dict:
        """작업 상태 확인"""
        task_file = self.agents[agent]["folder"] / "tasks" / f"{task_id}.json"
        
        if not task_file.exists():
            return {"status": "not_found", "message": f"Task {task_id} not found"}
        
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
        
        return {
            "status": "found",
            "task": task_data,
            "last_updated": datetime.fromtimestamp(task_file.stat().st_mtime).isoformat()
        }
    
    def get_pending_tasks(self, agent: str) -> List[Dict]:
        """대기 중인 작업 목록 조회"""
        agent_folder = self.agents[agent]["folder"]
        tasks = []
        
        # NEW_TASK_ 알림 파일들 확인
        for notification_file in agent_folder.glob("NEW_TASK_*.md"):
            task_id = notification_file.stem.replace("NEW_TASK_", "")
            task_file = agent_folder / "tasks" / f"{task_id}.json"
            
            if task_file.exists():
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                    tasks.append(task_data)
        
        return sorted(tasks, key=lambda x: x['created_at'], reverse=True)
    
    def create_handoff_document(self, from_agent: str, to_agent: str, 
                              work_summary: str, files: List[str] = None) -> str:
        """작업 인계 문서 생성"""
        handoff_id = f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        handoff_content = f"""# 작업 인계 문서
        
## 📋 인계 정보
- **인계자**: {self.agents[from_agent]['name']} ({from_agent})
- **인수자**: {self.agents[to_agent]['name']} ({to_agent})
- **일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **인계 ID**: {handoff_id}

## 📝 작업 요약
{work_summary}

## 📁 관련 파일
{chr(10).join([f'- `{file}`' for file in (files or [])])}

## ✅ 인계 체크리스트
- [ ] 작업 파일 확인
- [ ] 문서 검토
- [ ] 테스트 실행
- [ ] 품질 검증

## 💬 추가 메모
[인수자가 작성할 내용]

---
**🚨 중요**: 인수 확인 후 이 문서를 `{to_agent}/reports/` 폴더로 이동해주세요.
"""
        
        handoff_file = self.comm_dir / "shared" / "handoffs" / f"{handoff_id}.md"
        with open(handoff_file, 'w', encoding='utf-8') as f:
            f.write(handoff_content)
        
        return handoff_id
    
    def search_with_context7(self, query: str, library: str = None) -> Dict:
        """Context7 MCP를 활용한 정보 검색"""
        if library:
            # 특정 라이브러리 문서 검색
            result = self.context7.search_documentation(library, query)
        else:
            # 일반 검색
            result = self.context7.query_context("development", query)
        
        return result
    
    def enhance_task_with_context7(self, task_info: Dict) -> Dict:
        """Context7를 활용하여 작업 정보 보강"""
        enhanced_task = task_info.copy()
        
        # 작업 제목에서 기술 키워드 추출
        title = task_info.get("title", "").lower()
        
        # 관련 기술 정보 검색
        if any(keyword in title for keyword in ["python", "requests", "pandas", "numpy"]):
            for keyword in ["python", "requests", "pandas", "numpy"]:
                if keyword in title:
                    context_info = self.search_with_context7("best practices", keyword)
                    enhanced_task["context7_suggestions"] = context_info
                    break
        
        # 코드 예제 추가
        if "개발" in title or "코드" in title:
            examples = self.context7.get_code_examples("python")
            if examples:
                enhanced_task["code_examples"] = examples[:3]  # 최대 3개
        
        return enhanced_task
    
    def generate_collaboration_report(self) -> Dict:
        """협업 현황 보고서 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        for agent_id, agent_info in self.agents.items():
            agent_folder = agent_info["folder"]
            
            # 대기 중인 작업 수
            pending_tasks = len(list(agent_folder.glob("NEW_TASK_*.md")))
            
            # 완료된 작업 수 (archive 폴더 확인)
            completed_tasks = len(list((agent_folder / "archive").glob("*")))
            
            # 보고서 수
            reports = len(list((agent_folder / "reports").glob("*.md")))
            
            report["agents"][agent_id] = {
                "name": agent_info["name"],
                "role": agent_info["role"],
                "pending_tasks": pending_tasks,
                "completed_tasks": completed_tasks,
                "reports": reports,
                "last_activity": self._get_last_activity(agent_folder)
            }
        
        # Context7 통계 추가
        context7_stats = self.context7.get_statistics()
        report["context7_stats"] = context7_stats
        
        return report
    
    def _get_last_activity(self, agent_folder: Path) -> str:
        """에이전트의 마지막 활동 시간 조회"""
        try:
            files = list(agent_folder.rglob("*"))
            if not files:
                return "활동 없음"
            
            latest_file = max(files, key=lambda f: f.stat().st_mtime if f.is_file() else 0)
            if latest_file.is_file():
                return datetime.fromtimestamp(latest_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            return "활동 없음"
        except:
            return "확인 불가"

# CLI 인터페이스
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="멀티 에이전트 협업 시스템")
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")
    
    # 작업 요청 명령어
    task_parser = subparsers.add_parser("request", help="작업 요청")
    task_parser.add_argument("agent", choices=["gemini", "codex"], help="대상 에이전트")
    task_parser.add_argument("title", help="작업 제목")
    task_parser.add_argument("--priority", choices=["P0", "P1", "P2", "P3"], default="P2")
    task_parser.add_argument("--description", help="작업 설명")
    
    # 상태 확인 명령어
    status_parser = subparsers.add_parser("status", help="상태 확인")
    status_parser.add_argument("--agent", choices=["claude", "gemini", "codex"], help="특정 에이전트")
    
    # 보고서 생성 명령어
    report_parser = subparsers.add_parser("report", help="협업 보고서 생성")
    
    # Context7 검색 명령어
    search_parser = subparsers.add_parser("search", help="Context7 검색")
    search_parser.add_argument("query", help="검색 쿼리")
    search_parser.add_argument("--library", help="라이브러리 이름")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    collaborator = AgentCollaborator()
    
    if args.command == "request":
        task_info = {
            "title": args.title,
            "priority": args.priority,
            "description": args.description or ""
        }
        
        # Context7로 작업 정보 보강
        enhanced_task = collaborator.enhance_task_with_context7(task_info)
        
        task_id = collaborator.create_task_request(args.agent, enhanced_task)
        print(f"[성공] 작업 요청 생성: {task_id}")
        print(f"[파일위치] communication/{args.agent}/NEW_TASK_{task_id}.md")
    
    elif args.command == "status":
        if args.agent:
            tasks = collaborator.get_pending_tasks(args.agent)
            print(f"\n[작업현황] {args.agent} 대기 중인 작업: {len(tasks)}개")
            for task in tasks:
                print(f"  - [{task['priority']}] {task['title']} ({task['created_at'][:10]})")
        else:
            report = collaborator.generate_collaboration_report()
            print("\n[시스템현황] 멀티 에이전트 현황")
            print(f"[보고서생성] {report['timestamp'][:19]}")
            
            for agent_id, stats in report["agents"].items():
                print(f"\n{stats['name']} ({agent_id}):")
                print(f"  - 역할: {stats['role']}")
                print(f"  - 대기 작업: {stats['pending_tasks']}개")
                print(f"  - 완료 작업: {stats['completed_tasks']}개")
                print(f"  - 보고서: {stats['reports']}개")
                print(f"  - 마지막 활동: {stats['last_activity']}")
    
    elif args.command == "report":
        report = collaborator.generate_collaboration_report()
        
        # 보고서 파일 저장
        report_file = Path("communication/shared/collaboration_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[성공] 협업 보고서 생성: {report_file}")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.command == "search":
        result = collaborator.search_with_context7(args.query, args.library)
        print("\n[Context7검색결과]")
        print(json.dumps(result, indent=2, ensure_ascii=False))