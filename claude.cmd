@echo off
REM Repo-local shim to launch global 'claude' with repo config and secrets
setlocal
set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tools\claude_ui.ps1" %*
endlocal

