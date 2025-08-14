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
  Write-Host "Dry-run: 실제 VACUUM 미수행. 아래 명령을 참고하세요:" -ForegroundColor Yellow
  Write-Host ("  {0} {1} \"VACUUM;\"" -f $Sqlite3, $DbPath)
  exit 0
}

try {
  & $Sqlite3 $DbPath "VACUUM;"
} catch {
  Write-Error "sqlite3 실행 실패. PATH에 sqlite3가 없을 수 있습니다. -Sqlite3 파라미터로 경로를 지정하거나 앱 내 유지 기능을 사용하세요."
  exit 3
}

$sizeAfter = (Get-Item $DbPath).Length
Write-Host ("VACUUM 완료: {0} -> {1} bytes (Δ{2})" -f $sizeBefore, $sizeAfter, ($sizeAfter - $sizeBefore)) -ForegroundColor Green

