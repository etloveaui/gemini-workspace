# tasks.py
#Foundational Enhancements.md]
from invoke import task, run

@task
def start(c):
    """[Session Start] 세션 시작 프로세스를 자동화합니다."""
    print("Starting session...")

    # 1. GEMINI.md 규칙 로딩 및 확인
    print("  - Loading GEMINI.md rules...")
    gemini_md_content = c.run("type GEMINI.md", hide=True).stdout
    # 실제 규칙 로딩 및 확인 로직은 여기에 추가될 수 있습니다.

    # 2. HUB.md 읽기 및 현재 작업 상태 파악
    print("  - Reading HUB.md to understand current task status...")
    hub_md_content = c.run(r"type C:\Users\etlov\gemini-workspace\docs\HUB.md", hide=True).stdout

    # 3. .gitignore에서 /projects/ 라인 자동 주석 처리
    print("  - Commenting out /projects/ line in .gitignore...")
    c.run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1")

    # 4. __lastSession__ 블록 존재 시 자동 복구 제안
    if "__lastSession__" in hub_md_content:
        print("  - __lastSession__ block found in HUB.md. Would you like to restore the previous session? (Y/N)")
        # 사용자 입력 대기 로직은 CLI 환경에서 직접 구현하기 어려우므로, 여기서는 메시지만 출력합니다.
        # 실제 구현에서는 사용자 입력을 받는 로직이 필요합니다.
        # 일단은 복구하지 않는 것으로 가정하고 진행합니다。
        # TODO: 사용자 입력 처리 로직 추가
        pass

    # 5. 활성/일시정지 작업 브리핑 (5초 내 완료)
    print("  - Briefing active/paused tasks...")
    # HUB.md 파싱하여 작업 목록 브리핑 로직 추가
    hub_md_lines = hub_md_content.splitlines()
    active_tasks = []
    paused_tasks = []
    in_active_section = False
    in_paused_section = False

    for line in hub_md_lines:
        if line.startswith("## Active Tasks"):
            in_active_section = True
            in_paused_section = False
            continue
        elif line.startswith("## Paused Tasks"):
            in_paused_section = True
            in_active_section = False
            continue
        elif line.startswith("## Completed Tasks"):
            in_active_section = False
            in_paused_section = False
            break

        if in_active_section and line.strip() and not line.strip().startswith("(") and not line.strip().startswith("-") and not line.strip().startswith("Log:"):
            active_tasks.append(line.strip())
        elif in_paused_section and line.strip() and not line.strip().startswith("(") and not line.strip().startswith("-") and not line.strip().startswith("Log:"):
            paused_tasks.append(line.strip())

    print("Current Active Tasks:")
    if active_tasks:
        for task_item in active_tasks:
            print(f"  - {task_item}")
    else:
        print("  - None")

    print("\nCurrent Paused Tasks:")
    if paused_tasks:
        for task_item in paused_tasks:
            print(f"  - {task_item}")
    else:
        print("  - None")

    print("Session started successfully.")

@task
def end(c, task_id="general"):
    """[Session End] 세션 종료 프로세스를 자동화합니다.""" 
    print("Ending session...")

    # 1. 현재 작업 상태를 Paused로 업데이트
    print("  - Updating current task status to Paused in HUB.md...")
    hub_md_content = c.run(r"type C:\Users\etlov\gemini-workspace\docs\HUB.md", hide=True).stdout
    hub_md_lines = hub_md_content.splitlines()

    active_tasks_section_start = -1
    paused_tasks_section_start = -1
    completed_tasks_section_start = -1

    for i, line in enumerate(hub_md_lines):
        if line.startswith("## Active Tasks"):
            active_tasks_section_start = i
        elif line.startswith("## Paused Tasks"):
            paused_tasks_section_start = i
        elif line.startswith("## Completed Tasks"):
            completed_tasks_section_start = i

    # Find the task to move/update
    task_line_to_move = None
    if active_tasks_section_start != -1 and paused_tasks_section_start != -1:
        for i in range(active_tasks_section_start + 1, paused_tasks_section_start):
            if task_id in hub_md_lines[i]:
                task_line_to_move = hub_md_lines[i]
                hub_md_lines.pop(i) # Remove from active section
                break

    if task_line_to_move:
        # Add to paused section
        hub_md_lines.insert(paused_tasks_section_start + 1, task_line_to_move.replace("(Active)", "(Paused)"))
        print(f"  - Task '{task_id}' moved from Active to Paused.")
    else:
        print(f"  - Task '{task_id}' not found in Active Tasks or already Paused.")

    # 2. git status 확인 후 변경사항 있으면 WIP 커밋 실행
    print("  - Checking for uncommitted changes...")
    git_status_output = c.run("git status --porcelain", hide=True).stdout
    if git_status_output.strip():
        print("  - Uncommitted changes found. Staging all changes and performing WIP commit...")
        c.run("git add .") # 모든 변경 사항 스테이징
        c.run("invoke wip")
    else:
        print("  - No uncommitted changes.")

    # 3. .gitignore 복원 (/projects/ 주석 제거)
    print("  - Restoring /projects/ line in .gitignore...")
    c.run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1 -Restore")

    # 4. 세션 사용량 요약 (추후 구현 예정)
    # print("  - Summarizing session usage...\n")
    # c.run(f"powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\log_usage.ps1 -TaskId {task_id}")

    # 5. __lastSession__ 블록 생성
    print("  - Generating __lastSession__ block in HUB.md...")
    # 기존 __lastSession__ 블록 제거
    new_hub_md_content_lines = []
    in_last_session_block = False
    for line in hub_md_lines:
        if line.strip() == "---" and new_hub_md_content_lines and new_hub_md_content_lines[-1].strip() == "": # --- 앞에 빈 줄이 있으면 블록 시작으로 간주
            in_last_session_block = True
        if not in_last_session_block:
            new_hub_md_content_lines.append(line)
        if in_last_session_block and line.strip() == "": # 빈 줄로 블록 끝을 가정
            in_last_session_block = False
    
    # 변경된 파일 목록 가져오기
    changed_files_output = c.run("git diff HEAD~1 --name-only", hide=True).stdout
    changed_files = [f.strip() for f in changed_files_output.splitlines() if f.strip()]

    # 현재 타임스탬프 생성
    import datetime
    timestamp = datetime.datetime.now().isoformat(timespec='seconds') + '+09:00' # KST

    # __lastSession__ 블록 생성
    last_session_block = """
---
__lastSession__: 
  active_task_id: {active_task_id}
  changed_files:
{changed_files_yaml}
  timestamp: {timestamp}
""".format(
        active_task_id=task_id, # 현재는 task_id를 사용, 향후 동적 할당 필요
        changed_files_yaml="\n".join([f"    - {f}" for f in changed_files]),
        timestamp=timestamp
    )

    # HUB.md에 새로운 __lastSession__ 블록 추가
    final_hub_md_content = "\n".join(new_hub_md_content_lines).strip() + "\n" + last_session_block
    with open("C:/Users/etlov/gemini-workspace/docs/HUB.md", "w", encoding="utf-8") as f:
        f.write(final_hub_md_content)

    print("Session ended successfully. All records saved and environment cleaned.")

@task
def status(c):
    """[Status Check] 현재 워크스페이스의 Git 상태를 간략히 확인합니다."""
    print("Workspace Status:")
    run("git status --short")

@task
def wip(c, message=""):
    """WIP 커밋 생성"""
    run(f'powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\git-wip.ps1 -Message "{message}"')