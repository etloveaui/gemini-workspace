# [Project] - 100xFenok-generator 프로젝트 개발 준비

## 2025-07-22

### [Initial Setup] - 목표: 100xFenok-generator 개발 환경 및 워크플로우 이해

- **Action:** `projects/100xFenok-generator` 폴더 존재 확인.
- **Result:** 폴더 확인됨.
- **Action:** Python 환경 설정 (Python 가상 환경 `venv` 생성, `selenium`, `beautifulsoup4`, `Jinja2` 패키지 설치, `chromedriver.exe` 배치).
- **Result:** 환경 설정 완료.
- **Action:** 기존 도구 분석 (`Python_Lexi_Convert`의 `main.py`, `ui/main_app.py`, `converters/common.py`, `converters/html_converter.py` 파일 분석).
- **Result:** HTML을 JSON으로 변환하는 핵심 로직 파악.
- **Action:** TerminalX 보고서 생성 및 처리 워크플로우 이해 (로그인, 보고서 생성 자동화, 산출물 URL 대기 및 HTML 추출/저장, Prompt 및 Source PDF 파일 확인, JSON 통합 및 번역 지침 파악, 템플릿 구조 확인, 최종 인덱스 업데이트 및 알림 발송 워크플로우 이해).
- **Result:** 워크플로우 이해 완료.
- **Action:** 알림 기능 처리 (OneSignal 푸시 알림 기능 비활성화, 추후 텔레그램 봇 전환 대비).
- **Result:** 알림 기능 처리 방안 결정.
- **Action:** Jinja2 사용 확인.
- **Result:** 최종 HTML 빌드에 Jinja2 사용 결정.
- **Note:** 이 작업은 현재 보류 상태입니다. 다음 단계는 `100xFenok-generator` 프로젝트의 전체적인 Python 스크립트 뼈대 작성입니다.

### [Project Plan] - 목표: 100xFenok-generator 개발 상세 계획 수립

- **Goal:** The TerminalX 로그인 -> 데이터 추출 -> 가공 -> `데일리랩.html` 파일 생성을 완전 자동화.
- **Location:** `C:\Users\eunta\gemini-workspace\projects\` 안에 `100xFenok-generator` 폴더.
- **Development Order:**
    1.  **로그인 및 데이터 추출:** `Selenium`을 사용하여 The TerminalX에 로그인하고, 10개의 산출물 HTML을 변수로 가져오는 스크립트 작성.
    2.  **데이터 가공 및 통합:** `BeautifulSoup`을 사용하여 HTML에서 데이터를 추출/가공하고, 2개의 핵심 JSON 객체로 통합하는 스크립트 작성.
    3.  **최종 HTML 빌드:** `Jinja2` 템플릿 엔진을 사용하여, 가공된 데이터를 `100x-daily-wrap-template.html`에 삽입하여 최종 결과물을 `../100xFenok/100x/daily-wrap/` 폴더에 저장하는 스크립트 작성.

### [Code Analysis] - `main_generator.py` 분석

- **Overall Purpose:** TerminalX에서 "100x Daily Wrap" 보고서를 자동 생성하고, 데이터를 처리하며, 최종 HTML 보고서를 빌드하는 전체 워크플로우를 자동화하는 스크립트. 관련 파일(`main.html`, `version.js`) 업데이트 기능 포함.

- **Key Classes and Methods:**
    - **`FenokReportGenerator` Class:**
        - **`__init__(self)`:** 경로 초기화, 자격 증명 로드, WebDriver 설정, 디렉토리 생성.
        - **`_load_credentials(self)`:** `secrets/my_sensitive_data.md`에서 TerminalX 사용자 이름/비밀번호 로드 (현재 간단한 파싱).
        - **`_setup_webdriver(self)`:** Selenium Chrome WebDriver 설정 (headless, no-sandbox 옵션 등).
        - **`_create_directories(self)`:** `generated_html`, `generated_json` 디렉토리 생성.
        - **`_login_terminalx(self)`:** TerminalX 로그인 자동화 (알림 팝업, 로그인 폼 입력, 성공 확인).
        - **`generate_report_html(...)`:** TerminalX 보고서 폼 입력, 파일 업로드, 프롬프트 입력, "Generate" 버튼 클릭, 생성된 보고서 HTML 추출 및 저장.
        - **`convert_html_to_json(self, html_file_path)`:** `Python_Lexi_Convert`를 사용하여 HTML을 JSON으로 변환 및 저장.
        - **`integrate_json_data(self, json_file_paths)`:** JSON 데이터 가공 및 통합 (현재 `Instruction_Json.md` 기반의 플레이스홀더).
        - **`_process_and_integrate_part_jsons(...)`:** 특정 PART의 JSON 파일 처리 및 통합 (현재 플레이스홀더).
        - **`build_final_html(...)`:** Jinja2를 사용하여 최종 HTML 빌드 (현재 템플릿 복사 플레이스홀더).
        - **`update_main_html_and_version_js(...)`:** `main.html` 링크 및 `version.js` 버전 업데이트 (현재 간단한 문자열 교체).
        - **`run_full_automation(self)`:** 전체 워크플로우 오케스트레이션.
        - **`close(self)`:** WebDriver 종료.

- **Dependencies (주석 처리 또는 언급):** `bs4` (BeautifulSoup), `jinja2`, `pyperclip`, `selenium.webdriver.common.action_chains.ActionChains`, `selenium.webdriver.common.keys.Keys`, `Python_Lexi_Convert`.

- **Missing/Placeholder Implementations (향후 개발 필요 사항):**
    - `secrets/my_sensitive_data.md`에서 자격 증명 파싱의 견고성 강화.
    - `integrate_json_data` 및 `_process_and_integrate_part_jsons`에 `Instruction_Json.md` 기반의 복잡한 JSON 처리 및 통합 로직 구현.
    - `build_final_html`에 Jinja2 템플릿 렌더링 로직 구현.
    - `main.html` 업데이트 로직을 BeautifulSoup 등으로 개선.
    - `generate_report_html` 내 날짜 계산 로직 구체화.
    - 필요한 외부 라이브러리(`pyperclip`, `bs4`, `jinja2`) 설치 및 관리.
