Param(
  [string]$Root = (Resolve-Path '.').Path,
  [string]$Input = (Join-Path (Resolve-Path '.').Path 'context/messages.jsonl'),
  [string]$OutDir = (Join-Path (Resolve-Path '.').Path 'context/archive'),
  [switch]$Apply,
  [switch]$Verbose
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

if (-not (Test-Path $Input)) { Write-Error "Input not found: $Input"; exit 2 }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

function Get-MonthKey([string]$ts){
  try { return ([DateTimeOffset]::Parse($ts)).ToString('yyyyMM') } catch { return $null }
}

$counts = @{}
$tmpMap = @{}
$lineNum = 0

Write-Host "Scanning $Input ..."
Get-Content -LiteralPath $Input -ReadCount 1000 | ForEach-Object {
  foreach($line in $_){
    $lineNum++
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $month = $null
    try { $obj = $line | ConvertFrom-Json -ErrorAction Stop; $month = Get-MonthKey $obj.ts } catch { $month = $null }
    if (-not $month) { $month = (Get-Item $Input).LastWriteTime.ToString('yyyyMM') }
    if (-not $counts.ContainsKey($month)) { $counts[$month] = 0 }
    $counts[$month] += 1
    if ($Apply) {
      if (-not $tmpMap.ContainsKey($month)) {
        $tmp = [System.IO.Path]::GetTempFileName()
        $tmpMap[$month] = $tmp
      }
      Add-Content -LiteralPath $tmpMap[$month] -Value $line -Encoding UTF8
    }
  }
}

Write-Host "Found months: " ($counts.Keys -join ', ')
foreach($k in ($counts.Keys | Sort-Object)){
  Write-Host ("- {0}: {1} lines" -f $k, $counts[$k])
}

if ($Apply) {
  foreach($k in $tmpMap.Keys){
    $target = Join-Path $OutDir ("messages_" + $k + ".jsonl")
    Write-Host ("Writing -> {0}" -f $target)
    if (-not (Test-Path (Split-Path $target -Parent))) { New-Item -ItemType Directory -Force -Path (Split-Path $target -Parent) | Out-Null }
    Move-Item -Force -LiteralPath $tmpMap[$k] -Destination $target
  }
  Write-Host "Done. Original 파일은 보존됩니다(안전). 필요시 수동 로테이트 권장." -ForegroundColor Green
} else {
  Write-Host "미적용(dry-run). --Apply로 실제 파일 생성." -ForegroundColor Yellow
}

