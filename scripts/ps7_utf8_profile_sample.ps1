# PowerShell 7 UTF-8/Rendering recommended tweaks (session-scoped)

# Encoding: ensure UTF-8 without BOM across pipeline and console
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

# Rendering: prefer Host rendering to avoid odd reflow/ANSI issues in some terminals
try { $PSStyle.OutputRendering = 'Host' } catch { }

# Python I/O encoding hint
$env:PYTHONIOENCODING = 'utf-8'

Write-Host "[ps7-utf8] Applied UTF-8 and rendering hints for this session." -ForegroundColor Green

