@echo off
chcp 65001 > nul
title 완전 자동화 시스템 시작

echo ================================
echo 🚀 멀티 에이전트 워크스페이스
echo    완전 자동화 시스템 시작
echo ================================
echo.

echo 📋 시스템 초기화 중...
python scripts\session_startup.py

echo.
echo 🔍 초기 상태 체크 중...
python scripts\token_usage_report.py --update-hub

echo.
echo 🤖 MCP 시스템 확인 중...
python scripts\claude_mcp_final.py

echo.
echo ⚡ 자동 스케줄러 시작...
echo    - 토큰 모니터링: 매 15분
echo    - 세션 자동화: 매 시간  
echo    - 일일 보고서: 매일 18:00
echo    - 헬스 체크: 매 30분
echo.
echo 백그라운드에서 실행됩니다. 종료하려면 Ctrl+C를 누르세요.
echo.

python scripts\auto_system_scheduler.py --background

pause