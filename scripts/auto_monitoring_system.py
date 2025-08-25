#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 모니터링 및 업데이트 시스템
실시간으로 워크스페이스 상태를 파악하고 새로운 구성요소 통합을 자동 제안
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import importlib
import time
from typing import Dict, List, Any
import subprocess

# 인코딩 및 경로 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding
setup_utf8_encoding()

class AutoMonitoringSystem:
    """자동 모니터링 및 업데이트 시스템"""
    
    def __init__(self):
        self.workspace_root = Path("C:/Users/eunta/multi-agent-workspace")
        self.state_file = self.workspace_root / "cache" / "system_state.json"
        self.last_scan = None
        self.state_file.parent.mkdir(exist_ok=True)
        
        # 모니터링 대상 경로들
        self.monitor_paths = {
            "mcp_servers": self.workspace_root / "src" / "ai_integration" / "mcp_servers",
            "scripts": self.workspace_root / "scripts",
            "communication": self.workspace_root / "communication",
            "docs_core": self.workspace_root / "docs" / "CORE",
            "requirements": self.workspace_root / "requirements.txt",
            "pyproject": self.workspace_root / "pyproject.toml"
        }
        
        # 자동 통합 가능한 패턴들
        self.auto_integration_patterns = {
            "new_mcp_server": r".*_server\.py$",
            "new_script": r".*\.py$",
            "new_comm_agent": r"communication/[^/]+/$",
            "new_requirement": r"requirements.*\.txt$"
        }
        
        self._load_current_state()
    
    def _load_current_state(self) -> None:
        """현재 시스템 상태 로드"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.last_scan = datetime.fromisoformat(state_data.get("last_scan", ""))
            else:
                self.last_scan = datetime.now() - timedelta(days=1)  # 첫 실행시 어제로 설정
        except:
            self.last_scan = datetime.now() - timedelta(days=1)
    
    def _save_current_state(self, scan_results: Dict) -> None:
        """현재 상태 저장"""
        state_data = {
            "last_scan": datetime.now().isoformat(),
            "scan_results": scan_results,
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    
    # === 실시간 변경 감지 ===
    
    def scan_for_changes(self) -> Dict[str, Any]:
        """워크스페이스 변경사항 스캔"""
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "new_dependencies": [],
            "integration_suggestions": []
        }
        
        # 파일 변경 감지
        for name, path in self.monitor_paths.items():
            if not path.exists():
                continue
                
            if path.is_file():
                # 단일 파일 체크
                if path.stat().st_mtime > self.last_scan.timestamp():
                    changes["modified_files"].append(str(path))
            else:
                # 디렉터리 내 파일들 체크
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime > self.last_scan:
                            if self._is_new_file(file_path):
                                changes["new_files"].append(str(file_path))
                            else:
                                changes["modified_files"].append(str(file_path))
        
        # 새로운 의존성 체크
        changes["new_dependencies"] = self._check_new_dependencies()
        
        # 자동 통합 제안 생성
        changes["integration_suggestions"] = self._generate_integration_suggestions(changes)
        
        return changes
    
    def _is_new_file(self, file_path: Path) -> bool:
        """파일이 새로 생성된 것인지 확인"""
        creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
        return creation_time > self.last_scan
    
    def _check_new_dependencies(self) -> List[str]:
        """새로운 Python 의존성 체크"""
        new_deps = []
        
        # requirements.txt 변경 체크
        req_file = self.workspace_root / "requirements.txt"
        if req_file.exists():
            mtime = datetime.fromtimestamp(req_file.stat().st_mtime)
            if mtime > self.last_scan:
                # 실제 새로운 패키지 식별은 복잡하므로 파일 변경 알림만
                new_deps.append("requirements.txt 변경됨 - 새 패키지 설치 필요할 수 있음")
        
        return new_deps
    
    def _generate_integration_suggestions(self, changes: Dict) -> List[Dict]:
        """자동 통합 제안 생성"""
        suggestions = []
        
        for new_file in changes["new_files"]:
            file_path = Path(new_file)
            
            # MCP 서버 자동 통합 제안
            if "mcp_servers" in str(file_path) and file_path.name.endswith("_server.py"):
                suggestions.append({
                    "type": "mcp_integration",
                    "file": str(file_path),
                    "suggestion": f"새 MCP 서버 감지: {file_path.name}",
                    "auto_actions": [
                        f"mcp_auto_system.py에 {file_path.stem} 모듈 추가",
                        "MCP 서버 목록 업데이트",
                        "자동 로드 함수에 추가"
                    ]
                })
            
            # 새 에이전트 폴더 감지
            if "communication" in str(file_path):
                agent_match = self._extract_agent_name(file_path)
                if agent_match and agent_match not in ["claude", "codex", "gemini", "shared"]:
                    suggestions.append({
                        "type": "new_agent",
                        "agent_name": agent_match,
                        "suggestion": f"새 에이전트 감지: {agent_match}",
                        "auto_actions": [
                            f"agent_task_dispatcher.py에 {agent_match} 추가",
                            f"{agent_match.upper()}.md 설정 파일 생성",
                            "워크스페이스 모니터링에 추가"
                        ]
                    })
            
            # 새 스크립트 자동 등록 제안
            if file_path.parent.name == "scripts" and file_path.suffix == ".py":
                suggestions.append({
                    "type": "script_integration",
                    "file": str(file_path),
                    "suggestion": f"새 스크립트 감지: {file_path.name}",
                    "auto_actions": [
                        "session_startup.py에 자동 실행 추가 검토",
                        "다른 에이전트에서 사용 가능하도록 경로 추가"
                    ]
                })
        
        return suggestions
    
    def _extract_agent_name(self, file_path: Path) -> str:
        """파일 경로에서 에이전트 이름 추출"""
        parts = file_path.parts
        if "communication" in parts:
            comm_index = parts.index("communication")
            if len(parts) > comm_index + 1:
                return parts[comm_index + 1]
        return None
    
    # === 자동 시스템 건강도 체크 ===
    
    def health_check_comprehensive(self) -> Dict[str, Any]:
        """종합적인 시스템 건강도 체크"""
        health = {
            "overall_status": "healthy",
            "components": {},
            "issues": [],
            "recommendations": [],
            "performance_metrics": {}
        }
        
        # 1. 핵심 파일 존재 확인
        critical_files = [
            "docs/CORE/HUB_ENHANCED.md",
            "scripts/mcp_auto_system.py",
            "scripts/agent_task_dispatcher.py",
            "scripts/session_startup.py",
            "CLAUDE.md"
        ]
        
        for file_path in critical_files:
            full_path = self.workspace_root / file_path
            health["components"][file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0,
                "last_modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat() if full_path.exists() else None
            }
            
            if not full_path.exists():
                health["issues"].append(f"중요 파일 누락: {file_path}")
                health["overall_status"] = "warning"
        
        # 2. MCP 시스템 상태 확인
        try:
            sys.path.append(str(self.workspace_root / "scripts"))
            from mcp_auto_system import mcp_auto
            mcp_status = mcp_auto.get_current_workspace_status()
            health["components"]["mcp_system"] = {
                "available": mcp_auto.mcp_available,
                "status": mcp_status.get("status", "unknown")
            }
        except Exception as e:
            health["issues"].append(f"MCP 시스템 체크 실패: {e}")
            health["overall_status"] = "warning"
        
        # 3. 에이전트 활동 상태 확인
        agent_dirs = ["claude", "codex", "gemini"]
        for agent in agent_dirs:
            agent_path = self.workspace_root / "communication" / agent
            if agent_path.exists():
                recent_files = list(agent_path.glob("*.md"))
                health["components"][f"{agent}_activity"] = {
                    "active": len(recent_files) > 0,
                    "recent_files": len(recent_files),
                    "last_activity": max([f.stat().st_mtime for f in recent_files]) if recent_files else 0
                }
        
        # 4. 성능 메트릭
        health["performance_metrics"] = {
            "total_files": len(list(self.workspace_root.rglob("*"))),
            "python_files": len(list(self.workspace_root.rglob("*.py"))),
            "communication_files": len(list((self.workspace_root / "communication").rglob("*.md"))),
            "cache_size": sum(f.stat().st_size for f in (self.workspace_root / "cache").rglob("*") if f.is_file()) if (self.workspace_root / "cache").exists() else 0
        }
        
        # 5. 권장사항 생성
        if health["performance_metrics"]["communication_files"] > 50:
            health["recommendations"].append("Communication 파일 정리 권장")
        
        if health["performance_metrics"]["cache_size"] > 10 * 1024 * 1024:  # 10MB
            health["recommendations"].append("캐시 정리 권장")
        
        return health
    
    # === 자동 제안 시스템 ===
    
    def generate_system_improvements(self) -> List[Dict]:
        """시스템 개선사항 자동 제안"""
        improvements = []
        
        # 최근 변경 패턴 분석
        changes = self.scan_for_changes()
        
        if len(changes["new_files"]) > 10:
            improvements.append({
                "category": "organization",
                "priority": "medium",
                "suggestion": "많은 새 파일이 감지됨 - 자동 정리 시스템 활성화 권장",
                "implementation": "auto_cleanup_scheduler 실행"
            })
        
        # MCP 시스템 최적화 제안
        try:
            from mcp_auto_system import optimize_tokens_auto
            token_info = optimize_tokens_auto()
            if token_info["token_estimate"] > 5000:
                improvements.append({
                    "category": "performance",
                    "priority": "high", 
                    "suggestion": "토큰 사용량 최적화 필요",
                    "implementation": f"큰 파일 {len(token_info['large_files'])}개 요약 처리 권장"
                })
        except:
            pass
        
        return improvements
    
    # === 실시간 모니터링 실행 ===
    
    def start_monitoring_cycle(self) -> Dict[str, Any]:
        """모니터링 사이클 시작"""
        print("🔍 자동 모니터링 시스템 시작...")
        
        # 변경사항 스캔
        changes = self.scan_for_changes()
        print(f"📊 스캔 완료: 새 파일 {len(changes['new_files'])}개, 수정 파일 {len(changes['modified_files'])}개")
        
        # 건강도 체크
        health = self.health_check_comprehensive()
        print(f"💊 시스템 상태: {health['overall_status']}")
        
        # 개선사항 제안
        improvements = self.generate_system_improvements()
        print(f"🎯 개선 제안: {len(improvements)}개")
        
        # 상태 저장
        scan_results = {
            "changes": changes,
            "health": health,
            "improvements": improvements,
            "timestamp": datetime.now().isoformat()
        }
        self._save_current_state(scan_results)
        
        return scan_results

# 전역 인스턴스
auto_monitor = AutoMonitoringSystem()

# 편의 함수들
def monitor_workspace_changes() -> Dict[str, Any]:
    """워크스페이스 변경사항 모니터링"""
    return auto_monitor.scan_for_changes()

def check_system_health() -> Dict[str, Any]:
    """시스템 건강도 체크"""
    return auto_monitor.health_check_comprehensive()

def get_improvement_suggestions() -> List[Dict]:
    """시스템 개선 제안"""
    return auto_monitor.generate_system_improvements()

def run_full_monitoring() -> Dict[str, Any]:
    """전체 모니터링 실행"""
    return auto_monitor.start_monitoring_cycle()

if __name__ == "__main__":
    print("=== 자동 모니터링 시스템 실행 ===")
    results = run_full_monitoring()
    
    if results["changes"]["integration_suggestions"]:
        print("\n🚀 통합 제안사항:")
        for suggestion in results["changes"]["integration_suggestions"]:
            print(f"  • {suggestion['suggestion']}")
            for action in suggestion.get("auto_actions", []):
                print(f"    - {action}")
    
    if results["health"]["issues"]:
        print("\n⚠️ 발견된 문제:")
        for issue in results["health"]["issues"]:
            print(f"  • {issue}")
    
    if results["improvements"]:
        print("\n🎯 개선 제안:")
        for imp in results["improvements"]:
            print(f"  • [{imp['priority'].upper()}] {imp['suggestion']}")
    
    print("\n✅ 자동 모니터링 완료")