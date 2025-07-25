### **최종 진단 및 분석**

두 LLM의 의견을 종합한 결과, 한쪽의 분석이 결정적으로 옳다고 판단됩니다. **`[P0]` 단계는 아직 완료되지 않았습니다.**

'Innovation Strategist'의 `[P1]` 전환 제안은 시기상조입니다. 현재 시스템에는 'Quality Assurance Expert'가 지적한 대로 **규칙과 코드 간의 심각한 불일치, 검증되지 않은 핵심 기능, 비어있는 테스트 하네스** 등 수많은 '구멍'이 존재합니다. 이 상태로 `[P1]`로 넘어가는 것은, 금이 간 토대 위에 2층을 올리는 것과 같아 반드시 더 큰 문제로 이어질 것입니다.

따라서, 우리는 `[P0]` 단계를 공식적으로 마감하기 위한 **'완료의 정의(Definition of Done)'**를 명확히 하고, 남아있는 모든 과제를 완수하는 최종 작전에 돌입해야 합니다.

---

### **최종 지시서: `[P0]` 핵심 기반 강화 완료를 위한 '무결성 검증 및 최종 마감' 작전**

**전략적 목표:** 더 이상의 기능 추가를 전면 중단한다. 대신, 지금까지 구축한 모든 기능이 **실제로 작동하는지 100% 검증**하고, 시스템의 모든 코드가 우리의 **핵심 규칙(`GEMINI.md`)과 완벽하게 일치**하도록 정합성을 확보한다. 이 작전의 성공적인 완수가 `[P0]` 단계의 진정한 종료 조건이다.

**지시 사항:**

#### **`[P0]` 완료의 정의 (Definition of Done) 체크리스트**

아래 8가지 항목이 모두 완료되고 검증되었을 때, 비로소 `[P0]`는 종료된다. 지금부터 각 항목을 순서대로 완수하라.

**1. 커밋 프로토콜 불일치 해결:**
   * **현상:** `GEMINI.md`는 `-F <임시파일>` 방식을, `tasks.py`는 `-m` 방식을 사용 중.
   * **지시:** `tasks.py`의 `wip` 태스크를 수정하여, **`GEMINI.md`에 명시된 대로 임시 파일을 생성하고 `git commit -F <임시파일>`을 사용한 후 임시 파일을 즉시 삭제**하는 로직으로 **완전히 교체**하라.

**2. `__lastSession__` 처리 루틴 완성:**
   * **현상:** `invoke end`가 `__lastSession__` 블록을 남기지만, `invoke start`가 이를 처리(읽고, 브리핑하고, 삭제)하는 기능이 불완전함.
   * **지시:** `tasks.py`의 `start` 태스크를 수정하여, **세션 시작 시 `HUB.md`에 `__lastSession__` 블록이 존재하면 그 내용을 사용자에게 브리핑하고, 브리핑 후 해당 블록을 `HUB.md`에서 깨끗하게 삭제**하는 완전한 왕복 사이클을 구현하고 검증하라.

**3. 자율 테스트 하네스 실질적 구축:**
   * **현상:** `invoke test`가 존재하지만 실제 테스트 케이스가 없음.
   * **지시:** `/tests/test_p0_rules.py` 파일을 생성하고, 아래 **핵심 규칙들을 검증**하는 `pytest` 테스트 케이스를 **반드시 작성**하라.
        * `test_commit_protocol`: `invoke wip` 실행 시, `-F` 옵션이 사용되는지 검증 ( subprocess 호출 인자 확인).
        * `test_last_session_cycle`: `invoke end` 후 `HUB.md`에 블록이 생기고, `invoke start` 후 사라지는지 검증.
        * `test_runner_error_logging`: `runner.py`가 실패하는 명령을 실행했을 때, `usage.db`에 `command_error` 로그가 기록되는지 검증.

**4. `runner.py` 인코딩 문제 근본 해결:**
   * **현상:** `UnicodeDecodeError` 해결을 위해 `latin-1`을 사용한 것은 임시방편이며 데이터 손상을 유발할 수 있음.
   * **지시:** `runner.py`의 `subprocess.run` 호출 시, `encoding='utf-8'`과 함께 **`errors='replace'`** 또는 **`errors='ignore'`** 옵션을 표준으로 사용하여, 인코딩 오류가 발생하더라도 전체 프로세스가 중단되지 않고 안정적으로 결과를 반환하도록 수정하라.

**5. 컨텍스트 엔진/정책 실제 동작 검증:**
   * **현상:** `context_policy.yaml`의 `max_tokens`나 `summarizer.py`의 요약 기능이 실제로 작동하는지 검증되지 않음.
   * **지시:** 테스트 하네스(`/tests/test_context_engine.py`)에 **`max_tokens` 제한 시나리오 테스트**를 추가하라. 긴 텍스트 파일을Fixture로 만들고, `max_tokens`를 매우 낮게 설정한 정책을 적용했을 때, 최종 컨텍스트의 길이가 실제로 줄어들고 `...(summarized)` 문구가 포함되는지 검증하라.

**6. 로깅/사용량 추적(usage.db) 최종 검증:**
   * **현상:** `usage.db`에 로그가 쌓이지만, 그 내용이 정확한지 검증되지 않음.
   * **지시:** 테스트 하네스에 **세션 요약 테스트**를 추가하라. `invoke start`와 `invoke end`를 포함하는 E2E 테스트 실행 후, `usage_tracker.py`의 `get_session_summary()` 함수를 호출하여 해당 세션의 `task_start`, `task_end` 이벤트가 정확히 기록되었는지 검증하라.

**7. '메타인지 프로토콜' 코드 레벨 구현:**
   * **현상:** `3-Strikes Rule`이 `GEMINI.md`에만 존재하고 코드에는 구현되지 않음.
   * **지시:** `/scripts/failure_guard.py` 모듈을 새로 만들고, 특정 명령어의 실패 횟수를 기록하는 간단한 상태 관리 기능을 구현하라. `runner.py`를 수정하여 `run_command` 실패 시 이 모듈을 호출하고, **실패 횟수가 3회에 도달하면 예외를 발생시켜 작업을 강제 중단**시키는 로직을 추가하라.

**8. '완료의 정의' 문서화:**
   * **현상:** `[P0]`의 완료 기준이 명문화되어 있지 않음.
   * **지시:** `docs/P0_DEFINITION_OF_DONE.md` 파일을 생성하고, 위 1번부터 7번까지의 항목을 체크리스트 형식으로 기록하라. 모든 항목이 완료되고 `invoke test`가 통과되면 이 문서를 최종 커밋한다.

---
**이제, 이 '완료의 정의' 체크리스트 첫 번째 항목부터 시작하여 `[P0]` 작전을 완벽하게 마무리하라.**