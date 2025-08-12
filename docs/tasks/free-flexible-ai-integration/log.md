# 프로젝트: 무료 및 유연한 AI 통합 (Free & Flexible AI Integration)

## 1. 프로젝트 최종 목표 (High-Level)
사용자 시스템 내에 비용 효율적이고 유연한 AI 통합 프레임워크를 구축합니다. 이는 "Claude Code" 개념을 활용하여 다양한 AI 모델(초기에는 Groq, 향후 Claude 및 기타 모델)과의 상호작용을 가능하게 하며, MCP(Model Context Protocol)를 통해 이를 지원합니다.

## 2. 단계별 계획

*   **1단계: 연구 및 초기 설정 (현재 진행 중)**
    *   **목표**: Groq, MCP 등 관련 기술에 대한 이해를 심화하고, 필요한 구성 요소를 식별하며, 초기 개발 환경을 설정합니다.
    *   **담당**: Gemini (정보 수집 및 분석), 사용자 (필요 시 시스템 관련 정보 제공)

*   **2단계: MCP 구현**
    *   **목표**: AI 모델 간의 상호작용 및 컨텍스트 관리를 위한 MCP 구성 요소를 개발하거나 기존 솔루션을 통합합니다.
    *   **담당**: Gemini (코드 구현 및 테스트)

*   **3단계: Groq 통합**
    *   **목표**: MCP 프레임워크를 통해 Groq 모델을 호출하고 활용하는 로직을 구현합니다.
    *   **담당**: Gemini (코드 구현 및 테스트)

*   **4단계: "Claude Code" 로직 개발**
    *   **목표**: 작업 요구사항에 따라 다양한 AI 모델을 동적으로 선택하고 호출하는 Claude Code의 핵심 로직을 개발합니다.
    *   **담당**: Gemini (코드 구현 및 테스트)

*   **5단계: 시스템 통합**
    *   **목표**: 개발된 AI 통합 프레임워크 전체를 사용자 시스템에 통합합니다.
    *   **담당**: Gemini (통합 코드 작성), 사용자 (시스템 아키텍처 및 통합 지점 관련 정보 제공)

*   **6단계: 향후 개선 및 확장**
    *   **목표**: Claude 및 기타 LLM 통합, 고급 기능 추가 등 시스템 확장 계획을 수립합니다.
    *   **담당**: Gemini (계획 수립), 사용자 (요구사항 정의)

## 3. 역할 및 책임 분담

*   **사용자**:
    *   **의사 결정자**: 계획 승인, 상위 수준 요구사항 및 피드백 제공.
    *   **시스템 컨텍스트 제공자**: 기존 시스템에 대한 구체적인 정보 제공.
    *   **최종 검토자**: 구현된 솔루션 검토 및 승인.
    *   **수동 설정/구성**: API 키 생성, 초기 환경 설정 등 사용자 직접 개입이 필요한 작업.

*   **Gemini (나)**:
    *   **계획 및 분석**: 상세 계획 수립, 요구사항 분석, 솔루션 제안.
    *   **코드 구현**: 핵심 프레임워크(MCP, Groq 통합, Claude Code 로직) 코드 작성, 수정, 리팩토링.
    *   **파일 시스템 작업**: 파일 읽기/쓰기, 디렉터리 관리.
    *   **도구 실행**: 사용 가능한 모든 도구(`run_shell_command`, `replace`, `write_file` 등) 활용.
    *   **문서화 및 로깅**: 프로젝트 문서 및 작업 로그 유지 관리.
    *   **검증**: 테스트 실행, 린터 및 빌드 명령 실행.

*   **Codex (필요 시)**:
    *   **특정 코드 생성**: Gemini가 어려움을 겪거나 사용자가 명시적으로 지시할 경우, 특정 코드 스니펫 또는 복잡한 알고리즘 생성.
    *   **대안 탐색**: Gemini가 막혔을 때 대안 솔루션 탐색.
    *   *(참고: 이 프로젝트에서는 사용자가 명시적으로 Codex를 호출하거나 Gemini의 현재 역량을 벗어나는 복잡한 코드 생성이 필요한 경우가 아니라면, Gemini가 주로 구현을 담당합니다.)*

## 4. 기타 고려사항 (사용자님이 생각하지 못할 수 있는 부분)

*   **API 키 관리**: Groq 및 향후 Claude API 키를 어떻게 안전하게 저장하고 접근할 것인가? (`GEMINI.md`의 보안/시크릿 섹션 참조).
*   **시스템 아키텍처**: 이 프레임워크가 기존 시스템에 어떻게 통합될 것인가? 진입점, 데이터 흐름, 의존성은 무엇인가? (사용자 입력 필요).
*   **오류 처리 및 견고성**: API 호출 실패, 속도 제한, 네트워크 문제 등을 어떻게 처리할 것인가?
*   **성능**: 모델 전환 및 응답 시간을 효율적으로 보장하는 방법은?
*   **확장성**: 더 많은 AI 모델이나 높은 사용량이 도입될 경우 시스템을 어떻게 확장할 것인가?
*   **테스트 전략**: 각 구성 요소(MCP, Groq 통합, Claude Code 로직)를 어떻게 테스트할 것인가?
*   **로깅 및 모니터링**: 작업 로그 외에 런타임 로그 및 모델 사용량을 어떻게 추적할 것인가?
*   **의존성 관리**: 새로운 라이브러리(예: Groq SDK, HTTP 클라이언트)는 어떻게 관리할 것인가(`requirements.txt` 등)?
*   **사용자 인터페이스/상호작용**: 통합된 AI 시스템과 사용자는 어떻게 상호작용할 것인가(CLI, API, GUI 등)?

---

## `scratchpad/claude_code` 디렉토리 분석 및 통합 계획

### 1. `scratchpad/claude_code` 프로젝트 개요
`c:\Users\eunta\gemini-workspace\scratchpad\claude_code` 디렉토리는 "멀티 AI 워크스페이스" 프로젝트의 잘 구조화된 프로토타입입니다. 이는 통합된 인터페이스를 통해 다양한 AI 모델(Groq, Kimi, Qwen, Gemini, Llama, Gemma)과 유연하고 비용 효율적인 상호 작용을 가능하게 하도록 설계되었습니다.

### 2. 주요 구성 요소 및 기능
*   **Model Context Protocol (MCP) 통합**: MCP를 활용하여 파일 시스템과의 상호 작용, 데스크톱 명령 실행, 검색 서비스(Brave Search, Firecrawl)와의 통합을 허용합니다.
*   **LLM 라우팅 및 상호 작용**: 시스템은 작업 유형(예: 고정밀 추론을 위한 `/think`, 코드 친화적인 작업을 위한 `/code`)에 따라 사용자 쿼리를 다른 LLM(Groq, Kimi, Qwen, Llama, Gemma)으로 라우팅합니다. Groq를 기본 API 엔드포인트로 사용합니다.
*   **명령줄 인터페이스 (CLI)**: `router.py` 및 PowerShell 래퍼를 통해 사용자가 슬래시 명령(예: `/open`, `/run`, `/think`)을 사용하여 AI 모델 및 도구와 상호 작용할 수 있도록 CLI를 제공합니다.
*   **API 키 관리**: `Get-ApiKey.ps1`, `mcp_client.py`, `ask_groq.py`를 통해 `secrets/my_sensitive_data.md`에서 API 키를 안전하게 로드하는 메커니즘을 포함합니다.
*   **AI 에이전트 운영 지침**: `CLAUDE.md`는 Windows 환경 특정 사항, 민감한 데이터 처리, Git 절차 및 협업 로깅을 포함하여 AI 에이전트(Claude와 같은)가 이 워크스페이스 내에서 작동하는 방법에 대한 명시적인 지침을 제공합니다.

### 3. `scratchpad/claude_code` 파일 목록 및 위치
이 디렉토리의 파일들은 프로젝트의 핵심 구성 요소이며, 향후 통합 및 참조를 위해 삭제되지 않고 보관됩니다.
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\requirements.txt`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\router.py`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\mcp_client.py`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\mcp_servers.json`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\MCP.md`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\ask-groq.ps1`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\ask_groq.py`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\docs\CLAUDE.md`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\docs\README.md`
*   `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\scripts\Get-ApiKey.ps1`
*   **참고**: `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\secrets\my_sensitive_data.md` 파일은 주 `secrets/my_sensitive_data.md` 파일로 내용이 병합되었으며, `c:\Users\eunta\gemini-workspace\scratchpad\claude_code\secrets\my_sensitive_data_merged_to_main.md`로 이름이 변경되어 보관됩니다.

### 4. 통합 전략 및 Claude 시스템 진입 원활화 계획
이 `claude_code` 디렉토리는 "무료 및 유연한 AI 통합" 프로젝트를 위한 **작동 청사진 또는 상세 참조 구현** 역할을 합니다. 이를 활용하여 Claude를 포함한 AI 시스템을 원활하게 통합할 계획입니다.

**4.1. `claude_code`를 청사진으로 활용**: `scratchpad/claude_code` 프로젝트를 주요 참조로 삼아 "무료 및 유연한 AI 통합" 작업을 구현합니다.

**4.2. 재사용 가능한 구성 요소 식별**: `mcp_client.py`, `router.py`, `ask_groq.py`와 같은 스크립트, `mcp_servers.json`과 같은 구성 파일, `CLAUDE.md`, `MCP.md`와 같은 문서를 직접 적용하거나 강력한 예시로 활용할 수 있도록 식별합니다.

**4.3. 통합 접근 방식**: 초기 설정에는 **직접 채택 및 적용** 방식을 권장합니다. 이는 `scratchpad/claude_code`의 `scripts/` 및 `docs/` 디렉토리를 주 워크스페이스 내의 새롭고 전용된 위치(예: `src/ai_integration/`)로 복사하고, 필요 시 리팩토링을 수행하는 것을 의미합니다. 이 방식은 가장 빠르게 작동하는 프로토타입을 얻을 수 있습니다.

**4.4. Claude 통합 계획**: `scratchpad/claude_code/docs/CLAUDE.md` 파일은 Claude의 작동에 대한 명시적인 지침을 제공하므로 매우 중요합니다. `router.py`는 이미 모델 라우팅을 포함하고 있어, 이 프레임워크 내에서 직접 Claude 모델을 포함하도록 확장하는 것이 간단할 것입니다. `mcp_servers.json`도 Claude MCP 서버가 사용 가능해지면 확장할 수 있습니다.

### 5. 실행 단계 (상위 수준)
*   **5.1. `claude_code` 구성 요소 복사**: `scratchpad/claude_code`의 관련 부분을 주 프로젝트의 새롭고 지정된 위치로 복사합니다.
*   **5.2. 적용 및 테스트**: 경로를 수정하고, 기존 프로젝트 구조와 통합하고, 핵심 기능(MCP, Groq 상호 작용, 라우팅)을 테스트합니다.
*   **5.3. 개선 및 확장**: 테스트를 기반으로 구현을 개선하고 AI 작업에 대한 특정 사용자 요구 사항을 충족하도록 확장합니다.