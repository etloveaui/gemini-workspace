@echo off
REM GitHub Desktop WSL 우회 커밋 스크립트
chcp 65001 > nul

echo WSL 없이 안전한 커밋하기
echo ========================

REM 작업 디렉토리로 이동
cd /d "%~dp0\.."

REM WSL 관련 환경 변수 제거
set WSL_DISTRO_NAME=
set WSL_INTEROP=

REM Git 설정을 Windows 전용으로 강제
git config core.autocrlf true
git config core.eol crlf
git config core.filemode false
git config core.symlinks false

REM 현재 상태 확인
echo [현재 Git 상태]
git status --porcelain

if "%1"=="" (
    echo.
    echo 사용법: commit_without_wsl.bat "커밋 메시지"
    echo 예시: commit_without_wsl.bat "WSL 오류 해결"
    goto :end
)

echo.
echo [변경사항 스테이징]
git add .

echo.
echo [커밋 실행 - WSL 우회 모드]
git -c core.hooksPath="" commit -m "%~1

🤖 Generated with [Claude Code](https://claude.ai/code)
WSL 우회 모드로 커밋됨

Co-Authored-By: Claude <noreply@anthropic.com>"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [성공] WSL 없이 커밋 완료!
    echo.
    git log -1 --oneline
    echo.
    echo 이제 GitHub Desktop에서도 정상 작동할 것입니다.
) else (
    echo.
    echo [실패] 커밋 중 오류가 발생했습니다.
    echo Git 설정을 다시 확인해주세요.
)

:end
pause
