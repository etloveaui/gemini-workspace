Answer
The current automation selects a date by operating the calendar widget.
The relevant code is the _select_date_from_calendar helper and its use in
generate_report_html:

def _select_date_from_calendar(self, date_str, calendar_button_xpath):
    # ...
    calendar_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, calendar_button_xpath))
    )
    calendar_button.click()
    # move month until target date appears
    # ...
    target_day_element = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, date_xpath))
    )
    target_day_element.click()

And inside generate_report_html:

# 시작 날짜 캘린더 버튼 클릭
start_date_calendar_button_xpath = "//button[@data-slot='selector-button' and @aria-label='달력'][1]"
self._select_date_from_calendar(ref_date_start_str, start_date_calendar_button_xpath)

# 종료 날짜 캘린더 버튼 클릭
end_date_calendar_button_xpath = "//button[@data-slot='selector-button' and @aria-label='달력'][2]"
self._select_date_from_calendar(ref_date_end_str, end_date_calendar_button_xpath)

Because the calendar is dynamically rendered, these steps occasionally time out or fail.

1. Is typing into the editable fields recommended?
Typing directly into the underlying date fields is often more reliable than
script‑driving a complex calendar UI. If the date inputs are contenteditable
elements or editable <input> fields, filling them with send_keys bypasses
UI animation and month navigation logic.
When using this approach, verify that changing the visible fields updates any
hidden form inputs the page uses for submission. In many web apps, the hidden
value automatically syncs when the field loses focus (e.g., after pressing
TAB or firing a blur event), but it is worth checking.

2. Alternative approaches
JavaScript API
Some date pickers expose a JavaScript API. If you can identify the widget or
hidden input that stores the date, you can call JavaScript directly:

self.driver.execute_script(
    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
    hidden_input,
    "2025-07-22"
)
This avoids UI interaction entirely.

Simulated typing
If the date field is an <input type="date">, you can send a complete
string like "2025-07-22" without splitting month/day/year.

Custom waits
If you must continue using the calendar widget, add longer waits and
additional checks (e.g., wait for the calendar to be visible before
interacting), but this tends to be brittle.

3. Example implementation for direct typing
Below is an illustrative snippet that writes YYYY-MM-DD into three
contenteditable <div> elements representing month, day, and year:

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def _set_reference_date(self, date_str, container_selector):
    """Type a date directly into editable fields inside the given container."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    base = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
    )

    month_el = base.find_element(By.CSS_SELECTOR, "[data-slot='month'][contenteditable]")
    day_el   = base.find_element(By.CSS_SELECTOR, "[data-slot='day'][contenteditable]")
    year_el  = base.find_element(By.CSS_SELECTOR, "[data-slot='year'][contenteditable]")

    # helper to clear and type
    def fill(el, value):
        el.click()
        el.send_keys(Keys.CONTROL, 'a')  # select existing text
        el.send_keys(value)
        el.send_keys(Keys.TAB)           # trigger blur/change

    fill(month_el, date_obj.strftime("%m"))
    fill(day_el,   date_obj.strftime("%d"))
    fill(year_el,  date_obj.strftime("%Y"))
Usage inside generate_report_html would replace the calendar calls:

self._set_reference_date(ref_date_start_str, "div[data-testid='start-date']")
self._set_reference_date(ref_date_end_str, "div[data-testid='end-date']")
Selectors such as [data-testid='start-date'] are placeholders—you must adjust
them based on the actual DOM (e.g., unique IDs or other stable attributes).
After typing, confirm that the page shows the expected dates and that the form
submits correctly. If the page maintains hidden inputs for each date, check
their values with get_attribute("value") to verify the change.

Summary
The failure stems from manipulating the calendar widget (_select_date_from_calendar), which is fragile.

Directly editing the fields (contenteditable or <input>) is usually more dependable if the page supports it.

Alternatively, use JavaScript to set the hidden value.

Implement a helper like _set_reference_date to type month/day/year and trigger a blur or change event.

This approach simplifies the code and reduces the likelihood of timeouts when the calendar UI changes.