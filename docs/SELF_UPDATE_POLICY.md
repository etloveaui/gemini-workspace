Self-Update Policy (MVP)

- Windows-first, repo-internal only, UTF-8 I/O.
- Safety-first: proposals before applies; applies are opt-in and bounded.

Cadence
- Scan: manual or ad-hoc via `invoke auto.scan` (baseline MVP).
- Propose: `invoke auto.propose` generates `docs/proposals/auto_update_YYYYMMDD.md`.

Scope
- Packages: `pip list --outdated` surfaced packages relevant to workspace tooling.
- Code warnings: DeprecationWarning signals collected from `pytest -q`.
- Code policy: lightweight static checks (disallowed patterns), Windows-first rules.

Apply Policy (MVP)
- Manual apply by maintainer after reading the proposal file.
- Allowed without explicit review: patch/minor upgrades of non-critical dev-only deps.
- Requires review: major upgrades, runtime-critical deps, transitive breakage risk.

Safety & Dry-Run
- Always prefer dry-run or staged changes; commit in small, isolated patches.
- Use `invoke git.commit-safe -m "..."` for guarded commits (bypass pre-commit only when justified).

Commit/Message Guidelines
- Proposal: `chore(auto-update): add auto_update_<date> proposal`
- Apply: `chore(deps): bump <pkg> <from> -> <to>` with short rationale.

Ownership
- Primary: active agent (Codex), with Gemini as reviewer via inbox message or PR comment.
- Conflicts or uncertainty: leave a message to the other agent and wait for ack.

Out-of-Scope (MVP)
- Automated `pip install -U` execution inside repo automation.
- System-wide package managers or non-Python package updates.
