Param(
  [string]$Root = (Resolve-Path '.').Path,
  [int]$TrimLogsDays = 14,
  [switch]$Fix,
  [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Size-Pretty([Int64]$b){ if($b -ge 1GB){ return [string]::Format('{0:N2} GB',$b/1GB)}elseif($b -ge 1MB){return [string]::Format('{0:N2} MB',$b/1MB)}elseif($b -ge 1KB){return [string]::Format('{0:N2} KB',$b/1KB)}else{return "$b B"}}

$actions = @()

# 1) 터미널 로그 정리 계획
$termDir = Join-Path $Root 'terminal_logs'
if (Test-Path $termDir) {
  $cut = (Get-Date).AddDays(-$TrimLogsDays)
  $oldLogs = Get-ChildItem -LiteralPath $termDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt $cut }
  $total = ($oldLogs | Measure-Object Length -Sum).Sum
  $dest = Join-Path $Root ("archive/terminal_logs/" + (Get-Date -Format 'yyyyMMdd_HHmmss'))
  $actions += [pscustomobject]@{ kind='logs-archive'; files=$oldLogs.Count; size_bytes=$total; size=(Size-Pretty $total); from=$termDir; to=$dest }
  if ($Fix) {
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    foreach($f in $oldLogs){ $rel = $f.FullName.Substring($termDir.Length).TrimStart('\\'); $target = Join-Path $dest $rel; New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($target)) | Out-Null; if (-not $WhatIf) { Move-Item -LiteralPath $f.FullName -Destination $target -Force } }
  }
}

# 2) 메시지 허브 파일 크기 경고
$msgFile = Join-Path $Root 'context\messages.jsonl'
if (Test-Path $msgFile) {
  $fi = Get-Item $msgFile
  if ($fi.Length -gt 50MB) { $actions += [pscustomobject]@{ kind='messages-split-recommend'; path=$msgFile; size_bytes=$fi.Length; size=(Size-Pretty $fi.Length); note='50MB 초과 — 월별 파일로 분할 권장' } }
}

# 3) usage.db 진공 권고(외부 도구 필요)
foreach($cand in @('usage.db','scripts\usage.db')){
  $db = Join-Path $Root $cand
  if (Test-Path $db) {
    $fi = Get-Item $db
    $actions += [pscustomobject]@{ kind='sqlite-vacuum-recommend'; path=$db; size_bytes=$fi.Length; size=(Size-Pretty $fi.Length); note='sqlite3 또는 앱 내 유지 기능으로 VACUUM 권장' }
  }
}

# 출력
"# Maintenance Plan (dry-run=$(-not $Fix))" | Write-Output
foreach($a in $actions){
  Write-Output ("- {0}: {1}" -f $a.kind, ($a | ConvertTo-Json -Compress))
}

if ($Fix) {
  Write-Host "[APPLIED] 일부 정리 작업이 수행되었습니다." -ForegroundColor Green
} else {
  Write-Host "미적용(dry-run). --Fix 스위치로 적용할 수 있습니다." -ForegroundColor Yellow
}

