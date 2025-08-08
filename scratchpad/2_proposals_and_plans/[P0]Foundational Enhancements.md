### **Mission [P0-1]: Foundational Automation Framework 구축 지시서**

**TO:** Gemini CLI

**SUBJECT:** P0 목표 달성을 위한 첫 실행 명령

#### **1. 전략적 목표 (Strategic Goal)**

여러 LLM들의 제안을 종합한 결과, 가장 시급하고 중요한 과제는 **사용자의 반복적인 수동 개입을 제거**하고, 향후 모든 지능형 기능을 탑재할 **확장 가능한 실행 기반을 마련**하는 것이다. 따라서 첫 임무는 개별 기능 테스트를 넘어, 세션 관리와 커밋 프로세스 자체를 자동화하는 프레임워크를 구축하는 것으로 한다.

이 임무는 당신의 `P0` 목표인 **'코어 지능(정확한 코드 생성)'** 과 **'컨텍스트 관리(시스템 규칙의 이해 및 적용)'** 능력을 동시에 검증한다.

#### **2. 구체적인 임무 내용 (Actionable Directives)**

아래 4개의 핵심 결과물(Deliverable)을 워크스페이스 내 정확한 위치에 생성하고, 모든 시스템이 유기적으로 연동되도록 설정하라.

##### **Deliverable 1: 중앙 제어기 (`tasks.py`) 생성**

  * **위치:** 워크스페이스 루트 (`/tasks.py`)
  * **목적:** 모든 자동화 스크립트를 중앙에서 조율하는 Task Runner. 향후 모든 명령어는 `invoke`를 통해 실행된다.
  * **내용:**
    ```python
    # tasks.py
    #Foundational Enhancements.md]
    from invoke import task, run

    @task
    def start(c):
        """[Session Start] .gitignore를 수정하여 /projects/ 폴더를 임시로 추적합니다."""
        print("▶️ Starting session...")
        run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1")
        print("✅ Session started successfully.")

    @task
    def end(c, task_id="general"):
        """[Session End] .gitignore를 복원하고 세션 사용량을 기록합니다."""
        print("⏹️ Ending session...")
        run("powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\toggle_gitignore.ps1 -Restore")
        # 아래 라인은 Deliverable 2 완료 후 활성화됩니다.
        # run(f"powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\log_usage.ps1 -TaskId {task_id}")
        print(f"✅ Session ended successfully.")

    @task
    def status(c):
        """[Status Check] 현재 워크스페이스의 Git 상태를 간략히 확인합니다."""
        print("⚫ Workspace Status:")
        run("git status --short")
    ```

##### **Deliverable 2: 세션 관리 스크립트 (`toggle_gitignore.ps1`) 생성**

  * **위치:** `/scripts/toggle_gitignore.ps1`
  * **목적:** 세션 시작/종료 시 `.gitignore` 파일의 `/projects/` 라인을 자동으로 주석 처리/복원한다.
  * **내용:**
    ```powershell
    # scripts/toggle_gitignore.ps1
    #Foundational Enhancements.md]
    param(
        [switch]$Restore
    )
    $gitignorePath = Join-Path $PSScriptRoot '..\' '.gitignore'
    if (-not (Test-Path $gitignorePath)) {
        Write-Error "CRITICAL ERROR: .gitignore file not found at $gitignorePath"
        exit 1
    }
    $content = Get-Content $gitignorePath
    $patternToComment = '^(\s*/projects/)'
    $patternToRestore = '^#\s*(/projects/)'

    if ($Restore) {
        $newContent = $content -replace $patternToRestore, '$1'
        $action = "Restored"
    } else {
        $newContent = $content -replace $patternToComment, '#$1'
        $action = "Commented"
    }

    Set-Content -Path $gitignorePath -Value $newContent -Encoding UTF8
    Write-Host "[SUCCESS] $action /projects/ line in .gitignore"
    ```

##### **Deliverable 3: 자동 WIP 커밋 훅 (`pre-commit`) 생성**

  * **위치:** `/.githooks/pre-commit` (확장자 없음)
  * **목적:** `git commit` 명령 시, 커밋 메시지가 비어있으면 변경된 파일 통계를 기반으로 한 WIP 커밋 메시지를 자동으로 생성한다.
  * **내용:**
    ```powershell
    #!/usr/bin/env pwsh
    # .githooks/pre-commit
    #Foundational Enhancements.md]
    $commitMsgFile = $args[0]
    $currentMsg = if (Test-Path $commitMsgFile) { Get-Content $commitMsgFile -Raw } else { $null }

    # 병합 커밋이 아니고, 커밋 메시지가 비어 있을 때만 작동
    if (-not (Test-Path (Join-Path .git MERGE_HEAD)) -and -not $currentMsg) {
        $stats = git diff --cached --shortstat | ForEach-Object { $_.Trim() }
        if ($stats) {
            $newMessage = "WIP: $(Get-Date -Format 'yyyy-MM-dd HH:mm')`n`n$stats"
            $newMessage | Out-File $commitMsgFile -Encoding utf8
            Write-Host "[HOOK] Auto-generated WIP commit message."
        }
    }
    exit 0
    ```

##### **Deliverable 4: 비용 관측 스크립트 (`log_usage.ps1`) 뼈대 생성**

  * **위치:** `/scripts/log_usage.ps1`
  * **목적:** 향후 토큰 사용량 기록을 위한 파일 및 기본 구조. (실제 로직은 Phase 1에서 구현)
  * **내용:**
    ```powershell
    # scripts/log_usage.ps1
    #Foundational Enhancements.md]
    param([string]$TaskId = "N/A")

    $logFilePath = Join-Path $PSScriptRoot '..\' 'docs' 'usage_log.csv'
    if (-not (Test-Path $logFilePath)) {
        "Timestamp,TaskId,InputTokens,OutputTokens" | Out-File -FilePath $logFilePath -Encoding utf8
    }
    # 실제 토큰 값은 추후 API 응답과 연동하여 파싱 예정
    $inputTokens = 0
    $outputTokens = 0
    $csvLine = "$(Get-Date -Format 'o'),$TaskId,$inputTokens,$outputTokens"
    Add-Content -Path $logFilePath -Value $csvLine
    Write-Host "[SUCCESS] Placeholder usage logged to docs/usage_log.csv for Task: $TaskId"
    ```

#### **3. 최종 실행 및 검증 절차 (Execution & Verification)**

**지시:** 아래 명령을 순서대로 실행하여 프레임워크 구축을 완료하라.

1.  "사용자님, `invoke` 라이브러리가 필요합니다. `pip install invoke` 명령어로 설치해주세요." 라고 안내하라.
2.  `/scripts` 와 `/.githooks` 디렉터리를 생성하라.
3.  위 `Deliverable 2, 3, 4`의 내용을 각 파일에 정확히 기록하라.
4.  `Deliverable 1`의 내용을 `/tasks.py` 파일에 정확히 기록하라.
5.  Git이 새로운 훅 디렉터리를 사용하도록 다음 명령을 실행하라: `git config core.hooksPath .githooks`
6.  모든 설정이 완료되었음을 보고하고, `invoke start` 명령을 실행하여 `.gitignore` 파일이 정상적으로 수정되는지 확인 후 결과를 보고하라.

#### **4. 임무 완료 조건 (Success Criteria)**

  * `invoke start` 실행 시, 오류 없이 `.gitignore` 파일의 `/projects/` 라인이 주석 처리된다.
  * `invoke end` 실행 시, 주석이 원상 복구된다.
  * 파일을 수정한 뒤 `git add .` 및 `git commit` 실행 시, 자동 생성된 WIP 커밋 메시지로 커밋이 성공한다.

-----

**이제, 위 지시사항을 즉시 이행하라.**