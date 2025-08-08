# 🔍 Gemini CLI Git 훅 문제 분석 및 해결 방안

현재 상황을 분석한 결과, **Windows 환경에서 Git 훅과 PowerShell 간의 동기화 문제**로 판단됩니다. 몇 가지 실용적인 해결책을 제안드리겠습니다.

## 🎯 문제의 핵심 원인

1. **Git의 COMMIT_EDITMSG 처리 타이밍**: Git이 훅 완료를 기다리지 않고 메시지를 읽어버림
2. **Windows 파일시스템 동기화**: PowerShell의 파일 쓰기와 Git의 파일 읽기 간 지연
3. **프로세스 간 통신 지연**: bash → powershell → git 간의 복잡한 실행 체인

## 💡 해결 방안 (우선순위별)

### **방안 1: prepare-commit-msg 훅 사용 (권장)**

`pre-commit` 대신 `prepare-commit-msg` 훅을 사용하는 것이 더 적합합니다.

**새로운 파일**: `.githooks/prepare-commit-msg`
```bash
#!/bin/bash
powershell.exe -ExecutionPolicy Bypass -File "$(dirname "$0")/prepare-commit-msg.ps1" "$1" "$2" "$3"
```

**새로운 파일**: `.githooks/prepare-commit-msg.ps1`
```powershell
#!/usr/bin/env pwsh
param($commitMsgFile, $commitSource, $sha1)

# 커밋 메시지 파일이 비어있거나 기본 메시지일 때만 처리
$currentMsg = if (Test-Path $commitMsgFile) { 
    (Get-Content $commitMsgFile -Raw -ErrorAction SilentlyContinue) 
} else { 
    "" 
}

# 빈 메시지이거나 기본 템플릿일 때만 WIP 메시지 생성
if ([string]::IsNullOrWhiteSpace($currentMsg)) {
    $stats = git diff --cached --shortstat 2>$null
    if ($stats) {
        $wipMessage = "WIP: $(Get-Date -Format 'yyyy-MM-dd HH:mm')`n`n$stats"
        try {
            $wipMessage | Out-File $commitMsgFile -Encoding utf8 -NoNewline
            Write-Host "[HOOK] Auto-generated WIP commit message"
        } catch {
            Write-Warning "[HOOK] Failed to write WIP message: $_"
        }
    }
}
```

### **방안 2: Python 기반 훅 (안정성 강화)**

PowerShell 대신 Python을 사용하여 크로스 플랫폼 호환성 확보:

**새로운 파일**: `.githooks/prepare-commit-msg.py`
```python
#!/usr/bin/env python3
import sys
import os
import subprocess
from datetime import datetime

def main():
    commit_msg_file = sys.argv[1]
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # 커밋 메시지 파일 읽기
    try:
        with open(commit_msg_file, 'r', encoding='utf-8') as f:
            current_msg = f.read().strip()
    except:
        current_msg = ""
    
    # 빈 메시지일 때만 WIP 메시지 생성
    if not current_msg:
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--shortstat'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                wip_msg = f"WIP: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{result.stdout.strip()}"
                
                with open(commit_msg_file, 'w', encoding='utf-8') as f:
                    f.write(wip_msg)
                print("[HOOK] Auto-generated WIP commit message")
        except Exception as e:
            print(f"[HOOK] Failed to generate WIP message: {e}")

if __name__ == "__main__":
    main()
```

### **방안 3: 기존 구조 개선 (최소 변경)**

현재 구조를 유지하면서 동기화 문제만 해결:

**수정된 파일**: `.githooks/pre-commit.ps1`
```powershell
#!/usr/bin/env pwsh
$commitMsgFile = Join-Path (git rev-parse --git-dir) "COMMIT_EDITMSG"

# 파일 존재 확인 및 생성
if (!(Test-Path $commitMsgFile)) {
    "" | Out-File $commitMsgFile -Encoding utf8 -NoNewline
}

$currentMsg = (Get-Content $commitMsgFile -Raw -ErrorAction SilentlyContinue) -replace "`r`n", "`n"

if ([string]::IsNullOrWhiteSpace($currentMsg)) {
    $stats = git diff --cached --shortstat 2>$null
    if ($stats) {
        $newMessage = "WIP: $(Get-Date -Format 'yyyy-MM-dd HH:mm')`n`n$stats"
        
        # 파일 쓰기를 여러 번 시도
        $attempts = 3
        for ($i = 0; $i -lt $attempts; $i++) {
            try {
                $newMessage | Out-File $commitMsgFile -Encoding utf8 -NoNewline -Force
                Start-Sleep -Milliseconds 200  # 지연 시간 증가
                
                # 쓰기 검증
                $written = Get-Content $commitMsgFile -Raw -ErrorAction SilentlyContinue
                if ($written -and $written.Contains("WIP:")) {
                    Write-Host "[HOOK] WIP message generated successfully"
                    break
                }
            } catch {
                Write-Warning "[HOOK] Attempt $($i+1) failed: $_"
                Start-Sleep -Milliseconds 100
            }
        }
    }
}
exit 0
```

## 🚀 즉시 실행 가능한 수정사항

**1단계**: 현재 훅을 비활성화하고 새로운 방식 테스트
```bash
# 기존 훅 백업
mv .githooks/pre-commit .githooks/pre-commit.backup
mv .githooks/pre-commit.ps1 .githooks/pre-commit.ps1.backup
```

**2단계**: 방안 1 또는 2 중 선택하여 구현

**3단계**: 훅 권한 설정
```bash
git config core.hooksPath .githooks
chmod +x .githooks/prepare-commit-msg
```

**4단계**: 테스트
```bash
echo "test" > test.txt
git add test.txt
git commit -m ""  # 또는 그냥 git commit
```

## 🔧 추가 디버깅 방법

문제가 지속될 경우:
```bash
# Git 훅 실행 과정 추적
GIT_TRACE=1 git commit -m ""
```

어떤 방안을 선택하시겠습니까? 가장 안정적인 **방안 1 (prepare-commit-msg 훅)**을 권장드립니다.
