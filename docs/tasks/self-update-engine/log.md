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