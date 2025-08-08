# 작업 지시 요청서: [P2-SU] Self-Update Engine 구축

**To:** 최종 컨설팅 LLM
**From:** Gemini-CLI 개발팀
**Date:** 2025-08-08
**Version:** 1.0

## [서론]

저희 Gemini-CLI는 `[P2-SU] Self-Update Engine` 구축 프로젝트를 진행하고 있습니다. 이 프로젝트의 목표는 Gemini-CLI가 스스로 기술 부채를 인지하고, 외부 환경 변화에 적응하며, 지속적으로 자가 개선할 수 있도록 만드는 것입니다.

이전에 요청드렸던 심층 분석에 대한 상세하고 통찰력 있는 보고서(`P2-SU.pdf`)를 제공해주셔서 진심으로 감사드립니다. 보고서의 내용은 저희의 초기 계획을 훨씬 뛰어넘는 깊이와 실용성을 담고 있었으며, 특히 `P1-2` 파일 시스템 에이전트와의 통합 아키텍처 제안은 매우 인상 깊었습니다.

## [1부] 심층 분석 보고서 요약 및 수용

저희는 귀하께서 제공해주신 `P2-SU.pdf` 보고서의 핵심 내용을 완전히 이해하고 수용합니다. 주요 내용은 다음과 같습니다.

-   **`P1-2` 파일 시스템 에이전트와의 통합:** `proposer.py`가 `file_agent.py`의 규칙 플러그인을 호출하여 자동 제안된 리팩토링 작업을 수행하는 통합 아키텍처를 채택합니다. 이는 `Self-Update Engine`이 `File Agent`의 핵심 클라이언트가 됨을 의미합니다.
-   **`SELF_UPDATE_POLICY.md` 초안 및 자동 승인 기준:** 보고서에서 제안된 `SELF_UPDATE_POLICY.md`의 초기 초안과 자동 승인 기준(패치 버전 업데이트, `DeprecationWarning` 수정, 안전한 Lint 규칙 적용 등)을 수용합니다. 이 정책은 시스템의 안전한 자동화를 위한 핵심 가이드라인이 될 것입니다.
-   **상세한 테스트 전략:** 각 구성 요소별 단위 테스트, `proposer` 모듈 단위 테스트, 통합 테스트, 정책 준수 테스트 등 보고서에서 제시된 다층적인 테스트 전략을 따를 것입니다.
-   **시스템 동작 흐름:** `scanner` -> `proposer` -> `file_agent` -> `tester` -> `committer` -> `reporter`로 이어지는 상세한 시스템 동작 흐름을 이해하고 이를 구현의 기반으로 삼습니다.

## [2부] 구체적인 작업 지시 요청

귀하께서 제공해주신 분석 보고서의 내용을 바탕으로, 저희 Gemini-CLI가 `[P2-SU] Self-Update Engine`을 구현하기 위한 **매우 구체적이고 실행 가능한 작업 지시서**를 작성해주시길 요청합니다. 이 지시서는 제가 직접 코드를 작성하고 시스템을 구축할 수 있도록, 다음 내용을 반드시 포함해야 합니다.

1.  **단계별 구현 지침:**
    -   `scripts/auto_update/scanner.py`: `pip list --outdated`, `pytest` 로그의 `DeprecationWarning` 스캔 등 보고서에 명시된 스캔 대상을 구현하기 위한 상세 지침 및 코드 스켈레톤/의사 코드.
    -   `scripts/auto_update/proposer.py`: 스캔 결과를 바탕으로 `docs/proposals/auto_update_YYYYMMDD.md` 형식의 제안서를 생성하는 로직, 그리고 `P1-2` `file_agent.py`의 `invoke refactor` 명령을 생성하는 로직에 대한 상세 지침 및 코드 스켈레톤/의사 코드.
    -   `scripts/auto_update/apply.py` (초안): `SELF_UPDATE_POLICY.md`에 정의된 자동 승인 기준에 따라 `invoke refactor --yes` 명령을 호출하는 로직에 대한 상세 지침 및 코드 스켈레톤/의사 코드.

2.  **테스트 케이스:**
    -   각 모듈(scanner, proposer, apply) 및 통합 테스트를 위한 구체적인 `pytest` 테스트 케이스 예시. 특히, 보고서에서 강조된 모킹 기반 테스트 전략을 반영해야 합니다.

3.  **`tasks.py` 업데이트:**
    -   `invoke auto.scan`, `auto.propose`, `auto.apply` 태스크를 `tasks.py`에 어떻게 추가해야 하는지 명확한 지침 및 코드 스켈레톤.

4.  **문서화 지침:**
    -   `docs/SELF_UPDATE_POLICY.md`의 구체적인 내용(제안된 자동 승인 기준 포함) 및 `GEMINI.md` 업데이트에 대한 상세 지침.

5.  **Git 관리 지침:**
    -   이 프로젝트를 위한 브랜치 전략, 커밋 메시지 컨벤션 등 Git 관련 지침.

## [3부] 추가 질문

위 작업 지시서 작성에 필요한 추가적인 정보나 명확화가 필요한 부분이 있다면 자유롭게 질문해주십시오.
