# Gemini CLI 환경 설정 안내 (집/직장 공통)

이 문서는 새로운 PC(집, 직장 등)에서 Gemini CLI 환경을 현재 워크스페이스에 맞게 설정하는 방법을 안내합니다.

## 설정 목표
- Gemini 관련 모든 설정 파일(`settings.json` 등)이 사용자 홈 폴더(`C:\Users\사용자이름`)가 아닌, 현재 워크스페이스 폴더(`gemini-workspace\.gemini`)에 저장되도록 합니다.
- 이를 통해 어떤 PC에서든 동일한 환경으로 Gemini를 사용할 수 있습니다.

## 설정 방법

1.  **PowerShell 또는 명령 프롬프트(cmd) 실행**
    - `Win + R` 키를 누르고 `powershell` 또는 `cmd`를 입력하여 터미널을 엽니다.

2.  **아래 명령어 복사 및 붙여넣기**
    - 아래 명령어를 그대로 복사하여 터미널에 붙여넣고 Enter 키를 누릅니다.
    - 이 명령어는 Gemini 설정 디렉터리를 현재 워크스페이스 폴더로 지정하는 환경 변수를 영구적으로 추가합니다.

    ```powershell
    setx GEMINI_CONFIG_DIR "%USERPROFILE%\gemini-workspace\.gemini"
    ```

3.  **터미널 재시작**
    - 설정이 완전히 적용되려면, 현재 열려있는 모든 터미널 창을 닫고 새로 열어야 합니다.

이제 모든 설정이 완료되었습니다. 앞으로 Gemini CLI는 이 워크스페이스를 기준으로 작동합니다.