<#
.SYNOPSIS
  Resilient wrapper for Codex CLI with rate-limit/backoff handling.
.DESCRIPTION
  - Passes through args to Codex (or custom command via $env:CODEX_CMD)
  - Adds default "--max-tokens 3500" unless user explicitly provides one
  - Detects transient errors (rate limit / stream cut) and retries with backoff
  - Writes UTF-8 log to .logs/codex/codex_yyyyMMdd_HHmmss.log
#>
[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch {}
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { chcp 65001 > $null } catch {}

function New-LogFile {
  $dir = Join-Path (Get-Location) ".logs/codex"
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $name = 'codex_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log'
  return (Join-Path $dir $name)
}

function Write-Log([string]$Path, [string]$Message) {
  $ts = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffK')
  $line = "[$ts] $Message"
  Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
}

function ContainsMaxTokens([string[]]$a) {
  foreach ($x in $a) {
    if ($x -like '--max-tokens*' -or $x -like '-m*') { return $true }
  }
  return $false
}

function ParseRetryDelayMs([string]$s) {
  $m = [Regex]::Match($s, 'Please try again in\s+(\d+)ms', 'IgnoreCase')
  if ($m.Success) { return [int]$m.Groups[1].Value }
  return $null
}

$cmd = if ($env:CODEX_CMD -and $env:CODEX_CMD.Trim()) { $env:CODEX_CMD.Trim() } else { 'codex' }
$log = New-LogFile

# Build args with default max-tokens if not provided
$finalArgs = @()
$finalArgs += $Args
if (-not (ContainsMaxTokens $finalArgs)) {
  $finalArgs += @('--max-tokens','3500')
}

Write-Log $log "CMD: $cmd `"$($finalArgs -join ' ')`""

$maxRetries = 8
$baseDelay = 0.2  # seconds
$factor = 2.0
$maxDelay = 10.0  # seconds

$attempt = 0
$aggregateStdout = ''
$lastExit = 0

while ($true) {
  $attempt++
  Write-Log $log "Attempt #$attempt"

  $tmpOut = New-TemporaryFile
  $tmpErr = New-TemporaryFile
  try {
    $p = Start-Process -FilePath $cmd -ArgumentList $finalArgs -NoNewWindow -PassThru -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr
  } catch {
    Write-Log $log "FATAL: command not found or failed to start: $($_.Exception.Message)"
    throw
  }
  $p.WaitForExit()

  $stdout = Get-Content -Raw -Encoding UTF8 -ErrorAction SilentlyContinue $tmpOut
  $stderr = Get-Content -Raw -Encoding UTF8 -ErrorAction SilentlyContinue $tmpErr
  $code = $p.ExitCode
  Remove-Item -Force $tmpOut, $tmpErr -ErrorAction SilentlyContinue

  # Emit stdout immediately for user experience
  if ($stdout) { $aggregateStdout += $stdout; [Console]::Out.Write($stdout) }
  if ($stderr) { Write-Log $log ("STDERR: " + ($stderr -replace "`r?`n"," ")) }

  $lastExit = $code

  # Success path
  if ($code -eq 0) {
    Write-Log $log "SUCCESS: exit=0"
    exit 0
  }

  # Detect transient errors
  $err = ($stderr ?? '') + ' ' + ($stdout ?? '')
  $transient = $false
  if ($err -match 'Rate limit reached' -or $err -match 'stream disconnected before completion' -or $err -match '\b429\b' -or $err -match 'requests per min' -or $err -match 'tokens per min') {
    $transient = $true
  }

  if (-not $transient -or $attempt -ge $maxRetries) {
    Write-Log $log "FAIL: exit=$code transient=$transient attempts=$attempt"
    if ($attempt -ge $maxRetries) { Write-Log $log "RETRY_EXHAUSTED" }
    exit $code
  }

  # Compute delay (respect server-suggested if present)
  $suggest = ParseRetryDelayMs $err
  $delay = if ($suggest) { [Math]::Max($suggest/1000.0, $baseDelay) } else { [Math]::Min($baseDelay * [Math]::Pow($factor, $attempt-1), $maxDelay) }
  $jitter = (Get-Random -Minimum 0 -Maximum 250) / 1000.0
  $sleep = [Math]::Min($delay + $jitter, $maxDelay)

  # Inform user and log
  Write-Host "[RESUME] Retrying after $([int]([Math]::Round($sleep*1000)))ms due to transient error..." -ForegroundColor Yellow
  Write-Log $log "RETRY: sleep=${sleep}s reason=transient"

  Start-Sleep -Seconds $sleep
}

