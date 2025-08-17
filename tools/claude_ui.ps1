Param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args,
  [switch]$Extras
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Get-RepoRoot {
  try { $p = (git rev-parse --show-toplevel 2>$null).Trim(); if ($p) { return $p } } catch {}
  return (Resolve-Path '.').Path
}

$root = Get-RepoRoot
Set-Location $root

# Ensure agent label + auto transcript profile
$env:ACTIVE_AGENT = 'claude'
if (-not $env:AI_REC_AUTO) { $env:AI_REC_AUTO = '0' }
. "$root\scripts\ps7_utf8_profile_sample.ps1"
if ($Extras) { . "$root\scripts\ps7_utf8_profile_extras.ps1" }

# Inject GROQ_API_KEY from repo secrets if not set; also set OpenAI-compatible envs for Groq
if (-not $env:GROQ_API_KEY -or -not $env:GROQ_API_KEY.Trim()) {
  $secPath = Join-Path $root 'secrets\my_sensitive_data.md'
  if (Test-Path $secPath) {
    try {
      $txt = Get-Content -Raw -Encoding UTF8 $secPath
      $m = [Regex]::Match($txt, '(gsk_[A-Za-z0-9_-]+)')
      if ($m.Success) { $env:GROQ_API_KEY = $m.Groups[1].Value }
    } catch {}
  }
}

# Export OpenAI-compatible variables so CLIs that expect OpenAI schema can use Groq seamlessly
if ($env:GROQ_API_KEY -and $env:GROQ_API_KEY.Trim()) {
  if (-not $env:OPENAI_API_KEY)  { $env:OPENAI_API_KEY  = $env:GROQ_API_KEY }
  if (-not $env:OPENAI_BASE_URL) { $env:OPENAI_BASE_URL = 'https://api.groq.com/openai/v1' }
  if (-not $env:OPENAI_API_BASE) { $env:OPENAI_API_BASE = 'https://api.groq.com/openai/v1' }
}

# Hand off to global claude CLI (PATH)
$cli = Get-Command claude -ErrorAction SilentlyContinue
if (-not $cli) { Write-Error "Global 'claude' CLI not found in PATH (npm). Please install it."; exit 127 }

# Run with passthrough args; current dir is repo so it picks ./config.json if used
& $cli.Source @Args
