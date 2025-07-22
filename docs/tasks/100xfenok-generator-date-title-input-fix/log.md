# [Problem Solving] - 100xFenok-generator: TerminalX 날짜 및 타이틀 입력 문제 해결

## 2025-07-22

### [Problem Description] - 목표: TerminalX 보고서 생성 시 날짜 및 타이틀 입력 문제 분석

- **Context:** `main_generator.py`에서 TerminalX 보고서 생성 시 "Report Title" 및 "Report Reference Date" 입력 필드 자동화에 어려움 발생. `Generate` 버튼이 활성화되지 않아 작업이 멈춘 상태.
- **Symptoms:**
    - **Report Title:** 값이 입력되었다가 바로 사라짐.
    - **Report Reference Date:** `07/ ...`와 같이 한 자리만 남거나 새로고침됨.
- **Root Cause Analysis (`idea.txt` 기반):**
    - **Report Title:** React 컨트롤드 컴포넌트의 특성상 `value` 주입만으로는 부족하며, `keydown` → `keyup` → `blur` 체인과 같은 실제 키 입력 시퀀스를 기대함.
    - **Report Reference Date:** 커스텀 `DateRangePicker` (start/end segment + hidden input) 사용. 세그먼트에 값을 넣어도 내부 reducer가 "미완성"으로 간주하여 리렌더링되거나, 타이핑 사이클이 없으면 덜 채운 것으로 판단함. 캘린더 다이얼로그를 통한 클릭 방식이 가장 안전함.

### [Proposed Solutions] - 목표: 문제 해결 전략 수립

- **Source:** `날짜입력.txt`, `idea.txt`

#### 1. Report Title 입력 전략
- **방법:** `send_keys()`를 사용하여 실제 키 입력 시퀀스를 흉내내고, `Keys.TAB`으로 `blur` 이벤트를 트리거하여 React 컴포넌트의 상태를 올바르게 업데이트.
- **예시 코드 (Python/Selenium):**
    ```python
    title = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="What\'s the title?"]')
    title.click()
    title.send_keys("20250722 100x Daily Wrap Part2")
    title.send_keys(Keys.TAB)
    ```

#### 2. Report Reference Date 입력 전략
- **방법 1 (권장): 캘린더 다이얼로그를 열어 날짜 셀 직접 클릭.**
    - **설명:** `button[aria-haspopup="dialog"]`를 클릭하여 캘린더 팝업을 띄운 후, `data-date` 속성을 가진 날짜 셀을 직접 클릭하여 선택. 이 방식이 내부 상태를 가장 안전하게 변경함.
- **방법 2 (대안): `contenteditable` 세그먼트 직접 입력.**
    - **설명:** `div[contenteditable="true"]`로 구성된 월/일/년 세그먼트에 `click()` 후 `send_keys()`로 값을 입력. 각 세그먼트 입력 후 `Keys.TAB`으로 `blur` 이벤트를 트리거.
    - **핵심:** `div[contenteditable="true"]` 6개에 순차적으로 `.click()` → `.send_keys()` 조합으로 날짜 세그먼트 입력. 일반 `<input>` 필드처럼 `.fill()`은 작동하지 않음.

#### 3. Generate 버튼 활성화 검증
- **방법:** `WebDriverWait`를 사용하여 `Generate` 버튼의 `disabled` 속성이 사라질 때까지 대기한 후 클릭.
- **예시 코드 (Python/Selenium):**
    ```python
    WebDriverWait(driver, 10).until(
        lambda d: not d.find_element(By.XPATH, "//button[contains(.,'Generate')]").get_attribute("disabled")
    )
    ```

### [Next Steps]
- `main_generator.py`의 `generate_report_html` 함수를 위 전략에 따라 수정.
