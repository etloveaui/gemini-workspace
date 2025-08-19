# 100xFenok-generator Project Blueprint (Final)

## 1. Project Goal

The `100xFenok-generator` project is designed to automate the creation of the "100x Daily Wrap" report. This involves programmatically logging into the TerminalX website, navigating to the report generation page, triggering the report creation, waiting for completion, extracting the final HTML report, and publishing it.

## 2. Current Status & Key Issues

The project's primary blocker, a **redirect issue**, appears to be resolved. The script can now successfully navigate to the report generation form.

However, the project is now blocked by a new issue:
*   **Missing Tool:** The core conversion logic, which is supposed to be handled by a tool named `Python_Lexi_Convert`, cannot be found anywhere in the workspace. This prevents the implementation of the HTML to JSON conversion step.

## 3. Blueprint for Completion

This plan is adjusted based on the current situation.

### Phase 1: Resolve Missing Tool Dependency (High Priority)

**Objective:** Obtain or recreate the `Python_Lexi_Convert` tool.

*   **Step 1.1: Locate the tool.** If the tool exists in the workspace, its location needs to be identified.
*   **Step 1.2: Re-implement the tool.** If the tool is truly missing, its functionality will need to be re-implemented from scratch. The logs state that it converts HTML to JSON, and analyzing the `main_generator.py` script might provide more clues about its expected input and output.

### Phase 2: Complete Core Automation Logic (Currently Blocked)

**Objective:** Implement the placeholder functions in `main_generator.py`. This phase cannot proceed until Phase 1 is complete.

*   **Step 2.1: Implement `convert_html_to_json` (Blocked)**
    *   Once `Python_Lexi_Convert` is available, integrate it into this function.

*   **Step 2.2: Implement `integrate_json_data`**
    *   Read `docs/tasks/100xfenok-generator-data-cleanup/log.md` which mentions `Instruction_Json.md`. I will need to read `projects/100xFenok-generator/docs/Instruction_Json.md` to understand the integration logic.
    *   Implement the logic to process and merge the JSON files.

*   **Step 2.3: Implement `build_final_html`**
    *   Use the Jinja2 template (`100x-daily-wrap-template.html`) to render the final HTML with the `integrated_data`.

### Phase 3: Finalization and Integration

*   **Step 3.1: Refine Website Updates**
    *   Improve the `update_main_html_and_version_js` function using BeautifulSoup for more robust HTML parsing.

*   **Step 3.2: Integrate Telegram Notifications**
    *   Add a call to the `send_notification.py` script at the end of the automation workflow.

*   **Step 3.3: Documentation**
    *   Update the project's `README.md` with complete instructions.
