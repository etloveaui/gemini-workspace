**LLM 작업 지시 요청서: Gemini CLI 시스템 개선 및 다음 단계 진행**

**작성일:** 2025-07-28
**요청 대상:** LLM (Gemini)
**작성자:** Gemini CLI Agent

**1. 수행된 주요 작업 요약:**

최근 `[P1]UX_01_Doctor_Quickstart_Help` 태스크를 성공적으로 완료했습니다. 주요 내용은 다음과 같습니다.

*   **`invoke doctor`, `invoke quickstart`, `invoke help` 기능 구현:** 사용자 진입점 강화를 위한 핵심 UX 기능을 구현하고, 관련 스크립트(`scripts/doctor.py`, `scripts/quickstart.py`, `scripts/help.py`) 및 문서(`docs/HELP.md`)를 생성했습니다.
*   **Windows 환경 인코딩 문제 해결:** `tasks.py`에서 PowerShell을 통해 스크립트를 실행하도록 변경하여 Windows 환경에서의 한글 출력 인코딩 문제를 우회했습니다.
*   **테스트 코드 개선:** 새로 구현된 기능에 대한 `tests/test_ux_enhancements.py`를 작성하고, 기존 `tests/test_help_system.py`의 `UnicodeDecodeError` 문제를 해결하여 모든 테스트가 통과하도록 조치했습니다.
*   **Git 관리 및 기록:** 모든 변경 사항을 Git에 커밋하고 `master` 브랜치에 머지했으며, `docs/tasks/gemini-cli-ux-enhancement/log.md`에 상세 작업 보고서를 기록하고 `docs/HUB.md`를 업데이트하여 작업 기록 시스템을 준수했습니다.

**2. `GEMINI.md` 개선 필요성 및 다른 LLM 의견 수렴 요청:**

현재 `GEMINI.md`는 Gemini CLI Agent의 핵심 행동 지침을 담고 있습니다. 하지만 최근의 작업 경험과 시스템의 발전 속도를 고려할 때, `GEMINI.md`가 현재 시스템의 요구사항에 다소 뒤처지는 느낌을 받습니다. 특히 다음과 같은 측면에서 개선이 필요하다고 생각합니다.

*   **동적 환경 변화 반영:** Windows 환경에서의 인코딩 문제와 같이, 실제 운영 환경에서 발생하는 미묘한 문제들에 대한 더욱 구체적이고 실용적인 지침이 필요합니다.
*   **메타인지 프로토콜의 정교화:** "3-Strikes Rule"과 같은 메타인지 프로토콜은 중요하지만, 실패 원인 분석 및 대안 탐색 과정에 대한 더욱 상세한 가이드라인이 필요합니다.
*   **자동화된 기록 시스템의 강화:** 현재 `log.md` 및 `HUB.md` 기록은 수동으로 이루어지는 부분이 많습니다. 이를 더욱 자동화하고, 기록 주기를 유연하게 조절할 수 있는 메커니즘이 필요합니다.
*   **새로운 기능 및 도구 통합:** `Google Search`와 같은 새로운 도구의 통합 및 활용에 대한 지침이 `GEMINI.md`에 명확히 반영되어야 합니다.

**요청:**
다른 LLM(예: ChatGPT, Claude, Grok 등)에게 현재 `GEMINI.md`의 내용을 제공하고, 다음 질문에 대한 의견을 수렴하여 개선 방안을 도출해 주십시오.

*   **`GEMINI.md`의 현재 내용 중 개선이 필요하다고 생각하는 부분은 무엇입니까?**
*   **어떤 새로운 규칙이나 지침을 추가하면 Gemini CLI Agent의 효율성과 안정성을 더욱 높일 수 있을까요?**
*   **특히 Windows 환경에서의 개발 및 운영에 대한 추가적인 고려사항이나 모범 사례가 있다면 제안해 주십시오.**
*   **LLM Agent의 자율성과 사용자 통제 사이의 균형을 최적화하기 위한 아이디어가 있다면 공유해 주십시오.**

수렴된 의견을 바탕으로 `GEMINI.md`를 업데이트하는 작업 지시를 내려주십시오.

**3. 청사진에 따른 다음 요청:**

`[P0]` 및 `[P1]` 청사진에 따라, 다음 단계인 `[P1-1]: '실시간 웹 연동 에이전트' 구현`을 진행하고자 합니다.

**작업 지시:**

*   **목표:** 정적인 내부 파일을 넘어, 실시간 외부 정보에 접근하여 문제 해결 능력을 극대화하는 '실시간 웹 연동 에이전트'를 구현합니다.
*   **세부 기능:**
    1.  **`Google Search` 도구 공식 통합:** 내장된 웹 검색 도구를 `runner.py`를 통해 안정적으로 호출할 수 있는 인터페이스를 구축합니다.
    2.  **`web_agent.py` 모듈 생성:** `/scripts` 내부에 웹 검색, 결과 스크래핑, `summarizer.py`를 이용한 요약까지 전담하는 모듈을 생성합니다.
    3.  **`invoke search` 태스크 도입:** `tasks.py`에 `search` 태스크를 추가하여, 사용자가 `invoke search "검색어"` 형식으로 웹 검색을 직접 지시할 수 있도록 합니다.
*   **완료 조건:** `invoke search "Python official website"` 실행 시, 검색된 웹 페이지의 핵심 내용이 요약되어 터미널에 출력됩니다.
*   **브랜치:** `p1/web_agent_integration` 브랜치를 생성하고 해당 브랜치에서 작업합니다.
*   **테스트:** `tests/test_p1_web_tool.py`를 생성하여 웹 툴 호출 및 요약 검증 테스트를 포함합니다. (모킹 사용)
*   **기록:** 작업 진행 상황을 `docs/tasks/web-agent-integration/log.md`에 기록하고, `docs/HUB.md`를 업데이트합니다.
