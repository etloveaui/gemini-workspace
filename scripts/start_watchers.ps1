Param(
  [Parameter(Mandatory=$true)][string]$PromptFile,
  [switch]$Hidden
)

$ErrorActionPreference = 'Stop'

if (-Not (Test-Path "venv")) { python -m venv venv }
& ./venv/Scripts/Activate.ps1

New-Item -ItemType Directory -Force -Path logs | Out-Null

$python = Join-Path (Resolve-Path ".\venv\Scripts").Path "python.exe"
$watchArgs = "scripts/watch_file.py --path communication --interval 1.0"
$promptArgs = "scripts/monitor_prompt.py --file `"$PromptFile`" --interval 0.5 --debounce 0.5"

$style = if ($Hidden) { 'Hidden' } else { 'Normal' }

$p1 = Start-Process -FilePath $python -ArgumentList $watchArgs -WindowStyle $style -PassThru -RedirectStandardOutput "logs/watch_comm.out" -RedirectStandardError "logs/watch_comm.err"
$p2 = Start-Process -FilePath $python -ArgumentList $promptArgs -WindowStyle $style -PassThru -RedirectStandardOutput "logs/prompt_monitor.out" -RedirectStandardError "logs/prompt_monitor.err"

"watch_comm PID=$($p1.Id)" | Out-File -FilePath logs/watchers.pid -Encoding utf8
"prompt_monitor PID=$($p2.Id)" | Out-File -FilePath logs/watchers.pid -Append -Encoding utf8

Write-Output "Started watchers. PIDs: $($p1.Id), $($p2.Id)"
Write-Output "Logs: logs/watch_comm.out, logs/prompt_monitor.out"

