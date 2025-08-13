param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsFromUser
)
$ErrorActionPreference = 'Stop'
$python = Join-Path (Resolve-Path .).Path 'venv\Scripts\python.exe'
if(-not (Test-Path $python)){
  Write-Host "[claude] venv/Scripts/python.exe not found. Using system python." -ForegroundColor Yellow
  $python = 'python'
}
& $python 'claude.py' @ArgsFromUser

