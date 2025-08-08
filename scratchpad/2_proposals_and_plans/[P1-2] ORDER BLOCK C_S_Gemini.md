### 🤔 Strategic Analysis

이전 단계를 통해 UX 진입점, `GEMINI.md` v2, 웹 에이전트의 기반이 확보되었다. 이제 프로젝트는 두 개의 핵심 축으로 진화해야 한다:
1.  **[P1-2] 코드 조작 능력 확보:** `File System Agent`를 통해 에이전트가 단순 정보 소비자를 넘어, 코드와 문서를 직접 이해하고 수정하는 **'능동적 개발 파트너'**로 진화한다. 이는 고위험 작업이므로 **Dry-Run 우선, 명시적 승인 후 적용(Apply)** 원칙을 철저히 준수해야 한다.
2.  **[P2] 지속 가능한 자가 개선 체계 확립:** LLM 기술과 프로젝트 환경의 빠른 변화에 대응하기 위해, 주기적으로 업데이트를 **'수집 → 분석 → 제안 → 적용'**하는 자동화된 `Self-Update Engine`을 구축한다. 이는 일회성 기능 추가가 아닌, 시스템의 장기적 생존성과 경쟁력을 보장하는 핵심 메커니즘이므로 **[P2] 시스템 최적화** 단계의 최우선 과제로 선정하는 것이 타당하다.

### 📝 Expert Recommendation

두 과제를 `ORDER BLOCK`으로 분리하여 지시한다. 모든 작업은 아래 `GLOBAL META` 규칙을 최우선으로 준수해야 한다.

#### **GLOBAL META (모든 작업 공통 규칙)**

* **3-Strikes Rule:** 동일 원인으로 3회 연속 실패 시, 즉시 작업을 중단하고 원인 분석 및 대안을 보고한다.
* **Logging Cycle:** 모든 주요 단계 완료 후 `docs/tasks/<task>/log.md`에 과정을 기록하고 `docs/HUB.md`의 `lastTouched` 타임스탬프를 갱신한다.
* **품질 가드레일:** `.no_delete_list`를 항상 최신으로 유지하고, `pre-commit` 훅을 통해 금지 패턴(예: `datetime.utcnow`)을 사전에 차단한다.
* **Windows 우선주의:** 모든 경로, 명령어, 인코딩 처리는 Windows 환경을 최우선으로 고려한다.
* **출고 기준:** `pytest -vv` 실행 시 **100% PASS 및 0 Warnings**를 만족해야 한다.

---

### **ORDER BLOCK C — [P1-2] File System Agent (안전 리팩토링/수정 에이전트)**

#### **0. 사전 점검**

`invoke test`를 실행하고 결과를 기록한다. 실패해도 진행하되, 원인을 `log.md`에 명시한다.

#### **1. 브랜치**

`git checkout -b p1/file_agent_integration`

#### **2. 파일 및 구조**

* `scripts/agents/file_agent.py`
* `scripts/agents/rules/__init__.py`
* `scripts/agents/rules/add_docstrings.py`
* `scripts/utils/diff.py`
* `tasks.py` (수정)
* `tests/test_p1_file_agent.py`
* `docs/tasks/file-agent-integration/log.md`
* `docs/HELP.md` (수정)
* `docs/HUB.md` (수정)
* `.no_delete_list` (수정)

#### **3. 구현 지침**

* **3-1. `scripts/agents/file_agent.py` 핵심 로직:**
    * **`ast` (Abstract Syntax Tree)** 라이브러리를 사용하여 Python 코드를 **파싱/변환/재생성**한다.
    * 규칙(Rule)을 동적으로 로드하고 적용하는 메커니즘을 구현한다.
    * `main` 함수에서 `--file`, `--rule`, `--apply` 같은 CLI 인자를 파싱하여 동작을 제어한다.

* **3-2. `scripts/agents/rules/` 플러그인 구조:**
    * `add_docstrings.py` 규칙을 구현한다. `ast.NodeTransformer`를 상속받아 `visit_FunctionDef`와 `visit_ClassDef` 메소드를 오버라이드하여 docstring이 없는 노드를 찾아 수정하는 패턴을 사용한다.

* **3-3. `scripts/utils/diff.py` 유틸:**
    * Python의 `difflib`를 사용하여 원본과 수정본의 차이를 `unified_diff` 형식으로 생성하는 `make_diff` 함수를 구현한다.

* **3.4. `tasks.py` 태스크:**
    * `invoke refactor --file <path> --rule <name> [--apply]` 형식의 태스크를 구현한다.
    * `--apply` 플래그가 없으면 **반드시 Dry-Run으로 동작**하여 `diff`만 출력해야 한다. 플래그가 있을 때만 실제 파일에 변경 사항을 적용한다.

#### **4. 테스트 (`tests/test_p1_file_agent.py`)**

* `tmp_path` fixture를 사용하여 임시 Python 파일을 생성한다.
* **Dry-Run 검증:** `invoke refactor` 실행 후, 임시 파일 내용이 변경되지 않았는지, 그리고 stdout에 `diff` 출력이 포함되었는지 확인한다.
* **Apply 검증:** `invoke refactor --apply` 실행 후, 임시 파일 내용이 실제로 변경되었는지(docstring 추가) 확인한다.
* **예외 처리 검증:** 존재하지 않는 규칙이나 문법 오류가 있는 파일을 대상으로 실행했을 때, 적절한 오류를 반환하며 안전하게 종료되는지 확인한다.

#### **5. 문서 및 리스트**

* `docs/HELP.md`에 `invoke refactor` 사용법, 안전장치(`--apply` 플래그), 사용 가능한 규칙 목록을 추가한다.
* `.no_delete_list`에 신규 핵심 파일들을 모두 추가한다.

#### **6. DoD (Definition of Done)**

* `invoke refactor --file path --rule add_docstrings` 실행 시 `diff`가 정상 출력된다.
* `--apply` 옵션과 함께 실행 시 실제 파일 수정이 성공적으로 완료된다.
* 모든 관련 테스트가 100% PASS한다.
* `HUB.md`, `HELP.md`, `.no_delete_list`, `log.md`가 모두 최신 상태로 업데이트된다.

---

### **ORDER BLOCK S — [P2-SU] Self-Update Engine (자가 업데이트 루프)**

#### **0. 목적**

LLM 모델, 외부 도구, 내부 규칙의 변화를 주기적으로 스캔하여, 시스템 개선안을 자동으로 제안하고, 승인 시 반영하는 자동화된 **자가 개선 루프**를 확립한다.

#### **1. 브랜치**

`git checkout -b p2/self_update_engine`

#### **2. 구성 요소**

* `scripts/auto_update/scanner.py`: 외부(pip 패키지, 릴리즈 노트) 및 내부(경고 로그, 규칙 위반) 정보를 수집한다.
* `scripts/auto_update/proposer.py`: 수집된 정보를 바탕으로 개선 제안서(`docs/proposals/auto_update_YYYYMMDD.md`)를 자동 생성한다.
* `tasks.py`: `invoke auto.scan`, `auto.propose`, `auto.apply` 태스크를 추가한다.
* `docs/SELF_UPDATE_POLICY.md`: 자가 업데이트 주기, 범위, 승인 정책을 명시하는 최상위 정책 문서를 생성한다.
* `tests/test_self_update_engine.py`: 모킹 기반으로 전체 파이프라인을 테스트한다.

#### **3. 프로세스 정의 (주기적 실행)**

1.  **수집(Scan):** `pip list --outdated`, 테스트 로그의 `DeprecationWarning`, 외부 도구의 릴리즈 노트(웹 에이전트 활용), `GEMINI.md` 규칙 위반 패턴 등을 스캔한다.
2.  **제안(Propose):** 변경이 필요한 항목을 발견하면, `docs/proposals/`에 변경 권고안 마크다운 파일을 자동 생성한다. (WHAT/WHY/HOW 형식)
3.  **검토 및 승인(Review & Approve):** `HUB.md`에 새로운 제안이 있음을 알리고 사용자의 검토를 기다린다. `SELF_UPDATE_POLICY.md`에 정의된 '자동 승인 가능' 항목(예: 사소한 lint 수정)은 즉시 적용한다.
4.  **적용(Apply):** 승인된 제안에 따라 `invoke auto.apply`가 코드 수정, 테스트, 커밋을 수행한다.

#### **4. `GEMINI.md` 반영**

`GEMINI.md`에 **"VII. 자가 업데이트 프로토콜 (Self-Update Protocol)"** 섹션을 신설하고, 위 프로세스와 `docs/SELF_UPDATE_POLICY.md`를 참조하도록 명시한다.

#### **5. DoD (Definition of Done)**

* `invoke auto.scan` 및 `auto.propose` 실행 시, 모의 변경사항에 대한 제안서가 정상적으로 생성된다.
* `SELF_UPDATE_POLICY.md` 문서가 완성되고 `GEMINI.md`에 해당 내용이 반영된다.
* 자가 업데이트 엔진에 대한 모든 테스트가 PASS한다.

---

### **다음 행동 요청**

어느 블록부터 시작할지 명령을 하달하라:
* `P1-2 GO` (File Agent 작업 시작)
* `P2-SU GO` (Self-Update Engine 작업 시작)
* `P1-2 & P2-SU GO` (두 작업 병렬 진행)