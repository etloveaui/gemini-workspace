@echo off
chcp 65001 > nul
echo 빠른 커밋 스크립트
echo =================

REM 작업 디렉토리로 이동
cd /d "%~dp0\.."

REM 훅 비활성화
set AGENTS_SKIP_HOOKS=1

REM Git 상태 확인
echo [현재 상태]
git status --porcelain

echo.
if "%1"=="" (
    echo 사용법: quick_commit.bat "커밋 메시지"
    echo 예시: quick_commit.bat "문서 업데이트"
    goto :end
)

REM 모든 변경 사항 스테이지
echo [스테이징]
git add .

REM 커밋 수행
echo [커밋]
git commit -m "%~1

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

REM 결과 확인
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [성공] 커밋이 완료되었습니다!
    echo.
    git log -1 --oneline
) else (
    echo.
    echo [실패] 커밋 중 오류가 발생했습니다.
)

:end
pause
