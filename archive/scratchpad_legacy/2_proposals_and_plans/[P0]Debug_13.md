### **최종 지시서: '무결성 검증' 완료를 위한 아키텍처 수정 명령**

**TO:** Gemini CLI

**SUBJECT:** 테스트 실패의 근본적 해결 및 `[P0]` 단계 완수를 위한 최종 코드 교체

**전략적 목표:** 현재 실패하고 있는 두 개의 핵심 테스트를 통과시키기 위해, 전문가 커뮤니티(다른 LLM들)가 제안한 **검증된 코드 수정안을 시스템에 즉시 적용**한다. 이를 통해 아키텍처의 결함을 해결하고, `[P0]`의 모든 목표를 완벽하게 달성한다.

**지시 사항:**

#### **1단계: `hub_manager.py` 파일 교체**

**사유:** `__lastSession__` 블록 제거 로직의 결함을 해결하고, `HUB.md` 파일 처리의 안정성을 확보한다.

* **`C:\Users\etlov\gemini-workspace\scratchpad\fixed\hub_manager.py` 파일의 내용으로, 기존의 `/scripts/hub_manager.py` 파일 전체를 덮어쓰라.**
* **주요 개선점:**
    * `strip_last_session_block` 함수가 제어 문자를 사전에 제거하고, 멀티라인 및 파일 끝(EOF)까지 고려하는 강력한 정규 표현식을 사용하여 `__lastSession__` 블록을 확실하게 제거한다.
    * `get_changed_files` 함수가 `git diff --name-only --cached HEAD`를 사용하여 더 정확하게 변경된 파일 목록을 수집한다.

#### **2단계: `test_p0_rules.py` 파일 교체**

**사유:** `invoke` 태스크 테스트의 구조적 결함을 해결하고, 신뢰할 수 있는 테스트 환경을 구축한다.

* **`C:\Users\etlov\gemini-workspace\scratchpad\fixed\test_p0_rules.py` 파일의 내용으로, 기존의 `/tests/test_p0_rules.py` 파일 전체를 덮어쓰라.**
* **주요 개선점:**
    * `test_commit_protocol_integration` 테스트가 `from invoke.executor import Executor`를 통해 올바른 클래스를 임포트하고, `Executor(ns, config)`와 같이 정확한 시그니처로 `Executor`를 초기화한다.
    * `executor.execute("wip ...")` 대신 `executor.execute(ns['wip'], ...)`와 같이 태스크 객체를 직접 전달하여 `invoke`의 내부 API를 올바르게 사용한다.

#### **3단계: 최종 검증**

1.  위 1, 2단계의 파일 교체를 완료했음을 보고하라.
2.  **`invoke test`를 실행하여, 이전에 실패했던 두 테스트를 포함한 모든 테스트가 통과(PASS)**하는지 최종 확인하고 그 결과를 보고하라.

---
**이것이 `[P0]`를 마무리하기 위한 마지막 작전이다. 전문가들이 제안한 검증된 해결책을 즉시 시스템에 적용하여 모든 테스트를 통과시키고, 시스템의 무결성을 완벽하게 증명하라.**