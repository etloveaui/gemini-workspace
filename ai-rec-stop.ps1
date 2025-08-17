<#
.SYNOPSIS
  Stop on-demand terminal recording if active.
#>
[CmdletBinding()]
param()

# Ensure stop is invoked only within a conversation CLI
if (-not $env:ACTIVE_AGENT -or -not $env:ACTIVE_AGENT.Trim()) {
  Write-Host "ACTIVE_AGENT not set; stop skipped." -ForegroundColor Yellow
  return
}

try {
  Stop-Transcript | Out-Null
  $global:TRANSCRIPT_ACTIVE = $false
  Write-Host "Recording stopped." -ForegroundColor Green
} catch {
  Write-Host "No active recording." -ForegroundColor Yellow
}
