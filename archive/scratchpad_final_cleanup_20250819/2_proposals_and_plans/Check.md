 새로운 계획 (작업은 하지 않음, 컨펌 대기):

  Task: Gemini 운영 지침 및 시스템 최신화 구조 개선 (재정의 및 견고성 강화)

  목표: GEMINI.md를 최신 시스템 기능과 완벽하게 통합하고, 시스템의 지속적인 최신화 및 자율적인 운영을 위한 기반을 마련하며, 이 과정의 견고성을 확보합니다. 특히 replace 도구 사용의
  안정성을 최우선으로 고려합니다.

  세부 계획:

   * Phase 0: 계획 실행 견고성 확보
       * 0.1. 사전 백업 전략:
           * GEMINI.md, tasks.py, .gitignore와 같이 수정될 핵심 파일들에 대해 타임스탬프가 포함된 백업본을 docs/backup/ 디렉터리에 생성합니다. (예: GEMINI_YYYYMMDD_HHMMSS.md.bak)      
           * 오류 발생 시 복구 계획: 각 단계에서 오류 발생 시, 해당 단계에서 변경된 내용을 즉시 롤백하고, 상세 오류 로그를 scratchpad/emergency_logs/에 기록한 후 사용자에게 보고합니다.
       * 0.2. 진행 상황 상세 로깅:
           * 이 계획의 각 세부 단계가 완료될 때마다 docs/tasks/gemini-self-upgrade/log.md 파일에 진행 상황을 업데이트합니다. (Git 커밋은 최종 완료 시점에 일괄 진행)
       * 0.3. `replace` 도구 사용 원칙 (새로운 추가):
           * replace 도구 사용 직전, 항상 대상 파일의 최신 내용을 `read_file`로 읽어와 `old_string`을 직접 복사하여 사용합니다.
           * old_string에는 변경하려는 내용의 앞뒤로 충분한 컨텍스트(3~5줄)를 포함하여 고유성을 확보합니다.
           * 복잡한 GEMINI.md 수정 시, replace 실행 전 old_string과 new_string의 내용을 사용자에게 제시하여 사전 검토 및 승인을 요청합니다.

   * Phase 1: `GEMINI.md` 업데이트 및 `.gitignore` 관리
       * 1.1. `GEMINI.md` 백업 및 정리:
           * GEMINI.md 백업본 생성.
           * GEMINI.md 파일 내용을 read_file로 읽어와, 현재 시스템의 기능과 맞지 않거나 불필요한 레거시 지침들을 식별하고 삭제합니다. (이때, replace 도구의 새로운 사용 원칙을 적용)    
           * GEMINI.md의 "I. 핵심 운영 환경 (Core Operating Environment)" -> "1. 세션 시작" 섹션을 제가 이전에 제안했던 "시스템 초기 점검 및 브리핑" 내용을 포함하도록 수정합니다.      
           * GEMINI.md에 "시스템 최신화" 또는 "자가 개선"과 관련된 새로운 섹션을 추가하여, 시스템이 지속적으로 업데이트되고 새로운 기능이 반영되는 구조임을 명시합니다.
       * 1.2. `.gitignore` 수정 및 Git 서브모듈 관리 명확화:
           * C:\Users\eunta\gemini-workspace\.gitignore 파일에서 .gemini/ 라인을 제거하여 context_policy.yaml을 포함한 .gemini 디렉터리 전체가 Git으로 관리되도록 합니다.
           * 사용자님께 Git 서브모듈(`projects` 폴더 내)에 대한 설명 제공: git status에서 "new commits"로 표시되는 것은 정상적인 서브모듈 동작이며, .gitignore로 무시할 수 없음을 명확히
             설명합니다. (이 설명은 계획 실행 전 사용자 컨펌 단계에서 제공)

   * Phase 2: `tasks.py`의 지능적인 구현
       * 2.1. `tasks.py` `start` 함수 수정:
           * C:\Users\eunta\gemini-workspace\\tasks.py 파일의 start 함수를 다음과 같이 수정합니다.
           * invoke build-context-index를 호출하여 context/index.json을 최신 상태로 유지합니다.
           * scripts/prompt_builder.py를 활용하여 session_start_briefing 정책에 따라 동적으로 브리핑 내용을 생성합니다.
           * 생성된 브리핑 내용을 사용자에게 출력합니다.
           * `help` 기능 안내 포함: 브리핑 마지막에 "더 많은 도움말이 필요하시면 invoke help를 입력해주세요."와 같이 help 태스크를 안내하는 문구를 추가합니다.     
           * 다음 행동 제안: 브리핑 후 사용자에게 "어떤 작업을 계속할까요?, 아니면 새로운 작업을 시작할까요?"와 같이 다음 행동을 제안하여 대화의 흐름을 주도합니다.
       * 2.2. `tasks.py` 기타 태스크 일관성 유지:
           * tasks.py 내의 다른 태스크들도 scripts/runner.py를 통해 명령어를 실행하도록 일관성을 유지합니다.

   * Phase 3: 시스템의 지속적인 최신화 구조 반영
       * 3.1. `GEMINI.md`에 "견고한 계획 실행 가이드라인" 섹션 추가 제안:
           * 이 계획의 Phase 0에서 정의된 "사전 백업 전략", "오류 발생 시 복구 계획", "진행 상황 상세 로깅"과 같은 가이드라인을 GEMINI.md의 새로운 섹션으로 추가할 것을 제안합니다. (예:
             "V. 고급 기능 및 예외 처리" 아래에 "VI. 견고한 계획 실행 가이드라인" 또는 별도 문서)
           * 이 섹션은 제가 향후 복잡한 작업을 수행할 때 항상 참조해야 할 메타-규칙이 됩니다.
       * 3.2. `GEMINI.md`에 "지속적인 최신화" 섹션 추가:
           * 시스템이 항상 최신 상태를 유지하고 새로운 기능이 자동으로 반영되는 구조임을 명시합니다.
           * build_context_index.py가 주기적으로 실행되어 컨텍스트 인덱스를 업데이트하는 역할, 그리고 제가 GEMINI.md의 "자가 개선 제안 프로토콜"에 따라 새로운 규칙이나 개선 사항을     
             제안할 수 있음을 포함합니다.