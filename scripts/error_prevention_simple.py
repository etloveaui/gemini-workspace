#!/usr/bin/env python3
"""
간단한 오류 방지 시스템 - 이모지 없는 버전
"""

import platform
from pathlib import Path
from datetime import datetime

class SimpleErrorPrevention:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.workspace_path = Path(__file__).parent.parent
        self.is_venv = (self.workspace_path / "venv").exists()
    
    def get_correct_pytest_command(self):
        """올바른 pytest 명령어 반환"""
        if self.is_windows and self.is_venv:
            return 'powershell -Command "& { .\\venv\\Scripts\\python.exe -m pytest -v }"'
        elif self.is_windows:
            return "python -m pytest -v"
        elif self.is_venv:
            return "./venv/bin/python -m pytest -v"
        else:
            return "python3 -m pytest -v"
    
    def get_correct_python_command(self):
        """올바른 python 명령어 반환"""
        if self.is_windows and self.is_venv:
            return ".\\venv\\Scripts\\python.exe"
        elif self.is_windows:
            return "python"
        elif self.is_venv:
            return "./venv/bin/python"
        else:
            return "python3"
    
    def check_command(self, command):
        """명령어 확인 및 수정 제안"""
        command = command.strip().lower()
        
        if command in ["pytest", "pytest -v"]:
            correct = self.get_correct_pytest_command()
            return f"권장 명령어: {correct}"
        
        if command.startswith("python") and not command.startswith(".\\venv"):
            correct = self.get_correct_python_command()
            return f"권장 명령어: {correct} (나머지 인수 포함)"
        
        return "명령어가 올바른 것 같습니다."
    
    def get_environment_info(self):
        """환경 정보 반환"""
        return {
            "os": "Windows" if self.is_windows else "Linux/MacOS",
            "venv": "활성화됨" if self.is_venv else "비활성화됨",
            "workspace": str(self.workspace_path)
        }
    
    def get_tips(self):
        """예방 팁 반환"""
        tips = []
        env = self.get_environment_info()
        
        tips.append(f"현재 환경: {env['os']}, 가상환경: {env['venv']}")
        
        if self.is_windows and self.is_venv:
            tips.extend([
                "pytest 실행: " + self.get_correct_pytest_command(),
                "Python 실행: " + self.get_correct_python_command(),
                "복잡한 명령어는 powershell -Command로 감싸기"
            ])
        elif self.is_windows:
            tips.extend([
                "pytest 실행: python -m pytest -v",
                "복잡한 명령어는 powershell -Command로 감싸기"
            ])
        
        tips.extend([
            "명령어 실행 전 파일 존재 확인",
            "경로에 공백이 있으면 따옴표로 감싸기",
            "환경변수 설정 확인"
        ])
        
        return tips

def main():
    eps = SimpleErrorPrevention()
    
    print("오류 방지 시스템")
    print("=" * 40)
    
    for tip in eps.get_tips():
        print(f"- {tip}")
    
    print("\n환경 정보:")
    env = eps.get_environment_info()
    for key, value in env.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()