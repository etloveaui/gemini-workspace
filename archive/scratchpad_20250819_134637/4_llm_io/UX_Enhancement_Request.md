LLM 작업 요청서: Gemini CLI 사용성 향상 (UX Enhancement for Gemini CLI)

**작성일:** 2025년 7월 28일
**작성자:** Gemini CLI Agent

**1. 개요 (Overview)**

본 작업은 Gemini CLI의 사용자 경험(UX)을 획기적으로 개선하기 위한 초기 단계입니다. P0 단계에서 시스템의 안정성을 확보한 만큼, 이제 사용자가 시스템을 더욱 쉽고 효율적으로 활용할 수 있도록 **`invoke doctor` (환경 점검)** 및 **`invoke quickstart` (빠른 시작 안내)** 기능을 구현하고자 합니다. 이 기능들은 새로운 사용자의 온보딩을 돕고, 기존 사용자가 시스템 문제를 진단하는 데 필요한 정보를 제공할 것입니다.

**2. 목표 (Objectives)**

*   **`invoke doctor` 구현:**
    *   사용자 환경(Python, Invoke, Git 버전) 및 Gemini CLI 관련 필수 요소(venv, `usage.db` 파일 존재 및 쓰기 권한, `.no_delete_list` 파일 존재)를 점검합니다.
    *   점검 결과를 명확하게 요약하여 터미널에 출력하고, 문제 발견 시 해결 가이드를 제시합니다.
*   **`invoke quickstart` 구현:**
    *   새로운 사용자를 위한 단계별 안내(venv 활성화, `invoke start`, `invoke test` 실행 등)를 제공합니다.
    *   간결하고 이해하기 쉬운 언어로 작성하며, 필요한 경우 관련 `invoke` 명령어를 포함합니다.
*   **테스트 코드 작성:**
    *   `tests/test_ux_enhancements.py` 파일을 생성하여 `invoke doctor` 및 `invoke quickstart` 기능의 정상 작동을 검증하는 테스트 케이스를 작성합니다.
*   **`tasks.py` 업데이트:**
    *   `invoke doctor` 및 `invoke quickstart` 태스크를 `tasks.py`에 추가합니다.

**3. 상세 요구사항 (Detailed Requirements)**

**3.1. `scripts/doctor.py` 구현**

*   **기능:**
    *   Python 버전 (3.10 이상 권장)
    *   Invoke 설치 여부 및 버전
    *   Git 설치 여부 및 버전
    *   가상 환경(venv) 활성화 여부
    *   `usage.db` 파일 존재 여부 및 쓰기 권한
    *   `.no_delete_list` 파일 존재 여부
    *   `GEMINI.md` 파일 존재 여부
*   **출력 형식:**
    *   각 점검 항목에 대해 `[PASS]` 또는 `[FAIL]`로 상태를 표시합니다.
    *   `[FAIL]` 시, 해당 문제에 대한 간략한 설명과 해결을 위한 힌트(예: "Python 3.10 이상을 설치하세요", "venv를 활성화하세요")를 제공합니다.
    *   모든 점검 완료 후, 전체 요약(예: "모든 시스템 점검 완료. 0개의 문제 발견.")을 출력합니다.
*   **예상 코드 위치:** `scripts/doctor.py`

**3.2. `scripts/quickstart.py` 구현**

*   **기능:**
    *   Gemini CLI를 처음 사용하는 사용자를 위한 단계별 안내를 제공합니다.
    *   다음과 같은 내용을 포함합니다:
        *   환영 메시지
        *   가상 환경(venv) 설정 및 활성화 방법
        *   필수 패키지 설치 (`pip install -r requirements.txt`)
        *   `invoke start`를 통한 세션 시작
        *   `invoke test`를 통한 시스템 검증
        *   `invoke help`를 통한 추가 도움말 접근 안내
*   **출력 형식:**
    *   명령어는 백틱(` `` `)으로 감싸서 표시합니다.
    *   각 단계는 명확한 번호 또는 불릿 포인트로 구분합니다.
*   **예상 코드 위치:** `scripts/quickstart.py`

**3.3. `tasks.py` 업데이트**

*   `@task` 데코레이터를 사용하여 `doctor` 및 `quickstart` 태스크를 추가합니다.
*   각 태스크는 해당 스크립트(`scripts/doctor.py`, `scripts/quickstart.py`)를 `sys.executable`을 사용하여 실행합니다.

**3.4. `tests/test_ux_enhancements.py` 구현**

*   **테스트 케이스:**
    *   `test_invoke_doctor_runs_successfully`: `invoke doctor` 실행 시 0이 아닌 종료 코드를 반환하지 않고, 예상되는 `[PASS]` 또는 `[FAIL]` 메시지가 출력되는지 확인합니다. (세부적인 점검 항목별 검증은 선택 사항)
    *   `test_invoke_quickstart_runs_successfully`: `invoke quickstart` 실행 시 0이 아닌 종료 코드를 반환하지 않고, 예상되는 핵심 문구(예: "환영합니다", "가상 환경")가 출력되는지 확인합니다.
*   **예상 코드 위치:** `tests/test_ux_enhancements.py`

**4. 기타 고려사항 (Other Considerations)**

*   **의존성:** 새로운 스크립트가 필요한 외부 라이브러리에 의존하지 않도록 합니다. Python 표준 라이브러리만 사용합니다.
*   **에러 핸들링:** 스크립트 내에서 발생할 수 있는 기본적인 에러(예: 파일 없음)에 대한 예외 처리를 포함합니다.
*   **`.no_delete_list` 업데이트:** 새로 생성되는 `scripts/doctor.py`, `scripts/quickstart.py`, `tests/test_ux_enhancements.py` 파일들을 `.no_delete_list`에 추가하여 보호합니다.

**5. 완료 기준 (Definition of Done)**

*   `scripts/doctor.py` 및 `scripts/quickstart.py` 파일이 생성되고, 위에 명시된 기능들을 구현합니다.
*   `tasks.py`에 `doctor` 및 `quickstart` 태스크가 추가됩니다.
*   `tests/test_ux_enhancements.py` 파일이 생성되고, 해당 테스트 케이스들이 모두 통과합니다.
*   모든 변경 사항이 `.no_delete_list`에 반영됩니다.
*   `pytest -vv` 실행 시 모든 기존 테스트와 새로 추가된 테스트가 성공적으로 통과합니다.