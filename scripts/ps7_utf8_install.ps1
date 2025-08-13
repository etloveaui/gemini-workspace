<#
.SYNOPSIS
  Install UTF-8/Rendering profile block safely to current user's PowerShell 7 profile.

.DESCRIPTION
  - Backs up existing profile to *.bak-YYYYMMDD-HHMMSS.ps1
  - Appends or updates a named block only once
  - Safe for both Gemini CLI and Codex CLI
#>

[CmdletBinding()]
param(
  [string]$BlockName = 'utf8-safe-block',
  [string]$ProfilePath = $PROFILE # Current user, current host
)

$ErrorActionPreference = 'Stop'

# Ensure profile directory exists
$dir = Split-Path -Parent $ProfilePath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }

# Read current content if any
$existing = ''
if (Test-Path $ProfilePath) { $existing = Get-Content -LiteralPath $ProfilePath -Raw -ErrorAction SilentlyContinue }

# Define the block content
$block = @"
# BEGIN $BlockName
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(\$false) } catch { }
try { \$OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
try { \$PSStyle.OutputRendering = 'Host' } catch { }
try { chcp 65001 > \$null } catch { }
# Codex-only guard
if (\$env:ACTIVE_AGENT -eq 'codex') {
  try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(\$false) } catch { }
  try { \$OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
  try { \$PSStyle.OutputRendering = 'Host' } catch { }
}
# END $BlockName
"@

# If block already exists, replace it. Else append.
$pattern = "(?s)# BEGIN $BlockName.*?# END $BlockName"
$timestamp = (Get-Date).ToString('yyyyMMdd-HHmmss')

if ($existing -match $pattern) {
  Write-Host "Existing block found. Updating..." -ForegroundColor Yellow
  $updated = [System.Text.RegularExpressions.Regex]::Replace($existing, $pattern, [System.Text.RegularExpressions.Regex]::Escape($block))
  # backup
  $bak = "$ProfilePath.bak-$timestamp.ps1"
  Set-Content -LiteralPath $bak -Value $existing -Encoding UTF8
  Set-Content -LiteralPath $ProfilePath -Value $updated -Encoding UTF8
} else {
  Write-Host "No existing block. Appending..." -ForegroundColor Yellow
  if ($existing) {
    $newContent = $existing.TrimEnd() + "`r`n`r`n" + $block
  } else {
    $newContent = $block
  }
  # backup
  $bak = "$ProfilePath.bak-$timestamp.ps1"
  if ($existing) { Set-Content -LiteralPath $bak -Value $existing -Encoding UTF8 }
  Set-Content -LiteralPath $ProfilePath -Value $newContent -Encoding UTF8
}

Write-Host "Done. Profile updated: $ProfilePath" -ForegroundColor Green
Write-Host "Backup: $bak" -ForegroundColor Green
