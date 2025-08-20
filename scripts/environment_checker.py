#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🔍 환경 차이 진단 도구 - 집/회사 환경 차이점 분석"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def get_git_config() -> Dict[str, str]:
    """Git 설정 정보 수집"""
    try:
        result = subprocess.run(['git', 'config', '--list'], 
                              capture_output=True, text=True, encoding='utf-8')
        config = {}
        for line in result.stdout.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
        return config
    except Exception as e:
        return {'error': str(e)}

def get_system_info() -> Dict[str, Any]:
    """시스템 정보 수집"""
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'python_executable': sys.executable,
        'encoding': sys.getdefaultencoding(),
        'filesystem_encoding': sys.getfilesystemencoding(),
        'locale_encoding': sys.getdefaultencoding(),
    }

def get_env_variables() -> Dict[str, str]:
    """주요 환경 변수 수집"""
    important_vars = [
        'PATH', 'PYTHONPATH', 'PYTHONIOENCODING', 'PYTHONUTF8',
        'HOME', 'USERPROFILE', 'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV',
        'LANG', 'LC_ALL', 'SHELL', 'ComSpec', 'TERM'
    ]
    
    env_vars = {}
    for var in important_vars:
        env_vars[var] = os.environ.get(var, 'NOT_SET')
    
    return env_vars

def get_python_packages() -> Dict[str, str]:
    """설치된 주요 Python 패키지 버전"""
    important_packages = ['invoke', 'requests', 'sqlite3', 'pathlib']
    packages = {}
    
    for pkg in important_packages:
        try:
            if pkg == 'sqlite3':
                import sqlite3
                packages[pkg] = sqlite3.sqlite_version
            else:
                result = subprocess.run([sys.executable, '-c', f'import {pkg}; print({pkg}.__version__)'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    packages[pkg] = result.stdout.strip()
                else:
                    packages[pkg] = 'NOT_INSTALLED'
        except Exception:
            packages[pkg] = 'ERROR'
    
    return packages

def check_workspace_permissions() -> Dict[str, Any]:
    """워크스페이스 권한 체크"""
    workspace_root = Path(__file__).parent.parent
    
    permissions = {
        'workspace_readable': os.access(workspace_root, os.R_OK),
        'workspace_writable': os.access(workspace_root, os.W_OK),
        'workspace_executable': os.access(workspace_root, os.X_OK),
        'secrets_exists': (workspace_root / 'secrets').exists(),
        'venv_exists': (workspace_root / 'venv').exists(),
        'git_exists': (workspace_root / '.git').exists(),
    }
    
    # 파일 생성 테스트
    try:
        test_file = workspace_root / '.env_test_temp'
        test_file.write_text('test', encoding='utf-8')
        test_file.unlink()
        permissions['file_creation_ok'] = True
    except Exception as e:
        permissions['file_creation_ok'] = False
        permissions['file_creation_error'] = str(e)
    
    return permissions

def detect_environment_type() -> str:
    """환경 타입 감지 (집/회사 구분)"""
    # 컴퓨터명, 네트워크, 경로 등을 통한 추론
    computer_name = platform.node()
    user_profile = os.environ.get('USERPROFILE', '')
    
    # 간단한 휴리스틱
    indicators = {
        'home_indicators': ['home', 'personal', 'etlov'],
        'work_indicators': ['work', 'corp', 'company', 'office']
    }
    
    environment = 'unknown'
    
    # 컴퓨터명 기반 추론
    computer_lower = computer_name.lower()
    if any(indicator in computer_lower for indicator in indicators['home_indicators']):
        environment = 'home'
    elif any(indicator in computer_lower for indicator in indicators['work_indicators']):
        environment = 'work'
    
    # 사용자 경로 기반 추론
    if 'etlov' in user_profile.lower():
        environment = 'home'
    
    return environment

def analyze_differences(current_data: Dict, reference_data: Dict = None) -> Dict[str, Any]:
    """환경 차이점 분석"""
    if not reference_data:
        # 기본 예상 설정 (회사 환경 기준)
        reference_data = {
            'git_config': {
                'user.name': 'El Fenomeno',
                'user.email': 'etloveaui@gmail.com',
                'core.autocrlf': 'true',
                'core.quotepath': 'false'
            }
        }
    
    differences = {}
    
    # Git 설정 비교
    if 'git_config' in current_data and 'git_config' in reference_data:
        git_diffs = {}
        for key, expected_value in reference_data['git_config'].items():
            current_value = current_data['git_config'].get(key, 'MISSING')
            if current_value != expected_value:
                git_diffs[key] = {
                    'expected': expected_value,
                    'current': current_value
                }
        differences['git_config'] = git_diffs
    
    return differences

def generate_recommendations(data: Dict[str, Any]) -> List[str]:
    """환경 개선 권장사항 생성"""
    recommendations = []
    
    # Git 설정 권장사항
    git_config = data.get('git_config', {})
    if git_config.get('core.quotepath', '').lower() != 'false':
        recommendations.append("git config --global core.quotepath false (한글 파일명 문제 해결)")
    
    if git_config.get('core.autocrlf', '').lower() != 'true':
        recommendations.append("git config --global core.autocrlf true (Windows CRLF 처리)")
    
    # 인코딩 관련
    env_vars = data.get('environment_variables', {})
    if env_vars.get('PYTHONIOENCODING', '') != 'utf-8':
        recommendations.append("환경 변수 PYTHONIOENCODING=utf-8 설정")
    
    if env_vars.get('PYTHONUTF8', '') != '1':
        recommendations.append("환경 변수 PYTHONUTF8=1 설정")
    
    # 권한 관련
    permissions = data.get('workspace_permissions', {})
    if not permissions.get('workspace_writable', True):
        recommendations.append("워크스페이스 쓰기 권한 확인 필요")
    
    return recommendations

def main():
    """메인 진단 함수"""
    # Windows 인코딩 문제 해결
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    print("🔍 멀티 에이전트 워크스페이스 환경 진단 시작\n")
    
    # 데이터 수집
    diagnosis_data = {
        'timestamp': datetime.now().isoformat(),
        'environment_type': detect_environment_type(),
        'system_info': get_system_info(),
        'git_config': get_git_config(),
        'environment_variables': get_env_variables(),
        'python_packages': get_python_packages(),
        'workspace_permissions': check_workspace_permissions(),
    }
    
    # 결과 출력
    print(f"🏠 감지된 환경: {diagnosis_data['environment_type'].upper()}")
    print(f"🖥️  시스템: {diagnosis_data['system_info']['platform']}")
    print(f"🐍 Python: {diagnosis_data['system_info']['python_version'].split()[0]}")
    print(f"📧 Git 사용자: {diagnosis_data['git_config'].get('user.name', 'NOT_SET')} <{diagnosis_data['git_config'].get('user.email', 'NOT_SET')}>")
    
    # 차이점 분석
    differences = analyze_differences(diagnosis_data)
    if differences:
        print("\n⚠️  감지된 차이점:")
        for category, diffs in differences.items():
            if diffs:
                print(f"  {category}:")
                for key, diff in diffs.items():
                    print(f"    {key}: {diff['current']} (예상: {diff['expected']})")
    
    # 권장사항
    recommendations = generate_recommendations(diagnosis_data)
    if recommendations:
        print("\n💡 개선 권장사항:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("\n✅ 환경 설정이 최적화되어 있습니다")
    
    # 보고서 저장
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / f"environment_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(diagnosis_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 상세 보고서: {report_file}")
    
    # Windows 래퍼 사용 안내
    print("\n🔧 Windows 환경 최적화:")
    print("  scripts/windows_wrapper.ps1 -Command encoding-check")
    print("  scripts/windows_wrapper.ps1 -Command git-commit -Message 'message'")

if __name__ == "__main__":
    main()