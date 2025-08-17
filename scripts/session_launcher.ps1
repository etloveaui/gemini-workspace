<#
.SYNOPSIS
  Launch or configure a workspace session with optional recording and agent label.
.DESCRIPTION
  - Sets ACTIVE_AGENT and AI_REC_AUTO=0
  - Moves to repo root and imports UTF-8 profile sample (ai-rec must be enabled separately)
  - Can optionally spawn a new PowerShell session (-Spawn)
#>
[CmdletBinding()]
param(
  [ValidateSet('codex','gemini','claude')]
  [string]$Agent = 'codex',
  [switch]$Spawn
)

function Get-WorkspaceRoot {
  try {
    $p = (git rev-parse --show-toplevel 2>$null).Trim()
    if ($p) { return $p }
  } catch {}
  return (Split-Path -Parent $PSCommandPath)
}

$root = Get-WorkspaceRoot
if (-not (Test-Path $root)) { throw "Workspace root not found." }

# Set environment and initialize
$env:ACTIVE_AGENT = $Agent
$env:AI_REC_AUTO = '0'
Set-Location $root

# Import UTF-8 + auto-rec profile block (idempotent)
. "$root\scripts\ps7_utf8_profile_sample.ps1"

Write-Host "Session prepared: ROOT=$root, AGENT=$Agent, AI_REC_AUTO=$($env:AI_REC_AUTO)" -ForegroundColor Green

if ($Spawn) {
  $cmd = "`$env:ACTIVE_AGENT='$Agent'; `$env:AI_REC_AUTO='0'; Set-Location '$root'; . .\scripts\ps7_utf8_profile_sample.ps1" 
  Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-NoLogo','-Command', $cmd) -WorkingDirectory $root | Out-Null
}

