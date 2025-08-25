# 2025-08-25 공통 로깅 훅 확장 상태 보고

- 상태: Phase 2 최소 확장 완료 (신속 처리)
- 범위:
  - claude_integration.py, session_startup_enhanced.py (기 반영)
  - 추가 주입: realtime_agent_sync.py, onboarding.py, agent_task_dispatcher.py, auto_monitoring_system.py
- 집계/허브: token_usage_report.py 재실행, HUB P1-TOKEN 마커 자동 갱신 확인
- 보류: Gemini/Codex 추가 런처 세부 경로 검토 및 주입(후속)

- 비고: projects/ 독립성 준수, UTF-8, 실패내성 설계
