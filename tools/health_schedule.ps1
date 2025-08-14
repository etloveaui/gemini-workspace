<#
.SYNOPSIS
  Registers Windows Task Scheduler job to run health_check daily.
.NOTES
  This script only registers a task; requires Windows and appropriate privileges.
  It does not run automatically in this repo workflow unless invoked by user.
#>
Param(
  [string]$Root = (Resolve-Path '.').Path,
  [string]$Time = '03:30',
  [string]$TaskName = 'MultiAgent-HealthCheck',
  [switch]$Apply,
  [switch]$Remove
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

if ($Remove) {
  try { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop; Write-Host "Removed task: $TaskName" -ForegroundColor Yellow } catch { Write-Warning $_.Exception.Message }
  exit 0
}

$ps = (Get-Command pwsh -ErrorAction Stop).Source
$script = Join-Path $Root 'tools/health_check.ps1'
if (-not (Test-Path $script)) { throw "health_check.ps1 not found at $script" }

$action = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`" -Apply"
$trigger = New-ScheduledTaskTrigger -Daily -At ([DateTime]::Parse($Time))
$settings = New-ScheduledTaskSettingsSet -Compatibility Win8 -StartWhenAvailable

if ($Apply) {
  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily health_check -Apply for multi-agent workspace" -Force | Out-Null
  Write-Host "Registered task: $TaskName @ $Time daily" -ForegroundColor Green
} else {
  Write-Host "Preview registration:" -ForegroundColor Yellow
  Write-Host "  TaskName: $TaskName"
  Write-Host "  Time:     $Time"
  Write-Host "  Command:  $ps -NoProfile -ExecutionPolicy Bypass -File `"$script`" -Apply"
  Write-Host "Use -Apply to register, or -Remove to delete."
}

