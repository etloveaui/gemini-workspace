#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🚀 자동 디스패치 시스템 - 스마트 디스패처 + 자동 실행"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from smart_dispatcher import SmartDispatcher

sys.stdout.reconfigure(encoding='utf-8')

def execute_task(agent: str, task: str, workspace_root: Path) -> dict:
    """에이전트별 작업 실행"""
    
    # 에이전트별 실행 명령어
    commands = {
        'claude': ['python', 'claude.py', task],
        'codex': ['python', 'ma.py', 'codex', task],
        'gemini': ['python', 'ma.py', 'gemini', task]
    }
    
    if agent not in commands:
        return {
            'success': False,
            'error': f'Unknown agent: {agent}',
            'output': '',
            'agent': agent,
            'task': task
        }
    
    try:
        # 명령어 실행
        print(f"🚀 {agent.upper()} 에이전트 실행 중...")
        print(f"📝 작업: {task}")
        print(f"⚡ 명령어: {' '.join(commands[agent])}")
        print("-" * 50)
        
        result = subprocess.run(
            commands[agent], 
            cwd=workspace_root,
            capture_output=True, 
            text=True,
            encoding='utf-8',
            timeout=300  # 5분 제한
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'output': result.stdout,
            'error': result.stderr,
            'agent': agent,
            'task': task,
            'timestamp': datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout: 작업이 5분을 초과했습니다',
            'output': '',
            'agent': agent,
            'task': task
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'실행 오류: {str(e)}',
            'output': '',
            'agent': agent,
            'task': task
        }

def save_execution_log(result: dict, workspace_root: Path):
    """실행 결과 로그 저장"""
    logs_dir = workspace_root / 'logs' / 'auto_dispatch'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f"{result['agent']}_{timestamp}.json"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return log_file

def main():
    """메인 자동 디스패치 시스템"""
    workspace_root = Path(__file__).parent.parent
    
    if len(sys.argv) < 2:
        print("🚀 자동 디스패치 시스템 v1.0")
        print("작업을 분석하여 최적 에이전트를 선택하고 자동 실행합니다")
        print()
        print("사용법: python scripts/auto_dispatch.py \"작업 내용\"")
        print()
        print("예시:")
        print("  python scripts/auto_dispatch.py \"코딩 버그 수정\"")
        print("  python scripts/auto_dispatch.py \"아키텍처 설계\"")
        print("  python scripts/auto_dispatch.py \"파일 정리\"")
        print()
        print("옵션:")
        print("  --dry-run : 실제 실행 없이 분석만 수행")
        print("  --verbose : 상세 정보 출력")
        return
    
    task = " ".join([arg for arg in sys.argv[1:] if not arg.startswith('--')])
    dry_run = '--dry-run' in sys.argv
    verbose = '--verbose' in sys.argv
    
    # 1. 스마트 디스패치 분석
    print("🧠 스마트 디스패처 분석 중...")
    dispatcher = SmartDispatcher(workspace_root)
    dispatch_result = dispatcher.dispatch(task)
    
    print(f"✅ 분석 완료:")
    print(f"   🤖 선택된 에이전트: {dispatch_result['selected_agent'].upper()}")
    print(f"   📊 신뢰도: {dispatch_result['confidence']:.1%}")
    print(f"   💡 이유: {dispatch_result['reason']}")
    print(f"   ⚡ 우선순위: {dispatch_result['priority']}")
    
    if verbose:
        print(f"   📈 전체 점수: {dispatch_result['all_scores']}")
    
    print()
    
    if dry_run:
        print("🔍 Dry-run 모드: 실제 실행하지 않습니다")
        print(f"실행될 명령어: python ma.py {dispatch_result['selected_agent']} \"{task}\"")
        return
    
    # 2. 에이전트 실행
    agent = dispatch_result['selected_agent']
    
    # 사용자 확인 (신뢰도가 낮은 경우)
    if dispatch_result['confidence'] < 0.7:
        print(f"⚠️  신뢰도가 {dispatch_result['confidence']:.1%}로 낮습니다")
        try:
            confirm = input("계속 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', '예']:
                print("❌ 사용자가 취소했습니다")
                return
        except (EOFError, KeyboardInterrupt):
            print("\\n❌ 사용자가 취소했습니다")
            return
    
    # 3. 실행 및 결과 처리
    execution_result = execute_task(agent, task, workspace_root)
    
    # 4. 결과 출력
    print("=" * 60)
    if execution_result['success']:
        print("✅ 작업 성공적으로 완료!")
        if execution_result['output']:
            print("📤 출력:")
            print(execution_result['output'])
    else:
        print("❌ 작업 실행 실패")
        print(f"🔍 오류: {execution_result['error']}")
        if execution_result['output']:
            print("📤 부분 출력:")
            print(execution_result['output'])
    
    # 5. 로그 저장
    log_file = save_execution_log(execution_result, workspace_root)
    print(f"📋 실행 로그: {log_file}")
    
    # 6. 피드백 수집 (선택적)
    if execution_result['success']:
        print("\\n💭 이 결과가 만족스러우셨나요? (향후 개선을 위해)")
        try:
            feedback = input("평점 (1-5, Enter는 건너뛰기): ").strip()
            if feedback and feedback.isdigit():
                # 피드백 저장 (향후 학습용)
                feedback_data = {
                    'dispatch_result': dispatch_result,
                    'execution_result': execution_result,
                    'user_rating': int(feedback),
                    'timestamp': datetime.now().isoformat()
                }
                
                feedback_file = workspace_root / 'logs' / 'dispatcher_feedback.jsonl'
                with open(feedback_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(feedback_data, ensure_ascii=False) + '\\n')
                
                print("📝 피드백 감사합니다! 시스템 개선에 활용하겠습니다")
        except (EOFError, KeyboardInterrupt):
            pass

if __name__ == "__main__":
    main()