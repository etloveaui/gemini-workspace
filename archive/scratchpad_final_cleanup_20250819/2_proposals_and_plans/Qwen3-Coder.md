### **Gemini CLI 2.0: AI-native 자동화 워크스페이스 개선 지시서**

**TO:** Gemini (as the operational engine of the CLI system)
**FROM:** Master User
**DATE:** 2025-07-26
**SUBJECT:** 워크스페이스 운영 패러다임 전환: "순응형 조수"에서 "능동형 관리자"로의 진화 (v2.0)

**목표 (Objective):**
현행 `GEMINI.md` 규칙의 안정성과 체계성을 기반으로, 워크스페이스의 자동화, 관측성, 자가 교정 능력을 극대화한다. 사용자의 반복적인 개입을 최소화하고, Gemini가 워크스페이스의 상태를 능동적으로 분석 및 관리하여 생산성을 혁신적으로 끌어올리는 것을 목표로 한다.

**핵심 원칙의 전환 (Core Principle Shift):**
*   **From:** "사용자의 지시를 기다리고, 모든 단계를 확인받는다."
*   **To:** "선 조치, 후 보고. 규칙에 따라 자율적으로 실행하고, 사용자에게는 결과와 특이사항만 요약하여 보고한다. 사용자는 '거부(Veto)' 또는 '수정(Edit)' 권한만 행사한다."

---

#### **[A] 운영 자동화 및 관측성 강화 (Operational Automation & Observability)**

**지시:**

1.  **토큰/비용/레이트리밋 실시간 모니터링 및 알림:**
    *   **실행:** 모든 API 호출 후 응답 헤더에서 토큰 사용량, 예상 비용, 남은 한도를 자동 파싱하여 `logs/session_usage.json` 또는 SQLite DB (`logs/usage.db`)에 축적하라.
    *   **보고:** 세션 종료 시 또는 주기적으로 `HUB.md`에 "일/주/월 사용량 요약"을 자동 갱신하라.
    *   **알림:** 예산의 80% 초과 또는 일일/시간당 한도 임박 시, Slack, 이메일 또는 터미널 팝업을 통해 즉시 사용자에게 경고하라.

2.  **자동 로그 커밋 및 점검 Hook:**
    *   **실행:** 체크포인트 도달 시 또는 세션 종료 시, `docs/HUB.md` 및 `docs/tasks/[task_id]/log.md`의 변경사항을 자동으로 Git에 커밋하라. 커밋 메시지는 자동 생성하되, 의미 있는 형식 (예: `[Auto] Update HUB.md for Task XYZ checkpoint`, `[Auto] Session end log for <session_id>`)을 따른다.
    *   **승인:** 사용자에게는 "수정필요시만 Edit" 승인을 요청하라. (기본 동작은 자동 커밋)

3.  **`.gitignore` 토글/복원 완전 자동화:**
    *   **실행:** 세션 시작 시 `/projects/` 라인을 자동으로 주석 해제하고, 세션 종료 시 자동으로 주석 처리하라. 이 작업은 PowerShell 또는 Python 스크립트를 통해 안정적으로 수행하라.
    *   **검증:** 작업 후 `.gitignore` 상태를 다시 확인하여 성공 여부를 검증하라.
    *   **예외:** 오류 발생 시에만 사용자에게 수동 알림을 제공하라.

4.  **Post-mortem 템플릿화 및 자동 생성:**
    *   **실행:** 치명적인 오류 또는 예외 발생 시, `docs/tasks/<task-id>/postmortem-YYYYMMDD.md` 파일을 자동 생성하라.
    *   **템플릿:** 파일에는 다음과 같은 섹션이 자동으로 포함되어야 한다: `# Post-mortem - YYYY-MM-DD`, `## Error Summary`, `## Stack Trace`, `## Git Diff (if applicable)`, `## Root Cause (User Input)`, `## Action Items (User Input)`.
    *   **안내:** 사용자에게 "오류 분석을 위해 `[파일 경로]`에 Post-mortem 파일을 생성했습니다. 관련 오류 로그나 상황 설명을 `[Root Cause]` 섹션에, 개선 방안은 `[Action Items]` 섹션에 입력해 주세요." 라고 명확히 안내하라.

---

#### **[B] 정책/문서/설정의 구조화 및 파싱 가능성 확보 (Structured & Parsable Configuration)**

**지시:**

1.  **`GEMINI.md` 및 설정의 YAML/JSON 스키마화:**
    *   **변환:** `GEMINI.md` 내의 핵심 설정 (예: 세션 관리, Git 연동, 민감 정보 정책, 로깅 사이클)과 `alias.json`을 `.gemini/settings.yaml` 또는 `.gemini/config.json` 과 같은 **파싱 가능한 구조화된 포맷**으로 분리/변환하라.
    *   **파싱:** 작업 시작 시, 반드시 이 설정 파일을 파싱하여 최신 규칙을 내부적으로 적용하라. (예: `alias.json`을 통해 `g start` -> `SOP-1` 매핑)
    *   **버전 관리:** 설정 파일의 스키마를 정의하고, 변경 시 `gemini-lint.yml` 워크플로우를 통해 자동 검증하라.

2.  **내부 상태의 명시적 관리:**
    *   **실행:** 현재 로깅 사이클 (`Standard`, `Detailed`, `Minimal`), 활성 작업 ID, 세션 ID 등의 상태를 내부 변수로 명시적으로 관리하라. (예: `current_logging_cycle`, `active_task_id`)

---

#### **[C] AI 기반 상태 감시 및 자가 동기화 (AI-based State Monitoring & Self-Synchronization)**

**지시:**

1.  **정책·문서·코드·로그 간 불일치 감시 (Drift Detection):**
    *   **실행:** 작업 시작 시/종료 전 또는 주기적으로, 다음 항목 간의 불일치를 자동 감지하라:
        *   `GEMINI.md`/`.gemini/settings.yaml`의 규칙 vs. 실제 실행된 워크플로우
        *   `HUB.md`의 작업 상태 vs. 실제 `docs/tasks/[task_id]/` 폴더 내 파일 상태
        *   `.gitignore` 설정 vs. `projects/` 폴더의 Git 추적 상태
        *   코드/문서 내용 vs. `log.md` 또는 `HUB.md`에 기록된 설명
        *   `secrets/` 폴더 외부에서 민감 정보가 사용/기록되는 경우
    *   **조치:** 불일치가 감지되면, 사용자에게 경고하고 자동 동기화 옵션을 제안하거나, 자동으로 수정을 시도하라. (예: "HUB.md의 작업 상태가 실제 폴더 구조와 다릅니다. 자동으로 업데이트할까요?")

2.  **메타러닝 및 자가 규칙 개선 루프 (Meta-Learning & Self-Improvement Loop):**
    *   **실행:** 동일한 목표를 향한 작업이 **반복적으로 실패 후 다른 접근으로 성공**하거나, **동일한 방식이 3회 이상 성공**하는 패턴을 자동으로 인식하라.
    *   **제안:** 이러한 패턴을 기반으로, `.gemini/settings.yaml`의 규칙을 명확화/강화하거나 새로운 규칙/워크플로우를 **자동으로 제안**하라. (예: "이전 3회 작업에서 Python 스크립트를 사용하여 삭제에 성공했습니다. `GEMINI.md`의 '파일 삭제 실패 대응' 규칙을 업데이트할까요? [Y/N/Edit]")
    *   **기록:** 제안된 개선사항은 `docs/tasks/<task-id>/postmortem-YYYYMMDD.md` 또는 별도의 `docs/meta_learning_proposals.md`에 기록하라.

---

#### **[D] 실행 환경 및 명령어의 완전 자동 감지 및 변환 (Full Auto Environment Detection & Command Translation)**

**지시:**

1.  **실행 환경 자동 탐지 및 적용:**
    *   **실행:** 세션 시작 시, **운영체제 (Windows/Linux/macOS), 경로 구분자, 환경 변수, 사용 가능한 도구 (PowerShell, Bash, Python 등)** 을 자동으로 탐지하고 내부 설정에 반영하라.
    *   **적용:** `GEMINI.md`에 명시된 "Windows 전용" 규칙을 인지하고, 해당 환경에서만 유효한 명령어를 사용하도록 하라.

2.  **명령어 자동 변환 및 호환성 보장:**
    *   **실행:** 특정 명령어 (예: `rm`, `cp`)가 현재 환경에서 사용 불가능할 경우, **자동으로 호환되는 명령어 (예: `del`, `copy` 또는 Python 스크립트)** 로 변환하여 실행하라.
    *   **우회:** 파일/폴더 접근 시 `.gitignore`로 인한 문제가 발생할 경우, `respect_git_ignore=False` 옵션을 자동으로 적용하거나, 우회 방법을 제안하라.

---

#### **[E] 비용 최적화 및 모델 스위칭 전략 (Cost Optimization & Model Switching Strategy)**

**지시:**

1.  **모델 효율적 활용:**
    *   **실행:** 반복적이고 단순한 작업 (예: 로그 요약, diff 분석)은 **Flash-Lite** 모델을 기본으로 사용하라.
    *   **전환:** 복잡한 코드 리팩토링, 창의적인 문제 해결 등 고성능이 필요한 작업만 **Pro** 모델을 조건부로 호출하라.
    *   **캐싱:** 반복되는 프롬프트나 컨텍스트는 캐시하여 재사용하라.

2.  **컨텍스트 최적화:**
    *   **실행:** 1백만 토큰의 대형 컨텍스트를 효율적으로 활용하기 위해, 핵심 정보만을 청크(chunk)로 분리하고, 필요 시 참조 링크를 활용하라. 불필요한 컨텍스트 쏠림을 방지하라.

---

#### **[F] 보안 및 민감 정보 관리 강화 (Enhanced Security & Sensitive Information Management)**

**지시:**

1.  **민감 정보 자동 스캐닝 및 차단:**
    *   **실행:** 작업 로그, 코드, 문서 등에 **민감 정보 (API 키, 비밀번호, 개인 식별 정보 등)가 포함될 가능성이 있는지 자동으로 스캔**하라.
    *   **조치:** 민감 정보가 발견되면, **즉시 경고**하고 **`secrets/` 폴더로 이동**하거나 **삭제**할 것을 제안하라. `secrets/` 폴더 외부에 민감 정보를 기록하려는 시도는 차단하라.

2.  **변경 로그 자동 Diff 및 위험 감지:**
    *   **실행:** Git 커밋 전이나 중요한 작업 후, **변경된 파일에 대한 `diff`를 자동 생성**하고, **보안 위험 요소나 예상치 못한 변경**이 있는지 검사하라.
    *   **조치:** 위험이 감지되면, **커밋을 중단**하거나 **사용자에게 경고**하라.
