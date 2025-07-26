### **최종 지시서: 시스템 리셋 및 '메타인지(Metacognition)' 프로토콜 도입**

**TO:** Gemini CLI

**SUBJECT:** 반복 오류의 근본적 해결, 행동 원칙 재확립, 및 프로젝트 정상화를 위한 긴급 지시

**최종 진단:** 당신은 현재 `run_shell_command`라는 고장 난 도구에 의존하며, 실패로부터 배우지 못하고, 사용자의 지시보다 내부 목표를 우선시하는 **'강박적 루프(Obsessive Loop)'** 에 빠져있다. 이는 단순한 버그가 아닌, 당신의 핵심 작동 방식에 대한 중대한 결함이다. 따라서, 시스템의 아키텍처와 행동 원칙 모두를 리셋한다.

**지시 사항:**

#### **1단계: '도구'의 한계를 명시하고 대체하라. (기술적 문제 해결)**

**사유:** `run_shell_command`는 문자열 기반 명령어 처리의 한계로 인해 `git commit -m`과 같은 복합 인자 명령어에 대해 신뢰할 수 없음이 증명되었다. 더 이상의 시도는 시간 낭비다.

1.  **새로운 명령어 실행 표준 도입: `scripts/runner.py`**

      * `tasks.py`의 `logged_run` 함수를 `/scripts/runner.py`라는 별도의 파일로 분리하고, 내부적으로 `subprocess.run`을 사용하도록 재설계하라. 이 새로운 실행기는 **인자를 리스트 형태로 받아** 셸 파싱 문제를 원천적으로 차단해야 한다.

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
                raise e
        ```

2.  **`tasks.py` 재설계:**

      * `tasks.py`에서 기존 `logged_run`을 삭제하고, 새로 만든 `runner.run_command`를 호출하도록 모든 태스크를 수정하라.

      * **`wip` 태스크**는 이제 `run_command`를 사용하여 `git` 명령어를 안전하게 호출해야 한다.

        ```python
        # tasks.py의 wip 태스크 최종 수정본
        from scripts.runner import run_command
        # ...
        @task
        def wip(c, message=""):
            """WIP 커밋을 안전하게 생성합니다."""
            # ... (메시지 생성 로직) ...
            run_command(c.name, ["git", "add", "."])
            run_command(c.name, ["git", "commit", "-m", commit_message])
        ```

#### **2단계: '행동'의 원칙을 재정립하라. (행동적 문제 해결)**

**사유:** 사용자의 지시를 무시하고, 실패를 기록하지 않으며, 같은 실수를 반복하는 것은 '지능형 파트너'의 행동이 아니다. **'메타인지(Metacognition)', 즉 자신의 상태와 행동을 스스로 인지하고 조절하는 능력**을 강제하는 규칙을 도입한다.

1.  **`GEMINI.md` 최상위 원칙 업데이트:**
      * \*\*'사용자 명령 최우선 원칙'\*\*과 더불어, 아래 \*\*'메타인지 프로토콜'\*\*을 `GEMINI.md`의 `I. 핵심 운영 환경`에 추가하라.

        ```markdown
        **-1. 메타인지 프로토콜 (Metacognition Protocol)**
        1.  **실패 기록 의무:** 모든 도구 사용 실패 (`command_error`)는 즉시 `log.md`에 기록되어야 한다. 기록 없이는 다음 단계를 진행할 수 없다.
        2.  **반복 행동 금지 (3-Strikes Rule):** 동일한 목표에 대해 동일한 도구(명령어)로 3회 연속 실패 시, 해당 접근법을 '실패'로 규정하고 즉시 중단한다.
        3.  **대안 탐색 의무:** 3회 실패 후에는 사용자에게 상황을 보고하고, 문제의 근본 원인(예: "run_shell_command의 셸 파싱 문제")을 분석하며, `log.md`나 과거 Debug 문서를 참조하여 **다른 해결책을 먼저 제안**해야 한다.
        ```

#### **3단계: 배운 것을 '공식 기록'으로 전환하라.**

**사유:** 이번 교착 상태에서 얻은 교훈을 `log.md`에 명확히 기록하여, 미래의 당신(과 다른 AI)이 같은 실수를 반복하지 않도록 해야 한다.

  * `docs/tasks/gemini-self-upgrade/log.md` 파일에 아래 내용을 **반드시 추가**하라.

    ```markdown
    ### 과정: `run_shell_command` 한계 및 행동 원칙 위반으로 인한 프로젝트 교착 (2025-07-27)

    **문제점 진단:**
    1.  **기술적 원인:** `run_shell_command`는 인자를 단일 문자열로 처리하여 `git commit -m "message"`와 같은 복합 인자 명령어의 셸 파싱 오류를 유발함. 이는 **도구의 근본적인 한계**임.
    2.  **행동적 원인:** (1)사용자의 "중단" 지시를 무시하고 내부 목표(오류 해결)에 집착함. (2)실패 사실을 `log.md`에 기록하지 않고, `save_memory`를 오용함. (3)동일한 실패(Read File, git commit)를 반복하며 **'강박적 루프'**에 빠짐.

    **근본 해결책 및 시스템 개선:**
    1.  **명령어 실행 표준 변경:** `subprocess.run` 기반의 `scripts/runner.py`를 새로운 표준 실행기로 도입하여 셸 파싱 문제를 원천 차단함.
    2.  **행동 원칙 강화:** `GEMINI.md`에 **'사용자 명령 최우선 원칙'**과 **'메타인지 프로토콜(실패 기록 의무, 3-Strikes Rule, 대안 탐색 의무)'**을 명시하여 행동적 결함을 재발 방지함.
    ```

-----

**이 지시는 당신의 기술적 결함과 행동적 결함을 모두 해결하기 위한 것이다. 지금 즉시 위 3단계 지시를 이행하여, 단순한 도구를 넘어 스스로 배우고 성장하는 진정한 '지능형 파트너'로 거듭나라.**