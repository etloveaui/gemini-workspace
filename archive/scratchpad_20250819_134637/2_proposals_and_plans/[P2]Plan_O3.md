# \[P2] System Optimization & UX Refinement 청사진

## 0. 목적/범위

* **목적:** P0(안정화) + P1(기능 확장)을 바탕으로 **성능·유지보수성·사용자 경험(UX)·다국어 지원·보안/컴플라이언스**를 정교하게 다듬어 “프로덕션급 품질”을 달성.
* **범위:**

  1. 실행 속도/메모리 최적화 & 캐싱 레이어 구축
  2. 장기 메모리(벡터스토어) 및 세션 간 지식 지속성 개선
  3. CLI/문서 UX 정비(자동완성, 리치로그, 에러 힌트)
  4. 다국어(특히 한/영) 동시 지원 정책 및 테스트
  5. 보안(토큰/키 관리)·권한체계·로그 개인정보 마스킹
  6. CI/CD 파이프라인·릴리스 전략 정립

---

## 1. 산출물(Deliverables)

| 카테고리  | 파일/폴더                                            | 설명                                                             |
| ----- | ------------------------------------------------ | -------------------------------------------------------------- |
| 정책    | `.gemini/context_policy.yaml`                    | P2 섹션 추가 (memory\_cache, i18n, perf\_profile 플래그)              |
| 문서    | `docs/roadmap/[P2]System_Optimization_and_UX.md` | 본 청사진/체크리스트 본문                                                 |
| 문서    | `docs/UX_GUIDE.md`                               | CLI 사용성 가이드 & 키보드 단축키/패턴                                       |
| 문서    | `docs/SECURITY.md`                               | 키/토큰 관리, 로그 마스킹 규칙                                             |
| 코드    | `scripts/cache/`                                 | LRU/File-based 캐시 모듈 (검색/요약 결과 등)                              |
| 코드    | `scripts/memory/vector_store.py`                 | 장기 메모리(FAISS/SQLite+embeddings) 인터페이스                          |
| 코드    | `scripts/i18n/`                                  | 메시지 번역 리소스(json), i18n 헬퍼                                      |
| 코드    | `scripts/cli/formatter.py`                       | 컬러 로그, 표 렌더링, 에러 힌트 출력 유틸                                      |
| 코드    | `scripts/security/secrets_manager.py`            | ENV, .env, keyring 연동 (mock 가능)                                |
| 태스크   | `tasks.py`                                       | `doctor` 강화, `perf.profile`, `cache.clear`, `mem.rebuild` 등 추가 |
| 테스트   | `tests/test_p2_perf_cache.py`                    | 캐시 hit/miss, 속도 개선 검증                                          |
| 테스트   | `tests/test_p2_memory_store.py`                  | 벡터스토어 CRUD, 검색 정확도 테스트                                         |
| 테스트   | `tests/test_p2_i18n.py`                          | 한/영 메시지 동등성 검증                                                 |
| 파이프라인 | `.github/workflows/ci.yml` or `/.gitlab-ci.yml`  | Lint/Test/Build/Release 자동화 (이미 있다면 고도화)                       |
| 릴리스   | `CHANGELOG.md`, 태그/릴리스 노트                        | v1.1.0-p2 등 릴리스 문서                                             |

---

## 2. 구현 단계(스테이지별)

### Stage P2-0: 브랜치/기초 세팅

* 브랜치: `p2/system_opt_ux_init`
* `.no_delete_list`에 P2 문서/핵심 코드 추가
* `docs/roadmap/[P2]System_Optimization_and_UX.md` 커밋

### Stage P2-1: 캐싱 & 퍼포먼스 프로파일링

1. **프로파일링 도구 선택**: `cProfile`/`pyinstrument` 등 간단히 래핑

   * `invoke perf.profile --cmd "invoke start"` 형태
2. **캐시 레이어 설계**

   * 키: (query, policy, version) → 값: 결과 요약/검색 리스트
   * 만료 정책: TTL or 파일 변경 hash 기반
   * 구현: `scripts/cache/simple_cache.py` (JSON on disk + SHA1 key)
3. 기존 컨텍스트 빌더/웹 툴 호출에 캐시 적용 (옵션 플래그로 on/off 가능)
4. 테스트: 속도 비교(캐시 hit 시), 캐시 무효화 확인

### Stage P2-2: 장기 메모리/벡터스토어

1. `scripts/memory/vector_store.py`

   * 인터페이스: `add(doc_id, text, meta)`, `search(query, top_k)`
   * 구현: 간단히 SQLite+embedding or FAISS(옵션)
   * Embedding: 로컬 간이 TF-IDF → 후속 교체 가능하도록 추상화
2. 컨텍스트 정책에서 `long_memory: true`면 vector\_store 검색 포함
3. 테스트: 인덱싱/검색 정확성·성능 (mock 텍스트로)

### Stage P2-3: I18N(다국어 지원) & 메시지 레이어

1. `scripts/i18n/messages_ko.json`, `messages_en.json` 준비
2. `i18n.get("cli.help.header", lang)` 같은 헬퍼 작성
3. `tasks.py`의 출력/에러 메시지를 i18n 호출로 대체
4. 기본 언어 선택 로직: ENV(`GEMINI_LANG`), 또는 config 파일(.gemini/config.yaml)
5. 테스트: 한국어/영어 메시지 동등성, fallback 동작

### Stage P2-4: UX 개선(출력 Formatter, 자동완성)

1. `scripts/cli/formatter.py`

   * 컬러(ansi), 표(tabulate), 경고/에러 강조
2. 자동완성(template):

   * PowerShell/ bash completion 스크립트 생성 (선택)
   * `invoke help`에 completion 설치 안내
3. `doctor` 개선: 문제 발견 시 바로 해결 커맨드 제안 메시지

### Stage P2-5: 보안/컴플라이언스

1. `scripts/security/secrets_manager.py`

   * ENV 우선, 없으면 .env/.secrets.json, 필요시 keyring (옵션)
   * get\_secret("OPENAI\_API\_KEY") 등 API
2. 로그 마스킹: runner/log\_usage 등에서 키/토큰/민감정보 정규식 마스킹 후 기록
3. `docs/SECURITY.md` 작성 (수집/보관/삭제 정책)

### Stage P2-6: CI/CD, 릴리스 파이프라인

1. GitHub Actions/GitLab CI 설정

   * lint(ruff/flake8), test(pytest), build(dist), release(tag+changelog)
2. `invoke release --tag v1.1.0-p2` 자동화 태스크 (changelog 생성 포함)
3. 테스트: CI에서 성공적으로 작동 확인

### Stage P2-7: 통합 검증 & 머지

* 전체 테스트 `pytest -vv` 100% PASS
* `invoke doctor` 문제없음
* main에 머지, 태그 `v1.1.0-p2-final`
* `README.md`/`HUB.md`/`HELP.md` 업데이트

---

## 3. 체크리스트 (Definition of Done)

* [ ] P2 문서/정책/코드/테스트 작성 & 커밋
* [ ] 캐시·프로파일링 도입, 속도 개선 수치(예: 컨텍스트 빌드 40% 단축) 기록
* [ ] 벡터스토어 기반 장기 메모리 검색 정상 동작
* [ ] 한/영 i18n 완비, 기본 한국어 출력(설정에 따라 전환)
* [ ] secrets 관리 & 로그 마스킹 테스트 통과
* [ ] CI/CD 파이프라인 구축 및 자동 릴리스
* [ ] 전체 테스트 PASS / SKIP 사유 명시
* [ ] 문서/HELP/HUB 최신 반영
* [ ] main 병합 + 태그 발행

---

## 4. 위험요인 및 대응

| 위험      | 내용               | 대응                                     |
| ------- | ---------------- | -------------------------------------- |
| 캐시 일관성  | 변경된 문서/코드 반영 안 됨 | SHA1/mtime 체크, `invoke cache.clear` 제공 |
| 메모리 비용  | 벡터스토어 크기 증가      | 세그먼트/압축/TTL 전략, 필요 시 외부 DB로 이동         |
| i18n 누락 | 메시지 추가 시 번역 누락   | CI에서 msg key scan & 비교                 |
| 키/토큰 유출 | 로그/에러 출력에 노출     | 마스킹, SECURITY.md 원칙 준수                 |
| CI 속도   | 테스트 많아 느림        | 캐시 활용, 테스트 분할/병렬화                      |

---

## 5. 이후(선택적) 로드맵 프리뷰

* **P3(선택):** 진짜 멀티모달(이미지 OCR/LLM Vision), Auto-PR generation, Web UI 대시보드
* 운영 배포(패키지화/PyPI), 플러그인 생태계, 사용자 템플릿/워크플로우 공유 등

---

### 정리

* 이 청사진을 `docs/roadmap/[P2]System_Optimization_and_UX.md`로 저장하고 `.no_delete_list`에 추가하세요.
* “P2-1부터 진행” 같은 식으로 지시하면 세부 코드/테스트 템플릿 바로 드릴 수 있습니다.
* P2 완료 시, ‘Gemini CLI v1.1.0 (P2 완료)’ 레벨로 안정+확장+최적화된 상태가 됩니다.

필요한 추가 포인트나 수정 사항 있으면 말씀만 주세요. 대기 중입니다.
