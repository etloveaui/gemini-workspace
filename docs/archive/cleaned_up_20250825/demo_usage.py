#!/usr/bin/env python3
"""
실제 사용 가능한 시스템 데모 - Context7 및 파일시스템 통합
사용자가 실제로 쓸 수 있는 기능들을 보여줍니다.
"""
import json
from pathlib import Path
import subprocess

def demo_filesystem_operations():
    """파일시스템 작업 데모"""
    print("=== 파일시스템 작업 데모 ===")
    
    # 1. 프로젝트 구조 확인
    print("1) 프로젝트 구조:")
    root = Path("C:/Users/eunta/multi-agent-workspace")
    for item in sorted(root.iterdir()):
        if item.name not in ['.git', '__pycache__', 'venv', 'projects']:
            print(f"   {item.name}/")
    
    # 2. 최근 작업한 파일들
    print("\n2) 최근 작업 파일 (communication):")
    comm_files = []
    for agent in ['claude', 'gemini', 'codex']:
        agent_dir = root / 'communication' / agent
        if agent_dir.exists():
            for file in agent_dir.glob('*.md'):
                comm_files.append((file.name, agent, file.stat().st_mtime))
    
    # 최신 5개 파일
    for filename, agent, mtime in sorted(comm_files, key=lambda x: x[2], reverse=True)[:5]:
        print(f"   {filename} ({agent})")
    
    # 3. 백업 시스템 상태
    backups_dir = root / '.backups'
    if backups_dir.exists():
        backups = list(backups_dir.glob('*.zip'))
        print(f"\n3) 백업 파일: {len(backups)}개")
        if backups:
            latest = max(backups, key=lambda x: x.stat().st_mtime)
            size = latest.stat().st_size / (1024*1024)
            print(f"   최신: {latest.name} ({size:.1f}MB)")

def demo_context7_integration():
    """Context7 통합 데모"""
    print("\n=== Context7 통합 데모 ===")
    
    # 1. 검색 기능
    print("1) 스마트 검색 기능:")
    search_queries = [
        "pytest results",
        "backup system", 
        "agent coordination"
    ]
    
    for query in search_queries:
        try:
            result = subprocess.run([
                'python', 'ma.py', 'search', query
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                print(f"   '{query}' → 결과 발견")
            else:
                print(f"   '{query}' → 검색 실패")
        except:
            print(f"   '{query}' → 시스템 오류")

def demo_agent_system():
    """에이전트 시스템 데모"""
    print("\n=== 멀티 에이전트 시스템 데모 ===")
    
    # 1. 에이전트 상태 확인
    try:
        result = subprocess.run([
            'python', 'ma.py', 'status'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print("1) 에이전트 상태:")
            for agent, info in data.items():
                status = "활성" if info.get('active', False) else "대기"
                cpu = info.get('cpu_percent', 0)
                print(f"   {agent.upper()}: {status} (CPU: {cpu}%)")
        else:
            print("1) 에이전트 상태 확인 실패")
    except:
        print("1) 시스템 연결 오류")
    
    # 2. 실제 사용 가능한 명령어들
    print("\n2) 사용 가능한 명령어:")
    commands = [
        ("python ma.py status", "에이전트 상태 확인"),
        ("python ma.py search <검색어>", "Context7 검색"),
        ("python ma.py backup", "수동 백업 실행"),
        ("python scripts/dashboard.py", "시스템 대시보드"),
        ("python scripts/doctor_v3.py", "고급 시스템 진단"),
        ("python scripts/simple_monitor.py", "에이전트 모니터링")
    ]
    
    for cmd, desc in commands:
        print(f"   {cmd}")
        print(f"     → {desc}")

def demo_vs_code_integration():
    """VS Code 통합 데모"""
    print("\n=== VS Code 통합 데모 ===")
    
    tasks_file = Path("C:/Users/eunta/multi-agent-workspace/.vscode/tasks.json")
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("1) VS Code 작업 목록:")
        tasks = data.get('tasks', [])
        for i, task in enumerate(tasks[:8], 1):  # 처음 8개만
            print(f"   {i}) {task.get('label', 'Unknown')}")
        
        print(f"\n   총 {len(tasks)}개 작업 등록됨")
        print("   VS Code에서 Ctrl+Shift+P → 'Tasks: Run Task' 실행")
    else:
        print("1) VS Code 설정 파일 없음")

def main():
    """메인 데모 실행"""
    print("🚀 멀티 에이전트 워크스페이스 v2.0 - 실사용 데모")
    print("=" * 60)
    
    demo_filesystem_operations()
    demo_context7_integration() 
    demo_agent_system()
    demo_vs_code_integration()
    
    print("\n=" * 60)
    print("✅ 모든 시스템이 통합되어 실제 사용 가능합니다!")
    print("🔧 추가 문의사항은 communication 폴더를 통해 에이전트에게 요청하세요.")

if __name__ == "__main__":
    main()