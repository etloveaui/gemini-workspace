#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🌟 멀티 에이전트 워크스페이스 온보딩 시스템 - 신규 사용자 가이드"""

import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def welcome_message():
    """환영 메시지 및 시스템 소개"""
    print("🌟 멀티 에이전트 워크스페이스에 오신 것을 환영합니다!")
    print("=" * 60)
    print()
    print("🎯 이 시스템은 Claude, Gemini, Codex 3개 AI 에이전트가")
    print("   협업하여 개발 작업을 수행하는 고도화된 워크스페이스입니다.")
    print()
    print("🚀 5분 만에 시작할 수 있습니다!")
    print()

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
    
    print("📋 단계별 설정 가이드:")
    print("-" * 40)
    
    for step in steps:
        print(f"\n{step['title']}")
        print(f"  📝 {step['description']}")
        print(f"  ⌨️  명령어: {step['command']}")
        print(f"  ✨ 예상 결과: {step['expected']}")
    
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
    
    print("🔧 자주 발생하는 문제 해결:")
    print("-" * 40)
    
    for issue in issues:
        print(f"\n❌ {issue['problem']}")
        print(f"  💡 해결책: {issue['solution']}")
        print(f"  📝 설명: {issue['description']}")
    
    print()

def next_steps():
    """다음 단계 안내"""
    print("🎯 이제 시작할 준비가 되었습니다!")
    print("-" * 40)
    print()
    print("📚 추가 학습 자료:")
    print("  • docs/HELP.md - 상세 도움말")
    print("  • CLAUDE.md, GEMINI.md, AGENTS.md - 각 에이전트 설정 가이드")
    print("  • docs/HUB.md - 현재 진행 프로젝트 현황")
    print()
    print("🚀 첫 번째 작업 추천:")
    print("  1. python scripts/doctor.py로 시스템 상태 확인")
    print("  2. 간단한 질문으로 Claude 에이전트 테스트")
    print("  3. docs/HUB.md에서 관심 있는 프로젝트 확인")
    print()
    print("💬 도움이 필요하면:")
    print("  • python scripts/quick_help.py troubleshoot")
    print("  • communication/ 폴더의 각 에이전트별 가이드 참고")
    print()
    print("🎉 멀티 에이전트 워크스페이스와 함께 즐거운 개발하세요!")

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