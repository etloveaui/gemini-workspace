<#
.SYNOPSIS
  Stop on-demand terminal recording if active.
#>
[CmdletBinding()]
param()

try {
  Stop-Transcript | Out-Null
  $global:TRANSCRIPT_ACTIVE = $false
  Write-Host "Recording stopped." -ForegroundColor Green
} catch {
  Write-Host "No active recording." -ForegroundColor Yellow
}
