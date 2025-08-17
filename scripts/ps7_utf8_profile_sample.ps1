# =====================
# PowerShell 7 UTF-8 Profile Sample (safe for Codex & Gemini)
# =====================

# 1) Console I/O encoding to UTF-8 (no BOM)
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }
try { [Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false) } catch { }

# 2) $OutputEncoding for external process pipes (PowerShell 7+)
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# 2b) Default file encodings for common cmdlets
try {
  $PSDefaultParameterValues['Out-File:Encoding']   = 'utf8'
  $PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
  $PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
} catch { }

# 3) Rendering hint (PowerShell 7.2+). Ignore if not supported.
try { $PSStyle.OutputRendering = 'Host' } catch { }

# 4) Code page to 65001 for external legacy tools
try { chcp 65001 > $null } catch { }

# 4b) Python I/O encoding (explicit)
try {
  $env:PYTHONIOENCODING = 'utf-8'
  $env:PYTHONUTF8 = '1'
} catch { }

# 5) OPTIONAL: Add Copilot Chat debugCommand to PATH if present
$copilotPath = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat\debugCommand"
if (Test-Path $copilotPath) { $env:Path = "$env:Path;$copilotPath" }

# 6) OPTIONAL: Claude Code integration toggles
$env:CLAUDE_CODE_SSE_PORT = "16052"
$env:ENABLE_IDE_INTEGRATION = "true"

# 7) OPTIONAL: vscode debugpy dynamic wiring
$extRoot = "$env:USERPROFILE\.vscode\extensions"
if (Test-Path $extRoot) {
  $dbg = Get-ChildItem $extRoot -Directory -Filter "ms-python.debugpy-*" |
         Sort-Object Name -Descending | Select-Object -First 1
  if ($dbg) {
    $ncs = Join-Path $dbg.FullName "bundled\scripts\noConfigScripts"
    $lib = Join-Path $dbg.FullName "bundled\libs\debugpy"
    if (Test-Path $ncs) { $env:Path = "$env:Path;$ncs" }
    if (Test-Path $lib) { $env:BUNDLED_DEBUGPY_PATH = $lib }
    $env:PYDEVD_DISABLE_FILE_VALIDATION = "1"
  }
}

# 8) Aliases
Set-Alias cx codex -ErrorAction SilentlyContinue

# 9) Codex-only guard block. Runs only when Codex sets ACTIVE_AGENT.
if ($env:ACTIVE_AGENT -eq 'codex') {
  try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }
  try { [Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false) } catch { }
  try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
  try { $PSStyle.OutputRendering = 'Host' } catch { }
  try { $env:PYTHONIOENCODING = 'utf-8'; $env:PYTHONUTF8 = '1' } catch { }
}
