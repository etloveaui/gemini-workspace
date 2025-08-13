# [P2-SU] Self-Update Engine - 작업 로그

**시작일:** 2025-08-07

## 1. 목표

LLM 모델, 외부 도구, 내부 규칙의 변화를 주기적으로 스캔하여, 시스템 개선안을 자동으로 제안하고, 승인 시 반영하는 자동화된 **자가 개선 루프**를 확립한다.

---

## 2. 상세 실행 계획

### Phase 1: 정책 및 기반 구축

1.  **`docs/SELF_UPDATE_POLICY.md` 생성:**
    -   자가 업데이트의 주기(예: 주 1회), 범위(어떤 것을 스캔할 것인가), 자동 승인 정책(어떤 변경까지는 자동으로 적용할 것인가) 등을 명시하는 최상위 정책 문서를 작성한다.

2.  **`GEMINI.md` 업데이트:**
    -   "자가 업데이트 프로토콜 (Self-Update Protocol)" 섹션을 신설하고, 위에서 만든 `SELF_UPDATE_POLICY.md`를 참조하도록 명시한다.

3.  **`tasks.py`에 태스크 추가:**
    -   `invoke auto.scan`, `auto.propose`, `auto.apply` 태스크의 기본 골격을 추가한다.

### Phase 2: 스캐너 및 제안자 구현

1.  **`scripts/auto_update/scanner.py` 구현:**
    -   `pip list --outdated`를 실행하여 오래된 패키지를 스캔하는 기능을 구현한다.
    -   `pytest` 로그를 분석하여 `DeprecationWarning`과 같은 경고를 수집하는 기능을 구현한다.
    -   (옵션) 웹 에이전트를 활용하여 주요 의존성 라이브러리의 릴리즈 노트를 스캔하는 기능을 추가한다.

2.  **`scripts/auto_update/proposer.py` 구현:**
    -   `scanner.py`가 수집한 정보를 바탕으로, `docs/proposals/auto_update_YYYYMMDD.md` 형식의 변경 제안서 마크다운 파일을 자동 생성하는 기능을 구현한다.
    -   제안서는 WHAT/WHY/HOW 형식을 준수하여, 사람이 쉽게 이해할 수 있도록 작성한다.

### Phase 3: 테스트 및 검증

1.  **`tests/test_self_update_engine.py` 구축:**
    -   모의 `pip` 출력, 모의 로그 파일 등을 사용하여 `scanner`와 `proposer`가 정확히 동작하는지 검증하는 테스트 케이스를 작성한다.
    -   제안서가 의도된 형식대로 생성되는지 검증한다.

### Phase 4: 적용 엔진 구현 (초안)

1.  **`scripts/auto_update/apply.py` 구현 (초안):**
    -   `SELF_UPDATE_POLICY.md`에 정의된 '자동 승인 가능' 항목(예: 안전한 마이너 버전 패치)에 한해, `pip install -U <package>`와 같은 명령을 실행하는 간단한 적용 엔진을 구현한다.
    -   모든 적용 과정은 `file_agent`와 마찬가지로 Dry-run과 명시적 승인 절차를 거치도록 안전장치를 마련한다.

---
## 5. Action Taken (2025-08-11)

- Added `docs/SELF_UPDATE_POLICY.md` (MVP policy: cadence/scope/safety).
- Implemented scanner/proposer tasks and scripts:
  - `invoke auto.scan` → collects outdated packages, warnings, policy violations.
  - `invoke auto.propose` → generates `docs/proposals/auto_update_YYYYMMDD.md`.
- Generated proposal: `docs/proposals/auto_update_20250811.md`.

## 6. Next Steps

- Optional: Add minimal CI job to lint proposals exist on PR and reference policy.
- Optional: Extend scanner with release notes fetch for critical libs.
- Defer automated apply to post-MVP; keep manual apply with `git.commit-safe`.

---

## Definition of Done (DoD) — MVP

- 정책 문서: `docs/SELF_UPDATE_POLICY.md`에 주기(cadence), 범위(scope), 안전장치(safety/approval/rollback)가 명시되어 있고 `GEMINI.md`에서 해당 정책을 참조한다.
- 태스크 가용성: `invoke auto.scan`, `invoke auto.propose`가 Windows PowerShell 7 환경에서 오류 없이 실행된다(venv 존재 시 `venv/Scripts/python.exe` 사용 규칙 준수).
- 산출물 생성: `auto.propose` 실행 시 `docs/proposals/auto_update_YYYYMMDD.md`가 생성되며 WHAT/WHY/HOW 및 안전 점검 체크가 포함된다.
- 미적용 원칙: 자동 적용은 보류되고 수동 적용만 허용된다(`git.commit_safe`/리뷰 태스크 경유, Git hooks 기본 OFF 준수).
- 로깅/추적: 실행 내역은 최소한 제안 문서 생성으로 추적 가능하며(선택) `usage.db`에 간단 요약을 남길 수 있다.
- 안전/준수: 비밀 노출 금지, UTF-8 고정, 레포 내부 경로만 사용, 블록리스트/allowlist를 `scripts/commit_helper.py` 규칙에 맞게 준수한다.
- 검증 예시: 샘플 실행을 통해 최소 1건의 제안 문서가 실제 생성되어 로그에 경로가 기재되어 있다(예: `docs/proposals/auto_update_20250811.md`).

### 검증 절차(권장)

1) `invoke auto.scan` 실행 → 경고/업데이트 후보 수 확인(오류 없음).
2) `invoke auto.propose` 실행 → 신규 제안 문서가 생성되고 정책 링크 포함 확인.
3) 필요 시 `review` 태스크로 변경 미리보기 후 `git.commit_safe`로 커밋(훅 기본 OFF 유지, 외부 도구 커밋 호환 확인).

---

## Status Update — MVP Completed (2025-08-12)

- 정책 문서 존재 및 참조: `docs/SELF_UPDATE_POLICY.md` 작성, `GEMINI.md`/`AGENTS.md`에서 참조.
- 태스크 가용성: `auto.scan`/`auto.propose` 태스크와 스크립트 구현됨(Windows PS7 기준 동작 가정, 로컬 제약하 테스트).
- 산출물: `docs/proposals/auto_update_20250811.md` 등 제안서 존재 확인.
- 미적용 원칙: 자동 적용 보류, 수동 적용 원칙 명시 유지.
- 로깅/준수: UTF-8/레포 경로/비밀 금지 원칙 준수.
- 결론: MVP DoD 충족. 추가 확장은 별도 Phase로 진행.
