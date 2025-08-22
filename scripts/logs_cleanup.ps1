Param(
  [string]$Root = "logs",
  [int]$Days = 3
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Root)) {
  Write-Output "No logs directory: $Root"
  exit 0
}

$cutoff = (Get-Date).AddDays(-1 * [Math]::Abs($Days))
$today = Get-Date -Format 'yyyyMMdd'
$archive = Join-Path $Root ("archive/" + $today)
New-Item -ItemType Directory -Force -Path $archive | Out-Null

$moved = 0
Get-ChildItem $Root -File -Recurse -Include *.log | Where-Object { $_.LastWriteTime -lt $cutoff -and $_.FullName -notmatch '[\\/]archive[\\/]' } | ForEach-Object {
  $dest = Join-Path $archive $_.Name
  if (Test-Path $dest) {
    $dest = Join-Path $archive (('{0}_{1}{2}' -f [IO.Path]::GetFileNameWithoutExtension($_.Name), $_.LastWriteTime.ToString('yyyyMMddHHmmss'), [IO.Path]::GetExtension($_.Name)))
  }
  Move-Item -Path $_.FullName -Destination $dest
  $moved++
}

Write-Output ("LOGS_CLEANUP moved=" + $moved)

