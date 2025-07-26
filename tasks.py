from invoke import task, run

@task
def start(c):
    """[Session Start] 세션 시작 프로세스를 자동화합니다."""
    print("Starting session...")
    c.run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1")
    print("Session started successfully.")

@task
def end(c, task_id="general"):
    """[Session End] 세션 종료 프로세스를 자동화합니다."""
    print("Ending session...")

    print("  - Checking for uncommitted changes and creating WIP commit...")
    c.run("invoke wip")

    print("  - Restoring .gitignore...")
    c.run(r"powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1 -Restore")

    print("  - Updating __lastSession__ block in HUB.md...")
    c.run(f"python .\\scripts\\hub_manager.py {task_id}")
    c.run("git add docs/HUB.md")

    print("  - Creating final commit for session updates...")
    c.run("invoke wip")

    print("Session ended successfully. All records saved.")

@task
def status(c):
    """[Status Check] 현재 워크스페이스의 Git 상태를 간략히 확인합니다."""
    print("Workspace Status:")
    run("git status --short")

@task
def wip(c, message=""):
    """WIP 커밋을 생성합니다."""
    run(f'powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\git-wip.ps1 -Message "{message}"')
