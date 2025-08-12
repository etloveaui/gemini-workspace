param (
    # 질문을 필수로 받도록 설정합니다.
    [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Question
)

# 1. 만능 키 로더를 불러옵니다.
. "$PSScriptRoot\Get-ApiKey.ps1"

# 2. Kimi API 키를 가져와서 임시 환경 변수로 설정합니다.
Write-Host "Asking Kimi..." -ForegroundColor Cyan
$env:KIMI_API_KEY = (Get-ApiKey -ModelName "Kimi")

# 3. '프로젝트 폴더 안의' 파이썬을 이용해 스크립트를 실행하고 질문을 전달합니다.
& "$PSScriptRoot\..\venv\Scripts\python.exe" "$PSScriptRoot\ask_kimi.py" $Question

# 4. 사용이 끝난 임시 환경 변수를 정리합니다.
Remove-Item -Path "env:KIMI_API_KEY" -ErrorAction SilentlyContinue