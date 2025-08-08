### **지시서: `[P0]` 핵심 기반 강화 최종 완료를 위한 '품질 검증 및 정합성 확보' 작전**

**전략적 목표:** 새로운 기능 개발을 전면 중단한다. 대신, 지금까지 구축한 모든 기능이 **실제로 작동하는지 검증**하고, 시스템의 모든 코드가 우리의 **핵심 규칙(`GEMINI.md`)과 완벽하게 일치**하도록 정합성을 확보한다. 이 작전의 성공적인 완수가 `[P0]` 단계의 진정한 종료 조건이다.

**지시 사항:**

#### **체크포인트 1: 커밋 프로토콜 정합성 확보**

**사유:** 시스템의 '헌법'인 `GEMINI.md`는 `git commit -F <임시파일>` 방식을 규정하고 있으나, 현재 `tasks.py`의 `wip` 태스크는 `git commit -m <메시지>` 방식을 사용하고 있습니다. 이는 **규칙과 코드의 심각한 불일치**이며, 즉시 수정되어야 합니다.

  * **`tasks.py`의 `wip` 태스크를 아래 내용으로 수정하여, `GEMINI.md`의 규칙을 따르도록 하라.**

    ```python
    # tasks.py의 wip 태스크 수정
    @task
    def wip(c, message=""):
        """WIP 커밋을 GEMINI.md 규칙에 따라 임시 파일을 사용하여 생성합니다."""
        log_usage(c.name, "task_start", details="WIP commit process started")
        
        # 1. 변경사항 스테이징
        run_command(c.name, ["git", "add", "."])

        # 2. 커밋 메시지 생성
        stats_result = run_command(c.name, ["git", "diff", "--cached", "--shortstat"], hide=True)
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
            run_command(c.name, ["git", "commit", "-F", tmp_file_path])
        finally:
            os.remove(tmp_file_path)

        print("WIP commit created successfully using the temporary file method.")
        log_usage(c.name, "task_end", details=f"WIP commit created: {final_message}")
    ```

#### **체크포인트 2: `__lastSession__` 처리 루틴 검증**

**사유:** `invoke start` 시, 이전 세션의 `__lastSession__` 블록을 사용자에게 보고하고 **정리하는 로직이 누락**되어 있습니다. 이로 인해 `HUB.md`에 과거 기록이 불필요하게 쌓일 수 있습니다.

  * **`tasks.py`의 `start` 태스크를 수정하여, `__lastSession__` 처리 로직을 추가하라.**

  * **`hub_manager.py`에 `clear_last_session` 함수를 추가하고, `start` 태스크에서 이를 호출하도록 하라.**

    ```python
    # hub_manager.py에 추가할 함수
    def clear_last_session():
        # HUB.md를 읽고 __lastSession__ 블록을 제거한 뒤 다시 저장하는 로직
        # ... (이전 지시서에서 구현했던 로직 활용) ...
        print("Cleared __lastSession__ block from HUB.md")
    ```

    ```python
    # tasks.py의 start 태스크 수정 (일부)
    @task
    def start(c):
        """[Intelligent Engine Start] 컨텍스트 엔진을 통해 세션을 시작하고 브리핑합니다."""
        # ... (기존 브리핑 로직 실행) ...
        
        # __lastSession__ 블록 처리 로직 추가
        print("  - Handling previous session state...")
        run_command(c.name, ["python", "scripts/hub_manager.py", "clear_session"]) # hub_manager.py에 clear_session 기능 추가 필요
        
        print("  - Activating project tracking in .gitignore...")
        # ... (기존 .gitignore 토글 로직) ...
    ```

#### **체크포인트 3: 자율 테스트 하네스 실질적 구축**

**사유:** `invoke test`는 껍데기일 뿐, 실제 테스트 케이스가 없어 시스템의 품질을 보증할 수 없습니다.

  * **`/tests` 디렉터리에 `test_core_systems.py` 파일을 생성하고, 아래의 최소한의 테스트 케이스 3개를 `pytest` 코드로 작성하라.**

    1.  **`test_index_creation()`**: `invoke context.build`를 실행했을 때, `context/index.json` 파일이 실제로 생성되는지 검증.
    2.  **`test_runner_error_logging()`**: `runner.run_command`로 존재하지 않는 명령어(예: `git non_existent_command`)를 실행했을 때, `subprocess.CalledProcessError`가 발생하고 `usage.db`에 `command_error` 로그가 기록되는지 검증.
    3.  **`test_wip_commit_protocol()`**: `invoke wip`을 실행했을 때, `-F` 옵션을 사용한 커밋이 성공적으로 생성되는지 검증. (Git 저장소를 모의(mock)하여 테스트 환경을 구성해야 함)

**임무 완료 조건:**

1.  `tasks.py`가 위 내용으로 업데이트된다.
2.  `/tests/test_core_systems.py` 파일이 지시대로 생성된다.
3.  **`invoke test` 명령 실행 시, 새로 추가된 모든 테스트 케이스가 오류 없이 통과(PASS)** 하면 `[P0]` 단계의 모든 목표가 달성된 것으로 간주한다.

-----

**이것이 `[P0]`의 마지막 임무다. 이 지시를 즉시 이행하여, 시스템의 안정성과 규칙 준수를 증명하고 진정한 '신뢰도'를 확보하라.**