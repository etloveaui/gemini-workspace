# Workspace HUB

\*Last Updated: 2025-08-18

## Rollback Steps

1. Set `AGENTS_SKIP_HOOKS=1` to bypass malfunctioning automation hooks.
2. Alternatively edit `.agents/config.json` and set `"hooks": {"enabled": false}`.
3. After the issue is resolved, remove the env var or re-enable hooks in the config.
4. To undo a bad commit, run `git reset --hard HEAD~1`.

## Projects

## Project Blueprints

- **[P0] Foundational Enhancements:** `scratchpad/Gemini-Self-Upgrade/Plan/[P0]Plan_Gemini.md`, `scratchpad/Gemini-Self-Upgrade/Plan/[P0]Plan_O3.md`
- **[P1] Core Feature Expansion:** `scratchpad/Gemini-Self-Upgrade/Plan/[P1]Plan_O3.md`, `scratchpad/Gemini-Self-Upgrade/Plan/[P1_P2]Plan_Gemini.md`
- **[P2] System Optimization & UX Refinement:** `scratchpad/Gemini-Self-Upgrade/Plan/[P2]Plan_O3.md`, `scratchpad/Gemini-Self-Upgrade/[P1-2] ORDER BLOCK C_S_Gemini.md`, `scratchpad/Gemini-Self-Upgrade/[P1-2] ORDER BLOCK C_S_O3.md`

## Active Tasks
- [CODEX-P0] System Cleanup & Stabilization (2025-08-18) - 시스템 정리 및 안정화 최우선 작업 [instructions](docs/tasks/system_cleanup_instructions_for_codex.md)
- [CLAUDE-P0] System Integration & UTF-8 Encoding Fix (2025-08-18) - Claude 硫붿씤 泥댁젣 꾪솚 諛몄퐫몄젣 닿껐 [log](docs/tasks/claude-system-integration/action_plan.md)
- [P-AGENT] Repeated Modification Failures (for GEMINI)
- [Test] Fix 15 failing pytest tests
- [CLAUDE] 100xfenok-generator-date-title-input-fix (2025-08-18) - TerminalX 리다이렉션 문제 해결 중 [log](docs/tasks/100xfenok-generator-date-title-input-fix/log.md)

## Staging Tasks
- Claude CLI: direct PowerShell entry + Groq routing
- Always-on terminal transcript for agent sessions
- Claude Integration Complete

## Planned Tasks

## Paused Tasks

- vscode-integration-problem

## Completed Tasks
- [Claude] Multi-Agent Workspace Integration (2025-08-17) - Claude Code 완전 통합 및 설정 완료
- [100xFenok] Telegram Notification Integration [log](docs/tasks/100xfenok-telegram-notification/log.md)
- [100xFenok] Floating Button Responsive Glitch Fix [log](docs/tasks/100xfenok-floating-button-responsive-glitch/log.md)
- [P2-UX] UX Refinement [log](docs/tasks/ux-refinement/log.md)
- [P1-2] File System Agent Framework Upgrade [log](docs/tasks/file-agent-framework-upgrade/log.md)
- [Agent | PR-DPAPI] Add Windows DPAPI utility for local secret encryption
- [Agent | PR-SERPER] Add Serper provider with safe fallback & docs
- [Agent | PR-CI] Add Windows CI with pytest + Gitleaks

- gemini-system-upgrade

- [P2-3] 껋  [P2-1] 낅뮟 몛  [P1-3] 筌렺뺛걟꾨뻼 疫꿸퀡 [P1-2] 뵬 뽯뮞뵠뱜 닌딇뀧

- ars-can-busoff-recovery-fix
- P0 믩씜  뽯뮞됱젟 P0 믩씜  (DeprecationWarning 욧퍙, 뮞닌듼 Help 뽯뮞닌딇뀧)
- [P1]UX_01_Doctor_Quickstart_Help: CLI UX  quickstart, help 疫꿸퀡닌뗭겱) [log](docs/tasks/gemini-cli-ux-enhancement/log.md)
- [P1-0-GMD] GEMINI.md v2 껊젃됱뵠
- [P1-1] Web Agent Integration [log](docs/tasks/web-agent-integration/log.md)
- gemini-cli-setup
- gemini-self-upgrade
- secret-management-setup
- system-docs-revamp
- terminalx-ui-analysis
- venv-cleanup-and-rebuild
- workspace-setup
- test-task-1
- [P-CORE] HUB.md Auto-Commit Reliability [log](docs/tasks/core-hub-auto-commit-reliability/log.md)
- [P-CORE] eplace` Tool Reliability Enhancement [log](docs/tasks/core-replace-tool-reliability/log.md)
- [P2-UX] Fix `invoke start` Table Corruption [log](docs/tasks/ux-fix-invoke-start-corruption/log.md)

- [P-CH] Pre-commit Hook Troubleshooting [log](docs/tasks/pre-commit-hook-troubleshooting/log.md)
- [P-CH-ALT] Remove pre-commit hook if troubleshooting fails [log](docs/tasks/pre-commit-hook-alternative/log.md)
- [P-AGENT] OS Command Consistency [log](docs/tasks/agent-os-command-consistency/log.md)
- [Codex] PowerShell UX Fix [log](docs/tasks/codex-powershell-ux-fix/log.md)
- 100xfenok-generator-data-cleanup [log](docs/tasks/100xfenok-generator-data-cleanup/log.md)
- 100xfenok-generator-dev [log](docs/tasks/100xfenok-generator-dev/log.md)

- [P2-SU] Self-Update Engine (MVP) [log](docs/tasks/self-update-engine/log.md)
- [Codex] Terminal Output Width & Scrollback Wrap Fix (MVP) [log](docs/tasks/codex-terminal-output-wrap/log.md)

__lastSession__

- **Current Status**: Active. P2-SU DoD 癰귣떯而 筌롫뗀낅쑓꾨뱜 筌욊쑵六
- **Last Action**: P2-SU 嚥≪뮄 筌ｋ똾寃뺟뵳곕떽 Active 밴묶 雅뚯눘苑쏄퉮
- **Next Step**: 揶쏄쑬귐됰윮  筌ｋ똾寃뺟뵳띾뜄龜 (뤾문)  명닋 몄뒠 롫짗곗쨮  [P2-UX] UX Refinement
- Emergency wrapper toggle + health_check automation
- Hub split and SQLite VACUUM pipeline
