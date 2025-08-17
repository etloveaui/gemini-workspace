param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsFromUser,
  [switch]$Extras
)
$ErrorActionPreference = 'Stop'

try {
  $root = (Resolve-Path '.').Path
  $env:ACTIVE_AGENT = 'gemini'
  if (-not $env:AI_REC_AUTO) { $env:AI_REC_AUTO = '0' }
  . "$root\scripts\ps7_utf8_profile_sample.ps1"
  if ($Extras) { . "$root\scripts\ps7_utf8_profile_extras.ps1" }
} catch {}

& gemini @ArgsFromUser

