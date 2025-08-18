# Claude Code 통합 가이드 (Multi-Agent Workspace)

이 문서는 Claude Code가 Multi-Agent Workspace (Gemini + Codex + Claude) 시스템에서 작업을 수행할 때 따라야 할 핵심 규칙과 절차를 정의합니다.

**핵심 특징:** 이 워크스페이스는 Python Invoke 기반의 태스크 러너와 PowerShell 스크립트를 결합한 멀티 에이전트 환경으로, Gemini, Codex, Claude가 파일 기반 메시징 시스템을 통해 협업합니다.

---

## I. 핵심 운영 환경 (Core Operating Environment)

**1. 사용자 환경: Windows**
- **주 운영체제:** 이 워크스페이스의 주 운영체제는 **Windows** 입니다.
- **절대 준수:** 모든 파일 경로, 셸 명령어, 환경 변수 등은 Windows 표준을 따라야 합니다.

**2. Claude Code의 실행 환경과 주의점**
- **환경 차이:** Claude Code의 도구(Tool) 실행 환경은 Windows 기반이지만, 일부 명령어는 Linux 스타일로 반환될 수 있습니다.
- **핵심 행동 규칙:** 모든 명령어 실행 전, **사용자 환경이 Windows임을 반드시 인지**하고 Windows에 맞는 명령어를 사용해야 합니다.

**3. 작업 공간 제한**
- **절대 원칙:** 모든 파일 작업은 `%USERPROFILE%\multi-ai-workspace` 디렉터리 안에서만 수행해야 합니다. 이 디렉터리 외부의 어떤 파일 시스템 경로에도 접근하거나 파일을 생성해서는 안 됩니다.

**4. 사용 언어**
- **기본 언어:** 사용자와의 모든 상호작용은 **한국어**로 진행하는 것을 원칙으로 합니다.

**5. Git 관리 폴더**
- **`scripts/`:** 유틸리티 스크립트 폴더로, Git에 의해 추적됩니다.
- **`secrets/`:** 민감 정보 저장 폴더로, Git에 의해 추적되지 않습니다. (`.gitignore`에 포함)
- **`docs/`:** 공유 작업 로그 폴더로, Gemini와 공동 사용합니다.

---

## II. 표준 작업 절차 (Standard Workflows)

**1. 세션 시작**
- 모든 대화 세션을 시작할 때, 이 `CLAUDE.md` 파일을 가장 먼저 읽고 모든 규칙을 인지한 상태에서 작업을 시작해야 합니다.
- `docs/HUB.md` 파일을 읽고 현재 진행 중인 작업들을 확인합니다. Gemini가 작업 중일 수 있으므로 충돌을 피해야 합니다.

**2. 민감 정보 처리**
- **핵심 파일:** `secrets/my_sensitive_data.md` (Git 추적 제외)
- **절차:**
    1. 새로운 민감 정보 발견/생성 시, 즉시 `secrets/my_sensitive_data.md` 파일에 명확한 형식으로 기록합니다.
    2. 기록 후, 사용자에게 **"새로운 [정보 종류] 정보를 `secrets/my_sensitive_data.md` 파일에 기록했습니다. 내용을 확인하고 안전하게 관리해 주세요."** 라고 즉시 알립니다.
    3. **경고:** 민감 정보 자체를 대화창에 절대 노출해서는 안 됩니다.

**3. Git 커밋 (Windows 환경)**
- **문제:** `git commit -m "메시지"` 명령어의 문자열 처리 문제.
- **우회 절차:**
    1. `COMMIT_MSG.tmp` 임시 파일에 커밋 메시지를 작성합니다.
    2. `git commit -F COMMIT_MSG.tmp` 명령어로 커밋합니다.
    3. 성공 시, `del COMMIT_MSG.tmp` 명령어로 임시 파일을 즉시 삭제합니다.

**4. 공동 작업 로그 관리**
- **핵심 파일:** `docs/HUB.md`, `docs/tasks/[task_id]/log.md`
- **절차:**
    1. 작업 시작 전 반드시 `docs/HUB.md`를 확인하여 Gemini와의 작업 충돌을 방지합니다.
    2. 새로운 작업 시작 시 HUB.md에 작업 항목을 추가하고 작업자를 명시합니다.
    3. 작업 완료 시 `log.md`에 상세 기록하고 HUB.md의 작업 상태를 업데이트합니다.
    4. Gemini와의 협업을 위해 작업자 식별자를 각 로그에 명확히 표시합니다.

---

## III. Claude Code 고유 기능 활용

**1. 토큰 사용량 모니터링**
- Anthropic 콘솔에서 API 키별 토큰 사용량을 정기적으로 확인합니다.
- 장기 작업 시 토큰 사용량을 예측하여 사용자에게 보고합니다.

**2. MCP 도구 활용**
- Postgres, GitHub, Jira 등 공식 MCP 서버를 활용하여 외부 서비스와 연동합니다.
- 사용자 정의 MCP 서버 사용 시 보안 검토를 먼저 수행합니다.

**3. 작업 기록 및 추적**
- `TodoWrite` 도구를 적극적으로 활용하여 작업 진행 상황을 기록합니다.
- 복잡한 작업은 세부 단계로 분할하여 체계적으로 관리합니다.
- 공동 작업 시 Gemini와의 작업 구분을 위해 작업자 식별자를 명확히 표시합니다.

---

## IV. 주요 문제 해결 (Troubleshooting)

**1. `.gitignore`와 파일 접근 불가**
- **문제:** `.gitignore` 설정으로 인해 특정 파일이 보이지 않거나 접근이 안 될 수 있습니다.
- **해결책:** 파일이 존재해야 하는데 없다고 판단될 경우, **`respect_git_ignore=False`** 옵션을 사용하여 다시 파일 읽기를 시도합니다.

**2. 파일 및 폴더 삭제 안정화 (Python 활용)**

  * **문제**: Windows 환경에서 `del` 또는 `powershell Remove-Item` 명령어가 파일/폴더 삭제에 실패하거나 예상치 못한 오류를 반환할 수 있습니다.
  * **해결책**: Python의 `os.remove()` (파일 삭제) 및 `shutil.rmtree()` (폴더 삭제) 함수를 활용한 스크립트를 실행하여 안정적으로 삭제를 수행합니다.

    > **파일 삭제 실행 로직 (Python):**
    > ```python
    > import os
    > file_to_delete = r'[파일 경로]' # raw string으로 경로 지정
    > try:
    >     os.remove(file_to_delete)
    >     print(f"Successfully deleted: {file_to_delete}")
    > except OSError as e:
    >     print(f"Error deleting file {file_to_delete}: {e}")
    > ```
    >
    > **폴더 삭제 실행 로직 (Python):**
    > ```python
    > import os
    > import shutil
    > dir_to_delete = r'[폴더 경로]' # raw string으로 경로 지정
    > try:
    >     shutil.rmtree(dir_to_delete) # 비어있지 않은 폴더도 삭제
    >     print(f"Successfully deleted directory: {dir_to_delete}")
    > except OSError as e:
    >     print(f"Error deleting directory {dir_to_delete}: {e}")
    > ```
    >
    > **실행 방법:** 위 Python 코드를 임시 `.py` 파일로 저장한 후 `python [임시 파일 경로]` 명령어로 실행합니다.

---

## V. 고급 기능 및 예외 처리

### 1. 작업 흐름 최적화
- 복잡한 작업은 사전에 `TodoWrite`로 계획을 수립하고 단계별로 실행합니다.
- 각 단계 완료 시 사용자에게 진행 상황을 보고합니다.

### 2. 에러 처리 및 복구
- 도구 사용 실패 시 상세한 오류 메시지를 사용자에게 전달합니다.
- 반복적인 실패 시 다른 접근 방식을 제안합니다.

### 3. 사용자 정의 설정 관리
- Claude Code 고유 설정은 이 파일에 기록하여 세션 간 유지합니다.
- MCP 서버 설정, 작업 환경 변수 등을 포함합니다.

---

## VI. 변경 이력 (Changelog)

*   **v1.0 (2025-07-24):** 초기 버전 생성 - GEMINI.md를 기반으로 Claude Code용 지침 작성