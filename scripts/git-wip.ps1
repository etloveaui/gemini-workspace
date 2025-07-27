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
    
    $tmpFile = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmpFile -Value $commitMsg -Encoding utf8
    git commit -F $tmpFile
    Remove-Item $tmpFile
} else {
    Write-Host "No staged changes to commit"
}