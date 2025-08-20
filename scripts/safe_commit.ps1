# WSL 환경에서 안전한 Git 커밋 스크립트
# 사용법: powershell -ExecutionPolicy Bypass -File safe_commit.ps1 "커밋메시지"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

# UTF-8 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:LC_ALL = "C.UTF-8"

try {
    # Git 설정 확인/수정
    git config --global core.quotepath false
    git config --global core.autocrlf true
    git config --global i18n.commitencoding utf-8
    git config --global i18n.logoutputencoding utf-8
    
    # 임시 커밋 메시지 파일 생성
    $tempFile = "COMMIT_MSG.tmp"
    $Message | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    # 변경사항 스테이지
    Write-Host "[단계1] 변경사항 스테이지..." -ForegroundColor Green
    git add .
    
    # 커밋 실행
    Write-Host "[단계2] 커밋 실행..." -ForegroundColor Green
    git commit -F $tempFile
    
    # 임시 파일 삭제
    if (Test-Path $tempFile) {
        Remove-Item $tempFile
        Write-Host "[완료] 임시 파일 삭제" -ForegroundColor Green
    }
    
    Write-Host "[성공] 커밋 완료!" -ForegroundColor Green
    git status --short
    
} catch {
    Write-Host "[오류] $($_.Exception.Message)" -ForegroundColor Red
    
    # 임시 파일 정리
    if (Test-Path "COMMIT_MSG.tmp") {
        Remove-Item "COMMIT_MSG.tmp"
    }
}