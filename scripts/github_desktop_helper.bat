@echo off
chcp 65001 > nul
echo GitHub Desktop 커밋 도우미
echo ========================

REM UTF-8 환경 설정
set PYTHONIOENCODING=utf-8

REM 작업 디렉토리로 이동
cd /d "%~dp0\.."

REM Git 상태 확인
echo [상태 확인]
git status

echo.
echo [설정 확인]
git config --list | findstr encoding
git config --list | findstr autocrlf

echo.
echo 이제 GitHub Desktop에서 커밋을 진행할 수 있습니다.
echo 만약 여전히 문제가 있다면 관리자 권한으로 실행하세요.

pause
