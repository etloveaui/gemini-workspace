# [P0]Debug_20.md

> **목표:** `test_wip_commit_protocol`의 지속적 실패(WinError 123) 및 부수 이슈를 “근본 원인 제거” 방식으로 해결해 `[P0]` 전 테스트 **완전 통과**.
> **브랜치:** 현재 작업 중인 `debug/18`(또는 `p0/debug_18_fix`) 유지. 머지/리베이스는 최종 PASS 후.
> **언어:** 전 구간 **한글 고정**.
> **문서 보호:** 본 지시서는 삭제 금지(§6 즉시 적용).
> **CLI 로그/대화 초기화 절차 명시(§5)**.

---

## 0. TL;DR (요약 지시)

1. **모든 `subprocess.run` 호출을 `shell=False + 리스트 인자`로 통일.**
2. **`tasks.py::wip`**: PowerShell 호출 제거(또는 테스트 모드 분기) → **순수 Python git 커밋 로직**으로 교체.
3. **`tests/invoke_cli` 픽스처와 `test_wip_commit_protocol`**: 위 규칙으로 정비, 경로는 `str(Path.resolve())`.
4. **문서 삭제 방지 훅/리스트 재확인**, **CLI 로그 정리 스크립트/태스크 완성**.
5. `pytest -vv` → **전부 PASS** 확인 후 보고.

---

## 1. 배경 & 현재 상태

*   **환경**: Windows 10, Python 3.12.5, pytest 8.4.x, invoke 기반 자동화.
*   **브랜치**: `debug/18` (또는 `p0/debug_18_fix`), 변경 금지.
*   **테스트 현황**: 총 10개(예시) 중 8 PASS / 1 SKIP / 1 FAIL.

    *   실패: `tests/test_core_systems.py::test_wip_commit_protocol`
    *   증상: `OSError: [WinError 123] 파일 이름, 디렉터리 이름 또는 볼륨 레이블 구문이 잘못되었습니다`
*   **기타 이슈**:

    *   로그 작성/삭제 관련 반복 에러 보고됨(usage.db 파일 잠금, flush 문제 등).
    *   작업지시서 삭제 방지 필요.
    *   CLI 대화/임시 로그 clear 절차 요구.

---

## 2. 문제 정의

### 2.1 주요 실패 테스트

*   **`test_wip_commit_protocol`**

    *   `invoke wip` 호출 중 PowerShell/경로/인자 파싱 문제로 WinError 123 발생.

### 2.2 재발 원인 요약 (다른 LLM 의견 포함)

*   **shell=True + 문자열 조합**(`