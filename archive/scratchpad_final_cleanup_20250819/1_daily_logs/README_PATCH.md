# P0 Patch Bundle

Files included:

- tasks.py  – fixes start/end flow, logging, no emoji issues, correct __lastSession__ handling.
- scripts/hub_manager.py – robust regex remover for __lastSession__ block.
- pytest.ini – restricts discovery to tests/ to avoid scratchpad noise.

How to apply:
1. Backup your originals.
2. Copy `tasks.py` to project root.
3. Copy `scripts/hub_manager.py` to scripts/.
4. Drop `pytest.ini` into project root.
5. Run: `invoke test` or `pytest tests/ -v`

If tests still fail, verify:
- HUB.md doesn't contain stray control chars.
- PowerShell is available for git-wip.ps1.
