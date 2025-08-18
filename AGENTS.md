# Slim+Automation Guide

A single page reference for working in this multi?멲gent repo.

## Streamlined Workflow
1. **Start** ??`invoke start --fast` for status and context.
2. **Edit** ??modify files inside the repo only.
3. **Preview** ??`invoke review` or `git diff <file>`.
4. **Test** ??`pytest` to run checks.
5. **Commit** ??`invoke commit_safe` (hooks/diff confirm on).
6. **Report** ??optional `invoke hub.complete` to close a task.

## Default Settings
- Hooks enabled via `.agents/config.json`.
- Diff confirmation required before commits.
- UTF?? I/O; Windows?멹irst, Python called directly.
- Activity logged to `usage.db`.

## Manual Overrides
- Skip diff confirm: `SKIP_DIFF_CONFIRM=1` or `invoke commit_safe --skip-diff-confirm`.
- Disable hooks: `invoke git.set-hooks --off` (re?멷nable with `--on`).
- Emergency wrapper: toggle `.agents/emergency.json` `enabled` field.
- Agent switch: `invoke agent.set --name gemini|codex` or set `ACTIVE_AGENT` env var.
- Token/rate limits: use `codex --max-tokens <n>`; defaults apply if omitted.

Keep secrets (`.gemini/*`, `secrets/*`) out of commits and use UTF?? in all terminals.
