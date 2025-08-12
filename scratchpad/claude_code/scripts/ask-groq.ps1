# ask-groq.ps1
# Usage:
#   .\ask-groq.ps1 "질문"
#   .\ask-groq.ps1 -Route think "복잡한 추론"
#   "파이프" | .\ask-groq.ps1 -Route fast
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ArgsRest
)
$script = Join-Path $PSScriptRoot "ask_groq.py"

# 파워셸에서 STDIN 지원
if ($MyInvocation.ExpectingInput) {
  $stdin = [Console]::In.ReadToEnd()
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName  = "python"
  $psi.Arguments = "`"$script`" $($ArgsRest -join ' ')"
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardOutput = $true
  $psi.UseShellExecute = $false
  $p = [System.Diagnostics.Process]::Start($psi)
  $p.StandardInput.Write($stdin)
  $p.StandardInput.Close()
  $out = $p.StandardOutput.ReadToEnd()
  $p.WaitForExit()
  Write-Output $out
} else {
  python $script @ArgsRest
}
