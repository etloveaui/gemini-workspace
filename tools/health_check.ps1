Param(
  [string]$Root = (Resolve-Path '.').Path,
  [switch]$Json,
  [switch]$Apply,
  [int]$HubThresholdMB = 50,
  [switch]$Vacuum
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

function Section($title){ Write-Host ("`n=== {0} ===" -f $title) -ForegroundColor Cyan }
function Exists([string]$p){ return (Test-Path $p) }

Section 'Environment'
Write-Host ("Root: {0}" -f $Root)
Write-Host ("Agent: {0}" -f ($(if ($env:ACTIVE_AGENT) { $env:ACTIVE_AGENT } else { '(none)' })))

# 1) 시스템 감사
Section 'System Audit'
$auditArgs = @('-File', (Join-Path $Root 'tools/sys_audit.ps1'))
if ($Json) { $auditArgs += '-Json' }
& pwsh -ExecutionPolicy Bypass @auditArgs

# 2) 유지/정리 플랜(dry-run)
if ($Apply) {
  Section 'Maintenance Plan (apply)'
  & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/sys_maint.ps1') -Fix
} else {
  Section 'Maintenance Plan (dry-run)'
  & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/sys_maint.ps1')
}

# 3) 메시지 허브 분할(dry-run, 파일 있을 때만)
$hub = Join-Path $Root 'context/messages.jsonl'
if (Exists $hub) {
  $hubSize = (Get-Item $hub).Length
  $hubMB = [math]::Round($hubSize / 1MB, 2)
  if ($Apply -and $hubSize -gt ($HubThresholdMB * 1MB)) {
    Section ("Hub Split (apply) — {0} MB > {1} MB" -f $hubMB, $HubThresholdMB)
    & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/hub_split.ps1') -Apply
  } else {
    Section 'Hub Split (dry-run)'
    & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/hub_split.ps1')
  }
} else {
  Write-Host "context/messages.jsonl 없음 — 분할 스킵" -ForegroundColor DarkGray
}

# 4) SQLite VACUUM 헬프(dry-run, 파일 자동 탐색)
if ($Apply -or $Vacuum) { Section 'SQLite VACUUM (apply)' } else { Section 'SQLite VACUUM (dry-run)' }
$dbCandidates = @(
  (Join-Path $Root 'usage.db'),
  (Join-Path $Root 'scripts/usage.db')
)
$dbPath = $null
foreach($c in $dbCandidates){ if (Exists $c) { $dbPath = $c; break } }
if ($dbPath) {
  if ($Apply -or $Vacuum) {
    # Try helper; on failure fallback to Python
    try {
      & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/sqlite_vacuum_helper.ps1') -DbPath $dbPath
    } catch {
      Write-Warning "sqlite_vacuum_helper failed; falling back to Python"
      $py = Get-Command python -ErrorAction SilentlyContinue
      if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
      if ($py) {
        & $py.Source -c "import sqlite3; import sys; p=r'$dbPath'; con=sqlite3.connect(p); con.execute('VACUUM'); con.close(); print('VACUUM done via Python')"
      } else {
        Write-Error 'No python found for VACUUM fallback.'
      }
    }
  } else {
    & pwsh -ExecutionPolicy Bypass -File (Join-Path $Root 'tools/sqlite_vacuum_helper.ps1') -DbPath $dbPath -DryRun
  }
} else {
  Write-Host "usage.db 후보가 없어 VACUUM 스킵" -ForegroundColor DarkGray
}

if (-not $Apply -and -not $Vacuum) {
  Section 'Next Steps'
  Write-Host "적용 실행 예시:" -ForegroundColor Yellow
  Write-Host "  1) 로그 정리 적용:   pwsh -ExecutionPolicy Bypass -File tools/sys_maint.ps1 --Fix"
  Write-Host "  2) 허브 분할 적용:   pwsh -ExecutionPolicy Bypass -File tools/hub_split.ps1 --Apply"
  Write-Host "  3) DB VACUUM 적용:   pwsh -ExecutionPolicy Bypass -File tools/sqlite_vacuum_helper.ps1 -DbPath usage.db"
  Write-Host "  4) 과부하 완화 실행: pwsh -ExecutionPolicy Bypass -File tools/codex_emergency.ps1 -- codex <기존_인자들>"
}

Write-Host "완료. reports/ 디렉터리의 감사 결과를 확인하세요." -ForegroundColor Green
