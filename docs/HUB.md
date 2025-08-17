# Workspace HUB

\*Last Updated: 2025-08-17

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
- [P-AGENT] Repeated Modification Failures (for GEMINI)

## Staging Tasks
- Claude CLI: direct PowerShell entry + Groq routing
- Always-on terminal transcript for agent sessions

## Planned Tasks
- [Test] Fix 15 failing pytest tests

## Paused Tasks

- 100xfenok-generator-date-title-input-fix
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

- [P2-3] 理쒖쥌 ?ъ슜??寃쏀뿕(UX) 媛쒖꽑
- [P2-1] ?깅뒫 諛??⑥쑉 理쒖쟻??- [P1-3] 硫?곕え???몄떇 湲곕뒫 以鍮?- [P1-2] ?뚯씪 ?쒖뒪???먯씠?꾪듃 援ъ텞

- ars-can-busoff-recovery-fix
- P0 ?묒뾽 ?꾨즺 諛??쒖뒪???덉젙??- P0 ?묒뾽 ?꾨즺 (DeprecationWarning ?닿껐, ?뚯뒪??援ъ“ 媛쒖꽑, Help ?쒖뒪??援ъ텞)
- [P1]UX_01_Doctor_Quickstart_Help: CLI UX ?μ긽 (doctor, quickstart, help 湲곕뒫 援ы쁽) [log](docs/tasks/gemini-cli-ux-enhancement/log.md)
- [P1-0-GMD] GEMINI.md v2 ?낃렇?덉씠??[log](docs/tasks/gemini-md-v2/log.md)
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

- **Current Status**: Active. P2-SU DoD 蹂닿컯 諛?HUB 硫붾え ?낅뜲?댄듃 吏꾪뻾 以?
- **Last Action**: P2-SU 濡쒓렇??DoD(MVP) 泥댄겕由ъ뒪??異붽?, Active ?뱀뀡 ?곹깭 二쇱꽍 媛깆떊.
- **Next Step**: 媛꾨떒 由щ럭 ??DoD 泥댄겕由ъ뒪??留덈Т由? (?좏깮) 理쒖냼 CI ?멸툒 ?ы븿 諛??곸슜 ?④퀎???섎룞?쇰줈 ?좎?.- [P2-UX] UX Refinement
- Emergency wrapper toggle + health_check automation
- Hub split and SQLite VACUUM pipeline