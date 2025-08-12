# API 키를 secrets 파일에서 안전하게 읽어오는 범용 함수 (단순화 버전)
function Get-ApiKey {
    param (
        [Parameter(Mandatory=$true)]
        [string]$ModelName
    )
    $secretsFile = Join-Path $PSScriptRoot "../secrets/my_sensitive_data.md"
    $fileContent = Get-Content -Path $secretsFile -Raw

    # --- 복잡한 정규식 대신 단순 분할 방식으로 변경 ---
    $blocks = $fileContent -split '---'
    foreach ($block in $blocks) {
        if ($block -match "### $ModelName") {
            $lines = $block -split "`r`n"
            foreach ($line in $lines) {
                if ($line -match "API Key:") {
                    $key = ($line -split '`')[1]
                    if ($key) {
                        return $key
                    }
                }
            }
        }
    }
    # --- 여기까지 변경 ---

    throw "API Key for '$ModelName' not found in secrets/my_sensitive_data.md"
}
