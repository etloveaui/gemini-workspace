Param(
  [string[]]$ArgsPassthrough
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
try {
  Set-Location (Resolve-Path '.')
  $env:ACTIVE_AGENT = 'codex'
  $env:PYTHONIOENCODING = 'utf-8'

  if (-not $env:CODEX_RPS) { $env:CODEX_RPS = '0.3' }
  if (-not $env:CODEX_MAX_TOKENS) { $env:CODEX_MAX_TOKENS = '2500' }
  if (-not $env:CODEX_RETRY_MAX) { $env:CODEX_RETRY_MAX = '8' }
  if (-not $env:CODEX_BACKOFF_BASE_MS) { $env:CODEX_BACKOFF_BASE_MS = '200' }
  if (-not $env:CODEX_BACKOFF_MAX_MS) { $env:CODEX_BACKOFF_MAX_MS = '10000' }

  Write-Host "[Emergency Session] RPS=$($env:CODEX_RPS), MAX_TOKENS=$($env:CODEX_MAX_TOKENS)"
  if (-not (Test-Path 'tools/codex_emergency.ps1')) { throw 'tools/codex_emergency.ps1 not found' }

  pwsh -ExecutionPolicy Bypass -File 'tools/codex_emergency.ps1' -- codex @ArgsPassthrough
} finally {
  Pop-Location
}

