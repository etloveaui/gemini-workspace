# Install UTF-8 and rendering hints into PowerShell 7 profiles (per-user)
$ErrorActionPreference = 'Stop'

$doc = [Environment]::GetFolderPath('MyDocuments')
$dir = Join-Path $doc 'PowerShell'
New-Item -Path $dir -ItemType Directory -Force | Out-Null

$targets = @(
  (Join-Path $dir 'Profile.ps1'),
  (Join-Path $dir 'Microsoft.VSCode_profile.ps1'),
  (Join-Path $dir 'Microsoft.PowerShell_profile.ps1')
)

$marker = '# BEGIN codex-utf8-profile'
$content = @"
$marker
# Applied by Codex CLI: UTF-8 and rendering hints
try { $OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }
try { $PSStyle.OutputRendering = 'Host' } catch { }
$env:PYTHONIOENCODING = 'utf-8'
# END codex-utf8-profile
"@

foreach($t in $targets){
  if(-not (Test-Path $t)){
    New-Item -Path $t -ItemType File -Force | Out-Null
  }
  $has = Select-String -Path $t -Pattern ([regex]::Escape($marker)) -Quiet -ErrorAction SilentlyContinue
  if(-not $has){ Add-Content -Path $t -Value $content -Encoding UTF8 }
}

Write-Host "[ps7-utf8] Installed profile hints to:" -ForegroundColor Green
$targets | ForEach-Object { Write-Host " - $_" }
