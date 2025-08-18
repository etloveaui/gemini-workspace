#!/usr/bin/env python3
"""
반복 오류 방지 시스템
- Claude가 자주 틀리는 명령어들을 시스템적으로 방지
- 환경별 올바른 명령어 자동 제안
- 오류 패턴 학습 및 예방
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import platform

class ErrorPreventionSystem:
    """오류 방지 시스템"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.error_db_file = self.workspace_path / "scripts" / "common_errors.json"
        self.command_map_file = self.workspace_path / "scripts" / "correct_commands.json"
        
        # 플랫폼 정보
        self.is_windows = platform.system() == "Windows"
        self.is_venv = self._detect_venv()
        
        self.load_error_database()
        self.load_command_mappings()
    
    def _detect_venv(self) -> bool:
        """가상환경 활성화 상태 감지"""
        venv_path = self.workspace_path / "venv"
        return venv_path.exists()
    
    def load_error_database(self):
        """오류 데이터베이스 로드"""
        if self.error_db_file.exists():
            with open(self.error_db_file, 'r', encoding='utf-8') as f:
                self.error_db = json.load(f)
        else:
            self.error_db = self._create_initial_error_db()
            self.save_error_database()
    
    def load_command_mappings(self):
        """올바른 명령어 매핑 로드"""
        if self.command_map_file.exists():
            with open(self.command_map_file, 'r', encoding='utf-8') as f:
                self.command_mappings = json.load(f)
        else:
            self.command_mappings = self._create_command_mappings()
            self.save_command_mappings()
    
    def _create_initial_error_db(self) -> Dict:
        """초기 오류 데이터베이스 생성"""
        return {
            "common_errors": {
                "pytest_not_found": {
                    "error_pattern": "/usr/bin/bash: line 1: pytest: command not found",
                    "description": "pytest 명령어를 직접 실행할 때 발생하는 오류",
                    "correct_command": "powershell -Command \"& { .\\venv\\Scripts\\python.exe -m pytest -v }\"",
                    "frequency": 5,
                    "last_seen": datetime.now().isoformat(),
                    "environments": ["Windows", "venv"]
                },
                "python_module_not_found": {
                    "error_pattern": "No module named pytest",
                    "description": "가상환경에서 모듈을 찾을 수 없을 때",
                    "correct_command": ".\\venv\\Scripts\\python.exe -m pytest",
                    "frequency": 3,
                    "last_seen": datetime.now().isoformat(),
                    "environments": ["Windows", "venv"]
                },
                "bash_command_in_windows": {
                    "error_pattern": "/usr/bin/bash: command not found",
                    "description": "Windows에서 Linux bash 명령어 사용",
                    "correct_command": "powershell 사용 또는 Windows 명령어로 변환",
                    "frequency": 4,
                    "last_seen": datetime.now().isoformat(),
                    "environments": ["Windows"]
                }
            },
            "prevention_rules": {
                "always_use_venv_python": "가상환경이 있으면 항상 .\\venv\\Scripts\\python.exe 사용",
                "windows_powershell_wrapper": "Windows에서 복잡한 명령어는 powershell -Command로 감싸기",
                "check_file_existence": "명령어 실행 전 대상 파일/디렉터리 존재 확인"
            }
        }
    
    def _create_command_mappings(self) -> Dict:
        """환경별 올바른 명령어 매핑 생성"""
        return {
            "pytest": {
                "windows_venv": "powershell -Command \"& { .\\venv\\Scripts\\python.exe -m pytest -v }\"",
                "windows_system": "python -m pytest -v",
                "linux_venv": "./venv/bin/python -m pytest -v",
                "linux_system": "python3 -m pytest -v"
            },
            "pip_install": {
                "windows_venv": ".\\venv\\Scripts\\pip.exe install",
                "windows_system": "pip install",
                "linux_venv": "./venv/bin/pip install",
                "linux_system": "pip3 install"
            },
            "python_run": {
                "windows_venv": ".\\venv\\Scripts\\python.exe",
                "windows_system": "python",
                "linux_venv": "./venv/bin/python",
                "linux_system": "python3"
            },
            "activate_venv": {
                "windows": ".\\venv\\Scripts\\activate.bat",
                "linux": "source ./venv/bin/activate"
            }
        }
    
    def get_correct_command(self, intended_command: str) -> Tuple[str, str]:
        """의도한 명령어에 대한 올바른 명령어 반환"""
        # 환경 감지
        env_key = self._get_environment_key()
        
        # 명령어 매핑에서 찾기
        for base_cmd, mappings in self.command_mappings.items():
            if base_cmd in intended_command.lower():
                if env_key in mappings:
                    correct_cmd = mappings[env_key]
                    explanation = f"환경: {env_key}, 올바른 명령어 사용"
                    return correct_cmd, explanation
        
        # 일반적인 수정 규칙 적용
        if intended_command.startswith("pytest"):
            return self._fix_pytest_command(intended_command)
        elif "python" in intended_command and not intended_command.startswith(".\\venv"):
            return self._fix_python_command(intended_command)
        
        return intended_command, "수정 불필요"
    
    def _get_environment_key(self) -> str:
        """현재 환경에 맞는 키 반환"""
        if self.is_windows:
            return "windows_venv" if self.is_venv else "windows_system"
        else:
            return "linux_venv" if self.is_venv else "linux_system"
    
    def _fix_pytest_command(self, command: str) -> Tuple[str, str]:
        """pytest 명령어 수정"""
        if self.is_windows and self.is_venv:
            fixed = 'powershell -Command "& { .\\venv\\Scripts\\python.exe -m pytest -v }"'
            return fixed, "Windows 가상환경에서 pytest 실행"
        elif self.is_windows:
            fixed = "python -m pytest -v"
            return fixed, "Windows 시스템 Python으로 pytest 실행"
        else:
            fixed = "./venv/bin/python -m pytest -v" if self.is_venv else "python3 -m pytest -v"
            return fixed, "Linux 환경에서 pytest 실행"
    
    def _fix_python_command(self, command: str) -> Tuple[str, str]:
        """Python 명령어 수정"""
        if self.is_windows and self.is_venv:
            fixed = command.replace("python", ".\\venv\\Scripts\\python.exe")
            return fixed, "가상환경 Python 사용"
        return command, "수정 불필요"
    
    def record_error(self, error_message: str, attempted_command: str, context: str = ""):
        """오류 기록"""
        error_id = f"error_{len(self.error_db.get('recorded_errors', []))}"
        
        if 'recorded_errors' not in self.error_db:
            self.error_db['recorded_errors'] = []
        
        error_record = {
            "id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_message": error_message,
            "attempted_command": attempted_command,
            "context": context,
            "environment": self._get_environment_key(),
            "suggested_fix": self.get_correct_command(attempted_command)[0]
        }
        
        self.error_db['recorded_errors'].append(error_record)
        self.save_error_database()
    
    def get_prevention_tips(self) -> List[str]:
        """예방 팁 반환"""
        tips = [
            f"✅ 현재 환경: {self._get_environment_key()}",
            f"✅ 가상환경 감지: {'예' if self.is_venv else '아니오'}",
        ]
        
        # 환경별 권장사항
        if self.is_windows and self.is_venv:
            tips.extend([
                "🔧 pytest 실행: powershell -Command \"& { .\\venv\\Scripts\\python.exe -m pytest -v }\"",
                "🔧 Python 실행: .\\venv\\Scripts\\python.exe",
                "🔧 pip 설치: .\\venv\\Scripts\\pip.exe install"
            ])
        elif self.is_windows:
            tips.extend([
                "🔧 pytest 실행: python -m pytest -v",
                "🔧 복잡한 명령어는 powershell -Command로 감싸기"
            ])
        
        # 일반적인 예방 규칙
        tips.extend([
            "⚠️ 명령어 실행 전 파일 존재 확인",
            "⚠️ 경로에 공백이 있으면 따옴표로 감싸기",
            "⚠️ 환경변수 설정 확인"
        ])
        
        return tips
    
    def save_error_database(self):
        """오류 데이터베이스 저장"""
        self.error_db_file.parent.mkdir(exist_ok=True)
        with open(self.error_db_file, 'w', encoding='utf-8') as f:
            json.dump(self.error_db, f, ensure_ascii=False, indent=2)
    
    def save_command_mappings(self):
        """명령어 매핑 저장"""
        self.command_map_file.parent.mkdir(exist_ok=True)
        with open(self.command_map_file, 'w', encoding='utf-8') as f:
            json.dump(self.command_mappings, f, ensure_ascii=False, indent=2)
    
    def generate_prevention_report(self) -> str:
        """예방 보고서 생성"""
        report = f"""# 오류 방지 시스템 보고서

**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**환경**: {self._get_environment_key()}

## 📊 환경 정보
- **운영체제**: {'Windows' if self.is_windows else 'Linux/MacOS'}
- **가상환경**: {'활성화됨' if self.is_venv else '비활성화됨'}
- **작업공간**: {self.workspace_path}

## 🔧 권장 명령어

### pytest 실행
```bash
{self.get_correct_command('pytest -v')[0]}
```

### Python 스크립트 실행
```bash
{self.get_correct_command('python script.py')[0]}
```

## 💡 예방 팁
"""
        
        for tip in self.get_prevention_tips():
            report += f"- {tip}\n"
        
        # 최근 오류 기록 추가
        if 'recorded_errors' in self.error_db and self.error_db['recorded_errors']:
            report += "\n## 📋 최근 오류 기록\n"
            for error in self.error_db['recorded_errors'][-5:]:  # 최근 5개
                report += f"- **{error['timestamp'][:10]}**: {error['attempted_command']} → {error['suggested_fix']}\n"
        
        return report

def main():
    """CLI 실행"""
    import argparse
    
    parser = argparse.ArgumentParser(description="오류 방지 시스템")
    parser.add_argument("--check", help="명령어 확인", metavar="COMMAND")
    parser.add_argument("--report", action="store_true", help="예방 보고서 생성")
    parser.add_argument("--record", nargs=3, metavar=("ERROR", "COMMAND", "CONTEXT"), 
                       help="오류 기록")
    
    args = parser.parse_args()
    
    eps = ErrorPreventionSystem()
    
    if args.check:
        correct_cmd, explanation = eps.get_correct_command(args.check)
        print(f"입력 명령어: {args.check}")
        print(f"권장 명령어: {correct_cmd}")
        print(f"설명: {explanation}")
    
    elif args.report:
        report = eps.generate_prevention_report()
        print(report)
        
        # 파일로도 저장
        report_file = eps.workspace_path / "docs" / "error_prevention_report.md"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n보고서가 {report_file}에 저장되었습니다.")
    
    elif args.record:
        error_msg, command, context = args.record
        eps.record_error(error_msg, command, context)
        print(f"오류가 기록되었습니다: {command}")
    
    else:
        # 기본: 현재 환경 정보 및 권장사항 출력
        tips = eps.get_prevention_tips()
        print("🛡️ 오류 방지 시스템")
        print("=" * 40)
        for tip in tips:
            print(tip)

if __name__ == "__main__":
    main()