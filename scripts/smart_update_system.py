#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스마트 업데이트 시스템
새로운 구성요소 감지 시 자동으로 기존 시스템에 통합하는 지능형 시스템
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Optional
import shutil

# 인코딩 및 경로 설정
sys.path.append(str(Path(__file__).parent))
from fix_encoding_all import setup_utf8_encoding
setup_utf8_encoding()

class SmartUpdateSystem:
    """스마트 자동 업데이트 시스템"""
    
    def __init__(self):
        self.workspace_root = Path("C:/Users/eunta/multi-agent-workspace")
        self.templates_dir = self.workspace_root / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # 업데이트 규칙 정의
        self.update_rules = {
            "new_mcp_server": {
                "pattern": r".*_server\.py$",
                "location": "src/ai_integration/mcp_servers/",
                "integration_targets": [
                    "scripts/mcp_auto_system.py",
                    "scripts/claude_mcp_final.py"
                ]
            },
            "new_agent": {
                "pattern": r"communication/[^/]+/$",
                "integration_targets": [
                    "scripts/agent_task_dispatcher.py",
                    "scripts/session_startup.py"
                ]
            },
            "new_script": {
                "pattern": r"scripts/.*\.py$",
                "integration_targets": [
                    "scripts/session_startup.py"
                ]
            }
        }
        
        # 템플릿 시스템 초기화
        self._ensure_templates()
    
    def _ensure_templates(self) -> None:
        """필수 템플릿 파일들 생성"""
        templates = {
            "agent_template.md": """# {agent_name} Agent Guide

## 역할
{agent_role}

## 주요 기능
- 

## 통신 폴더
`communication/{agent_name}/`

## 자동화 시스템 통합
- Agent Task Dispatcher: ✅ 통합됨
- Session Startup: ✅ 포함됨
- MCP Auto System: ✅ 연동됨

---
🤖 자동 생성됨 - Smart Update System
""",
            
            "mcp_integration_template.py": '''# MCP 서버 통합 템플릿
# {server_name} 자동 통합

try:
    from {module_name} import {functions}
    print(f"✅ {server_name} MCP 서버 로드 완료")
    
    # 전역 함수 등록
    globals().update({{
        "{prefix}_function_name": function_name
    }})
    
except ImportError as e:
    print(f"⚠️ {server_name} MCP 서버 로드 실패: {{e}}")
    # Fallback 함수들 정의
''',
            
            "script_integration_template.py": '''# 스크립트 자동 통합 템플릿
# {script_name} 통합

import sys
from pathlib import Path

# 스크립트 경로 추가
script_path = Path(__file__).parent / "{script_name}"
if script_path.exists():
    sys.path.append(str(script_path.parent))
    
    try:
        import {module_name}
        print(f"✅ {script_name} 통합 완료")
    except Exception as e:
        print(f"⚠️ {script_name} 통합 실패: {{e}}")
'''
        }
        
        for template_name, content in templates.items():
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                template_path.write_text(content, encoding='utf-8')
    
    # === 새 MCP 서버 자동 통합 ===
    
    def integrate_new_mcp_server(self, server_file: Path) -> Dict[str, Any]:
        """새로운 MCP 서버 자동 통합"""
        result = {
            "server_name": server_file.stem,
            "success": False,
            "actions_taken": [],
            "errors": []
        }
        
        try:
            # 1. 서버 파일 분석
            server_analysis = self._analyze_mcp_server(server_file)
            
            # 2. mcp_auto_system.py 업데이트
            if self._update_mcp_auto_system(server_analysis):
                result["actions_taken"].append("mcp_auto_system.py 업데이트 완료")
            
            # 3. claude_mcp_final.py 업데이트
            if self._update_claude_mcp_final(server_analysis):
                result["actions_taken"].append("claude_mcp_final.py 업데이트 완료")
            
            # 4. 문서 업데이트
            if self._update_mcp_documentation(server_analysis):
                result["actions_taken"].append("MCP 문서 업데이트 완료")
            
            result["success"] = len(result["actions_taken"]) > 0
            
        except Exception as e:
            result["errors"].append(f"MCP 서버 통합 실패: {e}")
        
        return result
    
    def _analyze_mcp_server(self, server_file: Path) -> Dict[str, Any]:
        """MCP 서버 파일 분석"""
        analysis = {
            "server_name": server_file.stem,
            "functions": [],
            "resources": [],
            "tools": []
        }
        
        try:
            content = server_file.read_text(encoding='utf-8')
            
            # @mcp.tool() 데코레이터가 있는 함수 찾기
            tool_pattern = r'@mcp\.tool\(\)\s*\ndef\s+(\w+)\([^)]*\):'
            analysis["tools"] = re.findall(tool_pattern, content)
            
            # @mcp.resource() 데코레이터가 있는 함수 찾기  
            resource_pattern = r'@mcp\.resource\([^)]*\)\s*\ndef\s+(\w+)\([^)]*\):'
            analysis["resources"] = re.findall(resource_pattern, content)
            
            # 일반 함수들도 찾기
            function_pattern = r'def\s+(\w+)\([^)]*\):'
            all_functions = re.findall(function_pattern, content)
            analysis["functions"] = [f for f in all_functions if not f.startswith('_')]
            
        except Exception as e:
            print(f"⚠️ MCP 서버 분석 실패: {e}")
        
        return analysis
    
    def _update_mcp_auto_system(self, analysis: Dict) -> bool:
        """mcp_auto_system.py 파일 업데이트"""
        mcp_auto_file = self.workspace_root / "scripts" / "mcp_auto_system.py"
        if not mcp_auto_file.exists():
            return False
        
        try:
            content = mcp_auto_file.read_text(encoding='utf-8')
            server_name = analysis["server_name"]
            
            # _load_mcp_modules 함수에 새 서버 추가
            insert_point = content.find('print("✅ MCP 모듈 로드 완료")')
            if insert_point != -1:
                new_import = f"""
            # {server_name.title()} MCP 로드
            from {server_name} import {', '.join(analysis['functions'][:3])}  # 주요 함수들만
            self.{server_name}_functions = {analysis['functions'][:3]}
            """
                
                content = content[:insert_point] + new_import + "\n            " + content[insert_point:]
                
                mcp_auto_file.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            print(f"⚠️ mcp_auto_system.py 업데이트 실패: {e}")
        
        return False
    
    def _update_claude_mcp_final(self, analysis: Dict) -> bool:
        """claude_mcp_final.py 파일 업데이트"""
        claude_mcp_file = self.workspace_root / "scripts" / "claude_mcp_final.py"
        if not claude_mcp_file.exists():
            return False
        
        try:
            content = claude_mcp_file.read_text(encoding='utf-8')
            server_name = analysis["server_name"]
            
            # 새 MCP 서버 함수들 추가
            if analysis["tools"]:
                new_functions = f"""
# {server_name.title()} MCP 함수들
def mcp_{server_name}_tool(tool_name: str, **kwargs) -> Any:
    \"\"\"
    {server_name} MCP 도구 실행
    \"\"\"
    if mcp_auto.mcp_available:
        try:
            # 동적 함수 호출
            func = getattr(mcp_auto, f"{server_name}_{tool_name}", None)
            if func:
                return func(**kwargs)
        except:
            pass
    
    return f"{{tool_name}} 도구 실행 실패 (Fallback 필요)"

"""
                
                # 파일 끝에 추가
                content += new_functions
                claude_mcp_file.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            print(f"⚠️ claude_mcp_final.py 업데이트 실패: {e}")
        
        return False
    
    def _update_mcp_documentation(self, analysis: Dict) -> bool:
        """MCP 관련 문서 업데이트"""
        try:
            doc_file = self.workspace_root / "docs" / "MCP_SERVERS.md"
            
            if not doc_file.exists():
                # 문서 파일 생성
                doc_content = "# MCP 서버 목록\n\n"
            else:
                doc_content = doc_file.read_text(encoding='utf-8')
            
            # 새 서버 정보 추가
            server_info = f"""
## {analysis['server_name'].title()}
- **도구**: {', '.join(analysis['tools'])}
- **리소스**: {', '.join(analysis['resources'])}
- **통합 상태**: ✅ 자동 통합 완료
- **마지막 업데이트**: {datetime.now().strftime('%Y-%m-%d')}

"""
            
            doc_content += server_info
            doc_file.write_text(doc_content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"⚠️ MCP 문서 업데이트 실패: {e}")
        
        return False
    
    # === 새 에이전트 자동 통합 ===
    
    def integrate_new_agent(self, agent_name: str) -> Dict[str, Any]:
        """새로운 에이전트 자동 통합"""
        result = {
            "agent_name": agent_name,
            "success": False,
            "actions_taken": [],
            "errors": []
        }
        
        try:
            # 1. 에이전트 설정 파일 생성
            if self._create_agent_config(agent_name):
                result["actions_taken"].append(f"{agent_name.upper()}.md 생성")
            
            # 2. agent_task_dispatcher.py 업데이트
            if self._update_agent_dispatcher(agent_name):
                result["actions_taken"].append("Agent Task Dispatcher 업데이트")
            
            # 3. session_startup.py 업데이트
            if self._update_session_startup_for_agent(agent_name):
                result["actions_taken"].append("Session Startup 업데이트")
            
            # 4. 통신 폴더 구조 생성
            if self._setup_agent_communication(agent_name):
                result["actions_taken"].append("통신 폴더 구조 생성")
            
            result["success"] = len(result["actions_taken"]) > 0
            
        except Exception as e:
            result["errors"].append(f"에이전트 통합 실패: {e}")
        
        return result
    
    def _create_agent_config(self, agent_name: str) -> bool:
        """에이전트 설정 파일 생성"""
        try:
            template = (self.templates_dir / "agent_template.md").read_text(encoding='utf-8')
            
            config_content = template.format(
                agent_name=agent_name,
                agent_role=f"{agent_name.title()} 전용 에이전트"
            )
            
            config_file = self.workspace_root / f"{agent_name.upper()}.md"
            config_file.write_text(config_content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"⚠️ {agent_name} 설정 파일 생성 실패: {e}")
        
        return False
    
    def _update_agent_dispatcher(self, agent_name: str) -> bool:
        """agent_task_dispatcher.py 업데이트"""
        dispatcher_file = self.workspace_root / "scripts" / "agent_task_dispatcher.py"
        if not dispatcher_file.exists():
            return False
        
        try:
            content = dispatcher_file.read_text(encoding='utf-8')
            
            # agents 딕셔너리에 새 에이전트 추가
            insert_point = content.find('"gemini": {')
            if insert_point != -1:
                # gemini 섹션 끝 찾기
                gemini_end = content.find('}', content.find('}', insert_point) + 1) + 1
                
                new_agent_config = f''',
            "{agent_name}": {{
                "role": "{agent_name.title()} 전문가",
                "strengths": ["자동 생성된 에이전트"],
                "comm_folder": self.workspace / "communication" / "{agent_name}"
            }}'''
                
                content = content[:gemini_end] + new_agent_config + content[gemini_end:]
                
                dispatcher_file.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            print(f"⚠️ Agent Dispatcher 업데이트 실패: {e}")
        
        return False
    
    def _update_session_startup_for_agent(self, agent_name: str) -> bool:
        """session_startup.py에 새 에이전트 추가"""
        startup_file = self.workspace_root / "scripts" / "session_startup.py"
        if not startup_file.exists():
            return False
        
        try:
            content = startup_file.read_text(encoding='utf-8')
            
            # comm_cleanup_all 함수에 새 에이전트 추가
            agent_list_pattern = r'agents\s*=\s*\[(.*?)\]'
            match = re.search(agent_list_pattern, content, re.DOTALL)
            
            if match:
                current_agents = match.group(1)
                if f'"{agent_name}"' not in current_agents:
                    new_agents = current_agents.rstrip() + f', "{agent_name}"'
                    content = content.replace(match.group(1), new_agents)
                    
                    startup_file.write_text(content, encoding='utf-8')
                    return True
                    
        except Exception as e:
            print(f"⚠️ Session Startup 업데이트 실패: {e}")
        
        return False
    
    def _setup_agent_communication(self, agent_name: str) -> bool:
        """에이전트 통신 폴더 구조 생성"""
        try:
            comm_dir = self.workspace_root / "communication" / agent_name
            comm_dir.mkdir(parents=True, exist_ok=True)
            
            # README 파일 생성
            readme_content = f"""# {agent_name.title()} Communication Folder

이 폴더는 {agent_name.title()} 에이전트와의 통신을 위한 공간입니다.

## 자동 정리
- Session Startup 시 자동으로 오래된 파일들이 정리됩니다
- 보관 기간: 7일

---
🤖 자동 생성됨 - Smart Update System
"""
            
            (comm_dir / "README.md").write_text(readme_content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"⚠️ {agent_name} 통신 폴더 설정 실패: {e}")
        
        return False
    
    # === 전체 시스템 자동 업데이트 ===
    
    def run_smart_update_scan(self) -> Dict[str, Any]:
        """스마트 업데이트 전체 스캔"""
        print("🔄 스마트 업데이트 시스템 실행...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "new_mcp_servers": [],
            "new_agents": [],
            "new_scripts": [],
            "integration_results": []
        }
        
        # 1. 새 MCP 서버 감지
        mcp_dir = self.workspace_root / "src" / "ai_integration" / "mcp_servers"
        if mcp_dir.exists():
            for server_file in mcp_dir.glob("*_server.py"):
                if self._is_newly_added(server_file):
                    results["new_mcp_servers"].append(str(server_file))
                    integration_result = self.integrate_new_mcp_server(server_file)
                    results["integration_results"].append(integration_result)
        
        # 2. 새 에이전트 감지
        comm_dir = self.workspace_root / "communication"
        if comm_dir.exists():
            for agent_dir in comm_dir.iterdir():
                if agent_dir.is_dir() and agent_dir.name not in ["claude", "codex", "gemini", "shared"]:
                    if self._is_newly_added(agent_dir):
                        results["new_agents"].append(agent_dir.name)
                        integration_result = self.integrate_new_agent(agent_dir.name)
                        results["integration_results"].append(integration_result)
        
        # 3. 새 스크립트 감지 (간단한 통합만)
        scripts_dir = self.workspace_root / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                if self._is_newly_added(script_file) and not script_file.name.startswith("_"):
                    results["new_scripts"].append(str(script_file))
        
        return results
    
    def _is_newly_added(self, path: Path) -> bool:
        """파일/폴더가 최근 추가된 것인지 확인"""
        try:
            # 1시간 이내 생성된 것으로 판단
            creation_time = datetime.fromtimestamp(path.stat().st_ctime)
            return (datetime.now() - creation_time).seconds < 3600
        except:
            return False

# 전역 인스턴스
smart_updater = SmartUpdateSystem()

# 편의 함수들
def integrate_new_mcp(server_file: str) -> Dict[str, Any]:
    """새 MCP 서버 통합"""
    return smart_updater.integrate_new_mcp_server(Path(server_file))

def integrate_new_agent(agent_name: str) -> Dict[str, Any]:
    """새 에이전트 통합"""
    return smart_updater.integrate_new_agent(agent_name)

def run_auto_update() -> Dict[str, Any]:
    """자동 업데이트 실행"""
    return smart_updater.run_smart_update_scan()

if __name__ == "__main__":
    print("=== 스마트 업데이트 시스템 실행 ===")
    results = run_auto_update()
    
    if results["new_mcp_servers"]:
        print(f"🔌 새 MCP 서버: {len(results['new_mcp_servers'])}개")
    
    if results["new_agents"]:
        print(f"🤖 새 에이전트: {len(results['new_agents'])}개")
        
    if results["new_scripts"]:
        print(f"📜 새 스크립트: {len(results['new_scripts'])}개")
    
    if results["integration_results"]:
        print("\n🔗 통합 결과:")
        for result in results["integration_results"]:
            status = "✅ 성공" if result["success"] else "❌ 실패"
            print(f"  {status}: {result.get('server_name', result.get('agent_name', 'Unknown'))}")
    
    print("\n✅ 스마트 업데이트 완료")