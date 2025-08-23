# PowerShell 인코딩 문제 근본 해결 스크립트
# UTF-8 설정을 시스템 레벨에서 영구 적용

Write-Host "[시작] PowerShell 인코딩 문제 영구 해결 중..." -ForegroundColor Green

# 1. 현재 세션 UTF-8 설정
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[설정] 현재 세션 UTF-8 적용 완료" -ForegroundColor Yellow

# 2. PowerShell 프로필 경로 확인
$profilePath = $PROFILE.AllUsersAllHosts
$profileDir = Split-Path $profilePath -Parent

# 3. 프로필 디렉토리 생성 (없는 경우)
if (!(Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force
    Write-Host "[생성] 프로필 디렉토리 생성: $profileDir" -ForegroundColor Yellow
}

# 4. UTF-8 설정을 프로필에 추가
$utf8Settings = @"
# UTF-8 인코딩 영구 설정 (Claude Code 최적화)
try {
    `$OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    
    # 코드페이지 UTF-8로 설정
    chcp 65001 > `$null
} catch {
    Write-Warning "UTF-8 설정 중 오류 발생: `$_"
}
"@

# 5. 프로필에 설정 추가 (중복 방지)
$currentProfile = ""
if (Test-Path $profilePath) {
    $currentProfile = Get-Content $profilePath -Raw
}

if ($currentProfile -notmatch "UTF-8 인코딩 영구 설정") {
    Add-Content -Path $profilePath -Value $utf8Settings -Encoding UTF8
    Write-Host "[추가] UTF-8 설정을 PowerShell 프로필에 추가" -ForegroundColor Green
} else {
    Write-Host "[확인] UTF-8 설정이 이미 프로필에 존재함" -ForegroundColor Blue
}

# 6. 레지스트리 설정 (시스템 레벨)
try {
    # Windows 10/11 UTF-8 지원 활성화
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage"
    Set-ItemProperty -Path $regPath -Name "ACP" -Value "65001" -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $regPath -Name "OEMCP" -Value "65001" -ErrorAction SilentlyContinue
    
    Write-Host "[설정] 시스템 레지스트리 UTF-8 설정 적용" -ForegroundColor Green
} catch {
    Write-Host "[경고] 레지스트리 설정 권한 부족 (관리자 권한으로 재실행 권장)" -ForegroundColor Yellow
}

# 7. 환경 변수 설정
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")
Write-Host "[설정] PYTHONIOENCODING=utf-8 환경 변수 설정" -ForegroundColor Green

# 8. 현재 설정 확인
Write-Host "`n[확인] 현재 인코딩 설정:" -ForegroundColor Cyan
Write-Host "  - Output Encoding: $($OutputEncoding.EncodingName)" -ForegroundColor White
Write-Host "  - Console Output: $([Console]::OutputEncoding.EncodingName)" -ForegroundColor White
Write-Host "  - Console Input: $([Console]::InputEncoding.EncodingName)" -ForegroundColor White
Write-Host "  - Code Page: $(chcp)" -ForegroundColor White

Write-Host "`n[완료] PowerShell 인코딩 문제 영구 해결 완료!" -ForegroundColor Green
Write-Host "       새로운 PowerShell 세션에서 자동 적용됩니다." -ForegroundColor Green