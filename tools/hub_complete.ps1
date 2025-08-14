Param(
  [string]$Root = (Resolve-Path '.').Path,
  [string]$Agent = 'codex',
  [string]$QueueFile = 'agents_hub/queue/codex_followup_emergency.json',
  [ValidateSet('success','failed')]
  [string]$Result = 'success',
  [string]$Note = ''
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Ensure-Dir($p){ if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null } }

$qPath = if ([System.IO.Path]::IsPathRooted($QueueFile)) { $QueueFile } else { Join-Path $Root $QueueFile }
if (-not (Test-Path $qPath)) { Write-Error "Queue file not found: $qPath"; exit 2 }

$ts = [DateTime]::UtcNow.ToString('yyyyMMdd')
$archDir = Join-Path $Root ("agents_hub/archive/" + $ts + "/" + $Result)
Ensure-Dir $archDir

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($qPath)
$target = Join-Path $archDir ($baseName + "_" + (Get-Date -Format 'HHmmss') + '.json')
Move-Item -Force -LiteralPath $qPath -Destination $target

if ($Note -and $Note.Trim()) {
  $notePath = [System.IO.Path]::ChangeExtension($target, '.note.txt')
  Set-Content -LiteralPath $notePath -Value $Note -Encoding UTF8
}

Write-Host ("Archived -> {0}" -f $target) -ForegroundColor Green
