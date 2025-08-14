Param(
  [string]$DbPath = 'usage.db',
  [string]$Sqlite3 = 'sqlite3',
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8

if (-not (Test-Path $DbPath)) { Write-Error "DB not found: $DbPath"; exit 2 }
$sizeBefore = (Get-Item $DbPath).Length

Write-Host ("Target: {0} ({1} bytes)" -f $DbPath, $sizeBefore)

if ($DryRun) {
  Write-Host "Dry-run: 실제 VACUUM 미수행. 아래 정보를 참고하세요:" -ForegroundColor Yellow
  Write-Host "  sqlite3: $Sqlite3"
  Write-Host "  db: $DbPath"
  Write-Host "  SQL: VACUUM;"
  exit 0
}

try {
  & $Sqlite3 $DbPath "VACUUM;"
} catch {
  Write-Warning "sqlite3 실행 실패. PATH에 sqlite3가 없을 수 있습니다. Python fallback 시도."
  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
  if ($py) {
    & $py.Source -c "import sqlite3,sys; p=r'$DbPath'; con=sqlite3.connect(p); con.execute('VACUUM'); con.close()"
  } else {
    Write-Error "No Python found for VACUUM fallback."
    exit 3
  }
}

$sizeAfter = (Get-Item $DbPath).Length
Write-Host ("VACUUM 완료: {0} -> {1} bytes (Δ{2})" -f $sizeBefore, $sizeAfter, ($sizeAfter - $sizeBefore)) -ForegroundColor Green

