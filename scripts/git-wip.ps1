# scripts/git-wip.ps1
param([string]$Message = "")

if (-not (git diff --cached --quiet)) {
    $stats = git diff --cached --shortstat
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    
    if ([string]::IsNullOrEmpty($Message)) {
        $commitMsg = "WIP: $timestamp`n`n$stats"
    } else {
        $commitMsg = "$Message`n`n$stats"
    }
    
    $tempFile = [System.IO.Path]::GetTempFileName()
    $commitMsg | Out-File -FilePath $tempFile -Encoding UTF8
    
    git commit -F $tempFile
    Remove-Item $tempFile
} else {
    Write-Host "No staged changes to commit"
}