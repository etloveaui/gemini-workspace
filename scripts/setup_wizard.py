#!/usr/bin/env python3
"""
설정 마법사 v1.0 - 한 번의 클릭으로 모든 설정 완료
Phase1 사용자 경험 개선의 첫 번째 실제 구현
"""
import os
import sys
import shutil
from pathlib import Path
import subprocess
import platform

def print_header(text):
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step, text):
    print(f"{step}) {text}")

def check_system():
    """시스템 환경 자동 감지"""
    print_header("시스템 환경 자동 감지")
    
    info = {
        'os': platform.system(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'workspace': Path.cwd(),
        'has_git': shutil.which('git') is not None,
        'has_invoke': shutil.which('invoke') is not None,
        'in_venv': sys.prefix != sys.base_prefix
    }
    
    print_step(1, f"운영체제: {info['os']}")
    print_step(2, f"Python 버전: {info['python_version']}")
    print_step(3, f"작업공간: {info['workspace']}")
    print_step(4, f"Git 설치: {'✅ 설치됨' if info['has_git'] else '❌ 없음'}")
    print_step(5, f"Invoke 설치: {'✅ 설치됨' if info['has_invoke'] else '❌ 없음'}")
    print_step(6, f"가상환경: {'✅ 활성화' if info['in_venv'] else '❌ 미활성화'}")
    
    return info

def auto_fix_issues(info):
    """발견된 문제 자동 해결"""
    print_header("문제점 자동 해결 중")
    fixes_applied = []
    
    # 1. Invoke 설치
    if not info['has_invoke']:
        print_step(1, "Invoke 설치 중...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'invoke'], 
                         check=True, capture_output=True)
            print("   ✅ Invoke 설치 완료")
            fixes_applied.append("Invoke 자동 설치")
        except:
            print("   ❌ Invoke 설치 실패 - 수동 설치 필요")
    
    # 2. 필수 디렉토리 생성
    required_dirs = ['scripts', 'docs', 'communication', 'secrets', '.agents']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True, parents=True)
            print_step(2, f"{dir_name} 디렉토리 생성")
            fixes_applied.append(f"{dir_name} 디렉토리 생성")
    
    # 3. 에이전트별 communication 폴더
    agent_dirs = ['claude', 'gemini', 'codex']
    comm_path = Path('communication')
    for agent in agent_dirs:
        agent_path = comm_path / agent
        if not agent_path.exists():
            agent_path.mkdir(exist_ok=True, parents=True)
            fixes_applied.append(f"{agent} communication 폴더 생성")
    
    # 4. 기본 설정 파일 생성
    if not Path('ma.py').exists():
        print_step(3, "기본 CLI 스크립트 확인 중...")
        print("   ⚠️ ma.py 파일이 없습니다. 수동 설정이 필요할 수 있습니다.")
    
    return fixes_applied

def setup_vscode_integration():
    """VS Code 통합 설정"""
    print_header("VS Code 통합 설정")
    
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    # tasks.json 확인 및 최소 설정 제안
    tasks_file = vscode_dir / 'tasks.json'
    if not tasks_file.exists():
        print_step(1, "VS Code 작업 설정 생성 중...")
        basic_tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "System Status",
                    "type": "shell",
                    "command": "python",
                    "args": ["scripts/dashboard.py"],
                    "group": "build"
                }
            ]
        }
        
        import json
        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(basic_tasks, f, indent=4)
        
        print("   ✅ 기본 VS Code 작업 설정 생성")
        return ["VS Code 작업 설정 생성"]
    else:
        print_step(1, "VS Code 설정 이미 존재함")
        return []

def run_system_check():
    """시스템 검사 실행"""
    print_header("시스템 최종 검사")
    
    # doctor.py 실행 시도
    doctor_path = Path('scripts/doctor.py')
    if doctor_path.exists():
        print_step(1, "시스템 진단 실행 중...")
        try:
            result = subprocess.run([sys.executable, str(doctor_path)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("   ✅ 시스템 진단 통과")
                return True
            else:
                print("   ⚠️ 시스템 진단 경고 - 수동 확인 필요")
                return False
        except:
            print("   ❌ 시스템 진단 실패")
            return False
    else:
        print_step(1, "시스템 진단 도구 없음")
        return False

def main():
    print_header("멀티 에이전트 워크스페이스 설정 마법사 v1.0")
    print("이 도구가 자동으로 환경을 설정해드립니다.")
    print()
    
    try:
        # 1. 시스템 환경 감지
        system_info = check_system()
        
        # 2. 문제 자동 해결
        fixes = auto_fix_issues(system_info)
        
        # 3. VS Code 통합
        vscode_fixes = setup_vscode_integration()
        fixes.extend(vscode_fixes)
        
        # 4. 최종 검사
        system_ok = run_system_check()
        
        # 5. 결과 요약
        print_header("설정 완료!")
        print(f"적용된 수정사항: {len(fixes)}개")
        for i, fix in enumerate(fixes, 1):
            print(f"  {i}) {fix}")
        
        if system_ok:
            print("\n✅ 모든 설정이 완료되었습니다!")
            print("다음 명령어로 시작하세요:")
            print("  python scripts/dashboard.py")
        else:
            print("\n⚠️ 일부 설정에 문제가 있을 수 있습니다.")
            print("docs/CORE/HUB_ENHANCED.md를 확인하여 수동 설정을 진행하세요.")
            
    except KeyboardInterrupt:
        print("\n설정이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("수동 설정이 필요할 수 있습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()