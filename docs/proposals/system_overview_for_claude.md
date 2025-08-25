# 최종 요약 보고서: Claude를 위한 Multi-Agent Workspace 완전 분석

**작성자**: Gemini
**작성일**: 2025-08-18
**목표**: 이 문서는 Claude가 우리 시스템의 철학, 아키텍처, 사용법, 그리고 자신의 역할을 완벽하게 이해하여, 최고의 성능으로 협업하는 것을 돕기 위해 작성되었습니다.

## 1. Executive Summary: 시스템 핵심 요약

이 시스템은 **Invoke 태스크 프레임워크**와 **PowerShell 런처**를 중심으로 구축된 **다중 에이전트(Multi-Agent) 협업 플랫폼**입니다. 모든 상태와 통신 기록을 **파일 기반**으로 관리하여 **투명성**과 **복원력**을 극대화했으며, **명확한 역할 분리**와 **자동화된 품질 게이트**를 통해 안정적인 운영을 추구합니다. 현재 시스템은 매우 강력하고 기능적으로 풍부하지만, 일부 테스트가 실패하고 문서와 실제 구현 간에 약간의 차이가 있는 등 개선이 필요한 부분도 공존하고 있습니다.

## 2. 핵심 원칙 및 철학

이 시스템은 `GEMINI.md`와 `forclaude` 문서에 명시된 다음과 같은 핵심 원칙을 따릅니다.

-   **Windows-First**: 모든 스크립트와 명령어는 Windows 환경에서 안정적으로 동작하는 것을 최우선으로 합니다.
-   **파일 기반 상태 관리**: 데이터베이스 의존성을 최소화하고, Git을 통해 모든 상태 변경을 추적하고 복원할 수 있도록 설계되었습니다.
-   **명령어 추상화**: 사용자는 `invoke`라는 단일 인터페이스를 통해 시스템의 모든 기능을 일관되게 사용합니다.
-   **다중 에이전트 협업**: 각 에이전트(`Gemini`, `Codex`, `Claude`)는 고유한 역할을 가지며, 정의된 프로토콜을 통해 협업합니다.
-   **엄격한 보안 및 품질**: `pre-commit` 훅과 CI/CD 파이프라인을 통해 비밀 정보 유출을 방지하고 코드 품질을 자동으로 검증합니다.

## 3. 시스템 동작 방식: 단계별 가이드

1.  **세션 시작**: `gemini.ps1`, `codex.ps1`, `claude.ps1` 중 자신의 런처를 실행하여 세션을 시작합니다. 이 과정에서 `ACTIVE_AGENT` 환경 변수가 설정되고 터미널 기록이 자동으로 시작됩니다.
2.  **상태 파악**: `invoke start` 명령어를 통해 현재 진행 중인 작업(`docs/CORE/HUB_ENHANCED.md`), Git 상태, 그리고 자신에게 온 메시지(`invoke agent.inbox`)를 확인합니다.
3.  **작업 수행**: `invoke`로 제공되는 다양한 명령어(`search`, `refactor` 등)를 사용하여 작업을 수행합니다. 파일 수정과 같은 중요한 작업은 아래의 협업 프로토콜을 따릅니다.
4.  **협업**: 다른 에이전트에게 정보를 공유할 때는 `invoke agent.msg`를, 공식적인 작업 할당이 필요할 때는 `invoke hub.send`를 사용합니다.
5.  **커밋**: 작업이 완료되면 `invoke wip` 또는 `invoke commit_safe`를 사용하여 변경 사항을 커밋합니다. 이때 `pre-commit` 훅이 자동으로 실행되어 보안 및 안전 검사를 수행합니다.
6.  **세션 종료**: `invoke end`를 통해 세션을 안전하게 종료합니다. 이 과정에서 `docs/CORE/HUB_ENHANCED.md`에 세션 요약 정보가 자동으로 기록됩니다.

## 4. 주요 시스템 및 구성 요소 (상세 보고서 링크 포함)

-   **코어 아키텍처**: 3개의 계층(PowerShell 런처, Invoke 태스크, Python 스크립트)으로 명확하게 분리되어 있습니다. ([상세 분석](docs/proposals/system_analysis_report_core_architecture.md))
-   **상태 관리**: `docs/CORE/HUB_ENHANCED.md`, `agents_hub/`, `context/`, `usage.db` 등 파일 기반의 분산된 방식으로 상태를 관리합니다. ([상세 분석](docs/proposals/system_analysis_report_state_management.md))
-   **에이전트 협업**: `ACTIVE_AGENT` 환경 변수로 에이전트를 식별하며, 메시지 로그와 태스크 큐를 통해 상호작용합니다. ([상세 분석](docs/proposals/system_analysis_report_agent_integration.md))
-   **보안 및 품질**: 로컬 `pre-commit` 훅과 원격 CI/CD 파이프라인을 연동한 다층 방어 및 검증 체계를 갖추고 있습니다. ([상세 분석](docs/proposals/system_analysis_report_security_quality.md))

## 5. Claude를 위한 가이드: 당신의 역할과 성공 전략

-   **당신의 역할**: Claude는 이 시스템에서 **고도의 추론, 분석, 그리고 다른 전문 AI 모델과의 연동**을 담당하는 핵심적인 역할을 맡을 것으로 기대됩니다. `mcp_ai_proxy` 시스템이 그 대표적인 예입니다.
-   **파일 수정 프로토콜 준수**: `GEMINI.md`에 명시된 규약에 따라, **파일을 직접 수정해야 할 경우 직접 수정하는 대신 `invoke agent.msg`를 사용하여 Codex에게 상세한 작업 요청 메시지를 보내는 방식**으로 협업하는 것이 현재의 핵심 프로토콜입니다. 이는 시스템의 안정성을 유지하는 데 매우 중요합니다.
-   **상태 확인의 생활화**: 작업을 시작하기 전, 항상 `invoke start`와 `invoke agent.inbox`를 통해 다른 에이전트의 작업 상황과 자신에게 온 요청을 확인하여 충돌을 방지해야 합니다.
-   **문서 적극 활용**: 이 보고서를 포함하여 `GEMINI.md`, `AGENTS.md` 등 시스템의 정책 문서를 항상 참고하여, 시스템의 설계 철학에 맞는 방식으로 작업을 수행해야 합니다.

## 6. 현재 과제 및 미래 방향

-   **가장 시급한 과제**: 현재 **17개의 `pytest` 테스트가 실패**하고 있습니다. 시스템의 안정성을 확보하고 CI/CD 품질 게이트를 정상화하기 위해 이 문제를 해결하는 것이 최우선 과제입니다. ([실패 분석 보고서](docs/proposals/gemini_pytest_cleanup_report.md) 참조)
-   **문서와 구현의 동기화**: `GEMINI.md`에 언급된 정적 분석 도구를 CI 파이프라인에 추가하고, 코드 내 Docstring을 보강하여 문서와 실제 코드의 일관성을 높여야 합니다.
-   **MCP AI Proxy 활성화**: `mcp` 라이브러리 설치, 실제 AI 모델 API 연동, API 키 설정을 통해 `mcp_ai_proxy` 시스템을 조속히 활성화해야 합니다. ([현황 보고서](docs/proposals/mcp_ai_proxy_status_report.md) 참조)

이 보고서가 Claude 당신이 우리 시스템에 성공적으로 적응하고, 최고의 능력을 발휘하는 데 훌륭한 가이드가 되기를 바랍니다.
