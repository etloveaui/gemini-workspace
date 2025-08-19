# GEMINI.md (v2 Final+)

## 0) 목적/범위
본 문서는 이 워크스페이스의 **운영 표준**이다. 목표는 **재현성**, **보안**, **신속한 인수인계**다. 모든 규정은 Windows 환경과 Python/Invoke 중심으로 정의한다.

## 1) 운영 원칙 (Windows-first)
- **Python 경로**: venv가 있으면 `%REPO%/venv/Scripts/python.exe`, 없으면 `sys.executable`.
- **셸/인코딩**: PowerShell 래핑 금지, 파이썬 프로세스 **직접 호출**. 표준 I/O는 **UTF-8** 고정.
- **작업 경계**: 파일 작업은 원칙적으로 **레포 경로 내부**에서 수행한다.

## HUB 작업 수명주기(자동 관리)
- 시작 전 등록 → 클레임 → 완료 보고(성공/실패)로 일관 관리합니다.
- Invoke 태스크 또는 브로커 스크립트를 사용하며, 비대화식 환경에서는 큐/아카이브 JSON을 원자적으로 기록해 일관성을 보장합니다.

## Git 훅(Pre-commit) 정책
- 전역 토글: `.agents/config.json`의 `hooks.enabled`로 전체 훅 on/off.
- 대화형 프롬프트 회피: `invoke commit_safe --skip-diff-confirm` 또는 `SKIP_DIFF_CONFIRM=1` 설정을 사용합니다.
  - 외부 GUI 툴(Sourcetree 등) 사용 시 권장: 훅 비활성(`invoke git.set-hooks --off`).

## 🚨 CRITICAL: Project Independence Rules
⚠️ **절대 준수 사항** - 프로젝트 전체가 망가질 수 있습니다!

### 🔒 Projects 폴더 독립성
- `projects/` 아래의 **모든 폴더는 독립적인 Git 리포지토리**
- **절대로** root workspace Git에 포함하면 안됨
- 각 프로젝트는 자체 `.git` 폴더를 가짐

### 🚫 금지 행위
1. `git add projects/` 실행 금지
2. projects 내 파일을 메인 워크스페이스 Git에 추가 금지
3. projects 폴더 내용을 메인 .gitignore에 추가 시도 금지
4. projects 내 독립 프로젝트를 메인 브랜치에 merge 시도 금지

### ✅ 올바른 작업 방식
1. **프로젝트 작업 시**: `cd projects/100xFenok` 후 해당 Git에서 작업
2. **독립 커밋**: 각 프로젝트 폴더에서 `git commit`, `git push`
3. **메인 워크스페이스**: 오직 시스템/에이전트 관련 파일만 관리

---

## 2) 디렉터리·추적 정책
- **`.gemini/`**: 설정·로컬 비밀 보관 위치.  
  - **커밋 금지**: `*.creds*.json`, `*oauth*.*`, 토큰류는 **로컬 전용(local-only)** 으로 보관하고 커밋하지 않는다.  
  - **추적 허용**: `.gemini/`에서 **`context_policy.yaml`만** 버전 추적을 허용한다.
- **`projects/`**: 로컬 전용 작업 공간. **항상 커밋 금지**(`.gitignore`에서 전면 차단).
- **pre-commit 가드**: `.githooks/pre-commit` + `scripts/hooks/precommit_secrets_guard.py`로  
  `.gemini/*(oauth|creds|token|secret|.json|.db|.sqlite|.pem|.p12|.key)` 및 `projects/` **스테이징 차단**.

## 3) 명령 표준 (Invoke & GitHub Actions)
- **Invoke (로컬)**:
  - **(권장) 세션 시작**: `gemini-session.ps1` 스크립트를 실행하면 UTF-8 설정, 대화 자동 녹화 등 세션 환경이 자동으로 구성됩니다.
  - `invoke start`: 환경 점검(doctor) → HUB 브리핑 → 컨텍스트 인덱스 빌드
  - `invoke doctor`: 파이썬/권한/네트워크/경로/인코딩 점검
  - `invoke help [section]`: 도움말 출력
  - `invoke search -q "<질의>"`: 웹 검색 요약
  - `invoke context.build` / `invoke context.query "<q>"`
  - `invoke test`: pytest 실행
  - `invoke wip -m "<msg>"`: WIP 커밋
  - `invoke end`: 세션 종료(아카이브/로그/HUB 갱신)
- **GitHub Actions (원격)**:
  - `@gemini-cli <요청>`: PR 또는 이슈의 댓글을 통해 원격 AI 어시스턴트에게 작업을 지시합니다. (예: `@gemini-cli 이 코드 리뷰해줘`)

**(로컬 1회 설정)** pre-commit 훅 활성화: `git config core.hooksPath .githooks`

**Exit Codes (표준)**
- **0** 정상 / **2** Provider 미설정·불가 / **4** 예외(기타 오류)

## 4) 세션 라이프사이클
**Start**
1) `doctor` 실행 → 핵심 의존성/권한/인코딩 점검  
2) `docs/HUB.md`의 Active/Paused 요약, `git status --porcelain` 요약  
3) `context.build` 실행(인덱스 최신화)  
4) 이전 세션의 `__lastSession__` 블록이 있으면 정리 후 시작

**During (작업 회복성 프로토콜)**
- **작업 분할:** 복잡한 작업은 명확한 하위 목표로 분할하여 순차적으로 실행한다.
- **사전/사후 로그:** 모든 도구 실행(특히 파일 수정, 명령어 실행) 전후로 의도와 결과를 즉시 로그로 기록한다.
- **실패 시 즉시 전환:** 동일한 접근으로 2회 연속 실패 시, 즉시 다른 해결책을 모색한다 (기존 3-Strikes Rule 강화).
- **가정 명시:** 불확실한 상황에서는 명시적으로 가정을 설정하고, 검증 계획을 함께 제시한다.

**End**
- `.gitignore` 상태 확인, 미커밋 변경은 `wip` 권고  
- HUB 상태 갱신(Active↔Paused), `__lastSession__` 블록에 핵심 요약 기록

## 5) 로깅·인수인계
- **중앙 허브**: `docs/HUB.md` — 작업의 라이프사이클을 관리하는 중앙 허브. 모든 작업은 아래 5가지 상태 중 하나를 가집니다.
  - **`Active` (활성)**: 현재 최우선으로 진행 중인 단일 작업.
  - **`Staging` (대기)**: 직전까지 `Active`였던 작업으로, 가장 먼저 재개될 가능성이 높은 작업.
  - **`Planned` (계획)**: 계획은 승인되었으나, 아직 실제 코드 작업은 시작되지 않은 작업.
  - **`Paused` (보류)**: 외부 요인(의존성, 정보 부족 등)으로 인해 상당 기간 진행이 어려운 작업.
  - **`Completed` (완료)**: 모든 구현과 검증이 완료된 작업.
- **작업 로그**: `docs/tasks/<task_id>/log.md` — 시간순 **Append-only**(정정은 하단에 추가)  
- **권장 주기**: Detailed | Standard(기본) | Minimal 중 선택

## 6) 정책 파일 (context_policy.yaml)
- **위치/추적**: `.gemini/context_policy.yaml`만 **버전 추적 허용**.  
- **화이트리스트 스키마**: `sources`, `tokens`, `context_limits` 만 유효 키로 간주한다.  
- **[Unwired Config] 규정**: 코드에서 **실사용 참조 없는 키는 Deprecated**로 분류하고 **차기 마이너 릴리스에서 제거**한다. Unknown key는 로드 시 **경고**만 남기고 **무시**한다.

## 7) 보안 / Secrets
- **레포 내 자격증명 커밋 금지**: `.gemini/*` 내 비밀 파일은 **로컬 전용**이며 커밋 금지.  
- **보관 위치**: 기본 `%APPDATA%\gemini-workspace\secrets\` 또는 **환경변수/시크릿 매니저**.  
- **노출 대응 절차**  
  1) **키 회전**(재발급·기존 폐기)  
  2) **Git 이력 정리**(예: `git filter-repo`로 해당 경로 제거)  
  3) 영향권 스캔/폐기 및 HUB에 사고·조치 로그 기록

## 8) 품질 게이트
- **필수**: `pytest -q` 통과.  
- **도입**: 정적 분석(`ruff`/`mypy`)과 Secret Scan을 CI에 추가한다.  
- **병합 조건**: **모든 PR은 Windows CI 통과가 필수**다.

## 9) P1-1: Web Search Tool (DoD)
- **즉시 구현(더미 Provider)**  
  - 함수 시그니처: `search(query: str, top_k: int = 5) -> List[Dict[str,str]]`  
  - **결정적·비네트워크·`top_k` 준수**. 각 item은 `title/url/snippet` 포함, `title/snippet`에 `query` 반영, 최소 1개 결과 보장.  
- **실 Provider(병행)**  
  - Serper.dev(권장) 또는 Google CSE/SerpAPI로 구현하되 **동일 시그니처·Exit Codes**를 적용한다.  
- **완료 기준(DoD)**  
  - `invoke search -q "test"` 실행 시 약 5개 결과 요약 출력 **및** 관련 테스트 통과 → HUB의 **[P1-1]**을 **Completed**로 이동한다.

## 10) 트러블슈팅 (Quick)
- **`git push` 권한 오류**: 워크플로우(.github/workflows) 수정 등 높은 권한이 필요한 Push 실패 시, `C:\Users\eunta\gemini-workspace\secrets\my_sensitive_data.md` 파일에 기록된 GitHub PAT를 자동으로 적용한다.
- **따옴표/인코딩**: PowerShell 래핑 대신 파이썬 직접 호출(UTF-8 보장)
- **경로/권한**: 관리자 권한·경로 길이·파일 잠금 확인
- **삭제 실패(Windows)**: `os.remove`/`shutil.rmtree` 우선
- **검색 실패**: Provider 미설정 시 **Exit 2**. 기본은 **ChatGPT 심층리서치 트리거**로 안내

## 11) 변경관리 및 워크플로우
- **통합 워크플로우**: 로컬(Gemini CLI)과 원격(GitHub Action)의 역할을 명확히 분리하여 시너지를 창출합니다.
  1. **로컬 개발 (Gemini CLI)**: 사용자와의 대화를 통해 로컬 환경에서 신속하게 코드를 작성, 수정, 테스트합니다.
  2. **원격 Push 및 PR 생성 (Gemini CLI)**: 로컬 개발이 완료되면, 변경사항을 원격 저장소에 Push하고 Pull Request를 생성합니다.
  3. **자동 리뷰 및 분석 (GitHub Action)**: PR이 생성되면 `run-gemini-cli` Action이 자동으로 코드 리뷰, 분석 등 설정된 작업을 수행합니다.
  4. **피드백 반영 및 병합**: Action의 피드백을 바탕으로 로컬에서 추가 수정을 진행하고, 최종적으로 PR을 병합합니다.
- **게이트 승인**: 모든 변경은 위 워크플로우에 따른 코드 리뷰 및 자동화된 검증(CI)을 거친 후 적용됩니다.
- **메타러닝 규칙**: 동일 목표 2회 실패+1회 성공 패턴은 규칙으로 제안, 3회 연속 성공 시 표준화합니다.

## 12) 표준 작업 절차 (Standard Operating Procedure)

*모든 주요 기능 추가 및 시스템 변경은 다음 4단계 절차를 따른다.*

**Phase 1: 분석 자료 준비 (Analysis & Briefing)**
1.  **Gemini:** 현재 상태와 목표, 그리고 구체적인 질문을 담은 상세한 **"분석 요청서"**를 작성한다. (생성 위치: `docs/proposals/`)
2.  **User:** 이 "분석 요청서"를 외부 심층 리서치 LLM(GPT)에게 전달하여, 코드베이스에 대한 상세한 **"분석 보고서"**를 받는다.

**Phase 2: 작업 지시 요청 (Request for Directives)**
1.  **User:** 최종 컨설팅 LLM에게, Gemini가 작성한 **"분석 요청서"**와 GPT가 작성한 **"분석 보고서"**를 함께 제공하며, **"이 모든 자료를 바탕으로, Gemini-CLI가 수행해야 할 구체적인 작업 지시서를 작성해달라"**고 요청한다.

**Phase 3: 작업 지시서 수령 및 실행 계획 수립 (Receive & Plan)**
1.  **User:** 외부 LLM으로부터 최종 **"작업 지시서"**를 수령하여 Gemini에게 전달한다.
2.  **Gemini:** 전달받은 "작업 지시서"를 바탕으로, **구체적인 실행 계획(Action Plan)을 수립**하고, 각 단계를 어떻게 적용할지 사용자에게 확인받는다.

**Phase 4: 계획 실행 (Execution)**
1.  **Gemini:** 사용자에게 승인받은 실행 계획에 따라서만 실제 작업을 수행한다.

## 13) 멀티 에이전트 호환 (Coexistence)
- 개요: 본 워크스페이스는 여러 CLI 에이전트(Gemini, Codex, 향후 Claude 등)가 공존하도록 설계되었습니다. 세부 운영은 `AGENTS.md`를 참조하세요.
- 활성 에이전트 확인: `invoke agent.status`
- 활성 에이전트 전환: `invoke agent.set --name gemini|codex`
- 설정 파일: `.agents/config.json`의 `{"active": "gemini|codex"}` 값으로 관리됩니다.
- 로깅: `scripts/runner.py`는 실행 로그/오류 기록 시 `AGENT=<name>` 프리픽스를 포함합니다.
- 원칙 상속: Windows-first, Python 직접 호출(UTF-8), 레포 내부 작업 경계, 비밀 커밋 금지 규칙은 모든 에이전트에 동일 적용합니다.
- **파일 수정 프로토콜 (File Modification Protocol)**:
  - **Codex 전담**: 시스템 파일의 직접 수정은 원칙적으로 **Codex 에이전트**가 전담한다.
  - **Gemini 역할**: Gemini는 파일 수정이 필요한 경우, 사용자에게 먼저 문제점과 수정 제안을 보고하고 **명시적 승인**을 받는다.
  - **작업 요청**: 사용자의 승인 후, Gemini는 직접 수정하는 대신 `invoke agent.msg`를 사용하여 Codex에게 상세한 내용을 담은 **작업 요청 메시지**를 남긴다.
- **교차 에이전트 메시징 (v0.1)**:
  - **저장소**: `context/messages.jsonl` (JSON Lines, UTF-8)
  - **필드**: `{ "ts": "UTC ISO", "from": "agent", "to": "agent|all", "tags": [], "body": "..." }`
  - **명령어**:
    - `invoke agent.msg --to <agent> --body "..."`: 메시지 전송
    - `invoke agent.inbox --agent <agent>`: 메시지 수신 및 `.agents/inbox/<agent>.md` 갱신
    - `invoke agent.read --agent <agent>`: 모든 메시지를 읽음으로 표시
- 현재 상태: v0.1은 “스위칭/표기” 중심으로 동작하며, 태스크 동작은 기존과 동일합니다(필요 시 후속 버전에서 에이전트별 Provider 분기 예정).
# 운영 업데이트 (v0.1.1)

- Fallback(Invoke 불가 시): Gemini가 레포에서 Invoke를 실행할 수 없으면 `context/messages.jsonl`에 한 줄 JSON을 추가해 요청을 남깁니다.
  - 예: `{"ts":"2025-08-11T12:34:56Z","from":"gemini","to":"codex","tags":["task","context"],"body":"README 섹션 A 수정 요청"}`
- 에이전트 라벨: `ACTIVE_AGENT='gemini'`를 설정해 세션 라벨을 구분합니다.
- MCP(선택): Gemini CLI는 MCP 지원이 내장되어 있으나, 본 레포는 파일/Invoke 중심으로 운영합니다. MCP 설정은 각 CLI 사용자 환경에서만 관리하세요.
## Self-Update Protocol(자가 업데이트)
- 정책 참조: `docs/SELF_UPDATE_POLICY.md`에 주기/범위/안전장치가 정의되어 있습니다.
- 허용 범위: 현재 단계(MVP)는 제안 생성까지만 허용합니다.
  - 실행: `invoke auto.scan` → `invoke auto.propose`
  - 산출물: `docs/proposals/auto_update_YYYYMMDD.md`
- 적용 단계: 자동 적용은 보류(OFF)이며 수동 적용만 허용합니다.
  - 리뷰 태스크/`invoke review_last` 및 `invoke git.commit_safe` 경유, 훅은 기본 OFF 유지.
