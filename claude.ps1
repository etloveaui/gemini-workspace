param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsFromUser
)
$ErrorActionPreference = 'Stop'

# Prepare session env + UTF-8 profile for auto transcript
try {
  $root = (Resolve-Path '.').Path
  $env:ACTIVE_AGENT = 'claude'
  if (-not $env:AI_REC_AUTO) { $env:AI_REC_AUTO = '1' }
  . "$root\scripts\ps7_utf8_profile_sample.ps1"
} catch {}

$python = Join-Path (Resolve-Path .).Path 'venv\Scripts\python.exe'
if(-not (Test-Path $python)){
  Write-Host "[claude] venv/Scripts\python.exe not found. Using system python." -ForegroundColor Yellow
  $python = 'python'
}
& $python 'claude.py' @ArgsFromUser

