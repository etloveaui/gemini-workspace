param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsFromUser
)
$ErrorActionPreference = 'Stop'

# Prepare session env + UTF-8 profile for auto transcript
try {
  $root = (Resolve-Path '.').Path
  $env:ACTIVE_AGENT = 'codex'
  if (-not $env:AI_REC_AUTO) { $env:AI_REC_AUTO = '0' }
  . "$root\scripts\ps7_utf8_profile_sample.ps1"
} catch {}

# Pass-through to codex CLI (must be in PATH)
& codex @ArgsFromUser

