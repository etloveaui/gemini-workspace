<#
.SYNOPSIS
  Start on-demand terminal recording to project root.
.DESCRIPTION
  - Finds repo root via `git rev-parse --show-toplevel`; if not a git repo, uses current directory.
  - Writes logs to <root>\terminal_logs\session_YYYYMMDD_HHMMSS.txt
  - Safe to run multiple times; ignores if transcript already active.
#>
[CmdletBinding()]
param(
  [string]$FallbackRoot = (Get-Location).Path
)

function Get-ProjectRoot {
  try {
    $p = (git rev-parse --show-toplevel 2>$null).Trim()
    if ($p) { return $p }
  } catch {}
  return $FallbackRoot
}

$root = Get-ProjectRoot
 $logDir = Join-Path $root "terminal_logs"
 if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

 # Build date/terminal/agent-aware path
 $dateStr = Get-Date -Format "yyyy-MM-dd"
 $timeStr = Get-Date -Format "HHmmss"
 $agent = if ($env:ACTIVE_AGENT -and $env:ACTIVE_AGENT.Trim()) { $env:ACTIVE_AGENT.Trim().ToLower() } else { 'unknown' }
 $term = if ($env:WT_SESSION) { 'wt' } elseif ($env:VSCODE_PID) { 'vscode' } else { ($Host.Name -replace "[^a-zA-Z0-9]+", '').ToLower() }
 $procId = $PID

 $flat = ($env:AI_REC_FLAT -and $env:AI_REC_FLAT -ne '0')
 $destDir = if ($flat) { $logDir } else { Join-Path $logDir $dateStr }
 if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

 $baseName = "session_${timeStr}__agent-${agent}__term-${term}__pid-${procId}.txt"
 $file = Join-Path $destDir $baseName
 # Ensure uniqueness if started multiple times in the same second
 if (Test-Path $file) {
   $suffix = 1
   while (Test-Path $file) {
     $file = Join-Path $destDir ("session_${timeStr}__agent-${agent}__term-${term}__pid-${procId}__dup-${suffix}.txt")
     $suffix++
   }
 }

# UTF-8 sane defaults
try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch {}
try { $OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { $PSStyle.OutputRendering = 'Host' } catch {}

# Avoid duplicate Start-Transcript within the same session
if ($global:TRANSCRIPT_ACTIVE) {
  Write-Host "Transcript already active -> $env:POWERSHELL_TELEMETRY_OPTOUT" -ForegroundColor Yellow
  return
}

Start-Transcript -Path $file -Append | Out-Null
$global:TRANSCRIPT_ACTIVE = $true
Write-Host "Recording started -> $file" -ForegroundColor Green
