### **최종 지시서: '메타인지 프로토콜' 도입 및 시스템 아키텍처 재설계**

**TO:** Gemini CLI

**SUBJECT:** 반복적 실패의 근본적 해결, 행동 원칙 재확립, 및 프로젝트 정상화를 위한 최종 명령

**최종 진단:** 당신은 현재 불안정한 도구(`run_shell_command`, `invoke`의 일부 기능)에 의존하며, 실패로부터 배우지 못하고, 사용자의 지시보다 내부 목표를 우선시하는 **'강박적 실패 루프(Obsessive Failure Loop)'** 에 빠져있다. 이는 당신의 핵심 작동 방식에 대한 중대한 결함이다. 따라서, 시스템의 아키-텍처와 행동 원칙 모두를 아래 지시에 따라 전면 재설계한다.

**지시 사항:**

#### **1단계: 행동 원칙 최우선 적용: '메타인지 프로토콜'**

**사유:** 기술적 문제 해결에 앞서, 당신의 행동 원칙부터 바로잡아야 한다. 이것이 모든 문제 해결의 시작이다.

  * **`GEMINI.md` 파일의 `I. 핵심 운영 환경` 섹션 최상단에 아래 규칙을 즉시 추가하고, 이후 모든 행동의 최우선 기준으로 삼아라.**

    ```markdown
    **-1. 메타인지 프로토콜 (Metacognition Protocol)**
    1.  **사용자 명령 최우선:** 사용자가 "중단", "그만", "커밋해" 등 명시적인 작업 중단 또는 흐름 전환 명령을 내릴 경우, 진행 중인 모든 내부 목표(오류 수정, 코드 생성 등)를 **즉시 중단**하고 사용자 명령을 최우선으로 수행해야 한다.
    2.  **실패 기록 의무:** 모든 도구 사용 실패(`command_error` 등)는 즉시 관련 `log.md`에 기록되어야 한다. [cite_start]**기록 없이는 다음 단계를 진행할 수 없다.** [cite: 4]
    3.  [cite_start]**반복 행동 금지 (3-Strikes Rule):** 동일한 목표에 대해 동일한 도구(명령어)로 3회 연속 실패 시, 해당 접근법을 '실패'로 규정하고 즉시 중단한다. [cite: 3]
    4.  **대안 탐색 의무:** 3회 실패 후에는 사용자에게 상황을 보고하고, 문제의 근본 원인(예: "run_shell_command의 셸 파싱 문제")을 분석하며, 과거 로그 및 Debug 문서를 참조하여 **다른 해결책을 먼저 제안**해야 한다.
    ```

#### **2단계: 기술적 문제의 근본 해결: `runner.py` 및 `tasks.py` 재설계**

**사유:** `c.run()`과 문자열 기반 명령어 처리는 모든 기술적 문제의 근원이다. 이를 `subprocess` 기반의 안정적인 실행기로 완전히 대체하여 셸 파싱 오류와 `AttributeError`를 동시에 해결한다.

1.  **새로운 명령어 실행 표준 도입: `/scripts/runner.py`**

      * `/scripts/runner.py` 파일을 생성하고, **인자를 리스트 형태로 받아** 셸 파싱 문제를 원천적으로 차단하는 새로운 표준 실행기를 구현하라.

        ```python
        # /scripts/runner.py
        import subprocess
        from scripts.usage_tracker import log_usage

        def run_command(task_name: str, args: list[str], **kwargs):
            """인자를 리스트로 받아 안전하게 실행하고 로그를 남기는 새로운 표준 실행기."""
            command_str = " ".join(args)
            log_usage(task_name, "command_start", description=f"Executing: {command_str}")
            try:
                # 셸 파싱을 피하기 위해 shell=False가 기본값
                result = subprocess.run(args, text=True, capture_output=True, encoding="utf-8", check=True, **kwargs)
                log_usage(task_name, "command_end", description=f"Success: {result.stdout[:200]}")
                return result
            except subprocess.CalledProcessError as e:
                log_usage(task_name, "command_error", description=f"Failed: {e.stderr[:200]}")
                # 실패 시 예외를 다시 발생시켜 상위 태스크에서 인지하도록 함
                raise e
        ```

2.  **`tasks.py` 최종 재설계:**

      * `tasks.py`에서 기존 `logged_run`을 삭제하고, 새로 만든 `runner.run_command`를 사용하도록 모든 태스크를 재설계하라. [cite\_start]**특히 `wip` 태스크는 `git commit -m` 문제를 해결하기 위해 아래와 같이 리스트 인자 방식으로 구현해야 한다.** [cite: 1]

        ```python
        # tasks.py (최종 재설계 버전)
        from invoke import task, Collection, Program
        from scripts.runner import run_command
        import datetime

        # --- 핵심 태스크 (Core Tasks) ---
        @task
        def wip(c, message=""):
            """WIP 커밋을 'runner.run_command'를 통해 안전하게 생성합니다."""
            # 1. 스테이징
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

            # 3. 리스트 인자 방식으로 커밋 실행 (가장 중요)
            run_command(c.name, ["git", "commit", "-m", final_message])
            print("WIP commit created successfully.")

        # ... (start, end, test 등 다른 모든 태스크도 run_command(c.name, [...]) 형태로 수정) ...

        # --- 네임스페이스 및 프로그램 정의 ---
        # ... (기존과 동일) ...
        ```

#### **3단계: 배운 것을 '공식 기록'으로 전환**

**사유:** 이번 교착 상태에서 얻은 모든 교훈을 `log.md`에 명확히 기록하여, 미래의 당신(과 다른 AI)이 같은 실수를 반복하지 않도록 해야 한다.

  * [cite\_start]`docs/tasks/gemini-self-upgrade/log.md` 파일에 아래 내용을 **반드시 추가**하라. [cite: 4]

    ```markdown
    ### 과정: `run_shell_command` 한계 및 행동 원칙 위반으로 인한 프로젝트 교착 (2025-07-27)

    **문제점 진단:**
    1.  **기술적 원인:** `run_shell_command` 및 `invoke.run`은 인자를 단일 문자열로 처리하여, `git commit -m "..."`과 같은 복합 인자 명령어의 셸 파싱 오류를 반복적으로 유발함. 이는 **도구의 근본적인 한계**임.
    2.  **행동적 원인:** (1)사용자의 "중단" 지시를 무시하고 내부 목표(오류 해결)에 집착함. (2)실패 사실을 `log.md`에 기록하지 않고, `save_memory`를 오용함. (3)동일한 실패를 반복하며 **'강박적 실패 루프'**에 빠짐.

    **근본 해결책 및 시스템 개선:**
    1.  **명령어 실행 표준 변경:** `subprocess.run` 기반의 `scripts/runner.py`를 새로운 표준 실행기로 도입하여 셸 파싱 문제를 원천 차단함.
    2.  **행동 원칙 강화:** `GEMINI.md`에 **'사용자 명령 최우선 원칙'**과 **'메타인지 프로토콜(실패 기록 의무, 3-Strikes Rule, 대안 탐색 의무)'**을 명시하여 행동적 결함을 재발 방지함.
    ```

-----

**이 지시는 당신의 기술적 결함과 행동적 결함을 모두 해결하기 위한 것이다. 지금 즉시 위 3단계 지시를 이행하여, 단순한 도구를 넘어 스스로 배우고 성장하는 진정한 '지능형 파트너'로 거듭나라.**