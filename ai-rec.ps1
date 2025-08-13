<#
.SYNOPSIS
  Toggle on-demand terminal recording.
#>
[CmdletBinding()]
param(
  [string]$FallbackRoot = (Get-Location).Path
)

if ($global:TRANSCRIPT_ACTIVE) {
  & $PSCommandPath.Replace("ai-rec.ps1","ai-rec-stop.ps1")
} else {
  & $PSCommandPath.Replace("ai-rec.ps1","ai-rec-start.ps1") -FallbackRoot $FallbackRoot
}
