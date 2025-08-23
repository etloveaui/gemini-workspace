#!/usr/bin/env python3
"""멀티 에이전트 워크스페이스 통합 CLI"""
import sys
import subprocess
from pathlib import Path

def auto_cleanup_startup():
    """시스템 시작시 자동 정리 실행"""
    try:
        workspace = Path(__file__).parent
        # Claude comm 정리
        subprocess.run([sys.executable, workspace / "scripts/claude_comm_cleaner.py"], 
                      capture_output=True, text=True, encoding='utf-8')
        # 전체 파일 정리
        subprocess.run([sys.executable, workspace / ".agents/file_organizer.py"], 
                      capture_output=True, text=True)
        print("[CLEANUP] 자동 정리 완료")
    except Exception as e:
        print(f"자동 정리 실패: {e}")

def auto_environment_detect():
    """시스템 시작시 환경 자동 감지"""
    try:
        workspace = Path(__file__).parent
        result = subprocess.run([sys.executable, workspace / "scripts/environment_detector.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            # 환경 감지 결과에서 위치 정보 추출
            if "company" in result.stdout:
                print("[ENV] 회사 환경 감지됨")
            elif "home" in result.stdout:
                print("[ENV] 집 환경 감지됨") 
            elif "laptop" in result.stdout:
                print("[ENV] 노트북 환경 감지됨")
            else:
                print("[ENV] 환경 감지 완료")
    except Exception as e:
        print(f"환경 감지 실패: {e}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python ma.py <command> [args...]")
        print("명령어:")
        print("  status    - 에이전트 상태")
        print("  add <task> - 작업 추가") 
        print("  search <query> - Context7 검색")
        print("  backup    - 백업 실행")
        print("  cleanup   - 자동 정리 실행")
        print("  env       - 환경 감지 실행")
        # 시작시 자동 실행
        auto_environment_detect()
        auto_cleanup_startup()
        return
    
    command = sys.argv[1]
    workspace = Path(__file__).parent
    
    if command == "status":
        subprocess.run([sys.executable, workspace / ".agents/multi_agent_manager.py", "status"])
    elif command == "add":
        if len(sys.argv) < 3:
            print("사용법: ma.py add <task_name> [priority] [agent]")
            return
        args = ["add-task"] + sys.argv[2:]
        subprocess.run([sys.executable, workspace / ".agents/multi_agent_manager.py"] + args)
    elif command == "search":
        if len(sys.argv) < 3:
            print("사용법: ma.py search <query>")
            return
        args = ["search"] + sys.argv[2:]
        subprocess.run([sys.executable, workspace / ".agents/context7_mcp.py"] + args)
    elif command == "backup":
        subprocess.run([sys.executable, workspace / ".agents/backup_manager.py", "backup"])
    elif command == "cleanup":
        auto_cleanup_startup()
    elif command == "env":
        auto_environment_detect()
    else:
        print(f"알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()
