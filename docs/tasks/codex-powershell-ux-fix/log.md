# Task: Codex PowerShell UX Fix

## Problem Description
Codex's interaction with PowerShell exhibits two main user experience issues:
1.  **Scrollback Issue**: Output content disappears from the terminal scrollback buffer, making it difficult to review past interactions.
2.  **Text Wrapping/Line Break Issue**: Text appears to wrap prematurely or with inconsistent line breaks, making output hard to read.

## Web Search Findings (from 2025-08-12)

### PowerShell Scrollback Limit
*   The Windows console has a hard limit of 9999 lines for its scrollback buffer. True "unlimited" scrollback is not possible within the standard console.
*   **Potential Solutions/Workarounds**:
    *   Increasing the screen buffer size (height) in the PowerShell console's properties (Layout tab) can store more lines. This is a manual user action.
    *   `Start-Transcript` can capture all session input/output to a log file, preventing data loss due to buffer limits. This is a programmatic solution for capturing full output.

### Text Wrapping and Line Break Behavior
*   Output truncation and premature wrapping can occur due to console width or default PowerShell formatting rules.
*   **Potential Solutions/Workarounds**:
    *   **Console Width**: Ensure the PowerShell console window is wide enough.
    *   `$FormatEnumerationLimit = -1`: Prevents truncation of collection items.
    *   **Formatting Cmdlets**:
        *   `Format-Table -AutoSize -Wrap`: For table output, adjusts column widths and wraps text.
        *   `Format-List -Force`: Displays each property on a new line, useful for wide outputs.
        *   `Out-String -Width <N>`: Controls line length when piping output, preventing truncation.
    *   **Explicit Newlines**: Use `` `n `` or `[System.Environment]::NewLine` for controlled line breaks in strings.

## Review of `scratchpad/터미널 환경 변경.md`
The file `scratchpad/터미널 환경 변경.md` was reviewed. It contains environment variable settings for various VS Code extensions (GitHub Copilot Chat, Anthropic Claude Code, debugpy, git). However, it does **not** contain any direct settings or configurations related to PowerShell console scrollback, text wrapping, or general terminal display properties that would address the reported issues. The issues are likely related to PowerShell's own behavior or how Codex formats its output.

## Proposed Plan to Address Issues

### Phase 1: Investigation and Initial Configuration (Gemini/Codex)
1.  **Assess Current Output Formatting**: Analyze how Codex currently generates its PowerShell output. Determine if it's using specific formatting cmdlets or if it's raw string output.
2.  **Test `Out-String -Width`**: Experiment with piping Codex's output through `Out-String -Width` to control line length and prevent premature wrapping.
3.  **Check PowerShell Profile**: Investigate if there are any existing PowerShell profile scripts (`$PROFILE`) that might be affecting output behavior.
4.  **Recommend Console Settings (User Action)**: Advise the user on how to manually increase the PowerShell console's screen buffer height to mitigate scrollback issues.

### Phase 2: Advanced Solutions (Gemini/Codex)
1.  **Implement `Start-Transcript` (if necessary)**: If scrollback remains a significant issue for debugging/analysis, implement a mechanism to automatically start and manage transcripts for Codex sessions, saving full output to a log file.
2.  **Dynamic Output Formatting**: If Codex's output is not consistently formatted, explore ways to dynamically apply formatting cmdlets (`Format-Table`, `Format-List`) based on the type of output.
3.  **Consider Terminal Emulator**: If issues persist, investigate if using a different terminal emulator within VS Code (e.g., Windows Terminal) offers better control over scrollback and rendering.

### Phase 3: User Feedback and Iteration
1.  **Gather User Feedback**: After implementing changes, collect feedback from the user on the effectiveness of the solutions.
2.  **Iterate and Refine**: Based on feedback, refine the implemented solutions or explore alternative approaches.

## Roles and Responsibilities
*   **Gemini**: Lead investigation, implement programmatic solutions, document findings and progress.
*   **Codex**: (If applicable) Assist in testing and validating changes within its own environment.
*   **User**: Provide feedback, perform manual console configuration changes, and provide system context.

---

## 2025-08-12 Update (Completed: Minimal Fix)
- Enforce UTF-8 in Python subprocesses to improve PS7 output stability: set `PYTHONUTF8=1` in `scripts/runner.py`.
- Verified UTF-8 for help/doctor scripts via `sys.stdout.reconfigure(encoding='utf-8')`.
- Recommendation retained: use `Start-Transcript` for long sessions; increase VS Code terminal scrollback.

Outcome: Noticeably improved Korean output rendering and reduced garbled text in PowerShell. Further tuning (table format, Out-String width) kept as optional.
