# Claude Code 백엔드를 Kimi로 설정
Write-Host "Setting Claude Code backend to KIMI..." -ForegroundColor Cyan

# 주석 또는 삭제: Get-ApiKey 관련 기존 호출
# . "$PSScriptRoot\Get-ApiKey.ps1"
# $kimiKey = Get-ApiKey -ModelName "Kimi"

# 직접 API 키 대입
$kimiKey = "sk-nYIW86uHCFzrQAHt3tLyBcQbJ5uLBd19lKaOG6BgQWMHudGY"

$env:KIMI_API_KEY = $kimiKey
$env:ANTHROPIC_BASE_URL = "https://api.moonshot.ai/anthropic"
$env:ANTHROPIC_AUTH_TOKEN = $kimiKey

Write-Host "Done. You can now use 'claude' command with Kimi."
