Param(
    [string]$Base = "communication/codex",
    [int]$Days = 3,
    [string]$TaskFile = "communication/codex/20250822_urgent_task.md"
)

$ErrorActionPreference = 'Stop'

function New-ArchiveDirectory {
    param([string]$Base)
    $today = Get-Date -Format 'yyyyMMdd'
    $arch = Join-Path $Base ("archive/" + $today)
    New-Item -ItemType Directory -Force -Path $arch | Out-Null
    return $arch
}

function Remove-BakTmp {
    param([string]$Base)
    $targets = Get-ChildItem $Base -File -Recurse -Include *.bak,*.tmp |
        Where-Object { $_.FullName -notmatch '[\\/]archive[\\/]' }
    $count = ($targets | Measure-Object).Count
    if ($count -gt 0) { $targets | Remove-Item -Force }
    return $count
}

function Move-OldFiles {
    param([string]$Base, [DateTime]$Cutoff, [string]$Archive)
    $moved = 0
    $old = Get-ChildItem $Base -File -Recurse |
        Where-Object { $_.LastWriteTime -lt $Cutoff -and $_.FullName -notmatch '[\\/]archive[\\/]' }
    foreach ($f in $old) {
        $dest = Join-Path $Archive $f.Name
        if (Test-Path $dest) {
            $dest = Join-Path $Archive ("{0}_{1}{2}" -f [IO.Path]::GetFileNameWithoutExtension($f.Name), $f.LastWriteTime.ToString('yyyyMMddHHmmss'), [IO.Path]::GetExtension($f.Name))
        }
        Move-Item -Path $f.FullName -Destination $dest
        $moved++
    }
    return $moved
}

function Move-DuplicatesByHash {
    param([string]$Base, [string]$Archive)
    $dupDir = Join-Path $Archive 'duplicates'
    New-Item -ItemType Directory -Force -Path $dupDir | Out-Null
    $files = Get-ChildItem $Base -File -Recurse |
        Where-Object { $_.FullName -notmatch '[\\/]archive[\\/]' }
    $map = @{}
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    foreach ($f in $files) {
        $fs = [IO.File]::OpenRead($f.FullName)
        try {
            $bytes = $sha256.ComputeHash($fs)
        } finally { $fs.Dispose() }
        $h = ($bytes | ForEach-Object { $_.ToString('x2') }) -join ''
        if (-not $map.ContainsKey($h)) { $map[$h] = New-Object System.Collections.ArrayList }
        [void]$map[$h].Add($f)
    }
    $moved = 0
    foreach ($kv in $map.GetEnumerator()) {
        $list = $kv.Value | Sort-Object LastWriteTime -Descending
        if ($list.Count -gt 1) {
            # keep the newest
            foreach ($d in $list[1..($list.Count-1)]) {
                $dest = Join-Path $dupDir $d.Name
                if (Test-Path $dest) {
                    $dest = Join-Path $dupDir ("{0}_{1}{2}" -f [IO.Path]::GetFileNameWithoutExtension($d.Name), $d.LastWriteTime.ToString('yyyyMMddHHmmss'), [IO.Path]::GetExtension($d.Name))
                }
                Move-Item -Path $d.FullName -Destination $dest
                $moved++
            }
        }
    }
    return $moved
}

# Main
$arch = New-ArchiveDirectory -Base $Base
$cutoff = (Get-Date).AddDays(-1 * [Math]::Abs($Days))

$bakCount = Remove-BakTmp -Base $Base
$oldMoved = Move-OldFiles -Base $Base -Cutoff $cutoff -Archive $arch
$dupMoved = Move-DuplicatesByHash -Base $Base -Archive $arch

$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$nl = [Environment]::NewLine
$log = $nl + '## Update - ' + $ts + $nl + '- Cleanup: .bak/.tmp deleted ' + $bakCount + ', old moved ' + $oldMoved + ', duplicates moved ' + $dupMoved
Add-Content -Path $TaskFile -Value $log
