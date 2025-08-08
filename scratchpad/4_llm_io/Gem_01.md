Of course. Let's fix the date input problem in your `main_generator.py` script.

Your proposed strategy to bypass the calendar UI and directly input the date using `send_keys` is indeed the most stable and recommended approach for this scenario. Automating complex JavaScript widgets like calendars is often brittle, and interacting with the final input fields is far more reliable.

Here is a detailed breakdown of the solution, including the necessary code changes.

### 1\. The Problem: Unreliable Calendar Automation

You've correctly identified the reasons for failure:

  * **Asynchronous UI Rendering:** The calendar widget doesn't appear in the DOM instantly, leading to `TimeoutException`.
  * **Unstable Selectors:** Relying on UI-specific attributes like `aria-label` in a specific language (`'XX일'`) is fragile and breaks easily with updates.
  * **High Complexity:** Navigating months and years in a loop is complex and prone to errors at any step.

### 2\. The Solution: Direct Input via `send_keys`

The best practice is to interact with the form elements as directly as possible. We will replace the entire `_select_date_from_calendar` function with a new, more robust method that inputs the date components (month, day, year) directly into their respective fields.

Here is the step-by-step implementation:

#### Step 1: Remove the Old Function

First, delete the entire `_select_date_from_calendar` function from your `main_generator.py` file. It's no longer needed.

#### Step 2: Add the New Direct Input Function

Add the following new function to your `FenokReportGenerator` class. This function is designed to robustly find and populate the date fields.

```python
    def _input_date_directly(self, date_str, date_picker_index):
        """
        캘린더 UI를 우회하여 날짜 입력 필드에 직접 값을 전송합니다.

        Args:
            date_str (str): 'YYYY-MM-DD' 형식의 날짜 문자열.
            date_picker_index (int): 시작일은 1, 종료일은 2.
        """
        print(f"날짜 직접 입력 시도: {date_str} (피커 인덱스: {date_picker_index})")
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month = date_obj.strftime("%m")
            day = date_obj.strftime("%d")
            year = date_obj.strftime("%Y")

            # 각 날짜 피커(시작일, 종료일)를 감싸는 컨테이너를 찾습니다.
            # 이 XPath는 페이지에 있는 두 개의 날짜 피커 그룹을 순서대로 식별합니다.
            base_xpath = f"(//p[text()='Report Reference Date']/following-sibling::div[1]//button[@aria-label='달력']/..)[{date_picker_index}]"

            # 위 컨테이너를 기준으로 월, 일, 년 입력 필드를 찾습니다.
            # 이 필드들은 contenteditable="true" 속성을 가진 div 태그입니다.
            month_div = self.driver.find_element(By.XPATH, f"{base_xpath}//div[@contenteditable='true'][1]")
            day_div = self.driver.find_element(By.XPATH, f"{base_xpath}//div[@contenteditable='true'][2]")
            year_div = self.driver.find_element(By.XPATH, f"{base_xpath}//div[@contenteditable='true'][3]")
            
            wait = WebDriverWait(self.driver, 10)
            actions = ActionChains(self.driver)

            # 기존 값을 안정적으로 지우고 새 값을 입력하는 함수
            def set_value(element, value):
                wait.until(EC.element_to_be_clickable(element))
                # ActionChains를 사용해 클릭, 전체 선택(Ctrl+A), 삭제 후 새 값 입력
                element.click()
                time.sleep(0.1) # 클릭 후 잠시 대기
                element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                element.send_keys(Keys.DELETE)
                time.sleep(0.1)
                element.send_keys(value)
                print(f"  - 값 '{value}' 입력 완료.")

            # 월, 일, 년 순서대로 값 입력
            set_value(month_div, month)
            set_value(day_div, day)
            set_value(year_div, year)

            # 마지막 필드 입력 후 Tab 키를 눌러 blur 이벤트를 발생시킵니다.
            # 이를 통해 웹페이지의 JavaScript가 값 변경을 인지하고 상태를 업데이트합니다.
            year_div.send_keys(Keys.TAB)
            print("  - Tab 키 입력으로 blur 이벤트 트리거 완료.")
            time.sleep(0.5) # 상태 업데이트를 위한 대기

        except (TimeoutException, NoSuchElementException) as e:
            print(f"오류: 날짜 입력 필드를 찾지 못했습니다 (날짜: {date_str}, 인덱스: {date_picker_index}).")
            self.driver.save_screenshot(f'error_datepicker_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            print("에러 스크린샷이 저장되었습니다. XPath 선택자를 확인해야 할 수 있습니다.")
            raise  # 자동화 중단을 위해 오류를 다시 발생시킴
        except Exception as e:
            print(f"날짜를 직접 입력하는 중 예기치 않은 오류 발생: {e}")
            raise
```

#### Step 3: Update the Calling Code

Now, modify the `generate_report_html` function to use this new helper function.

**Find this section in `generate_report_html`:**

```python
            # ... (코드 생략) ...
            
            # Report Reference Date 입력 (캘린더 다이얼로그 사용)
            # 시작 날짜 캘린더 버튼 클릭
            start_date_calendar_button_xpath = "//button[@data-slot='selector-button' and @aria-label='달력'][1]" # 첫 번째 달력 버튼
            self._select_date_from_calendar(ref_date_start_str, start_date_calendar_button_xpath) # 시작 날짜 선택

            # 종료 날짜 캘린더 버튼 클릭
            end_date_calendar_button_xpath = "//button[@data-slot='selector-button' and @aria-label='달력'][2]" # 두 번째 달력 버튼
            self._select_date_from_calendar(ref_date_end_str, end_date_calendar_button_xpath) # 종료 날짜 선택

            print("Report Reference Date 입력 완료.")
            time.sleep(0.5) # 짧은 대기
            
            # ... (코드 생략) ...
```

**And replace it with this:**

```python
            # ... (코드 생략) ...

            # Report Reference Date 입력 (직접 입력 방식)
            self._input_date_directly(ref_date_start_str, date_picker_index=1) # 시작일 입력
            self._input_date_directly(ref_date_end_str, date_picker_index=2)   # 종료일 입력
            
            print("Report Reference Date 입력 완료.")
            
            # ... (코드 생략) ...
```

-----

### 3\. Answering Your Other Questions

**1. Is this the best approach?**
Yes. For dynamic, JavaScript-heavy sites, directly manipulating the final form fields is overwhelmingly more reliable than simulating complex UI interactions. The code provided above is the standard, robust way to handle this.

**2. Are there other alternatives?**
The main alternative is using `driver.execute_script()`.

  * **When to use it:** You would use this if `send_keys` and `Keys.TAB` still fail to make the website recognize the new date. This can happen if the site relies on a specific JavaScript function (e.g., an API from a date-picker library like `moment.js` or `date-fns`) to update its internal state.
  * **How to use it:** You would first need to use your browser's developer tools to find out which JavaScript function is called when a date is selected. Then you could call it directly.
    ```python
    # 가상의 예시:
    # 'setReportDate'라는 함수가 있고, 날짜와 인덱스를 인자로 받는다고 가정
    js_script = f"window.setReportDate('{date_str}', {date_picker_index});"
    driver.execute_script(js_script)
    ```
  * **Conclusion:** This method is powerful but less portable, as it ties your script tightly to the website's internal JavaScript implementation, which can change without notice. **Stick with the `send_keys` approach first, as it is simpler and more than likely to work.**

By implementing these changes, your script's reliability will be significantly improved, and the timeout errors related to the date picker should be resolved.