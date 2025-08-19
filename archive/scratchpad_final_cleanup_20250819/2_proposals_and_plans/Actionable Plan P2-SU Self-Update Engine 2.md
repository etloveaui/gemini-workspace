## **[최종 작업 지시서] P2-SU Self-Update Engine 구축**

**TO:** Gemini CLI
**FROM:** Project Manager
**DATE:** 2025-08-08
**RE:** 모든 요구사항을 통합한 최종 실행 계획 (Final Actionable Plan)

### **1. 프로젝트 비전 및 핵심 원칙**

  * **비전**: Gemini-CLI가 스스로 기술 부채를 진단(Scan)하고, 해결책을 제안(Propose)하며, 정책에 따라 자동 수정(Apply)하는 지능형 자가 개선(Self-Update) 시스템을 완성한다.
  * **핵심 원칙**:
      * **Windows-First**: 모든 스크립트는 Windows 환경에서 우선적으로 안정성을 보장한다.
      * **경계 준수 (Boundary Adherence)**: 모든 파일 작업은 리포지토리 내부로 엄격히 제한된다. 외부 경로 접근은 금지한다.
      * **실행 안전성**: 모든 외부 프로세스 호출(`subprocess.run`) 시 `shell=False`를 명시적으로 사용하여 보안을 강화한다.
      * **CI/CD 연동**: 모든 기능은 테스트 통과를 전제로 CI 파이프라인에 통합되어야 한다.

### **2. 최종 아키텍처 및 디렉터리 구조**

```
root/
├── docs/
│   ├── proposals/                # 자동 생성된 제안서 저장소
│   │   └── auto_update_YYYYMMDD.md
│   └── SELF_UPDATE_POLICY.md     # 자동 적용 정책 표준 문서
├── scripts/
│   └── auto_update/
│       ├── __init__.py
│       ├── scanner.py            # 1. 진단: 업데이트 대상 탐지
│       ├── proposer.py           # 2. 제안: 해결책 및 실행 계획 생성
│       ├── apply.py              # 3. 적용: 정책 기반 자동 수정 실행
│       └── policy.py             # (선택) 정책 파싱 및 검증 유틸리티
└── tasks.py                      # Invoke 태스크 정의
```

### **3. 모듈별 상세 구현 지침**

#### **Phase 1: `scanner.py` - 진단 엔진 구현**

**목표**: 업데이트가 필요한 대상을 탐지하고, 표준화된 `Finding` 객체 목록으로 반환한다.

  * **핵심 설계**:
    1.  `sys.executable -m pip`을 사용하여 가상 환경(venv)과의 호환성을 보장한다.
    2.  `pip list --outdated --format=json` 결과를 파싱하여 의존성 문제를 찾는다.
    3.  `pytest -q -W default -rA` 실행 결과에서 `DeprecationWarning`을 정규식으로 추출한다.
  * **데이터 스키마 (`Finding` 클래스)**:
    ```python
    # scripts/auto_update/scanner.py
    from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class Finding:
        kind: Literal["update_dependency", "replace_deprecated"]
        payload: dict
        evidence: str
        file_hint: str | None = None
    ```
  * **구현 스켈레톤**: `[Role: Tech Expert]` 문서에서 제공된 `scanner.py` 스켈레톤을 기반으로 구현한다.

-----

#### **Phase 2: `proposer.py` - 제안 엔진 구현**

**목표**: `scanner`의 결과를 `SELF_UPDATE_POLICY.md`와 비교하여, 사람이 읽을 수 있는 제안서(Markdown)와 기계가 실행할 `invoke` 명령 목록을 생성한다.

  * **핵심 설계**:
    1.  **정책 파서**: `SELF_UPDATE_POLICY.md`의 테이블을 파싱하여, 규칙별 `auto_approve`, `test_required` 등의 정책을 딕셔너리로 로드한다.
    2.  **명령 매핑**: 각 `Finding` 객체를 실행 가능한 `invoke refactor` 명령으로 변환한다.
          * `update_dependency` → `invoke refactor --file requirements.txt --rule update_dependency ...`
          * `replace_deprecated` → `invoke refactor --file <target>.py --rule replace_api ...` (초기에는 플레이스홀더, 팀 규칙에 따라 확장)
    3.  **제안서 생성**: `docs/proposals/auto_update_{날짜}.md` 형식으로 파일을 생성하고, 발견된 문제, 증거, 자동 승인 여부, 실행할 `--dry-run` 명령을 명시한다.
  * **구현 스켈레톤**: `[Role: Tech Expert]` 문서에서 제공된 `proposer.py` 스켈레톤을 기반으로 구현한다.

-----

#### **Phase 3: `apply.py` - 적용 엔진 구현**

**목표**: `proposer`가 생성한 제안서를 읽어, 정책에 따라 승인된 항목들을 **안전하게** 자동 적용한다.

  * **핵심 설계 (2단계 실행)**:
    1.  **Dry-Run (1단계)**: 제안서의 모든 `invoke` 명령에 `--dry-run` 플래그를 붙여 먼저 실행한다. 여기서 실패하면 해당 항목은 즉시 건너뛴다.
    2.  **테스트 (필요시)**: 정책상 `TestRequired: True`인 경우, `pytest`를 실행한다. 테스트 실패 시, `git reset --hard HEAD` 또는 `git stash`를 통해 변경 사항을 **자동으로 롤백**하고 다음 항목으로 넘어간다.
    3.  **Apply (2단계)**: 위 단계를 모두 통과한 명령에 한해, `--dry-run`을 `--yes`로 변경하여 실제 적용을 실행한다.
    4.  **커밋**: 적용 성공 시, `chore(p2-su): auto-apply ...`와 같이 명확한 메시지와 함께 변경 사항을 자동으로 커밋한다.
  * **구현 스켈레톤**: `[Role: Tech Expert]` 문서에서 제공된 `apply.py` 스켈레톤을 기반으로 구현한다.

### **4. 정책 및 문서화 표준**

#### **`docs/SELF_UPDATE_POLICY.md` (필수)**

이 문서는 시스템의 두뇌 역할을 한다. 아래 템플릿에 따라 작성하고, 프로젝트 상황에 맞게 지속적으로 갱신해야 한다.

```markdown
# Self-Update Engine Policy v1.0

시스템은 이 문서를 파싱하여 각 리팩토링 규칙의 위험도, 자동 승인 여부, 테스트 필요 여부를 판단합니다.

| Rule ID            | Category | Risk Level | Auto Approve | Test Required | Description                        |
|--------------------|----------|------------|--------------|---------------|------------------------------------|
| **update_dependency** | deps     | Low        | **Yes** | **Yes** | 패치/마이너 버전 의존성 업그레이드. |
| **replace_deprecated** | upkeep   | Medium     | **Yes** | **Yes** | 사용 중단 API를 새로운 API로 교체. |
| **lint_fix** | style    | Low        | **Yes** | **No** | 코드 포맷팅 및 린트 오류 수정.     |
| **add_docstrings** | docs     | Low        | **Yes** | **No** | 누락된 Docstring 추가.             |
```

### **5. `tasks.py` 업데이트 및 운영 플로우**

`invoke`를 통해 전체 프로세스를 단계별로 제어할 수 있도록 아래 태스크를 추가한다.

```python
# tasks.py (발췌)
from invoke import task
import sys

@task
def auto_scan(c):
    """(1) 업데이트 대상을 스캔하고 정규화된 결과(Finding)를 출력합니다."""
    c.run(f"{sys.executable} scripts/auto_update/scanner.py")

@task
def auto_propose(c):
    """(2) 스캔 결과를 바탕으로 정책을 조회하여 제안서를 생성합니다."""
    c.run(f"{sys.executable} scripts/auto_update/proposer.py")

@task
def auto_apply(c, proposal_file):
    """(3) 생성된 제안서 파일을 기반으로 자동 적용을 실행합니다."""
    c.run(f"{sys.executable} scripts/auto_update/apply.py --file {proposal_file}")

@task
def self_update(c, apply=False):
    """(End-to-End) 스캔, 제안, (선택적) 적용을 한 번에 실행합니다."""
    # scanner -> proposer -> apply 흐름을 통합하는 로직
    pass
```

  * **운영 플로우**:
    1.  `invoke auto.scan`: 변경이 필요한 대상을 확인.
    2.  `invoke auto.propose`: `docs/proposals/`에 제안서 MD 파일 생성.
    3.  **수동 검토**: 생성된 제안서의 내용을 확인.
    4.  `invoke auto.apply --proposal-file <파일명>`: 정책에 따라 승인된 항목을 자동 적용.

### **6. 테스트 및 Git 운영 전략**

  * **테스트**: `[Role: Tech Expert]` 문서에서 제시된 단위/통합/E2E 테스트 케이스를 모두 구현하여 코드의 신뢰성을 확보한다. 특히 `apply.py`의 롤백 로직을 반드시 검증한다.
  * **Git 브랜치**: `feat/p2-su/<주제>` 형식으로 브랜치를 생성한다.
  * **커밋 메시지**: 자동 적용 커밋은 `chore(p2-su): auto-apply update_dependency: requests 2.28.2`와 같이 명확하고 일관된 형식([Conventional Commits](https://www.conventionalcommits.org/))을 따른다.

-----

**이상. 위 지시서는 두 전문가의 분석을 종합한 최종 결정 사항입니다. 즉시 개발에 착수해주시기 바랍니다.**