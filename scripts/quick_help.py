#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🚀 빠른 도움말 시스템 - 멀티 에이전트 워크스페이스용 사용자 경험 개선"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 🎯 핵심 명령어 가이드
QUICK_COMMANDS = {
    'start': {
        'description': '워크스페이스 시작하기',
        'commands': [
            'python scripts/doctor.py  # 환경 검증',
            'invoke start  # 시스템 시작',
            'python scripts/quick_help.py status  # 현재 상태 확인'
        ]
    },
    'commit': {
        'description': 'Git 커밋 (Windows 안전모드)',
        'commands': [
            'scripts/windows_wrapper.ps1 -Command git-commit -Message "메시지"',
            '또는 기본: git add . && git commit -m "메시지"'
        ]
    },
    'agents': {
        'description': '에이전트 관련 명령어',
        'commands': [
            'python ma.py gemini "작업 내용"  # Gemini 에이전트',
            'python ma.py codex "코딩 작업"  # Codex 에이전트',
            'python ma.py claude "통합 작업"  # Claude 에이전트'
        ]
    },
    'diagnosis': {
        'description': '문제 진단 도구',
        'commands': [
            'python scripts/doctor.py  # 전체 시스템 진단',
            'python scripts/environment_checker.py  # 환경 차이 분석',
            'scripts/windows_wrapper.ps1 -Command encoding-check  # 인코딩 확인'
        ]
    }
}

# 🛠️ 문제 해결 가이드
TROUBLESHOOTING = {
    '인코딩 오류': {
        'symptoms': ['UnicodeEncodeError', '한글 깨짐', 'cp949 오류'],
        'solutions': [
            'scripts/windows_wrapper.ps1 -Command encoding-check',
            'PowerShell에서 실행: chcp 65001',
            '환경변수 설정: PYTHONIOENCODING=utf-8'
        ]
    },
    'Git 커밋 실패': {
        'symptoms': ['커밋 메시지 오류', '경로 문제', 'CRLF 경고'],
        'solutions': [
            'scripts/windows_wrapper.ps1 -Command git-commit -Message "메시지"',
            'git config --global core.autocrlf true',
            'git config --global core.quotepath false'
        ]
    },
    '가상환경 문제': {
        'symptoms': ['ModuleNotFoundError', 'venv 미활성화'],
        'solutions': [
            'venv\\Scripts\\activate.bat  # Windows',
            'python scripts/doctor.py  # 환경 검증',
            'pip install -r requirements.txt'
        ]
    },
    '에이전트 통신 실패': {
        'symptoms': ['API 오류', '토큰 제한', '응답 없음'],
        'solutions': [
            'docs/HUB.md에서 현재 진행 작업 확인',
            'usage.db 토큰 사용량 확인',
            'secrets/my_sensitive_data.md API 키 확인'
        ]
    }
}

def show_quick_guide(topic: str = None):
    """빠른 가이드 표시"""
    print("🚀 멀티 에이전트 워크스페이스 - 빠른 도움말\n")
    
    if not topic or topic == 'all':
        print("📋 주요 명령어:")
        for cmd, info in QUICK_COMMANDS.items():
            print(f"\n💡 {info['description']}:")
            for command in info['commands']:
                print(f"  {command}")
        
        print(f"\n🔧 문제 해결: python scripts/quick_help.py troubleshoot")
        print(f"📊 현재 상태: python scripts/quick_help.py status")
        
    elif topic in QUICK_COMMANDS:
        cmd_info = QUICK_COMMANDS[topic]
        print(f"💡 {cmd_info['description']}:")
        for command in cmd_info['commands']:
            print(f"  {command}")
    else:
        print(f"❌ 알 수 없는 주제: {topic}")
        print(f"💡 사용 가능한 주제: {', '.join(QUICK_COMMANDS.keys())}")

def show_troubleshooting():
    """문제 해결 가이드 표시"""
    print("🔧 자주 발생하는 문제 해결 가이드\n")
    
    for problem, info in TROUBLESHOOTING.items():
        print(f"❌ {problem}:")
        print(f"  증상: {', '.join(info['symptoms'])}")
        print(f"  해결책:")
        for solution in info['solutions']:
            print(f"    • {solution}")
        print()

def show_status():
    """현재 워크스페이스 상태 표시"""
    print("📊 워크스페이스 현재 상태\n")
    
    workspace_root = Path(__file__).parent.parent
    
    # 기본 구조 확인
    status = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'workspace_path': str(workspace_root),
        'key_files': {},
        'recent_activity': {}
    }
    
    # 핵심 파일 확인
    key_files = {
        'CLAUDE.md': 'Claude 설정',
        'GEMINI.md': 'Gemini 설정', 
        'AGENTS.md': 'Codex 설정',
        'docs/HUB.md': '작업 허브',
        'usage.db': '사용량 DB',
        'secrets/my_sensitive_data.md': '민감 정보'
    }
    
    for file_path, description in key_files.items():
        full_path = workspace_root / file_path
        exists = full_path.exists()
        icon = "✅" if exists else "❌"
        status['key_files'][file_path] = exists
        print(f"  {icon} {description}: {file_path}")
    
    # 최근 활동 확인
    print(f"\n📈 최근 활동:")
    
    # Git 최근 커밋
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True, cwd=workspace_root)
        if result.returncode == 0:
            print(f"  🔄 최근 커밋:")
            for line in result.stdout.strip().split('\n')[:3]:
                if line:
                    print(f"    {line}")
        status['recent_activity']['git_available'] = True
    except Exception:
        print(f"  ❌ Git 히스토리 조회 실패")
        status['recent_activity']['git_available'] = False
    
    # 보고서 파일 확인
    reports_dir = workspace_root / 'reports'
    if reports_dir.exists():
        report_files = list(reports_dir.glob('*.json'))
        if report_files:
            latest_report = max(report_files, key=os.path.getctime)
            print(f"  📋 최신 보고서: {latest_report.name}")
            status['recent_activity']['latest_report'] = str(latest_report)
    
    # 상태 저장
    status_file = workspace_root / 'reports' / f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    status_file.parent.mkdir(exist_ok=True)
    
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 상세 상태 보고서: {status_file}")

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        show_quick_guide()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'troubleshoot':
        show_troubleshooting()
    elif command == 'status':
        show_status()
    elif command in QUICK_COMMANDS:
        show_quick_guide(command)
    elif command == 'all':
        show_quick_guide('all')
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        print(f"\n사용법: python scripts/quick_help.py [명령어]")
        print(f"명령어: {', '.join(['all', 'troubleshoot', 'status'] + list(QUICK_COMMANDS.keys()))}")

if __name__ == "__main__":
    main()