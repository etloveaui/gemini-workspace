# =====================
# PowerShell 7 UTF-8 Profile Extras (recording & emergency wrapper)
# =====================

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
  if ($null -ne $auto -and $auto -ne '' -and $auto -ne '0' -and $env:ACTIVE_AGENT) {
    if (-not $global:TRANSCRIPT_ACTIVE) {
      $root = __Find-WorkspaceRoot
      $recStart = Join-Path $root 'ai-rec-start.ps1'
      if (Test-Path $recStart) {
        & $recStart -FallbackRoot $root
      }
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
