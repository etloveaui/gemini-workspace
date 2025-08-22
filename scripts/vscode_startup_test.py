"""
VS Code 자동 시작 테스트 및 검증
"""
import subprocess
import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line

def test_background_system():
    """백그라운드 시스템 테스트"""
    print(header("VS Code 자동 시작 시스템 테스트"))
    
    # 1. run_background.py 직접 테스트
    print(kv("테스트 1", "run_background.py 직접 실행"))
    try:
        result = subprocess.run(
            ['python', 'run_background.py', '--test'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            timeout=10
        )
        if result.returncode == 0:
            print(status_line(1, "OK", "직접 실행", "성공"))
        else:
            print(status_line(2, "WARN", "직접 실행", f"오류: {result.stderr[:100]}"))
    except subprocess.TimeoutExpired:
        print(status_line(3, "INFO", "직접 실행", "타임아웃 (정상 - 무한루프)"))
    except Exception as e:
        print(status_line(4, "ERROR", "직접 실행", f"실패: {e}"))
    
    # 2. tasks.json 설정 확인
    print(kv("테스트 2", "tasks.json 설정 검증"))
    vscode_tasks = Path('.vscode/tasks.json')
    if vscode_tasks.exists():
        import json
        with open(vscode_tasks, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        auto_task = None
        for task in tasks_data.get('tasks', []):
            if task.get('label') == 'Auto Background System':
                auto_task = task
                break
        
        if auto_task:
            run_on = auto_task.get('runOptions', {}).get('runOn')
            if run_on == 'folderOpen':
                print(status_line(1, "OK", "자동 실행 설정", "folderOpen 활성화"))
            else:
                print(status_line(2, "WARN", "자동 실행 설정", f"값: {run_on}"))
        else:
            print(status_line(3, "ERROR", "자동 실행 설정", "태스크 없음"))
    else:
        print(status_line(4, "ERROR", "VS Code 설정", "tasks.json 없음"))
    
    # 3. 자동 상태 업데이터 테스트
    print(kv("테스트 3", "auto_status_updater.py 단독 실행"))
    try:
        result = subprocess.run(
            ['python', 'scripts/auto_status_updater.py'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            timeout=30
        )
        if result.returncode == 0:
            print(status_line(1, "OK", "상태 업데이터", "정상 동작"))
        else:
            print(status_line(2, "WARN", "상태 업데이터", "오류 발생"))
    except subprocess.TimeoutExpired:
        print(status_line(3, "WARN", "상태 업데이터", "타임아웃"))
    except Exception as e:
        print(status_line(4, "ERROR", "상태 업데이터", f"실패: {e}"))

def create_startup_verification():
    """시작시 검증 스크립트 생성"""
    verification_script = Path('scripts/startup_verification.py')
    
    script_content = '''"""
VS Code 시작시 자동 검증
"""
import time
from datetime import datetime
from pathlib import Path

def log_startup():
    """시작 로그 기록"""
    log_file = Path('.agents/startup_logs.txt')
    log_file.parent.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - VS Code 자동 시작 확인\\n")
    
    print(f"[{timestamp}] VS Code 자동 시작 시스템 활성화됨")

if __name__ == "__main__":
    log_startup()
'''
    
    with open(verification_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(kv("생성됨", "startup_verification.py"))

def main():
    """메인 테스트 실행"""
    test_background_system()
    print()
    create_startup_verification()
    
    print(header("다음 단계"))
    print("1. VS Code를 완전히 종료")
    print("2. 이 프로젝트 폴더를 다시 열기") 
    print("3. 터미널에서 자동 실행 메시지 확인")
    print("4. .agents/startup_logs.txt 파일 생성 확인")

if __name__ == "__main__":
    main()