# USAGE

## 워처 실행(백그라운드)
- PowerShell: `./scripts/start_watchers.ps1 -PromptFile "C:\\Users\\etlov\\multi-agent-workspace\\communication\\codex\\20250823_01_prompt.md" -Hidden`

## 데모 실행
- Windows: `./venv/Scripts/python.exe scripts/demo_task.py --message "hello" --repeat 2 --log-level DEBUG`

## 스모크 테스트
- Windows: `./venv/Scripts/python.exe scripts/smoke_test.py`

## 로그 위치
- 프롬프트 이벤트: `communication/codex/YYYYMMDD_prompt_events.log`
- 워처/모니터: `logs/*.out`, `logs/*.err`

## Git 커밋/푸시 (분할 커밋)
- PowerShell:
  - 커밋만(푸시 생략): `./scripts/commit_and_push.ps1 -NoPush`
  - 원격 지정 후 푸시: `./scripts/commit_and_push.ps1 -RemoteUrl "https://<your-remote>.git" -Branch main`
  - 드라이런: `./scripts/commit_and_push.ps1 -DryRun`

