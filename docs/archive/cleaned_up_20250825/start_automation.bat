@echo off
echo 🤖 멀티 에이전트 자동화 시스템 시작
echo ===================================

echo 1) 자동 상태 업데이터 실행...
python scripts\auto_status_updater.py

echo.
echo 2) 성능 최적화 실행...
python scripts\performance_optimizer.py

echo.
echo 3) 시스템 대시보드 표시...
python scripts\dashboard.py

echo.
echo ✅ 자동화 시스템 준비 완료!
echo 이제 백그라운드에서 자동으로 관리됩니다.

pause