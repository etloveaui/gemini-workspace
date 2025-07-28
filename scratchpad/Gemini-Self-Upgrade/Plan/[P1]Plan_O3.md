# \[P1] Core Feature Expansion 청사진

## 0. 목적/범위

* **목적:** P0에서 확보한 안정 기반 위에, **외부 도구 활용·능동 제안·멀티모달 준비·UX 진입점 강화**를 통해 Gemini CLI를 “작업을 제안하고 확장하는 에이전트”로 진화.
* **범위:**

  1. 툴(웹/파일/시스템) 연동 레이어 정립
  2. 능동 행동(프로액티브 프롬프트/제안) 정책화 & 구현
  3. 멀티모달 입력(이미지/표/JSON) 처리 파이프라인 준비
  4. Help/Doctor/Quickstart 등 **사용자 진입점 완성**
  5. 테스트/CI/문서 체계 동시 강화

---

## 1. 산출물(Deliverables)

| 카테고리 | 파일/폴더                                                           | 설명                                                           |
| ---- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| 정책   | `.gemini/context_policy.yaml`                                   | P1용 정책 섹션 추가 (tool\_use, proactive\_suggest 등)               |
| 문서   | `docs/HELP.md`                                                  | 전체 명령어/흐름/FAQ/트러블슈팅 문서                                       |
| 문서   | `docs/roadmap/[P1]Core_Feature_Expansion.md`                    | 본 청사진/체크리스트 본문                                               |
| 문서   | `docs/debug/[P1]Debug_XX.md`                                    | 단계별 디버그/이행 기록 시리즈                                            |
| 코드   | `scripts/tools/web_search.py`                                   | 단순 검색(요약 포함) 래퍼                                              |
| 코드   | `scripts/tools/file_analyzer.py`                                | CSV/JSON/Markdown 요약 & 질문 응답                                 |
| 코드   | `scripts/utils/time.py`                                         | UTC aware 시간 헬퍼 (P0 경고 제거도 여기서 처리)                           |
| 코드   | `scripts/help.py`, `scripts/doctor.py`, `scripts/quickstart.py` | CLI 진입점들                                                     |
| 코드   | `scripts/proactive_engine.py`                                   | “언제/무엇을 제안할지” 규칙 + 힌트 생성                                     |
| 태스크  | `tasks.py`                                                      | `help`, `doctor`, `quickstart`, `web.search`, `p1.init` 등 추가 |
| 테스트  | `tests/test_p1_web_tool.py`                                     | 웹 툴 호출·요약 검증                                                 |
| 테스트  | `tests/test_help_entrypoints.py`                                | help/doctor/quickstart 정상 동작 검증                              |
| 테스트  | `tests/test_proactive_engine.py`                                | 제안 로직(조건/출력) 검증                                              |
| 목록   | `.no_delete_list`                                               | 새 문서/핵심 스크립트 추가                                              |

---

## 2. 구현 단계(스테이지별)

### Stage P1-0: 준비 & 동기화

* **브랜치 생성:** `p1/core_feature_expansion_init`
* **P0 → main 병합 완료 확인** (이미 안 했으면 지금)
* `.no_delete_list` 업데이트 (P1 문서들)
* `docs/roadmap/[P1]Core_Feature_Expansion.md` 생성 (이 문서 그대로)

### Stage P1-1: Help/Doctor/Quickstart 진입점

1. `docs/HELP.md` 뼈대 작성 (명령어, 최초 세팅, 문제 해결 절차)
2. `scripts/help.py`

   * `python -m scripts.help <section>` 형태
   * Markdown 섹션 파싱 후 콘솔 출력
3. `scripts/doctor.py`

   * 체크: Python/Invoke/Git 버전, venv 유무, usage.db 쓰기권한, .no\_delete\_list 존재 등
   * 결과 요약 출력 + 수정 가이드
4. `scripts/quickstart.py`

   * 새 프로젝트/새 PC 세팅 안내(venv, invoke start, test 등 순서)
5. `tasks.py`에 태스크 추가:

   ```python
   @task
   def help(c, section="all"):
       c.run(f"python -m scripts.help {section}")

   @task
   def doctor(c):
       c.run("python -m scripts.doctor")

   @task
   def quickstart(c):
       c.run("python -m scripts.quickstart")
   ```
6. 테스트: `tests/test_help_entrypoints.py`

### Stage P1-2: UTC/시간 유틸 통일 (P0 경고 제거 연계)

* `scripts/utils/time.py` 작성:

  ```python
  from datetime import datetime, timezone
  def utcnow():
      return datetime.now(timezone.utc)
  ```
* `runner.py`, `usage_tracker.py` 등 `datetime.utcnow()` 사용 부분 전량 치환
* 단위 테스트: `tests/test_time_utils.py`

### Stage P1-3: 외부 툴 레이어(웹 검색 등)

* **최소 기능 목표:** 검색 요청 -> 결과 요약 -> 저장/출력
* `scripts/tools/web_search.py` (추상화):

  * 함수: `search(query, top_k=5)` -> 구조화 결과 반환(dict list)
  * 임시로 실제 API 호출은 Mock/인터페이스만, 나중에 키 세팅 시 실서비스
* `tasks.py`:

  ```python
  @task
  def web_search(c, q):
      c.run(f"python -m scripts.tools.web_search \"{q}\"")
  ```
* 테스트: `tests/test_p1_web_tool.py` (모킹 사용)

### Stage P1-4: 프로액티브 엔진(제안 시스템) 초석

* `scripts/proactive_engine.py`

  * 입력: 최근 로그/usage.db, 변경 파일, 실패 테스트
  * 출력: “이번에 할 만한 액션 3가지” 리스트 (예: “invoke doctor 실행”, “docs/HELP.md 업데이트 필요”)
* `invoke suggest` 태스크로 노출
* 테스트: `tests/test_proactive_engine.py` (샘플 로그 DB 주입 후 기대 제안 비교)

### Stage P1-5: 멀티모달 준비(파이프라인만)

* `scripts/tools/file_analyzer.py`

  * CSV/JSON 등 구조화 파일 요약 및 Q\&A (pandas 사용)
* 이미지/표 처리: 일단 파일경로 + 요약(텍스트 기반)까지만. 실 이미지 OCR 등은 P2로
* 테스트: `tests/test_file_analyzer.py`

### Stage P1-6: 문서/정책/테스트 통합

* `.gemini/context_policy.yaml`에 `p1_feature` 섹션 추가

  * 예: tool\_use=true, proactive=true 등 플래그
* `docs/HUB.md`에 P1 작업 등록(Active Tasks)
* `docs/HELP.md`에 새 태스크/툴 반영
* FULL 테스트(`pytest -vv`), `invoke doctor` 통과 확인

### Stage P1-7: 머지 & 태그

* main에 머지, 태그 `v1.0.0-p1`(예시)
* 필요 시 `CHANGELOG.md` 갱신

---

## 3. 체크리스트 (Definition of Done)

* [ ] main에 P0 반영 및 깨끗한 상태
* [ ] `docs/roadmap/[P1]Core_Feature_Expansion.md` 커밋
* [ ] Help/Doctor/Quickstart 구현 및 테스트 통과
* [ ] UTC DeprecationWarning 제거(모든 datetime 호출 점검)
* [ ] web\_search / file\_analyzer 스켈레톤 & 테스트 완료
* [ ] proactive\_engine 초기 버전 동작 & 테스트
* [ ] 정책/문서/태스크/리스트(.no\_delete\_list) 업데이트
* [ ] 전체 테스트 100% PASS, 0 ERROR (SKIP은 이유 명시)
* [ ] 릴리스 태그/브랜치 정리

---

## 4. 위험 요소 & 대응

* **외부 API 키/요금:** 기본은 Mock/인터페이스로만. 실제 키 주입은 ENV로 관리, 테스트는 모킹.
* **프로액티브 오남용:** P0의 메타인지 규칙 준수. 제안은 “사용자 승인 필요” 표시.
* **문서-코드 싱크:** Help 문서 수정 시 CI에서 diff 감지(선택).
* **멀티모달 과도 확장:** P1에선 텍스트/표/간단 분석까지만. 이미지/OCR은 P2.

---

## 5. 다음 단계 프리뷰(P2)

* 실제 웹 API/검색·요약 모델 연동
* 이미지/OCR/음성 입력 처리
* 장기 메모리/벡터스토어 정착
* 성능 튜닝 & 캐시 레이어

---

### 정리

* 이 문서 그대로 `docs/roadmap/[P1]Core_Feature_Expansion.md`로 저장.
* `.no_delete_list`에 추가.
* `p1/core_feature_expansion_init` 브랜치 시작 후 단계별 커밋.
* 필요시 바로 코드/테스트 템플릿 던져줄 수 있음.

**다음 액션 지시만 주시면 실행 단계로 들어갑니다.** 🙇‍♂️
(“P1-1부터 진행” 같은 식으로 콜 주세요.)
