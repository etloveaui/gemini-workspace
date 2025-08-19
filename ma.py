#!/usr/bin/env python3
"""멀티 에이전트 워크스페이스 통합 CLI"""
import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("사용법: python ma.py <command> [args...]")
        print("명령어:")
        print("  status    - 에이전트 상태")
        print("  add <task> - 작업 추가") 
        print("  search <query> - Context7 검색")
        print("  backup    - 백업 실행")
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
    else:
        print(f"알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()
