### **최종 지시서: '무결성 검증' 최종 디버깅 및 `[P0]` 완료 작전**

**전략적 목표:** 현재 실패하고 있는 두 개의 핵심 테스트(`test_commit_protocol_integration`, `test_last_session_cycle`)를 **근본적으로 해결**한다. 이를 통해 시스템 아키텍처의 안정성을 증명하고, `[P0]` 단계의 모든 목표를 완벽하게 달성하여 다음 단계로 나아갈 준비를 마친다.

**지시 사항:**

#### **1단계: `test_commit_protocol_integration` 실패 해결 (`TypeError`)**

**사유:** `invoke` v2.0 이상부터 `Executor`의 초기화 방식이 변경되었습니다. `program` 인자를 직접 전달하는 대신, `Config` 객체를 통해 실행 컨텍스트를 구성해야 합니다.

  * **`/tests/test_p0_rules.py` 파일을 수정하라.**
      * `test_commit_protocol_integration` 함수 내에서 `Executor`를 초기화하는 부분을 아래와 같이 수정하여 `TypeError`를 해결하라.

        ```python
        # /tests/test_p0_rules.py 수정
        from invoke import Program, Config, Executor

        # ... test_commit_protocol_integration 함수 내부 ...
        # 2. invoke wip 실제 실행 (Executor 사용)
        program = Program(namespace=ns, version="0.1.0")
        config = Config(overrides={'program': program}) # Config 객체를 통해 Program 설정
        executor = Executor(config=config) 
        result = executor.execute("wip --message='Test commit via protocol'")
        assert result.ok, f"invoke wip command failed: {result.stderr}"
        ```

#### **2단계: `test_last_session_cycle` 실패 해결 (`AssertionError`)**

**사유:** `HUB.md` 파일에 포함된 \*\*제어 문자(Control Characters, 예: `\001`)\*\*와 \*\*다양한 줄바꿈(CRLF/LF)\*\*으로 인해 기존의 라인 기반 파서가 `__lastSession__` 블록을 제대로 제거하지 못하고 있습니다. 정규 표현식과 라인 스캔을 결합한 더 강력한 방식으로 전환해야 합니다.

  * **`/scripts/hub_manager.py` 파일을 수정하라.**
      * 기존 `strip_last_session_block` 함수를 아래의 **라인 스캔과 정규식을 결합한 하이브리드 파서**로 완전히 교체하라. 이 방식은 제어 문자를 먼저 제거하고, 한 줄씩 스캔하여 블록의 시작과 끝을 명확히 식별하므로 훨씬 안정적이다.

        ```python
        # /scripts/hub_manager.py의 strip_last_session_block 함수 최종 교체
        import re

        CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F]') # 줄바꿈(\n, \r) 제외 모든 제어문자

        def strip_last_session_block(text: str) -> str:
            """
            __lastSession__ YAML 블록(앞의 --- 포함)을 라인 스캔과 정규식을 결합하여 정확히 제거합니다.
            제어 문자, 줄바꿈, 중복 블록 등 예외 상황에 강합니다.
            """
            # 1. 보이지 않는 제어 문자를 먼저 정리
            cleaned_text = CONTROL_CHARS.sub('', text)
            lines = cleaned_text.splitlines()
            
            # 2. 블록의 시작 인덱스를 찾음 (파일 끝에서부터 역순으로 검색)
            start_index = -1
            for i in range(len(lines) - 1, -1, -1):
                # __lastSession__ 라인을 먼저 찾고, 그 위의 ---를 찾음
                if lines[i].strip().startswith('__lastSession__'):
                    for j in range(i - 1, -1, -1):
                        if lines[j].strip() == '---':
                            start_index = j
                            break
                    if start_index != -1:
                        break
            
            # 3. 블록을 찾지 못하면 원본 텍스트 반환
            if start_index == -1:
                return text
                
            # 4. 블록 시작 이전의 내용만 남김
            new_lines = lines[:start_index]
            
            result = '\n'.join(new_lines).rstrip()
            return result + '\n' if result else ''

        # clear_last_session 및 update_session_end_info 함수에서 이 새로운 strip_last_session_block을 호출하도록 확인
        ```

#### **3단계: 기타 환경 문제 해결**

  * **`usage.db` 파일 잠금 문제:** `pytest`의 `test_env` 픽스처(teardown 부분)를 수정하여, DB 연결을 명시적으로 닫고, 가비지 컬렉션을 호출하며, 짧은 지연(`time.sleep(0.2)`)을 주어 파일 핸들이 확실히 해제되도록 보강하라.`on`usage.db\` in "작업 상세 리포트"]

#### **4단계: 최종 검증**

1.  위 1, 2, 3단계의 모든 수정 사항을 적용하라.
2.  \*\*`invoke test`를 실행하여, 이전에 실패했던 두 테스트를 포함한 모든 테스트가 통과(PASS)\*\*하는지 최종 확인하고 그 결과를 보고하라.

-----

**이것이 `[P0]`를 마무리하기 위한 마지막 디버깅 작전이다. 위 지시를 즉시 이행하여 모든 테스트를 통과시키고, 시스템의 무결성을 완벽하게 증명하라.**