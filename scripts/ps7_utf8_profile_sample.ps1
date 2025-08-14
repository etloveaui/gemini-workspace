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
  # Default AI_REC_AUTO=1 when an agent session is active and not explicitly disabled
  if ((-not $env:AI_REC_AUTO) -and ($env:ACTIVE_AGENT -in @('codex','gemini','claude'))) { $env:AI_REC_AUTO = '1' }
  $auto = $env:AI_REC_AUTO
  if ($null -ne $auto -and $auto -ne '' -and $auto -ne '0') {
    $root = __Find-WorkspaceRoot
    $recStart = Join-Path $root 'ai-rec-start.ps1'
    if (Test-Path $recStart) {
      & $recStart -FallbackRoot $root
    }
  }
} catch { }

# 11) OPTIONAL: Emergency wrapper toggle for Codex
try {
  $root = __Find-WorkspaceRoot
  $cfg  = Join-Path $root '.agents/emergency.json'
  if ((Test-Path $cfg) -and $env:ACTIVE_AGENT -eq 'codex') {
    $json = Get-Content -Raw -Encoding UTF8 $cfg | ConvertFrom-Json
    if ($json.enabled -eq $true) {
      Set-Item -Path Env:CODEX_RPS -Value ([string]$json.rps) -ErrorAction SilentlyContinue
      Set-Item -Path Env:CODEX_MAX_TOKENS -Value ([string]$json.max_tokens) -ErrorAction SilentlyContinue
      if ($json.retry) {
        if ($json.retry.max)     { Set-Item Env:CODEX_RETRY_MAX        ([string]$json.retry.max)     -ErrorAction SilentlyContinue }
        if ($json.retry.base_ms) { Set-Item Env:CODEX_BACKOFF_BASE_MS  ([string]$json.retry.base_ms) -ErrorAction SilentlyContinue }
        if ($json.retry.max_ms)  { Set-Item Env:CODEX_BACKOFF_MAX_MS   ([string]$json.retry.max_ms)  -ErrorAction SilentlyContinue }
      }
      if (Test-Path (Join-Path $root 'tools/codex_emergency.ps1')) {
        function codex { pwsh -ExecutionPolicy Bypass -File (Join-Path $root 'tools/codex_emergency.ps1') -- 'codex' @args }
        Set-Alias cx codex -ErrorAction SilentlyContinue
        Write-Host "[profile] Codex emergency wrapper enabled (cx/codex wrapped)" -ForegroundColor Yellow
      }
    }
  }
} catch { }
