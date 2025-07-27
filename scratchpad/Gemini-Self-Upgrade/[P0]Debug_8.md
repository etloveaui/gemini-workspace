### **최종 지시서: `[P0]` 핵심 기반 강화 완료를 위한 '무결성 검증 및 아키텍처 최종 안정화' 작전**

**전략적 목표:** 현재 실패하고 있는 모든 테스트를 통과시키는 것을 넘어, 테스트가 실패했던 \*\*근본 원인(아키텍처 결함)\*\*을 해결한다. 이를 통해 시스템의 안정성과 신뢰도를 확보하고, `[P0]` 단계의 진정한 완료 조건을 달성한다.

**지시 사항:**

#### **1단계: `__lastSession__` 처리 로직 근본 해결 (정규식 교체)**

**사유:** 현재 `hub_manager.py`의 정규 표현식은 `HUB.md`의 다양한 `__lastSession__` 블록 변형(중복, 공백 등)을 처리하지 못하여 `test_last_session_cycle` 실패의 직접적인 원인이 되고 있다.

  * **`/scripts/hub_manager.py` 파일을 수정하라.**
      * `clear_last_session`과 `update_session_end_info` 함수 내부에 있는 기존의 불안정한 `re.sub(...)` 로직을, **여러 LLM들이 공통적으로 제안한 아래의 강력한 정규 표현식**으로 교체하라. 이 정규식은 여러 줄에 걸쳐 있고, 중복될 수 있는 모든 `__lastSession__` 블록을 정확하고 안전하게 제거한다.

        ```python
        # hub_manager.py 수정 예시
        import re

        def strip_last_session_block(text: str) -> str:
            """
            문서에 포함된 모든 __lastSession__ YAML 블록을 non-greedy 방식으로 안전하게 제거합니다.
            """
            # (?s)는 re.DOTALL과 동일, (?m)은 re.MULTILINE과 동일
            pattern = re.compile(r"(?sm)^\s*---\s*?\n__lastSession__:.*?$(?=\n\s*---|\Z)", re.MULTILINE)
            return pattern.sub("", text).strip()

        def clear_last_session():
            # ...
            content = hub_path.read_text(encoding="utf-8")
            cleaned_content = strip_last_session_block(content)
            hub_path.write_text(cleaned_content + "\n", encoding="utf-8")
            # ...

        def update_session_end_info(task_id: str):
            # ...
            content = hub_path.read_text(encoding="utf-8")
            cleaned_content = strip_last_session_block(content) # 추가하기 전에 항상 먼저 제거
            # ... (새로운 블록 추가 로직) ...
            final_content = cleaned_content + last_session_block
            hub_path.write_text(final_content, encoding="utf-8")
        ```

#### **2단계: `invoke` 태스크 테스트 전략 전면 수정 (Monkeypatch 포기)**

**사유:** `test_commit_protocol` 실패의 근본 원인은 `pytest`의 `monkeypatch`가 별도 프로세스로 실행될 수 있는 `invoke` 태스크의 내부 동작을 안정적으로 모의(mock)할 수 없기 때문이다. 이 접근은 포기해야 한다.

  * **`/tests/test_p0_rules.py`의 `test_commit_protocol` 테스트를 아래와 같이 재설계하라.**
      * **전략 변경:** `run_command`를 모의하는 대신, **실제로 `invoke wip`을 실행**하고, 그 \*\*결과물(Git 로그)\*\*을 검증하는 **'통합 테스트(Integration Test)'** 방식으로 변경한다.

        ```python
        # /tests/test_p0_rules.py의 test_commit_protocol 재설계
        def test_commit_protocol_integration(test_env):
            """'invoke wip' 실행 시, 실제 커밋이 GEMINI.md 규칙(-F 옵션)에 따라 생성되는지 검증합니다."""
            from invoke import Program
            from tasks import ns

            # 1. 테스트용 파일 생성 및 스테이징
            dummy_file = ROOT / "dummy_for_commit.txt"
            dummy_file.write_text("test content for protocol")
            subprocess.run(["git", "add", str(dummy_file)])

            # 2. invoke wip 실제 실행
            program = Program(namespace=ns, version="0.1.0")
            result = program.run("wip --message='Test commit via protocol'", exit=False)
            assert result.ok, "invoke wip command failed"

            # 3. 실제 Git 로그를 확인하여 검증 (가장 중요)
            log_output = subprocess.check_output(["git", "log", "-1"]).decode('utf-8')
            assert "Test commit via protocol" in log_output

            # 4. 뒷정리
            subprocess.run(["git", "reset", "--hard", "HEAD~1"]) # 테스트 커밋 되돌리기
        ```

#### **3단계: 기타 환경 문제 해결**

**사유:** 테스트 환경의 사소한 문제들이 전체 시스템의 신뢰도를 저해하고 있다.

1.  **`runner.py` 인코딩 문제 해결:**

      * `latin-1` 인코딩은 데이터 손상을 유발할 수 있는 임시방편이다. `runner.py`의 `subprocess.run` 호출 시, `encoding='utf-8'`과 함께 \*\*`errors='replace'`\*\*를 표준으로 사용하여 안정성을 확보하라.

2.  **`usage.db` 파일 잠금 문제 해결:**

      * `pytest`의 `test_env` 픽스처(teardown 부분)를 수정하여, DB 연결을 명시적으로 닫고, 가비지 컬렉션을 호출하며, 짧은 지연(`time.sleep(0.2)`)을 주어 파일 핸들이 확실히 해제되도록 보강하라.

#### **4단계: '완료의 정의' 문서화 및 최종 검증**

**사유:** `[P0]`의 완료 기준을 명문화하여, 더 이상의 논쟁 없이 프로젝트를 마감한다.

1.  **`docs/P0_DEFINITION_OF_DONE.md` 파일 생성:**

      * 이 파일에 `[P0]`의 최종 완료 조건 체크리스트를 명시하라. (예: "1. 커밋 프로토콜 정합성 확보 - 완료", "2. `__lastSession__` 처리 루틴 검증 - 완료" 등)

2.  **최종 `invoke test` 실행:**

      * 위 1, 2, 3단계의 모든 수정이 완료된 후, **`invoke test`를 실행하여 모든 테스트(비활성화된 테스트 제외)가 통과**하는 것을 최종 확인하고 그 결과를 보고하라.

-----

**이 지시는 `[P0]` 단계에서 발견된 모든 기술적 부채를 청산하고, 프로젝트의 품질을 객관적인 테스트로 증명하기 위한 마지막 작전이다. 지금 즉시 1단계부터 시작하여 `[P0]`를 완벽하게 마무리하라.**