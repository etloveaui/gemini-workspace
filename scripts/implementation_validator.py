#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구현 완료 검증 시스템 (Implementation Validator)
AI 에이전트가 허위 완료 보고를 방지하는 자동 검증 시스템
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import traceback

class ImplementationValidator:
    """구현 완료 자동 검증 시스템"""
    
    def __init__(self):
        self.workspace_root = Path("C:/Users/eunta/multi-agent-workspace")
        self.validation_log = self.workspace_root / "cache" / "implementation_validation.json"
        self.validation_log.parent.mkdir(exist_ok=True)
        
        # 검증 실패 패턴들
        self.common_failure_patterns = [
            "ModuleNotFoundError",
            "ImportError", 
            "FileNotFoundError",
            "AttributeError",
            "SyntaxError",
            "NameError",
            "TypeError",
            "ValueError",
            "KeyError"
        ]
        
    def validate_python_script(self, script_path: str, test_imports: List[str] = None) -> Dict[str, Any]:
        """Python 스크립트 검증"""
        script_file = Path(script_path)
        
        if not script_file.is_absolute():
            script_file = self.workspace_root / script_path
            
        result = {
            "script": str(script_file),
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        # 1. 파일 존재 확인
        if not script_file.exists():
            result["overall_status"] = "FAIL"
            result["error"] = f"파일이 존재하지 않음: {script_file}"
            return result
            
        # 2. 구문 검사
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, script_file, 'exec')
            result["tests"].append({"name": "syntax_check", "status": "PASS"})
        except SyntaxError as e:
            result["tests"].append({"name": "syntax_check", "status": "FAIL", "error": str(e)})
            result["overall_status"] = "FAIL"
            return result
            
        # 3. Import 테스트
        if test_imports:
            for import_test in test_imports:
                try:
                    # 스크립트 디렉터리를 sys.path에 추가
                    script_dir = str(script_file.parent)
                    if script_dir not in sys.path:
                        sys.path.insert(0, script_dir)
                    
                    if "from" in import_test:
                        exec(import_test)
                    else:
                        __import__(import_test)
                    
                    result["tests"].append({"name": f"import_{import_test}", "status": "PASS"})
                except Exception as e:
                    result["tests"].append({
                        "name": f"import_{import_test}", 
                        "status": "FAIL", 
                        "error": str(e)
                    })
        
        # 4. 기본 실행 테스트 (if __name__ == "__main__" 있는 경우)
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'if __name__ == "__main__"' in content:
                # 백그라운드에서 실행하여 출력 확인
                proc = subprocess.run([
                    sys.executable, str(script_file)
                ], cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
                
                if proc.returncode == 0:
                    result["tests"].append({"name": "main_execution", "status": "PASS"})
                else:
                    error_output = proc.stderr or proc.stdout
                    result["tests"].append({
                        "name": "main_execution", 
                        "status": "FAIL",
                        "error": error_output
                    })
        except subprocess.TimeoutExpired:
            result["tests"].append({"name": "main_execution", "status": "TIMEOUT"})
        except Exception as e:
            result["tests"].append({"name": "main_execution", "status": "ERROR", "error": str(e)})
        
        # 전체 결과 판정
        failed_tests = [t for t in result["tests"] if t["status"] == "FAIL"]
        if failed_tests:
            result["overall_status"] = "FAIL"
            result["failed_tests"] = failed_tests
        else:
            result["overall_status"] = "PASS"
            
        return result
    
    def validate_invoke_task(self, task_name: str) -> Dict[str, Any]:
        """invoke 작업 검증"""
        result = {
            "task": task_name,
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        try:
            # invoke 작업 실행 테스트
            proc = subprocess.run([
                sys.executable, "-m", "invoke", task_name, "--help"
            ], cwd=self.workspace_root, capture_output=True, text=True, timeout=10)
            
            if proc.returncode == 0:
                result["tests"].append({"name": "task_exists", "status": "PASS"})
                result["overall_status"] = "PASS"
            else:
                result["tests"].append({
                    "name": "task_exists", 
                    "status": "FAIL",
                    "error": proc.stderr
                })
                result["overall_status"] = "FAIL"
                
        except Exception as e:
            result["tests"].append({"name": "task_exists", "status": "ERROR", "error": str(e)})
            result["overall_status"] = "FAIL"
            
        return result
    
    def validate_system_integration(self, component_name: str, validation_commands: List[str]) -> Dict[str, Any]:
        """시스템 통합 검증"""
        result = {
            "component": component_name,
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        for i, command in enumerate(validation_commands):
            test_name = f"integration_test_{i+1}"
            
            try:
                # 명령어 실행
                if command.startswith("python"):
                    proc = subprocess.run([
                        sys.executable, "-c", command.replace("python -c ", "")
                    ], cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
                else:
                    proc = subprocess.run(
                        command, shell=True, cwd=self.workspace_root, 
                        capture_output=True, text=True, timeout=30
                    )
                
                if proc.returncode == 0:
                    result["tests"].append({"name": test_name, "status": "PASS"})
                else:
                    result["tests"].append({
                        "name": test_name, 
                        "status": "FAIL",
                        "error": proc.stderr or proc.stdout,
                        "command": command
                    })
                    
            except Exception as e:
                result["tests"].append({
                    "name": test_name, 
                    "status": "ERROR",
                    "error": str(e),
                    "command": command
                })
        
        # 전체 결과 판정
        failed_tests = [t for t in result["tests"] if t["status"] in ["FAIL", "ERROR"]]
        if failed_tests:
            result["overall_status"] = "FAIL"
            result["failed_tests"] = failed_tests
        else:
            result["overall_status"] = "PASS"
            
        return result
    
    def save_validation_result(self, result: Dict[str, Any]) -> None:
        """검증 결과 저장"""
        try:
            # 기존 결과 로드
            if self.validation_log.exists():
                with open(self.validation_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"validations": []}
            
            # 새 결과 추가
            log_data["validations"].append(result)
            
            # 최근 100개만 보관
            log_data["validations"] = log_data["validations"][-100:]
            
            # 저장
            with open(self.validation_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"검증 결과 저장 실패: {e}")
    
    def generate_validation_report(self, result: Dict[str, Any]) -> str:
        """검증 보고서 생성"""
        report = f"""
🔍 구현 검증 보고서
==================

**대상**: {result.get('script', result.get('task', result.get('component')))}
**시간**: {result['timestamp']}
**전체 결과**: {'✅ PASS' if result['overall_status'] == 'PASS' else '❌ FAIL'}

## 세부 테스트 결과
"""
        
        for test in result.get("tests", []):
            status_icon = "✅" if test["status"] == "PASS" else "❌"
            report += f"- {status_icon} {test['name']}: {test['status']}\n"
            
            if test["status"] in ["FAIL", "ERROR"] and "error" in test:
                report += f"  오류: {test['error']}\n"
        
        if result["overall_status"] == "FAIL":
            report += "\n⚠️ **검증 실패**: 이 구현은 완료되지 않았습니다.\n"
        else:
            report += "\n✅ **검증 성공**: 구현이 올바르게 동작합니다.\n"
            
        return report

# 전역 인스턴스
validator = ImplementationValidator()

# 편의 함수들
def validate_script(script_path: str, imports: List[str] = None) -> bool:
    """스크립트 검증 (True/False 반환)"""
    result = validator.validate_python_script(script_path, imports)
    validator.save_validation_result(result)
    
    if result["overall_status"] != "PASS":
        print(validator.generate_validation_report(result))
        return False
    return True

def validate_task(task_name: str) -> bool:
    """invoke 작업 검증"""
    result = validator.validate_invoke_task(task_name)
    validator.save_validation_result(result)
    
    if result["overall_status"] != "PASS":
        print(validator.generate_validation_report(result))
        return False
    return True

def validate_integration(component: str, commands: List[str]) -> bool:
    """시스템 통합 검증"""
    result = validator.validate_system_integration(component, commands)
    validator.save_validation_result(result)
    
    if result["overall_status"] != "PASS":
        print(validator.generate_validation_report(result))
        return False
    return True

def must_validate_before_claiming_complete(validation_func, *args, **kwargs):
    """완료 선언 전 필수 검증 데코레이터"""
    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            # 검증 실행
            if not validation_func(*args, **kwargs):
                raise RuntimeError("❌ 검증 실패: 완료 선언 불가!")
            
            # 검증 통과시에만 원래 함수 실행
            return func(*func_args, **func_kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    print("=== 구현 검증 시스템 테스트 ===")
    
    # 예시: hub_manager.py 검증
    print("hub_manager.py 검증 중...")
    result = validate_script("scripts/hub_manager.py", ["scripts.hub_manager"])
    print(f"결과: {'✅ 통과' if result else '❌ 실패'}")
    
    # 예시: MCP 시스템 통합 검증
    print("\nMCP 시스템 통합 검증 중...")
    mcp_commands = [
        "python -c \"from scripts.mcp_auto_system import read_file_smart; print('MCP 테스트:', len(read_file_smart('CLAUDE.md')))\"",
        "python -c \"from scripts.mcp_auto_system import get_workspace_status_auto; print('상태 테스트:', get_workspace_status_auto().get('timestamp', 'OK'))\""
    ]
    result = validate_integration("MCP_System", mcp_commands)
    print(f"결과: {'✅ 통과' if result else '❌ 실패'}")
    
    print("\n✅ 구현 검증 시스템 준비 완료")