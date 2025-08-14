Param(
  [string]$Root = (Resolve-Path '.').Path,
  [string]$OutputDir = (Join-Path (Resolve-Path '.').Path 'reports'),
  [int]$TopN = 50,
  [switch]$Json
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Ensure-Dir($p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null } }
Ensure-Dir $OutputDir
$ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
$reportTxt = Join-Path $OutputDir ("sys_audit_" + $ts + ".txt")
$reportJson = Join-Path $OutputDir ("sys_audit_" + $ts + ".json")

function Try-Run($scriptblock) { try { & $scriptblock } catch { "__ERROR__: " + $_.Exception.Message } }
function Size-Pretty([Int64]$b){ if($b -ge 1GB){ return [string]::Format('{0:N2} GB',$b/1GB)}elseif($b -ge 1MB){return [string]::Format('{0:N2} MB',$b/1MB)}elseif($b -ge 1KB){return [string]::Format('{0:N2} KB',$b/1KB)}else{return "$b B"}}

$result = [ordered]@{}
$result.environment = [ordered]@{
  time_utc = (Get-Date).ToUniversalTime().ToString('o')
  root = $Root
  ps_version = $PSVersionTable.PSVersion.ToString()
  os = (Get-CimInstance Win32_OperatingSystem | Select-Object -First 1 Caption, Version)
  env = @{
    ACTIVE_AGENT = $env:ACTIVE_AGENT
    AI_REC_AUTO = $env:AI_REC_AUTO
    PYTHONIOENCODING = $env:PYTHONIOENCODING
    CODEX_RPS = $env:CODEX_RPS
  }
}

# Git 요약(있으면)
$gitSummary = Try-Run { git -C $Root status -s -b }
$result.git = @{
  status = $gitSummary
}

# 상위 디렉터리 용량(1-depth)
$topDirs = @()
Get-ChildItem -LiteralPath $Root -Force -ErrorAction SilentlyContinue | Where-Object { $_.PSIsContainer } | ForEach-Object {
  $path = $_.FullName
  $name = $_.Name
  $filters = @('.git','venv','node_modules')
  $recurse = $true
  $size = 0
  try {
    if ($filters -contains $name) {
      # 큰 폴더는 빠르게 합산(파일만 카운트)
      Get-ChildItem -LiteralPath $path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $size += $_.Length }
    } else {
      Get-ChildItem -LiteralPath $path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $size += $_.Length }
    }
  } catch {}
  $topDirs += [pscustomobject]@{ name=$name; size_bytes=$size; size= (Size-Pretty $size) }
}
$result.top_dirs = $topDirs | Sort-Object size_bytes -Descending | Select-Object -First 20

# 큰 파일 TopN
$bigFiles = @()
Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch '\\.git|\\venv|\\node_modules|\\projects\\' } |
  Sort-Object Length -Descending | Select-Object -First $TopN |
  ForEach-Object { [pscustomobject]@{ path = $_.FullName.Substring($Root.Length).TrimStart('\\'); size_bytes = $_.Length; size=(Size-Pretty $_.Length) } }
$result.big_files = $bigFiles

# 로그/메시지/DB 크기
function File-Info($p){ if(Test-Path $p){ $f=Get-Item $p; return @{ path=$p; size_bytes=$f.Length; size=(Size-Pretty $f.Length)} } else { return $null } }
$candidateFiles = @(
  (Join-Path $Root 'context\messages.jsonl')
  (Join-Path $Root 'scripts\usage.db')
  (Join-Path $Root 'usage.db')
  (Join-Path $Root 'terminal_logs')
)
$pathsInfo = @()
foreach($p in $candidateFiles){
  if (Test-Path $p) {
    if ((Get-Item $p).PSIsContainer) {
      $sz=0; Get-ChildItem -LiteralPath $p -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $sz+=$_.Length }
      $pathsInfo += @{ path=$p; size_bytes=$sz; size=(Size-Pretty $sz); type='dir' }
    } else {
      $pathsInfo += (File-Info $p)
    }
  }
}
$result.heavy_paths = $pathsInfo

# 확장자별 파일 수 TopN
$extCounts = @{}
Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
  ForEach-Object {
    $ext = [IO.Path]::GetExtension($_.Name)
    if ([string]::IsNullOrWhiteSpace($ext)) { $ext = '(none)' }
    if (-not $extCounts.ContainsKey($ext)) { $extCounts[$ext] = 0 }
    $extCounts[$ext] += 1
  }
$extTable = $extCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 30 | ForEach-Object { [pscustomobject]@{ ext=$_.Key; count=$_.Value } }
$result.ext_counts = $extTable

# 시크릿/무시 규칙 점검(요약)
$gitignore = Join-Path $Root '.gitignore'
$shouldIgnore = @('.gemini/', 'secrets/', 'projects/', '*.log', '*.sqlite*')
$ignoreState = @()
foreach($pat in $shouldIgnore){
  $found = $false
  if (Test-Path $gitignore) { $content = Get-Content -LiteralPath $gitignore -ErrorAction SilentlyContinue; $found = ($content -contains $pat) -or ($content | Where-Object { $_ -like $pat }) }
  $exists = Test-Path (Join-Path $Root $pat.TrimEnd('/'))
  $ignoreState += [pscustomobject]@{ pattern=$pat; present_in_gitignore=$found; path_exists=$exists }
}
$result.ignore_checks = $ignoreState

# 이머전시 구성 확인
$emFile = Join-Path $Root '.agents\emergency.json'
$result.emergency = @{
  wrapper_present = (Test-Path (Join-Path $Root 'tools\codex_emergency.ps1'))
  config_present = (Test-Path $emFile)
}

# 출력
$lines = @()
$lines += "# System Audit Report ($($result.environment.time_utc))"
$lines += "Root: $($result.environment.root)"
$lines += "PowerShell: $($result.environment.ps_version)"
$lines += ""
$lines += "== Git status =="
$lines += "$($result.git.status)"
$lines += ""
$lines += "== Top directories by size =="
foreach($d in $result.top_dirs){ $lines += ("{0,12}  {1}" -f $d.size, $d.name) }
$lines += ""
$lines += "== Largest files =="
foreach($f in $result.big_files){ $lines += ("{0,12}  {1}" -f $f.size, $f.path) }
$lines += ""
$lines += "== Heavy paths =="
foreach($h in $result.heavy_paths){ $lines += ("{0,12}  {1}" -f $h.size, $h.path) }
$lines += ""
$lines += "== Top file extensions =="
foreach($e in $result.ext_counts){ $lines += ("{0,6}  {1}" -f $e.count, $e.ext) }
$lines += ""
$lines += "== Ignore rules check =="
foreach($i in $result.ignore_checks){ $lines += ("{0,-14} present={1}  exists={2}" -f $i.pattern, $i.present_in_gitignore, $i.path_exists) }
$lines += ""
$lines += "== Emergency config =="
$lines += ("wrapper_present={0} config_present={1}" -f $result.emergency.wrapper_present, $result.emergency.config_present)

Set-Content -LiteralPath $reportTxt -Value ($lines -join "`n") -Encoding UTF8
if ($Json) { $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportJson -Encoding UTF8 }

Write-Host "Audit complete -> $reportTxt"
if ($Json) { Write-Host "JSON -> $reportJson" }
