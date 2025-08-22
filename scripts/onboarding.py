#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""멀티 에이전트 워크스페이스 온보딩 시스템 - 신규 사용자 가이드 (단순 텍스트 출력)"""

import sys
import os
from pathlib import Path
from cli_style import header, section, item, kv

sys.stdout.reconfigure(encoding='utf-8')

def welcome_message():
    """환영 메시지 및 시스템 소개"""
    print(header("Onboarding"))
    print(kv("Intro", "Claude, Gemini, Codex 협업 워크스페이스"))
    print(kv("Getting Started", "5분 내 시작 가능"))
    print("===")

def step_by_step_guide():
    """단계별 설정 가이드"""
    steps = [
        {
            'title': '1단계: 환경 검증',
            'description': '시스템 환경이 올바르게 설정되었는지 확인합니다',
            'command': 'python scripts/doctor.py',
            'expected': '✅ 통과 항목들과 📋 진단 보고서 확인'
        },
        {
            'title': '2단계: 빠른 도움말 확인',
            'description': '주요 명령어와 사용법을 익힙니다',
            'command': 'python scripts/quick_help.py',
            'expected': '💡 주요 명령어들과 🔧 문제 해결 가이드 표시'
        },
        {
            'title': '3단계: 현재 상태 점검',
            'description': '워크스페이스 상태와 설정 파일들을 확인합니다',
            'command': 'python scripts/quick_help.py status',
            'expected': '✅ 핵심 설정 파일들과 📈 최근 활동 내역'
        },
        {
            'title': '4단계: HUB 확인',
            'description': '현재 진행 중인 작업들을 파악합니다',
            'command': 'type docs\\HUB.md | more  # Windows',
            'expected': '🚀 활성 작업 목록과 완료된 작업들 확인'
        },
        {
            'title': '5단계: 첫 번째 에이전트 사용',
            'description': 'Claude 에이전트에게 간단한 작업을 요청해봅니다',
            'command': 'python claude.py "현재 워크스페이스 상태를 알려주세요"',
            'expected': '🤖 Claude가 현재 상태와 가능한 작업들을 안내'
        }
    ]
    
    print(section("Step-by-step Guide"))
    
    for step in steps:
        print()
        print(step['title'])
        print(kv('Description', step['description']))
        print(kv('Command', step['command']))
        print(kv('Expected', step['expected']))
    
    print()

def common_issues():
    """자주 발생하는 문제와 해결책"""
    issues = [
        {
            'problem': '인코딩 오류 (한글 깨짐)',
            'solution': 'scripts\\windows_wrapper.ps1 -Command encoding-check',
            'description': 'Windows 콘솔 인코딩을 UTF-8로 설정'
        },
        {
            'problem': 'Git 커밋 실패',
            'solution': 'scripts\\windows_wrapper.ps1 -Command git-commit -Message "메시지"',
            'description': 'Windows 안전 모드로 Git 커밋 수행'
        },
        {
            'problem': '가상환경 미활성화',
            'solution': 'venv\\Scripts\\activate.bat',
            'description': 'Python 가상환경 활성화'
        },
        {
            'problem': 'API 키 오류',
            'solution': 'secrets\\my_sensitive_data.md 파일 확인',
            'description': '각 에이전트별 API 키 설정 확인'
        }
    ]
    
    print(section("Common Issues"))
    
    for issue in issues:
        print()
        print(section(issue['problem']))
        print(kv('Solution', issue['solution']))
        print(kv('Note', issue['description']))
    
    print()

def next_steps():
    """다음 단계 안내"""
    print(header("Next Steps"))
    print(section("Resources"))
    print(item(1, "docs/HELP.md - 상세 도움말"))
    print(item(2, "CLAUDE.md, GEMINI.md, AGENTS.md - 에이전트 설정"))
    print(item(3, "docs/HUB.md - 프로젝트 현황"))
    print(section("Try This"))
    print(item(1, "python scripts/doctor.py"))
    print(item(2, "python claude.py '현재 워크스페이스 상태'"))
    print(item(3, "docs/HUB.md 검토"))
    print(section("Help"))
    print(item(1, "python scripts/quick_help.py troubleshoot"))
    print(item(2, "communication/ 각 에이전트 가이드 확인"))

def main():
    """메인 온보딩 함수"""
    welcome_message()
    
    print("원하는 섹션을 선택하세요:")
    print("1. 단계별 설정 가이드")
    print("2. 자주 발생하는 문제 해결")
    print("3. 다음 단계 안내")
    print("4. 전체 가이드 보기")
    print()
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        try:
            choice = input("선택 (1-4, Enter는 전체): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "4"
    
    if not choice:
        choice = "4"
    
    print()
    
    if choice == "1":
        step_by_step_guide()
    elif choice == "2":
        common_issues()
    elif choice == "3":
        next_steps()
    elif choice == "4":
        step_by_step_guide()
        common_issues()
        next_steps()
    else:
        print("❌ 잘못된 선택입니다. 전체 가이드를 표시합니다.")
        print()
        step_by_step_guide()
        common_issues()
        next_steps()

if __name__ == "__main__":
    main()
