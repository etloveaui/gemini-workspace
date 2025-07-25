# scripts/log_usage.ps1
#Foundational Enhancements.md]
param([string]$TaskId = "N/A")

$logFilePath = Join-Path $PSScriptRoot '..' 'docs' 'usage_log.csv'
if (-not (Test-Path $logFilePath)) {
    "Timestamp,TaskId,InputTokens,OutputTokens" | Out-File -FilePath $logFilePath -Encoding utf8
}
# 실제 토큰 값은 추후 API 응답과 연동하여 파싱 예정
$inputTokens = 0
$outputTokens = 0
$csvLine = "$(Get-Date -Format 'o'),$TaskId,$inputTokens,$outputTokens"
Add-Content -Path $logFilePath -Value $csvLine
Write-Host "[SUCCESS] Placeholder usage logged to docs/usage_log.csv for Task: $TaskId"
