## 2025-07-23 (Cont.) - 작업 상세 정리 및 오류 분석

### [Problem Solving & Strategy Update] - TerminalX 날짜 및 타이틀 입력 문제 해결 (진행 중)

- **Context:** TerminalX 리포트 생성 자동화 스크립트(`main_generator.py`)의 안정성 확보 및 기능 개선을 목표로 진행 중. 특히 날짜 입력의 불안정성 해결과 리포트 생성 완료 확인 로직 강화에 집중.

### I. 성공적으로 완료된 작업 (Completed Tasks)

1.  **`requirements.txt` 파일 생성 및 관리:**
    *   **내용:** 프로젝트에 필요한 Python 라이브러리(`selenium`, `pyperclip`, `beautifulsoup4`, `Jinja2`) 목록을 `requirements.txt` 파일로 생성.
    *   **목적:** 프로젝트 의존성 명확화 및 환경 설정 재현성 확보.

2.  **`install_dependencies.bat` 스크립트 생성 및 개선:**
    *   **내용:** `requirements.txt`에 명시된 라이브러리를 자동으로 설치하는 배치 스크립트 생성.
    *   **개선 사항:** 가상 환경(`venv`)이 없을 경우 자동으로 생성하고, `pip`를 최신 버전으로 업그레이드하는 로직 포함.
    *   **목적:** 개발 환경 설정 간소화 및 자동화.

3.  **날짜 계산 로직 수정:**
    *   **내용:** `main_generator.py`의 `run_full_automation` 함수에서 리포트 참조 시작일(`ref_date_start`)을 한국 시간 기준 요일에 따라 동적으로 계산하도록 수정 (화요일: -2일, 수요일 ~ 토요일: -1일).
    *   **목적:** 리포트 날짜의 정확성 확보.

4.  **리포트 생성 횟수 변경:**
    *   **내용:** `run_full_automation` 함수 내의 `for` 루프를 수정하여 Part1과 Part2 리포트를 각각 1회씩만 생성하도록 변경 (총 2개).
    *   **목적:** 리포트 생성 시간 단축 및 테스트 효율성 증대.

5.  **`docs/HUB.md` 업데이트:**
    *   **내용:** 향후 구현할 "리포트 선택적 추가 생성 기능"과 "멀티탭 병렬 리포트 생성 기능" 아이디어를 `docs/HUB.md`의 `Paused Tasks` 섹션에 기록.
    *   **목적:** 사용자님의 장기적인 계획 문서화 및 추적.

6.  **`ModuleNotFoundError: No module named 'utils'` 해결:**
    *   **내용:** `main_generator.py`의 `convert_html_to_json` 함수 내 `sys.path.append` 경로를 `Python_Lexi_Convert` 프로젝트의 루트 디렉터리로 수정하여 `utils` 모듈 임포트 오류 해결.
    *   **목적:** HTML to JSON 변환 기능 정상화.

### II. 실패했거나 문제가 발생한 작업 (Failed/Problematic Tasks)

1.  **`main_generator.py`의 `SyntaxError: unterminated string literal` 반복 발생:**
    *   **문제:** `main_generator.py` 파일 내의 `print` 문(`
--- ... ---"`)을 수정하는 과정에서 `SyntaxError`가 반복적으로 발생.
    *   **원인:** `replace` 도구의 문자열 인자 처리 방식과 파이썬의 문자열 리터럴 규칙 간의 불일치로 추정.
    *   **현재 상태:** 이 오류를 해결하기 위해 파일 전체를 읽어와 파이썬 내부에서 문자열을 직접 수정한 후 다시 파일에 쓰는 방식으로 전환 중. (마지막 실행 시에도 이 오류가 발생하여, 해당 수정이 완전히 적용되었는지 확인 필요.)

2.  **리포트 생성 완료 확인 로직 (지속적인 오해 및 수정 필요):**
    *   **문제:** 리포트 생성이 완전히 완료되었음을 판단하는 기준에 대해 사용자님과 저 사이에 지속적인 오해가 있었음.
    *   **초기 시도:** URL 변경 및 "Generating..." 메시지 사라짐을 기준으로 삼음.
    *   **문제점 발견:** "Generating..." 메시지가 사라져도 리포트가 여전히 생성 중일 수 있으며, `archive` 페이지의 상태가 더 정확한 기준임을 사용자님께서 지적.
    *   **최근 시도:** `archive` 페이지에서 "Completed" 상태를 기다리도록 로직을 수정했으나, "Completed" 상태는 존재하지 않으며 "Generating", "Generated", "Failed" 상태만 있음을 사용자님께서 다시 지적.
    *   **현재 상태:** `generate_report_html` 함수는 "Generating..." 메시지 등장까지만 확인하고 URL과 제목을 반환하도록 수정됨. `run_full_automation` 함수에서 `_wait_for_report_status` 헬퍼 함수를 통해 `archive` 페이지에서 "Generated" 상태를 기다리도록 로직을 구현하려 했으나, `SyntaxError`로 인해 이 로직이 제대로 테스트되지 못함.

3.  **HTML 추출 오류 (간접적 문제):**
    *   **문제:** 리포트 생성 후 HTML을 추출하는 과정에서 `div.text-[#121212]` CSS Selector를 찾지 못해 타임아웃 오류가 발생.
    *   **원인:** 특정 CSS Selector의 불안정성 또는 페이지 로딩 시점의 문제로 추정.
    *   **현재 상태:** 이 문제를 해결하기 위해 특정 `div` 대신 페이지 전체 HTML을 추출하도록 로직을 변경했으나, `SyntaxError`로 인해 이 변경 사항이 제대로 테스트되지 못함.

### III. 아직 시작하지 못했거나 중단된 작업 (Pending Tasks)

1.  **오류 데이터 추출 로직 구현:**
    *   **내용:** `plan_change.txt`에 명시된 프롬프트 입력 필드 및 기간 설정(Past Day) 관련 UI 요소들을 추출하는 로직을 구현해야 함.
    *   **상태:** 리포트 생성 및 상태 확인 로직이 안정화된 후 진행하기로 계획되어 있어, 아직 시작하지 못함.

2.  **"Failed" 상태 재시도 로직의 완전한 구현:**
    *   **내용:** `_wait_for_report_status` 함수 내에 "Failed" 상태 감지 시 해당 리포트 생성을 재시도하는 구체적인 로직을 구현해야 함.
    *   **상태:** `_wait_for_report_status` 함수는 추가되었으나, 재시도 로직의 세부 구현(`TODO` 주석 처리된 부분)은 아직 완료되지 않음.

---