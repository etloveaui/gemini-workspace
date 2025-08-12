# Claude Code 백엔드를 Qwen으로 설정
Write-Host "Setting Claude Code backend to QWEN..." -ForegroundColor Green
. "$PSScriptRoot\Get-ApiKey.ps1"
$qwenKey = Get-ApiKey -ModelName "Qwen"

$env:ANTHROPIC_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v2/apps/claude-code-proxy"
$env:ANTHROPIC_AUTH_TOKEN=$qwenKey
Write-Host "Done. You can now use 'claude --model qwen3-coder-plus ...' command."