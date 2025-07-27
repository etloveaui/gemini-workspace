# P0_DEFINITION_OF_DONE.md

## P0 단계 완료 조건 체크리스트

다음 모든 항목이 완료되고 검증되었을 때, P0 단계는 완료된 것으로 간주합니다.

1.  **커밋 프로토콜 정합성 확보:**
    *   `tasks.py`의 `wip` 태스크가 `GEMINI.md`에 명시된 `git commit -F <임시파일>` 방식을 정확히 사용함을 검증.
    *   `scripts/git-wip.ps1` 또한 동일한 프로토콜을 따름을 검증.

2.  **`__lastSession__` 처리 루틴 검증:**
    *   `scripts/hub_manager.py`의 `strip_last_session_block` 함수가 `HUB.md` 내의 모든 `__lastSession__` 블록을 정확하고 안전하게 제거함을 검증.
    *   `invoke end` 실행 시 `__lastSession__` 블록이 올바르게 생성되고, `invoke start` 실행 시 해당 블록이 정확히 제거됨을 검증.

3.  **`runner.py` 인코딩 문제 해결:**
    *   `runner.py`의 `subprocess.run` 호출 시 `encoding='utf-8'` 및 `errors='replace'` 옵션이 적용되었음을 검증.

4.  **`usage.db` 파일 잠금 문제 해결:**
    *   테스트 환경에서 `usage.db` 파일에 대한 `PermissionError`가 발생하지 않음을 검증.
    *   `test_env` 픽스처의 `setup` 및 `teardown` 로직이 `usage.db` 파일을 안전하게 처리함을 검증.

5.  **자율 테스트 하네스 구축 및 통과:**
    *   `/tests/test_p0_rules.py` 파일이 존재하며, 위에 명시된 핵심 규칙들을 검증하는 `pytest` 테스트 케이스가 포함되어 있음을 검증.
    *   `invoke test` 실행 시 모든 테스트(비활성화된 테스트 제외)가 성공적으로 통과함을 검증.
