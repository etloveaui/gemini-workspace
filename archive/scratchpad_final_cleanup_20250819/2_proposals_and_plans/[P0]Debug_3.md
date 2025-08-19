# 🚨 Git 훅 WIP 메시지 생성 문제 - 종합 분석 및 해결 방안

## 📋 문제 상황 요약

**목표**: `git commit` 실행 시 자동으로 "WIP: [날짜] [변경 통계]" 메시지 생성
**현재 상태**: PowerShell → Python 기반으로 전환했지만 여전히 실패
**핵심 증상**: 
- `git commit` 무한 대기 또는 "Aborting commit due to empty commit message" 오류
- 훅이 실행되지만 COMMIT_EDITMSG 파일 수정이 Git에 반영되지 않음

## 🔍 문제 원인 분석

### **1. Windows 환경 특성으로 인한 문제**
- **파일 시스템 동기화 지연**: Windows에서 Python이 파일을 쓴 후 Git이 즉시 읽지 못하는 타이밍 이슈
- **프로세스 간 통신 문제**: Bash → Python → Git 간의 복잡한 실행 체인에서 발생하는 동기화 문제
- **표준 스트림 리디렉션**: Python의 `print()` 출력이 Git의 커밋 프로세스를 방해할 가능성

### **2. Git 훅 실행 방식의 제약**
- **비대화형 모드**: `git commit -m ""`에서 Git이 훅 완료를 기다리지 않고 처리
- **COMMIT_EDITMSG 읽기 타이밍**: 훅이 파일을 수정하기 전에 Git이 이미 내용을 읽어버림
- **Windows Git for Windows 특성**: POSIX 에뮬레이션 레이어와 네이티브 Windows 환경 간의 호환성 문제

## 💡 단계별 해결 방안

### **방안 1: Python 스크립트 최적화 (즉시 시도 가능)**

현재 Python 스크립트의 문제점을 해결:

```python
#!/usr/bin/env python3
import sys
import os
import subprocess
import time
from datetime import datetime

def main():
    if len(sys.argv)  2 else ""
    
    # 조건부 조기 종료 (출력 최소화)
    if commit_source in ['message', 'template', 'merge', 'squash']:
        sys.exit(0)
    
    # 파일 읽기 (더 안전한 방식)
    current_msg = ""
    try:
        if os.path.exists(commit_msg_filepath):
            with open(commit_msg_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                current_msg = f.read()
    except:
        pass
    
    # 빈 메시지일 때만 처리
    if not current_msg.strip():
        try:
            # Git diff 실행
            result = subprocess.run(
                ['git', 'diff', '--cached', '--shortstat'],
                capture_output=True, text=True, cwd=os.getcwd()
            )
            
            if result.returncode == 0 and result.stdout.strip():
                wip_msg = f"WIP: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{result.stdout.strip()}"
                
                # 파일 쓰기 (여러 번 시도 + 동기화)
                for attempt in range(3):
                    try:
                        with open(commit_msg_filepath, 'w', encoding='utf-8') as f:
                            f.write(wip_msg)
                        # 강제 동기화
                        os.fsync(f.fileno()) if hasattr(os, 'fsync') else None
                        time.sleep(0.1)  # Windows 파일시스템 지연 대응
                        
                        # 검증
                        with open(commit_msg_filepath, 'r', encoding='utf-8') as f:
                            written = f.read()
                        if "WIP:" in written:
                            break
                    except:
                        time.sleep(0.1)
                        
        except:
            pass  # 오류 시 조용히 실패
    
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### **방안 2: Git Alias 기반 우회 (권장)**

Git 훅 대신 사용자 정의 명령어 생성:

```bash
# .gitconfig에 추가
[alias]
    wip = "!f() { \
        if [ -z \"$(git diff --cached --name-only)\" ]; then \
            echo 'No staged changes for WIP commit'; \
            return 1; \
        fi; \
        STATS=$(git diff --cached --shortstat); \
        git commit -m \"WIP: $(date '+%Y-%m-%d %H:%M')\n\n$STATS\"; \
    }; f"
```

**사용법**: `git wip` 명령으로 자동 WIP 커밋

### **방안 3: PowerShell 통합 스크립트 (Windows 최적화)**

```powershell
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
```

**tasks.py에 통합**:
```python
@task
def wip(c, message=""):
    """WIP 커밋 생성"""
    run(f'powershell.exe -ExecutionPolicy Bypass -File .\\scripts\\git-wip.ps1 -Message "{message}"')
```

### **방안 4: commit-template 활용**

```bash
# .git/commit-template.txt 생성
WIP: TIMESTAMP_PLACEHOLDER

STATS_PLACEHOLDER

# Git 설정
git config commit.template .git/commit-template.txt
```

사전 처리 스크립트로 플레이스홀더를 실제 값으로 치환

## 🎯 즉시 실행 권장사항

### **1단계: Git Alias 방식 도입 (가장 안정적)**
```bash
git config --global alias.wip '!f() { STATS=$(git diff --cached --shortstat 2>/dev/null); if [ -n "$STATS" ]; then git commit -m "WIP: $(date "+%Y-%m-%d %H:%M")${STATS:+\n\n$STATS}"; else echo "No staged changes"; fi; }; f'
```

### **2단계: PowerShell 통합 스크립트 추가**
- `scripts/git-wip.ps1` 생성
- `tasks.py`에 `wip` 태스크 추가
- `invoke wip` 명령으로 사용

### **3단계: 기존 Git 훅 정리**
```bash
# 기존 훅 비활성화
mv .githooks/prepare-commit-msg .githooks/prepare-commit-msg.disabled
mv .githooks/prepare-commit-msg.py .githooks/prepare-commit-msg.py.disabled
```

## ⚠️ 디버깅을 위한 추가 확인사항

현재 상황을 정확히 파악하기 위해:

1. **COMMIT_EDITMSG 파일 상태 확인**:
   ```bash
   cat .git/COMMIT_EDITMSG
   ```

2. **Python 스크립트 직접 테스트**:
   ```bash
   python .githooks/prepare-commit-msg.py .git/COMMIT_EDITMSG
   ```

3. **Git 훅 실행 로그 확인**:
   ```bash
   GIT_TRACE=1 git commit 2>&1 | grep -i hook
   ```

## 🚀 결론 및 권장사항

**즉시 적용**: **Git Alias 방식(방안 2)**이 가장 안정적이고 Windows 환경에서 검증된 방법입니다.

**중장기적**: PowerShell 통합 스크립트를 통해 기존 워크플로우와 자연스럽게 통합하는 것을 권장합니다.

Git 훅은 Windows 환경에서 복잡한 호환성 이슈가 있으므로, 더 직관적이고 안정적인 사용자 정의 명령어 방식이 현재 상황에 가장 적합합니다.

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/cd2d9a94-694d-4245-8415-054312449d27/HUB.md
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/b4df6dbe-5941-47db-9e2a-0cb890225ef7/GEMINI.md
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/bb4e9591-25d0-40f8-9db6-31409203b7db/folder-structure.txt
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/29a1b4f2-4630-4f72-9860-9abeb3d91c96/file.gitignore
[5] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/de6f6208-9046-45eb-b9f8-29f2bbb03a42/Answer.md
[6] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/2e1e9a55-6ebb-4c3a-9627-8490ab372b6f/Claude-4.0-Sonnet-Thinking.md
[7] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/23ed0fe9-40f1-4fc9-9d67-a05b12099412/Gemini-2.5-Pro.md
[8] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/1161594d-8fd0-493c-8509-26c3cb647c92/Grok4.md
[9] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/17a0da9b-0e92-43e6-bddf-bcc21eec3cf5/Qwen3-Coder.md
[10] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/e6c87d27-4705-4a56-aeef-afd10cd06986/ChatGPT-4.1.md
[11] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/60bf4ca5-5926-41dd-a581-490dad05b67b/ChatGPT-O3.md
[12] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/715a7f99-d0d5-4ae2-a3e7-4c728ab22524/P0-Foundational-Enhancements.md
[13] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/af83805e-0f7a-43d8-b019-8cd45d531d71/file.gitignore
[14] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/ebeab35d-6c7d-488c-b71f-8272a37892d4/tasks.py
[15] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/7f96b0a2-f7ab-4cfa-a73a-fda33139d0fd/pre-commit
[16] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/89ed280a-8d53-42bc-9483-fae40ac98466/pre-commit.ps1
[17] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/a746ebf5-8c52-4877-af52-f7153fc700d4/COMMIT_EDITMSG
[18] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/6f5a54cc-6f3b-485e-87c3-bc4a32796dd8/file.gitignore
[19] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/b8ff9141-debf-49f7-9973-aff3ac623f1f/tasks.py
[20] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/ad335ce0-7413-4d0f-80c8-082fdc65f1bb/prepare-commit-msg
[21] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/2a68d084-d1ae-4dc9-b240-892eb4ea0a63/prepare-commit-msg.ps1
[22] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58009115/0d1ecfdf-3781-4476-a4f0-1df0b8c0187a/COMMIT_EDITMSG