Param(
  [string]$RemoteUrl = "",
  [string]$RemoteName = "origin",
  [string]$Branch = "main",
  [string]$GitPath = "",
  [switch]$NoPush,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Avoid WSL interference
$env:WSLENV = ""
$env:WSL_INTEROP = ""
$env:MSYS2_ARG_CONV_EXCL = "*"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Force -Path logs | Out-Null
$LogFile = "logs/git_commit_${timestamp}.log"

function Write-Log([string]$msg) {
  $line = "[{0}] {1}" -f (Get-Date -Format o), $msg
  $line | Tee-Object -FilePath $LogFile -Append
}

function Resolve-GitPath {
  if ($GitPath -and (Test-Path $GitPath)) { return (Resolve-Path $GitPath).Path }
  $candidates = @(
    "C:\\Program Files\\Git\\cmd\\git.exe",
    "C:\\Program Files\\Git\\bin\\git.exe",
    "C:\\Program Files\\Git\\mingw64\\bin\\git.exe"
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  $where = (where.exe git 2>$null | Select-Object -First 1)
  if ($where) { return $where }
  return "git"  # fallback to PATH
}

$GitExe = Resolve-GitPath
Write-Log "Using git: $GitExe"

function RunGit([string[]]$args) {
  $cmdline = "$GitExe " + ($args -join ' ')
  Write-Log "> $cmdline"
  if ($DryRun) { return 0 }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $GitExe
  $psi.ArgumentList.Clear()
  foreach ($a in $args) { [void]$psi.ArgumentList.Add($a) }
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $p = [System.Diagnostics.Process]::Start($psi)
  $out = $p.StandardOutput.ReadToEnd()
  $err = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  if ($out) { Write-Log $out }
  if ($err) { Write-Log $err }
  if ($p.ExitCode -ne 0) { throw "git exited with $($p.ExitCode)" }
  return 0
}

function EnsureGitRepo {
  if (-not (Test-Path ".git")) {
    RunGit @('init')
  }
  try { RunGit @('config','user.name') } catch { RunGit @('config','user.name','Codex Agent') }
  try { RunGit @('config','user.email') } catch { RunGit @('config','user.email','codex@example.com') }
  # Ensure branch exists and checked out
  try { RunGit @('checkout','-B',$Branch) } catch { }
}

function CommitChunk1 {
  Write-Log "Staging commit 1: communication scaffold + prompt"
  $paths = @(
    "communication/shared/COMMUNICATION_GUIDE.md",
    "communication/codex/20250823_01_prompt.md",
    "communication/codex/20250823_01_setup.md"
  )
  $existing = $paths | Where-Object { Test-Path $_ }
  if ($existing.Count -eq 0) { Write-Log "[warn] nothing to add for commit 1"; return }
  RunGit @('add','--') + $existing
  RunGit @('commit','-m','chore(comm): scaffold communication guide and add prompt channel (20250823_01_prompt.md)')
}

function CommitChunk2 {
  Write-Log "Staging commit 2: today work (scripts/docs/utils/hand-off)"
  $paths = @(
    ".vscode/settings.json",
    "docs",
    "scripts",
    "utils",
    "communication/codex/20250823_02_codex_to_claude_handoff.md"
  )
  $existing = $paths | Where-Object { Test-Path $_ }
  if ($existing.Count -eq 0) { Write-Log "[warn] nothing to add for commit 2"; return }
  RunGit @('add','--') + $existing
  RunGit @('commit','-m','feat(runtime): watchers, prompt monitor, logging/trace utils, docs + smoke')
}

function PushIfConfigured {
  if ($NoPush) { Write-Log "Skipping push (NoPush)"; return }
  $remotes = ''
  try { $remotes = & $GitExe remote 2>$null } catch { $remotes = '' }
  if (-not $remotes) {
    if (-not $RemoteUrl) { Write-Log "[info] Remote not set. Provide -RemoteUrl to push."; return }
    RunGit @('remote','add',$RemoteName,$RemoteUrl)
  }
  RunGit @('push','-u',$RemoteName,$Branch)
}

EnsureGitRepo
CommitChunk1
CommitChunk2
PushIfConfigured

Write-Log "Done. Review with: git log --oneline --graph --decorate -n 5"
