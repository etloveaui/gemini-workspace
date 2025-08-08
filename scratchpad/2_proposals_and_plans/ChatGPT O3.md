\[Role: Tech Expert]

## 🤔 Strategic Analysis

다섯 개의 LLM 제안들을 교차‑검토한 결과, **“Tool‑Planner + Auto‑Loop + 메타규칙 동기화”** 삼두마차를 갖추면 현재 승인‑중심 워크플로를 AI 주도형으로 전환하면서도 비용·보안·DX를 동시에 극대화할 수 있다.

---

## 📝 GEMINI CLI 개선 지시서 v3.0

| 우선순위   | 핵심 개선 블록                     | 구체적 지시 (필수 액션·근거)                                                                                                                                                                                                                                                                                                             |
| ------ | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0** | **운영 자동화 & 관측성**             | ● **토큰·비용·레이트리밋 대시보드 내장**: 모든 API 응답 헤더를 파싱해 `usage_stats.sqlite`에 축적, 세션·일·월 단위 요약을 HUB.md에 자동 삽입. 예산 80 % 초과 시 Slack DM 알림 트리거  <br>● **`.gitignore` 완전 자동토글**: `g start/end` 단계에서 PowerShell 스크립트로 `/projects/` 라인을 주석 전환·복원하고 실패 시 경고만 표시  <br>● **자동 WIP 커밋·로그 훅**: 체크포인트마다 `git diff`‑요약 → 5초 대기 후 자동 커밋 & log.md 업데이트  |
| **P0** | **Tool Planner + Auto‑Loop** | ● `tool_planner.py`: ReAct‑style 플래너가 파일읽기·웹검색·코드실행·이미지분석 도구를 그래프 형태로 자동 결선  <br>● `gemini --loop`: 테스트→lint→git status를 순환 호출, 실패 시 자동 롤백/수정하고 `_loops/` 폴더에 로그 저장                                                                                                                                                           |
| **P1** | **세션 메모리 & Drift Sync**      | ● `memory.sqlite`: 최근 N 세션 메타데이터를 저장, 재접속 시 상태·명령 히스토리 자동 Restore  <br>● 정책·문서·코드 불일치 자동 감지 → 수정안 제시(README↔코드, HUB↔폴더 구조 등)                                                                                                                                                                                                  |
| **P1** | **플러그인 SDK / Sandbox**       | ● `plugins/<name>/manifest.json` + `handler.py` 구조로 외부 MCP 도구를 핫스왑  <br>● 각 도구별 `permission.json`으로 FS·Network 권한을 선언하고 실행 전 Diff 검사                                                                                                                                                                                          |
| **P1** | **모델 비용 최적화**                | Flash Lite 기본, Pro는 대형 컨텍스트·복잡 리팩터일 때만 선택하는 `model_selector()` 헬퍼 함수 도입                                                                                                                                                                                                                                                       |
| **P2** | **멀티모달 + Deep Search**       | ● `--image` / `--pdf` 플래그 추가로 스크린샷, 다이어그램, PDF를 컨텍스트에 인라인  <br>● “Deep Search” 모드: 복잡한 질의 시 실시간 웹검색 결과를 컨텍스트에 자동 주입                                                                                                                                                                                                           |
| **P2** | **Think Harder 모드**          | `gemini -p "think harder:<prompt>"` 호출 시 추가 계산 쿼럼을 부여하여 세밀화 응답                                                                                                                                                                                                                                                                |
| **P2** | **DX 스위트**                   | ● `g new`, `g status`, `g template add` 등 명령으로 브랜치·HUB·비용 요약 자동 세팅  <br>● Task Runner(`invoke`/`Taskfile.yml`) 연동으로 SOP를 명령화 → 반복 피로도 감소                                                                                                                                                                                      |
| **P2** | **메타‑규칙 YAML화**              | GEMINI.md·settings.json·alias.json을 `.gemini/settings.yaml` 하나로 통합, CLI가 시작 시마다 파싱 → 규칙 동기화                                                                                                                                                                                                                                   |
| **P3** | **보안 & 실시간 감사**              | ● Win Credential Manager/1Password CLI로 API 키 Vaulting , pre‑push secret‑scanner 훅 내장  <br>● 민감 패턴 스캔·위험 Diff 검사 후 push 차단                                                                                                                                                                                                    |
| **P3** | **OS Auto‑Detect**           | 세션 초기화 시 OS·경로 구분자·환경변수를 자동 탐지하고 명령을 호환 포맷으로 변환                                                                                                                                                                                                                                                                               |

---

### ✨ 핵심 산출물 (Deliverables)

1. **`tool_planner.py`** – 도구 그래프 생성기
2. **`loop_runner.py`** – Auto‑loop 실행기
3. **`memory.sqlite`** – 세션 메모리 DB
4. **`settings.yaml`** – 통합 메타규칙 파일
5. **`dashboard.ps1`** – 토큰·비용 실시간 시각화 스크립트
6. **`plugins/README.md`** – SDK 가이드 & 예제

---

### ⏱️ 로드맵 (6‑주 Sprint)

| 주차     | 목표 마일스톤                               |
| ------ | ------------------------------------- |
| **W1** | P0 블록(대시보드·gitignore·WIP hook) 완료     |
| **W2** | Tool‑Planner & Auto‑Loop PoC → 내부 테스트 |
| **W3** | Memory DB, Drift Sync, YAML 메타규칙 통합   |
| **W4** | 플러그인 SDK·Sandbox·Model Selector 적용    |
| **W5** | 멀티모달·Deep Search·Think Harder 모드 통합   |
| **W6** | DX 스위트 정식 릴리즈 + 보안·감사 패키지 배포          |

---

### 🚀 Quick Wins (오늘 바로)

1. `powershell -File scripts/toggle_gitignore.ps1` 등록해 세션 토글 자동화 완료 (1 시간) 
2. `dashboard.ps1` 초안 작성 → 토큰·비용 CSV 생성 및 Slack Webhook 경보 (2 시간) 
3. `.gemini/settings.yaml` 스켈레톤 작성, GEMINI.md 내용 migrate (2 시간) 
4. `tool_planner.py` 최소 버전으로 파일 읽기→웹검색→코드 실행 흐름 테스트 (4 시간) 
5. `invoke tasks`: `start`, `end`, `status` 명령 등록 (1 시간) 

---

**지금 바로** `feature/v3-roadmap` 브랜치를 생성하고 위 로드맵대로 이슈·PR을 분할하세요.
추가 요청이 있으시면 알려주세요.
