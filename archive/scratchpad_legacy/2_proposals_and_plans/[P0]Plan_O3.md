# \[P0] Foundational Enhancements 청사진

## 0. 목적/범위

* **목적:** Gemini CLI의 “기본 신뢰도·안정성·통제력” 확보.
* **범위:** 실행 파이프라인 표준화, 세션/커밋 자동화, 컨텍스트 엔진 구축, 문서/파일 보호, 테스트 하네스 정립.

---

## 1. 핵심 원칙(Behavior Rules)

1. **사용자 명령 최우선 / 독단 금지** – GEMINI.md에 명시.
2. **모든 실패는 기록(log\_usage)하고, 3회 반복 금지(3-Strikes Rule).**
3. **컨텍스트는 정책에 따라 검색·요약·주입 (임의 추측 금지).**
4. **문서·중요 파일은 보호 리스트 기반 삭제 방지(.no\_delete\_list).**

---

## 2. 산출물(Deliverables)

| 카테고리   | 파일/폴더                            | 내용                                             |
| ------ | -------------------------------- | ---------------------------------------------- |
| 정책/규약  | `GEMINI.md`                      | 행동 규칙, 메타인지 프로토콜                               |
| 자동화    | `tasks.py`                       | `start/end/wip/test/clean-cli/help` 등 태스크      |
| 실행기    | `scripts/runner.py`              | `subprocess.run(shell=False)` 표준 실행 래퍼 + 에러 로깅 |
| 컨텍스트   | `scripts/build_context_index.py` | 문서 메타데이터 인덱싱                                   |
| 컨텍스트   | `scripts/context_store.py`       | BM25+신선도 가중치 리트리버                              |
| 컨텍스트   | `scripts/prompt_builder.py`      | 정책에 따른 컨텍스트 조합                                 |
| 컨텍스트   | `.gemini/context_policy.yaml`    | 상황별 컨텍스트 주입 규칙                                 |
| 요약     | `scripts/summarizer.py`          | 간단 추출 요약기                                      |
| 기록/로그  | `scripts/usage_tracker.py`       | SQLite 로깅(usage 테이블)                           |
| 보호     | `.no_delete_list`                | 삭제 금지 파일 목록                                    |
| 디버그 문서 | `docs/debug/[P0]Debug_XX.md`     | 각 디버그 세션 기록 (19,20,21…)                        |
| 테스트    | `/tests/*.py`                    | 핵심 시스템/규칙 검증 (11개 기준)                          |
| 허브     | `docs/HUB.md`                    | 프로젝트/태스크 인덱스 문서                                |

---

## 3. 구현 단계(스테이지)

### P0-0: 베이스라인 & 규약 수립

* GEMINI.md 작성(행동 원칙, 금지사항).
* `.no_delete_list` 초기화.

### P0-1: 세션 자동화·커밋 절차

* `invoke start/end/wip` 태스크 구축.
* PowerShell 훅 문제 우회 → `python_wip_commit` 방식으로 교체.
* `hub_manager.py`로 `__lastSession__` 블록 자동 업데이트.

### P0-2: 안전 실행기 구축

* `scripts/runner.py` 도입: 리스트 인자 기반 `run_command`.
* 오류 발생 시 DB에 command\_error 이벤트 로깅.

### P0-3: 컨텍스트 엔진

* 인덱서(build\_context\_index.py) → index.json 생성.
* 리트리버(context\_store.py) + 요약기(summarizer.py).
* 프롬프트 빌더(prompt\_builder.py)로 정책 기반 컨텍스트 합성.

### P0-4: 문서/파일 보호

* `.no_delete_list` 활용 + `scripts/check_no_delete.py` (pre-commit 훅).
* Debug 문서, HELP 문서 등 핵심 파일 지속 추가.

### P0-5: 테스트 하네스/품질보증

* pytest 도입, 핵심 테스트 10\~11개 작성.
* CI 전 단계로 `invoke test` 정착.
* 실패한 `test_runner_error_logging` 근본 해결(의존성 주입/임시 DB).

### P0-6: 마감 & 머지

* 브랜치(p0/debug\_XX\_fix) → main 머지 & 태그(`v0.9.0-p0-final`).
* `README.md`, `HUB.md` 최신화.

---

## 4. DoD 체크리스트

* [ ] 모든 테스트(P0 범위) PASS / SKIP 명확 사유 1개 이하
* [ ] runner.py 에러 로깅 DB 구조 완성 & 테스트 검증
* [ ] 컨텍스트 엔진 정상 작동 (인덱싱/검색/요약/조합)
* [ ] 세션 자동화(start/end/wip) 완전 동작
* [ ] 중요 문서 삭제 방지 장치 동작(.no\_delete\_list)
* [ ] HUB.md / Debug 문서 최신 반영
* [ ] main 병합 후 working tree clean

---

## 5. 리스크 & 완화

| 리스크                     | 내용                     | 완화책                                  |
| ----------------------- | ---------------------- | ------------------------------------ |
| Windows PowerShell 훅 문제 | Git 훅에서 pwsh 미탐지       | 훅 우회 + Python 스크립트 직접 커밋             |
| 전역 변수(DB\_PATH) 문제      | pytest monkeypatch 불안정 | 함수 인자화, ENV 주입, reload               |
| 컨텍스트 초과                 | 길이/토큰 초과 시 실패          | 요약기·정책 max\_tokens, 캐시(후속 P2)        |
| 문서 누락/삭제                | 실수로 중요한 문서 삭제          | .no\_delete\_list + pre-commit check |

---

## 6. 브랜치/머지 가이드 (기록용)

```bash
git checkout main && git pull
git checkout p0/debug_18_fix && git pull
git checkout main && git merge --no-ff p0/debug_18_fix
# 충돌 해결 후
pytest -vv
git push origin main
git tag v0.9.0-p0-final && git push origin --tags
```

---

## 7. 후속 단계 연결

* **P1**: 도구/웹·멀티모달 준비, 능동적 액션
* **P2**: 성능 최적화, UX 정련, i18n, 보안/CI

---

필요 시 이 청사진을 `docs/roadmap/[P0]Foundational_Enhancements.md`로 저장하고 `.no_delete_list`에 추가하세요.
추가 정정/세부 코드 템플릿이 필요하면 말씀만 하세요. 대기합니다.
