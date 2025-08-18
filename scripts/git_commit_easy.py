#!/usr/bin/env python3
"""
간편한 Git 커밋 스크립트 - pre-commit 훅 우회
사용자가 pre-commit 훅 문제로 커밋하지 못할 때 사용
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_command(command, shell=True):
    """명령어 실행"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_git_status():
    """Git 상태 확인"""
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        return False, []
    
    changes = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            changes.append(line)
    return len(changes) > 0, changes

def commit_with_bypass(message=None, add_all=True):
    """pre-commit 훅을 우회하여 커밋"""
    print("[INFO] Git 커밋 (pre-commit 훅 우회)")
    print("=" * 50)
    
    # Git 상태 확인
    has_changes, changes = get_git_status()
    if not has_changes:
        print("[INFO] 커밋할 변경사항이 없습니다.")
        return True
    
    print(f"[INFO] {len(changes)}개 변경사항 발견")
    
    # 모든 변경사항 추가
    if add_all:
        print("[INFO] 모든 변경사항을 스테이징 중...")
        success, stdout, stderr = run_command("git add .")
        if not success:
            print(f"[ERROR] git add 실패: {stderr}")
            return False
        print("[SUCCESS] 스테이징 완료")
    
    # 커밋 메시지 생성
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"작업 진행 백업 ({timestamp})"
    
    print(f"[INFO] 커밋 메시지: {message}")
    
    # --no-verify 옵션으로 커밋 (pre-commit 훅 우회)
    commit_command = f'git commit --no-verify -m "{message}"'
    print(f"[INFO] 실행 중: {commit_command}")
    
    success, stdout, stderr = run_command(commit_command)
    
    if success:
        print("[SUCCESS] 커밋 완료!")
        print(stdout)
        return True
    else:
        print(f"[ERROR] 커밋 실패: {stderr}")
        return False

def push_changes():
    """변경사항 푸시"""
    print("[INFO] 원격 저장소로 푸시 중...")
    success, stdout, stderr = run_command("git push")
    
    if success:
        print("[SUCCESS] 푸시 완료!")
        return True
    else:
        print(f"[ERROR] 푸시 실패: {stderr}")
        return False

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="간편한 Git 커밋 (pre-commit 훅 우회)")
    parser.add_argument("--message", "-m", help="커밋 메시지")
    parser.add_argument("--no-push", action="store_true", help="푸시하지 않음")
    parser.add_argument("--no-add", action="store_true", help="자동으로 add하지 않음")
    
    args = parser.parse_args()
    
    # 커밋 실행
    success = commit_with_bypass(args.message, not args.no_add)
    
    if success and not args.no_push:
        # 푸시 실행
        push_success = push_changes()
        if push_success:
            print("\n[SUCCESS] 모든 작업 완료!")
        else:
            print("\n[WARNING] 커밋은 성공했지만 푸시 실패")
    elif success:
        print("\n[SUCCESS] 커밋 완료! (푸시 생략)")
        print("수동 푸시: git push")
    else:
        print("\n[ERROR] 커밋 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()