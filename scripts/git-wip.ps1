# scripts/git-wip.ps1
param([string]$Message = "")

if (-not (git diff --cached --quiet)) {
    $stats = git diff --cached --shortstat | ForEach-Object { $_.Trim() } # 통계를 한 줄로 만듦
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    
    if ([string]::IsNullOrEmpty($Message)) {
        $commitMsg = "WIP: $timestamp - $stats" # 한 줄로 요약
    } else {
        $commitMsg = "$Message - $stats" # 한 줄로 요약
    }
    
    git commit -m "$commitMsg" # -F 대신 -m 사용
} else {
    Write-Host "No staged changes to commit"
}