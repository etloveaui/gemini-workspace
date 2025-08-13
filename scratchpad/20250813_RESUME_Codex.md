# Codex Resume Note — 2025-08-13

- When: 2025-08-13T00:00:00Z (local workday end snapshot)
- Agent: codex

What was in progress
- Auto recording: enabled via scripts/ps7_utf8_profile_sample.ps1 + ai-rec-*.ps1. Launchers added: codex-session.ps1, gemini-session.ps1.
- Rate-limit hardening (Step 1): tools/codex_safe.ps1 added with retry/backoff/jitter + `.logs/codex` logging; AGENTS.md minimal usage added.
- PowerShell UX (UTF-8) improvements: previous commits referenced as chore_ux_utf8_hub_merge, ensuring PYTHONUTF8=1 and UTF-8 output.
- HUB review: tasks status summarized; noted encoding issues when reading agents_hub JSON via PowerShell default codepage.
- P2-SU (Self-Update Engine): DoD strengthening in progress; needs short final pass and log update.

Where to resume (next 30–45 min)
1) Verify wrapper with real Codex CLI
   - Run: `pwsh -ExecutionPolicy Bypass -File tools/codex_safe.ps1 -- <your-codex-args>`
   - Expect: `.logs/codex/codex_*.log` created; on 429/TPM or stream cut shows `[RESUME]` + retries.
2) Optional Invoke tasks (if needed now)
   - Add: `invoke codex.safe -- --help` and `invoke codex.resume <log>` wiring in tasks.py.
3) HUB note
   - Send: hub note that Step 1 wrapper landed; tests/docs follow later.
4) agents_hub encoding read
   - Use: `Get-Content -Raw -Encoding UTF8` or Python to read JSON to avoid CP949 mojibake.
5) P2-SU DoD finalization
   - Update: docs/tasks/self-update-engine/log.md with DoD checklist closure; run `invoke end` to write HUB session block.

Refs
- Terminal notes: scratchpad/claude_code/진행중터미널.md
- Wrapper: tools/codex_safe.ps1
- Launchers: codex-session.ps1, gemini-session.ps1
- Profile: scripts/ps7_utf8_profile_sample.ps1
- Doc add: AGENTS.md (Rate-limit Hardening)

