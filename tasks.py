# tasks.py (최종 완성본 v4.0 - runner.py 분리 및 안정화)
from invoke import task, Collection, Program
import os
import subprocess
from scripts.usage_tracker import log_usage
from scripts.runner import run_command # logged_run 대신 run_command 임포트
import datetime # datetime 모듈 임포트
import tempfile # tempfile 모듈 임포트

# --- 핵심 태스크 (Core Tasks) ---
@task
def start(c):
    """[Intelligent Engine Start] 컨텍스트 엔진을 통해 세션을 시작하고 브리핑합니다."""
    log_usage('start', "task_start", details="Intelligent session started")
    print("Starting intelligent session...")
    
    print("  - Building context index...")
    build_context_index(c)

    print("  - Assembling context using the intelligent engine...")
    # prompt_builder.py를 직접 실행하여 출력을 캡처
    result = run_command('start', ["python", "scripts/prompt_builder.py"]) # run_command 사용
    briefing = result.stdout

    print("\nSession Start Briefing (Generated by Context Engine)")
    print("-" * 50)
    print(briefing)
    print("-" * 50)

    print("  - Handling previous session state...")
    run_command('start', ["python", "scripts/hub_manager.py", "handle_session"]) # hub_manager.py에 handle_session 기능 추가 필요
    
    print("  - Activating project tracking in .gitignore...")
    run_command('start', ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\toggle_gitignore.ps1"]) # run_command 사용
    
    print("Intelligent session started successfully.")
    log_usage('start', "task_end", details="Intelligent session finished")

@task
def wip(c, message=""):
    """WIP 커밋을 GEMINI.md 규칙에 따라 임시 파일을 사용하여 생성합니다."""
    log_usage('wip', "task_start", details="WIP commit process started")
    
    # 1. 변경사항 스테이징
    run_command('wip', ["git", "add", "."])

    # 2. 커밋 메시지 생성
    stats_result = run_command('wip', ["git", "diff", "--cached", "--shortstat"], hide=True)
    stats = stats_result.stdout.strip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    final_message = ""
    if not message:
        final_message = f"WIP: {timestamp}\n\n{stats}"
    else:
        final_message = f"{message}\n\n{stats}"

    # 3. 임시 파일에 메시지 작성 (GEMINI.md 규칙 준수)
    import tempfile
    import os
    tmp_file_path = os.path.join(tempfile.gettempdir(), "COMMIT_MSG.tmp")
    with open(tmp_file_path, 'w', encoding='utf-8') as f:
        f.write(final_message)

    # 4. -F 옵션으로 커밋하고 임시 파일 삭제
    try:
        run_command('wip', ["git", "commit", "-F", tmp_file_path])
    finally:
        os.remove(tmp_file_path)

    print("WIP commit created successfully using the temporary file method.")
    log_usage('wip', "task_end", details=f"WIP commit created: {final_message}")


@task
def end(c, task_id="general"):
    """[Session End] 세션 종료 프로세스를 자동화합니다."""
    log_usage('end', "task_start", details="Session end process started")
    print("Ending session...")
    
    print("  - Checking for uncommitted changes and creating WIP commit...")
    wip(c, message="WIP: Session End Backup")
    
    print("  - Restoring .gitignore...")
    run_command('end', ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ".\\scripts\\toggle_gitignore.ps1", "-Restore"]) # run_command 사용
    
    print("  - Updating __lastSession__ block in HUB.md...")
    run_command('end', ["python", "scripts/hub_manager.py", task_id]) # run_command 사용
    
    print("  - Creating final commit for session updates...")
    run_command('end', ["git", "add", "docs/HUB.md"]) # run_command 사용
    wip(c, message="docs: Update HUB.md with session state")

    print("Session ended successfully. All records saved.")
    log_usage('end', "task_end", details="Session end process finished")

@task
def status(c):
    """[Status Check] 현재 워크스페이스의 Git 상태를 간략히 확인합니다."""
    print("Workspace Status:")
    run_command('status', ["git", "status", "--short"]) # run_command 사용

# --- Context Sub-collection ---
@task(name="build")
def build_context_index(c):
    """워크스페이스의 컨텍스트 인덱스(index.json)를 생성하거나 업데이트합니다."""
    run_command('context.build', ["python", "scripts/build_context_index.py"]) # run_command 사용

@task(name="query")
def query_context(c, query):
    """컨텍스트 인덱스에서 정보를 검색합니다. (테스트용)"""
    print(f"Querying context for: '{query}'")
    run_command('context.query', ["python", "scripts/context_store.py", query]) # run_command 사용

# --- 테스트 하네스 태스크 (Test Harness Task) ---
@task
def test(c):
    """/tests 폴더의 모든 pytest 케이스를 실행하여 시스템 신뢰도를 검증합니다."""
    log_usage('test', "task_start", details="Autonomous Test Harness started")
    print("Running Autonomous Test Harness...")
    result = run_command('test', ["pytest", "-v"], check=False) # run_command 사용
    print("Pytest Stdout:")
    print(result.stdout.encode('cp949', errors='replace').decode('cp949'))
    print("Pytest Stderr:")
    print(result.stderr.encode('cp949', errors='replace').decode('cp949'))
    log_usage('test', "task_end", details="Autonomous Test Harness finished")

# --- 네임스페이스 및 프로그램 정의 ---
ns = Collection()
ns.add_task(start)
ns.add_task(end)
ns.add_task(status)
ns.add_task(wip)
ns.add_task(test)

context_ns = Collection('context')
context_ns.add_task(build_context_index, name='build')
context_ns.add_task(query_context, name='query')
ns.add_collection(context_ns)

program = Program(namespace=ns)