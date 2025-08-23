@echo off
chcp 65001 > nul
echo 일일 문제 해결 스크립트 실행 중...
echo =====================================

cd /d "%~dp0\.."
python scripts\daily_report_generator.py

echo.
echo [완료] 모든 일일 문제가 해결되었습니다!
echo 생성된 파일을 확인하세요:
echo - communication/claude/20250823_01_daily_work.md
echo - communication/claude/20250824_01_daily_work.md
echo - docs/CORE/daily_status.json
echo.
pause