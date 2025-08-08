# [P1-2] File System Agent Framework Upgrade - 작업 로그

**시작일:** 2025-08-07

## 최종 통합 실행 계획

*세 개의 핵심 자료(작업 지시서 2개, 분석 보고서 1개)의 아이디어를 종합하여, 다음과 같은 최종 실행 계획을 수립하고 이에 따라 작업을 진행한다.*

### Phase 1: 프레임워크 기반 구축 (Foundation)

1.  **디렉터리 구조 생성:** `scripts/agents/rules` 및 `scripts/utils` 디렉터리를 생성한다.
2.  **`RuleBase` 클래스 설계 (`scripts/agents/rules/base.py`):**
    -   `name`, `summary`, `params`, `idempotent` 등 풍부한 메타데이터를 포함하는 추상 클래스를 정의한다.
    -   `__init_subclass__`를 사용하여 규칙 클래스를 **자동으로 등록**하는 메커니즘을 구현한다.
3.  **규칙 로더 구현 (`scripts/agents/rules/__init__.py`):**
    -   `pkgutil`을 사용하여 `rules` 디렉터리 내의 모든 규칙 모듈을 동적으로 임포트하는 `load_rules()` 함수를 구현한다.

### Phase 2: 메인 엔진 및 안전장치 리팩토링 (Engine & Safety)

1.  **`file_agent.py` 리팩토링:**
    -   기존의 `if/else` 분기문을 제거하고, `load_rules()`와 `get_rule()`을 통해 **동적으로 규칙을 실행**하도록 수정한다.
    -   **보안 강화:** `Path.resolve()`와 `is_relative_to()`를 사용하여, 수정 대상 파일이 **프로젝트 경계를 벗어날 수 없도록 원천적으로 차단**하는 로직을 최우선으로 추가한다.
    -   **Undo 기능:** 실제 파일을 수정하기 전에, 원본 내용을 `.bak` 파일로 백업하는 기능을 추가한다.
    -   **UX 기능 추가:** `--list`와 `--explain` 옵션을 구현하여 사용자가 규칙을 쉽게 탐색할 수 있도록 한다.
2.  **규칙 모듈화:**
    -   기존 `add_docstrings` 로직을 `RuleBase`를 상속받는 `scripts/agents/rules/add_docstrings.py` 모듈로 분리한다.

### Phase 3: 테스트 하네스 및 CI 연동 (Testing & CI)

1.  **`tasks.py` 업데이트:** `invoke refactor`가 새로운 플래그들(`--list`, `--explain`, `--yes` 등)을 모두 처리할 수 있도록 수정한다.
2.  **테스트 스위트 구축 (`tests/test_p1_file_agent.py`):**
    -   Dry-run, Apply, **경계 위반 시도**, **멱등성**, 미지 규칙 요청 등 "제미나이 CLI 작업 지시서"에 명시된 모든 시나리오를 검증하는 `pytest` 테스트를 작성한다.

### Phase 4: 문서화 및 UX 개선 (Docs & UX)

1.  **`docs/HELP.md` 업데이트:** 새로운 프레임워크의 상세한 사용법과 **"신규 리팩토링 규칙 추가 가이드"**를 포함하여 문서를 최신화한다.
2.  **컬러 Diff 적용:** `rich` 라이브러리를 사용하여 `dry-run` 시 출력되는 `diff` 결과에 색상을 입혀 가독성을 극대화한다.

---
