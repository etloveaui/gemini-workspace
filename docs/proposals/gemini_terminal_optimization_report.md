# VSCode 터미널 환경 최적화 보고서

## 문제 원인 분석
### 1. 새 창 글씨 및 스크롤 문제의 근본 원인
- **주요 원인**: 현재 Gemini CLI가 실행되는 환경은 표준 대화형 터미널이 아닌 것으로 보입니다. `[Console]` 속성 접근 시 발생하는 `The handle is invalid` 오류는 현재 프로세스가 콘솔에 연결되어 있지 않음을 나타냅니다. 이는 터미널의 렌더링 및 버퍼 관리에 심각한 문제를 일으키며, 글씨가 보이지 않거나 스크롤이 동작하지 않는 현상의 직접적인 원인으로 추정됩니다.
- **PowerShell 버전 불일치**: Claude의 요청서는 PowerShell 7 환경을 전제로 하고 있으나, 실제 시스템은 **Windows PowerShell 5.1**을 사용하고 있습니다. 이는 기능 및 설정의 차이로 인해 예기치 않은 문제를 유발할 수 있습니다.

## 해결 방안
### 즉시 적용 가능한 해결책
1.  **PowerShell 7 설치**: 보다 안정적이고 기능이 풍부한 터미널 환경을 위해 PowerShell 7을 설치해야 합니다.
    ```powershell
    winget install --id Microsoft.PowerShell --source winget
    ```
2.  **VSCode 기본 터미널 설정**: VSCode가 PowerShell 7을 기본 터미널로 사용하도록 `settings.json` 파일을 수정해야 합니다.

### 환경 통합 방안
1.  **VSCode `settings.json` 표준 템플릿**: 모든 환경에서 일관된 터미널 경험을 위해 다음 설정을 VSCode에 적용하세요. 이 설정은 기본 터미널을 PowerShell 7로 지정하고, 스크롤백 버퍼 크기를 늘리며, UTF-8 인코딩을 명시적으로 설정합니다.
    ```json
    {
      "terminal.integrated.defaultProfile.windows": "PowerShell",
      "terminal.integrated.profiles.windows": {
        "PowerShell": {
          "source": "PowerShell",
          "path": "C:\\Program Files\\PowerShell\\7\\pwsh.exe",
          "icon": "terminal-powershell"
        }
      },
      "terminal.integrated.scrollback": 10000,
      "terminal.integrated.fontFamily": "D2Coding, Consolas, 'Courier New', monospace",
      "files.encoding": "utf8",
      "files.autoGuessEncoding": true
    }
    ```
2.  **PowerShell 프로필 설정**: `$PROFILE` 파일을 편집하여 모든 PowerShell 세션에서 일관된 인코딩을 유지하도록 설정합니다.
    ```powershell
    if ($PROFILE -eq $null) {
      New-Item -Path $PROFILE -ItemType File -Force
    }
    Add-Content -Path $PROFILE -Value '$OutputEncoding = [System.Text.Encoding]::UTF8'
    ```

## 다음 단계
1.  위에 제시된 `winget` 명령어를 사용하여 PowerShell 7을 설치하세요.
2.  VSCode의 `settings.json` 파일을 열어 위의 JSON 설정을 붙여넣으세요. (`F1` 키 > `Open User Settings (JSON)`)
3.  PowerShell을 열고 위의 프로필 설정 명령어를 실행하세요.
4.  VSCode를 다시 시작하여 모든 설정이 올바르게 적용되었는지 확인하세요.
