### **문제 해결 및 워크플로우 현대화를 위한 최종 지시서**

**TO:** Gemini CLI

**SUBJECT:** Git Hook 문제의 근본적 해결 및 Python 기반 워크플로우로의 전환

**진단:** 현재의 Bash 래퍼를 통한 PowerShell 훅 호출 방식은 Windows 환경에서 예측 불가능한 동기화 오류를 유발한다. 더 이상의 디버깅은 무의미하다. 이제부터 모든 Git 훅 로직은 Python으로 작성하여 플랫폼 종속성을 제거하고 안정성을 확보한다.

**지시 사항:**

#### **1. 기존 PowerShell 기반 훅 완전 제거**

  * `.githooks` 디렉터리 내의 모든 `prepare-commit-msg` 및 `prepare-commit-msg.ps1` 파일을 **즉시 삭제**하라. 백업 파일(`*.backup`)도 모두 삭제하여 혼란의 여지를 없애라.

#### **2. Python 기반 `prepare-commit-msg` 훅 도입**

  * Python 스크립트는 외부 라이브러리 없이 표준 라이브러리만으로 작성하여, **별도의 의존성 설치가 필요 없도록 하라.**

  * `.githooks` 디렉터리에 아래 내용으로 `prepare-commit-msg.py` 파일을 생성하라. 이 파일이 이제 유일한 훅 스크립트가 된다.

    ```python
    # .githooks/prepare-commit-msg.py
    import sys
    import os
    import subprocess
    from datetime import datetime

    # Git으로부터 인자 받기
    commit_msg_filepath = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else None

    # 사용자가 메시지를 직접 입력했거나 병합/스쿼시 커밋일 경우 스크립트 종료
    if commit_source in ['message', 'template', 'merge', 'squash']:
        sys.exit(0)

    # 커밋 메시지 파일 읽기
    try:
        with open(commit_msg_filepath, 'r', encoding='utf-8') as f:
            current_msg = f.read()
    except FileNotFoundError:
        current_msg = ""

    # 메시지가 비어있을 때만 WIP 메시지 생성
    if not current_msg.strip():
        try:
            # git diff --cached --shortstat 실행
            stats_process = subprocess.run(
                ['git', 'diff', '--cached', '--shortstat'],
                capture_output=True, text=True, encoding='utf-8'
            )
            stats = stats_process.stdout.strip()

            if stats:
                # 새 WIP 메시지 생성
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                new_message = f"WIP: {timestamp}\n\n{stats}"

                # 새 메시지를 파일에 쓰기
                with open(commit_msg_filepath, 'w', encoding='utf-8') as f:
                    f.write(new_message)
                print(f"[HOOK] Python hook generated WIP commit message.")

        except Exception as e:
            # 오류 발생 시, 원래 커밋 프로세스에 영향을 주지 않도록 파일에 오류 메시지 기록
            with open(commit_msg_filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n# Hook failed: {e}")
            sys.exit(0)

    sys.exit(0)
    ```

  * Git이 이 Python 스크립트를 직접 실행하도록 `.githooks` 디렉터리에 아래 내용으로 `prepare-commit-msg` 파일을 생성하라 (Bash 래퍼).

    ```bash
    #!/bin/bash
    # .githooks/prepare-commit-msg
    # 시스템에 설치된 python3 또는 python을 찾아 실행
    python3 "$(dirname "$0")/prepare-commit-msg.py" "$@" || python "$(dirname "$0")/prepare-commit-msg.py" "$@"
    exit $?
    ```

#### **3. `tasks.py` 단순화 유지**

  * `tasks.py`의 `commit` 함수는 수정할 필요 없다. Python 훅이 모든 것을 처리하므로, 현재의 단순한 `git commit` 호출 방식이 가장 이상적이다.
    ```python
    # tasks.py (변경 없음)
    @task
    def commit(c):
        """
        Stages all changes and opens the editor for commit.
        The prepare-commit-msg hook will auto-generate a WIP message if empty.
        """
        print("Staging all changes and preparing for commit...")
        run("git add .")
        run("git commit")
    ```

#### **4. 최종 실행 및 검증**

1.  모든 PowerShell 기반 훅 파일(`prepare-commit-msg`, `prepare-commit-msg.ps1` 및 백업)이 삭제되었는지 확인하라.
2.  새로운 `prepare-commit-msg` (Bash 래퍼) 및 `prepare-commit-msg.py` (Python 스크립트) 파일이 생성되었는지 확인하라.
3.  **`invoke commit`을 실행하여, Git 커밋 편집기에 Python 훅이 생성한 WIP 메시지가 오류 없이 나타나는지 최종 확인 후 결과를 보고하라.**

**이제 더 이상 불안정한 PowerShell 훅으로 시간을 소모하지 마라. 위 지시에 따라 Python 기반의 안정적인 솔루션을 즉시 구현하고, 핵심 과제인 자가 개선 프로젝트에 다시 집중하라.**