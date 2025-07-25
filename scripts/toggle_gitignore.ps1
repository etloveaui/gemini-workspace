# scripts/toggle_gitignore.ps1
#Foundational Enhancements.md]
param(
    [switch]$Restore
)
$gitignorePath = ".\.gitignore"
if (-not (Test-Path $gitignorePath)) {
    Write-Error "CRITICAL ERROR: .gitignore file not found at $gitignorePath"
    exit 1
}
$content = Get-Content $gitignorePath
$patternToComment = '^/projects/'
$patternToRestore = '^#\s*/projects/'

if ($Restore) {
    $newContent = $content -replace $patternToRestore, '/projects/'
    $action = "Restored"
} else {
    $newContent = $content -replace $patternToComment, '#/projects/'
    $action = "Commented"
}

Set-Content -Path $gitignorePath -Value $newContent -Encoding UTF8
Write-Host "[SUCCESS] $action /projects/ line in .gitignore"
