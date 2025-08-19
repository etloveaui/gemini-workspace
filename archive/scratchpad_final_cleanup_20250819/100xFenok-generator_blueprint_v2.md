# 100xFenok-generator Project Blueprint (v2)

## 1. Project Goal

The `100xFenok-generator` project is designed to automate the creation of the "100x Daily Wrap" report. This involves programmatically logging into the TerminalX website, navigating to the report generation page, triggering the report creation, waiting for completion, extracting the final HTML report, and publishing it.

## 2. Current Status & Key Issues

The project is currently **blocked** by a critical **redirect issue**.

*   **The Problem:** After a successful login, the Selenium script attempts to navigate to the report creation form (`.../report/form/10`). However, the website immediately redirects the browser to the report archive page (`.../report/archive`). This prevents the script from accessing the form and starting the report generation.
*   **Suspected Cause:** As documented in the logs, this is likely due to the website's session management, a security policy, or a client-side JavaScript redirect that isn't being handled correctly by the current script.
*   **Previous Work:** An agent named "Claude" has already implemented significant debugging improvements in `main_generator.py`, including detailed logging, redirection tracking, and a `--debug` flag to isolate the issue.

## 3. Blueprint for Completion

This plan is based on the detailed logs and the current state of the `main_generator.py` script.

### Phase 1: Resolve the Redirect Blocker (High Priority)

**Objective:** Successfully navigate to the report creation form and remain on that page.

*   **Step 1.1: Utilize Existing Debug Mode**
    *   Run the script in debug mode to replicate the issue and analyze the detailed logs produced by Claude's additions:
        ```bash
        python projects/100xFenok-generator/main_generator.py --debug
        ```
    *   Analyze the console output, paying close attention to the "실제 도착한 URL" (Actual URL) log message to confirm the exact point of redirection.

*   **Step 1.2: Execute Advanced Debugging based on Logs**
    *   **Hypothesis A: Cookie/Session State Issue:** The redirect may be happening because the session is not fully established before the `driver.get()` call.
        *   **Test:** Insert a hard `time.sleep(5)` after the successful login confirmation but *before* the `driver.get(report_form_url)` call to ensure all session-related scripts on the page have finished executing.
    *   **Hypothesis B: Bypassing via UI Interaction:** The previous agent suggested clicking the "New Report" button from the archive page as a workaround. The code for this exists but may not be robust.
        *   **Test & Refine:** Enhance the selector for the "New Report" button to be more resilient. Use a more specific XPath that is language-independent, for example: `//a[contains(@href, 'report/form')]`. Also, add a `WebDriverWait` to ensure the button is clickable before interacting with it.
    *   **Hypothesis C: Direct URL Manipulation is Blocked:** The site might have a security measure preventing direct navigation to the form page.
        *   **Test:** Instead of `driver.get()`, try using JavaScript to change the location: `self.driver.execute_script("window.location.href = '{}'".format(report_form_url))`

### Phase 2: Complete Core Automation Logic

**Objective:** Implement the placeholder functions in `main_generator.py`.

*   **Step 2.1: Implement `convert_html_to_json`**
    *   The logs mention `Python_Lexi_Convert`. I need to find and analyze this tool to understand how to integrate it. I will search for `Python_Lexi_Convert` in the project.
    *   Based on the analysis, I will replace the placeholder in `convert_html_to_json` with the actual conversion logic.

*   **Step 2.2: Implement `integrate_json_data`**
    *   The logs mention `Instruction_Json.md` contains the instructions for this. I will read this file.
    *   Based on the instructions, I will implement the logic to process and merge the JSON files from Part1 and Part2.

*   **Step 2.3: Implement `build_final_html`**
    *   This requires using the Jinja2 template (`100x-daily-wrap-template.html`).
    *   I will implement the Jinja2 rendering logic to populate the template with the `integrated_data` and save the final HTML.

### Phase 3: Finalization and Integration

*   **Step 3.1: Refine Website Updates**
    *   Improve the `update_main_html_and_version_js` function. Instead of simple string replacement, use a more robust method like BeautifulSoup to parse and update the `main.html` file.

*   **Step 3.2: Integrate Telegram Notifications**
    *   The Telegram notification system is complete and documented in `docs/tasks/100xfenok-telegram-notification/log.md`.
    *   Add a call to the `send_notification.py` script at the end of the `run_full_automation` workflow.

*   **Step 3.3: Documentation**
    *   Update the project's `README.md` with complete instructions.
    *   Remove the temporary `DEBUG_GUIDE.md` if the main `README.md` is sufficient.
