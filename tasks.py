# tasks.py
#Foundational Enhancements.md]
from invoke import task, run

@task
def start(c):
    """[Session Start] .gitignore를 수정하여 /projects/ 폴더를 임시로 추적합니다."""
    print("Starting session...")
    run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1")
    print("Session started successfully.")

@task
def end(c, task_id="general"):
    """[Session End] .gitignore를 복원하고 세션 사용량을 기록합니다."""
    print("Ending session...")
    run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1 -Restore")
    # 아래 라인은 Deliverable 2 완료 후 활성화됩니다.
    # run(f"powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\log_usage.ps1 -TaskId {task_id}")
    print(f"Session ended successfully.")

@task
def status(c):
    """[Status Check] 현재 워크스페이스의 Git 상태를 간략히 확인합니다."""
    print("Workspace Status:")
    run("git status --short")

@task
def wip(c, message=""):
    """WIP 커밋 생성"""
    run(f'powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\git-wip.ps1 -Message "{message}"')



