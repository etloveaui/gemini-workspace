Param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$CmdArgs
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Get-EnvOrDefault([string]$name, [object]$default) {
  if ($env:$name -ne $null -and $env:$name -ne '') { return $env:$name }
  return $default
}

# Settings
$maxRetries = [int](Get-EnvOrDefault 'CODEX_RETRY_MAX' 8)
$baseMs     = [int](Get-EnvOrDefault 'CODEX_BACKOFF_BASE_MS' 200)
$maxMs      = [int](Get-EnvOrDefault 'CODEX_BACKOFF_MAX_MS' 10000)
$minDelayMs = [int](Get-EnvOrDefault 'CODEX_EMERGENCY_MIN_DELAY_MS' 3500)
$rps        = Get-EnvOrDefault 'CODEX_RPS' ''
if ($rps -ne '') {
  try {
    $rpsVal = [double]$rps
    if ($rpsVal -gt 0) { $minDelayMs = [int][Math]::Ceiling(1000.0 / $rpsVal) }
  } catch {}
}
$injectMaxTokens = [int](Get-EnvOrDefault 'CODEX_MAX_TOKENS' 2500)

# Parse command and args (support `--` separator)
$sepIdx = [Array]::IndexOf($CmdArgs, '--')
if ($sepIdx -ge 0) {
  $exe  = $CmdArgs[$sepIdx + 1]
  $args = @()
  if ($sepIdx + 2 -lt $CmdArgs.Length) { $args = $CmdArgs[($sepIdx + 2)..($CmdArgs.Length - 1)] }
} else {
  if ($CmdArgs.Count -lt 1) { Write-Error 'Usage: codex_emergency.ps1 -- <command> <args...>'; exit 64 }
  $exe  = $CmdArgs[0]
  $args = @()
  if ($CmdArgs.Count -gt 1) { $args = $CmdArgs[1..($CmdArgs.Count - 1)] }
}

# Inject --max-tokens if missing
$hasMaxTokens = $false
foreach ($a in $args) { if ($a -match '^--max-tokens(=|$)') { $hasMaxTokens = $true; break } }
if (-not $hasMaxTokens) {
  $args = $args + @('--max-tokens', "$injectMaxTokens")
}

function New-BackoffMs([int]$attempt) {
  $pow = [Math]::Pow(2, [double]($attempt - 1))
  $ms  = [int][Math]::Min($baseMs * $pow, $maxMs)
  $jitter = Get-Random -Minimum 0 -Maximum 250
  return ($ms + $jitter)
}

function Acquire-DelayGate([int]$minMs) {
  try {
    $root = Resolve-Path (Join-Path $PSScriptRoot '..') | Select-Object -ExpandProperty Path
  } catch {
    $root = (Get-Location).Path
  }
  $agentsDir = Join-Path $root '.agents'
  $gateFile  = Join-Path $agentsDir '.emergency_gate'
  if (-not (Test-Path $agentsDir)) { New-Item -ItemType Directory -Force -Path $agentsDir | Out-Null }

  $now = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
  $last = $null

  for ($spin = 0; $spin -lt 40; $spin++) {
    try {
      $fs = [System.IO.File]::Open($gateFile, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
      try {
        $sr = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8, $true, 1024, $true)
        $content = $sr.ReadToEnd()
        $sr.Dispose()
        if ($content -match '^[0-9]+$') { $last = [int64]$content } else { $last = $null }
        $due = 0
        if ($last -ne $null -and $last -gt 0) {
          $elapsed = $now - $last
          if ($elapsed -lt $minMs) { $due = ($minMs - $elapsed) }
        }
        if ($due -gt 0) { Start-Sleep -Milliseconds $due }
        # update timestamp
        $fs.SetLength(0)
        $sw = New-Object System.IO.StreamWriter($fs, [System.Text.Encoding]::UTF8, 1024, $true)
        $sw.Write([string][DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
        $sw.Flush(); $sw.Dispose()
        break
      } finally { $fs.Dispose() }
    } catch { Start-Sleep -Milliseconds 50 }
  }
}

function Invoke-Once([string]$exe, [string[]]$args) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe
  # Quote args preserving spaces
  $quoted = @()
  foreach ($a in $args) {
    if ($a -match '^[A-Za-z0-9_\-\.:/\\=]+$') { $quoted += $a }
    else { $quoted += '"' + ($a -replace '"','\"') + '"' }
  }
  $psi.Arguments = [string]::Join(' ', $quoted)
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError  = $true
  $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
  $psi.StandardErrorEncoding  = [System.Text.Encoding]::UTF8
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  $null = $p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  return @{ code = $p.ExitCode; out = $stdout; err = $stderr }
}

function Should-Retry([int]$code, [string]$out, [string]$err) {
  if ($code -eq 0) { return $false }
  $txt = ($out + "`n" + $err)
  if ($txt -match '(?i)rate\s*limit|429|Please try again in|timeout|temporar(y|ily) unavailable|stream disconnected') { return $true }
  return $false
}

for ($attempt = 1; $attempt -le $maxRetries; $attempt++) {
  Acquire-DelayGate -minMs $minDelayMs
  Write-Host ("[EMERGENCY] Attempt {0}/{1} — {2} {3}" -f $attempt, $maxRetries, $exe, ([string]::Join(' ', $args)))
  $res = Invoke-Once -exe $exe -args $args
  if ($res.out) { Write-Output $res.out }
  if ($res.err) { Write-Error $res.err }
  if ($res.code -eq 0) { exit 0 }
  if (-not (Should-Retry -code $res.code -out $res.out -err $res.err)) { exit $res.code }
  if ($attempt -lt $maxRetries) {
    $sleepMs = New-BackoffMs -attempt ($attempt)
    Write-Warning ("[EMERGENCY] Retrying after {0} ms (code={1})" -f $sleepMs, $res.code)
    Start-Sleep -Milliseconds $sleepMs
  }
}

Write-Error "[EMERGENCY] All retries exhausted."
exit 75

