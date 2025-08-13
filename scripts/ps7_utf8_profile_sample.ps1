# =====================
# PowerShell 7 UTF-8 Profile Sample (safe for Codex & Gemini)
# =====================

# 1) Console output encoding to UTF-8
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }

# 2) $OutputEncoding for external process pipes (PowerShell 7+)
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# 3) Rendering hint (PowerShell 7.2+). Ignore if not supported.
try { $PSStyle.OutputRendering = 'Host' } catch { }

# 4) Code page to 65001 for external legacy tools
try { chcp 65001 > $null } catch { }

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
  try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
  try { $PSStyle.OutputRendering = 'Host' } catch { }
}

# 10) OPTIONAL: Auto conversation recording (ai-rec-*.ps1)
# - Enable by setting $env:AI_REC_AUTO = '1' (default: off)
# - Disable explicitly with $env:AI_REC_AUTO = '0'
# - If enabled and ai-rec-start.ps1 exists in current directory or parent repo root, start transcript.
function __Find-WorkspaceRoot {
  try {
    $p = (git rev-parse --show-toplevel 2>$null).Trim()
    if ($p) { return $p }
  } catch {}
  return (Get-Location).Path
}

try {
  $auto = $env:AI_REC_AUTO
  if ($null -ne $auto -and $auto -ne '' -and $auto -ne '0') {
    $root = __Find-WorkspaceRoot
    $recStart = Join-Path $root 'ai-rec-start.ps1'
    if (Test-Path $recStart) {
      & $recStart -FallbackRoot $root
    }
  }
} catch { }
