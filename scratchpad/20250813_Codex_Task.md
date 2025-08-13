You are my build engineer. Implement organization-wide hardening for rate limits and stream disconnects in this repo. Do not ask for confirmation. Make atomic commits per step with clear messages. Follow the plan and acceptance criteria.

# Objective
Systematically prevent stalls from "Rate limit reached / stream disconnected before completion" when using gpt-5 in Codex workflows.

# Scope
- Only this repo.
- Windows + PowerShell 7 environment primary.
- Do not modify unrelated files outside this workspace.

# Plan
1) Create a resilient CLI wrapper
   - File: tools/codex_safe.ps1
   - Behavior:
     - Accepts arbitrary Codex args and stdin.
     - Default output limit: --max-tokens 3500 unless user explicitly passes another.
     - Detect rate-limit errors by regex:
       - "Rate limit reached"
       - "stream disconnected before completion"
       - "429" or "requests per min" or "tokens per min"
     - Retry policy:
       - Exponential backoff with jitter: base=200ms, factor=2.0, maxDelay=10s, maxRetries=8.
       - If server returns "Please try again in Xms", wait at least Xms.
     - Resume logic:
       - If partial output captured before failure, append marker "\n[RESUME]\n" and continue.
     - Logging:
       - Log dir: .logs/codex (create if missing)
       - File: codex_yyyyMMdd_HHmmss.log (UTF-8, no BOM)
       - Log command line, retries, delays, stderr, and final exit code.
     - Exit with Codex exit code.

2) Add PowerShell helper functions
   - File: scripts/codex_helpers.ps1
   - Export:
     - Invoke-CodexSafe [string[]]$Args: calls tools/codex_safe.ps1 with passthrough.
     - Set default transcript toggle:
       - ENV guard: if $env:ACTIVE_AGENT -eq 'codex', ensure [Console]::OutputEncoding = UTF8, $OutputEncoding=UTF8, chcp 65001.
   - Provide import snippet for $PROFILE:
     - if (Test-Path "$PSScriptRoot/../scripts/codex_helpers.ps1") { . "$PSScriptRoot/../scripts/codex_helpers.ps1" }

3) Git pre-commit hook
   - Path: .githooks/pre-commit
   - Ensure .ps1, .md, .txt saved as UTF-8 (no BOM).
   - Enforce LF normalization for text files.
   - On nonzero hook exit, print actionable message.
   - Add `git config core.hooksPath .githooks` in docs.

4) Tasks integration
   - File: tasks.py (or scripts/tasks.py if exists)
   - Add targets:
     - codex:safe       -> run Codex via tools/codex_safe.ps1
     - codex:lint       -> quick dry-run that estimates tokens and warns if > 3,500 output tokens requested
     - codex:resume <logfile> -> re-run last failed command read from a given log with same args
   - Token estimator: simple heuristic from input size.

5) Documentation
   - Update AGENTS.md:
     - “Rate-limit hardening” section with how it works, usage, retry policy table.
     - Examples:
       - `pwsh -File tools/codex_safe.ps1 -- some codex args`
       - `invoke codex:safe -- args...`
   - Create docs/ops-codex-hardening.md with troubleshooting matrix.

6) Tests (lightweight)
   - Directory: tests/hardening/
   - Add a PowerShell test that simulates rate-limit stderr patterns and verifies retry loop and delays.
   - Add a unit test for log file creation.

# Acceptance Criteria
- Running `pwsh -File tools/codex_safe.ps1 --version` creates a UTF-8 log under .logs/codex and exits 0.
- When stderr contains "Rate limit reached ... Please try again in 87ms", wrapper waits ≥ 87ms and retries.
- After maxRetries exhausted, wrapper exits non-zero and writes the retry summary in the log.
- Passing `--max-tokens` explicitly disables the default 3500 cap.
- `invoke codex:safe -- --help` works and logs.
- AGENTS.md contains a clear “How to recover from mid-stream cut” subsection with `[RESUME]` marker explanation.
- Pre-commit hook converts .ps1/.md/.txt to UTF-8 and blocks commit on failure with a helpful message.
- No changes outside the repo root.

# Implementation Notes
- All PowerShell files must force UTF-8: [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); $OutputEncoding=[Text.Encoding]::UTF8; chcp 65001 > $null
- Use Start-Process or direct & invocation capturing stdout/stderr. Ensure exit codes propagate.
- Logs must include timestamped lines, attempt number, wait duration, and final outcome.

# Deliverables
- tools/codex_safe.ps1
- scripts/codex_helpers.ps1
- .githooks/pre-commit (+ configure instruction)
- tasks.py updates
- docs/ops-codex-hardening.md
- AGENTS.md patch
- tests/hardening/*

Begin now. Make minimal, focused commits per step with clear messages.
