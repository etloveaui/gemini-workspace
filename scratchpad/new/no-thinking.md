\[Role: Tech]

## 🤔 Strategic Analysis

가능. `thinking` 원문은 숨기고, 캡처해 GPT로 재번역해 대체 출력. 오버헤드는 토큰·지연 증가. CLI가 `--no-thinking`을 공식 지원한다면 그 옵션을 우선 사용.

## 📝 Expert Recommendation

아래 PowerShell 래퍼를 `~/codex-ko.ps1`로 저장해 실행하세요. `thinking`은 숨기고 한글 번역만 보여줍니다. `[불확실]` Codex 출력 포맷이 변하면 정규식 조정 필요.

```powershell
# codex-ko.ps1
param([Parameter(ValueFromRemainingArguments=$true)]$Args)

# 1) Codex 실행 및 원문 캡처
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "codex"
$psi.Arguments = ($Args -join " ")
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError  = $true
$psi.UseShellExecute = $false
$p = [System.Diagnostics.Process]::Start($psi)
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()

# 2) thinking 블록 추출 (헤더 'thinking'부터 다음 빈줄/새 섹션 전까지)
$pattern = '(?ms)^\s*thinking\s*\R(.*?)(?=^\S|\Z)'
$matches = [System.Text.RegularExpressions.Regex]::Matches($stdout, $pattern)

# 3) 번역 함수: Codex를 재호출해 한국어 번역(생각 출력은 비활성화 시도)
function Invoke-TranslateKo([string]$text) {
    $prompt = "아래 영어를 자연스러운 한국어로 간결히 번역:\n---\n$text\n---"
    $tpsi = New-Object System.Diagnostics.ProcessStartInfo
    $tpsi.FileName = "codex"
    $tpsi.Arguments = "-m gpt-5 --no-thinking --prompt " + ('"{0}"' -f ($prompt -replace '"','\"'))
    $tpsi.RedirectStandardOutput = $true
    $tpsi.RedirectStandardError  = $true
    $tpsi.UseShellExecute = $false
    $tp = [System.Diagnostics.Process]::Start($tpsi)
    $tout = $tp.StandardOutput.ReadToEnd()
    $terr = $tp.StandardError.ReadToEnd()
    $tp.WaitForExit()
    if ($tp.ExitCode -ne 0) { return "[번역오류] $terr".Trim() }
    return $tout.Trim()
}

# 4) 원문에서 thinking 제거 후 번역본 삽입
$processed = $stdout
foreach ($m in $matches) {
    $orig = $m.Value
    $body = $m.Groups[1].Value.Trim()
    $ko   = Invoke-TranslateKo $body
    $replacement = "thinking: [숨김]\n번역(thinking):`n$ko`n"
    $processed = $processed.Replace($orig, $replacement)
}

# 5) 출력
if ($stderr) { Write-Error $stderr }
$processed
```

사용법:

```powershell
# 1회 실행
pwsh -File ~/codex-ko.ps1 run

# 자주 쓰기: 짧은 별칭
Set-Alias cxk "$HOME/codex-ko.ps1"
cxk chat
cxk refactor --apply
```

옵션:

* `thinking 완전 비표시`: 번역도 빼고 숨기려면 3)\~4) 블록을 제거 후 정규식으로 `$processed = [regex]::Replace($stdout,$pattern,'')`.
* 지연 최소화: 여러 `thinking` 블록을 묶어 한 번에 번역하도록 3)에서 프롬프트를 하나로 합치기.

추가 요청이 있으시면 알려주세요.
