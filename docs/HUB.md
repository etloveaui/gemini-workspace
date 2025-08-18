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
- [CLAUDE-P0] System Integration & UTF-8 Encoding Fix (2025-08-18) - Claude 硫붿씤 泥댁젣 ?꾪솚 諛??몄퐫??臾몄젣 ?닿껐 [log](docs/tasks/claude-system-integration/action_plan.md)
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
- [Claude] Multi-Agent Workspace Integration (2025-08-17) - Claude Code ?꾩쟾 ?듯빀 諛??ㅼ젙 ?꾨즺
- [100xFenok] Telegram Notification Integration [log](docs/tasks/100xfenok-telegram-notification/log.md)
- [100xFenok] Floating Button Responsive Glitch Fix [log](docs/tasks/100xfenok-floating-button-responsive-glitch/log.md)
- [P2-UX] UX Refinement [log](docs/tasks/ux-refinement/log.md)
- [P1-2] File System Agent Framework Upgrade [log](docs/tasks/file-agent-framework-upgrade/log.md)
- [Agent | PR-DPAPI] Add Windows DPAPI utility for local secret encryption
- [Agent | PR-SERPER] Add Serper provider with safe fallback & docs
- [Agent | PR-CI] Add Windows CI with pytest + Gitleaks

- gemini-system-upgrade

- [P2-3] 筌ㅼ뮇伊??????野껋?肉?UX) 揶쏆뮇苑?- [P2-1] ?源낅뮟 獄???μ몛 筌ㅼ뮇???- [P1-3] 筌렺?怨뺛걟???紐꾨뻼 疫꿸퀡??餓Β??- [P1-2] ???뵬 ??뽯뮞???癒?뵠?袁る뱜 ?닌딇뀧

- ars-can-busoff-recovery-fix
- P0 ?臾믩씜 ?袁⑥┷ 獄???뽯뮞????됱젟??- P0 ?臾믩씜 ?袁⑥┷ (DeprecationWarning ??욧퍙, ???뮞???닌듼?揶쏆뮇苑? Help ??뽯뮞???닌딇뀧)
- [P1]UX_01_Doctor_Quickstart_Help: CLI UX ?關湲?(doctor, quickstart, help 疫꿸퀡???닌뗭겱) [log](docs/tasks/gemini-cli-ux-enhancement/log.md)
- [P1-0-GMD] GEMINI.md v2 ??껊젃??됱뵠??[log](docs/tasks/gemini-md-v2/log.md)
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

- **Current Status**: Active. P2-SU DoD 癰귣떯而?獄?HUB 筌롫뗀????낅쑓??꾨뱜 筌욊쑵六?餓?
- **Last Action**: P2-SU 嚥≪뮄???DoD(MVP) 筌ｋ똾寃뺟뵳?????곕떽?, Active ?諭???怨밴묶 雅뚯눘苑?揶쏄퉮??
- **Next Step**: 揶쏄쑬???귐됰윮 ??DoD 筌ｋ똾寃뺟뵳????筌띾뜄龜?? (?醫뤾문) 筌ㅼ뮇??CI ?硫명닋 ??釉?獄??怨몄뒠 ??ｍ????롫짗??곗쨮 ?醫?.- [P2-UX] UX Refinement
- Emergency wrapper toggle + health_check automation
- Hub split and SQLite VACUUM pipeline
