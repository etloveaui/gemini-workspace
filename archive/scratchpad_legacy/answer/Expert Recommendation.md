\[Role: Tech]

## 🤔 Strategic Analysis

핵심 이슈는 “동일 패치의 반복 시도”와 “실패 누적 재시도”로 인한 소모. 해결 레버는 edits\_manager의 diff-해시 기반 캐시·백오프를 표준 경로로 강제하고, usage.db 중심 통합 로깅과 토글형 우회 옵션을 제공하는 것.&#x20;

## 📝 Expert Recommendation

아래 순서로 바로 집행하세요. 각 항목은 목적→조치→검증 기준으로 기재.

1. 표준 경로 강제 (직접 치환 금지 기본화)

* 목적: 중복·실패 재시도 차단.
* 조치: tasks.py에서 `text.replace` 직호출을 `edits.capture→propose→diff→apply` 래퍼로 리다이렉트. `--force-direct`가 있을 때만 직호출 허용.
* 검증: 동일 요청 2회 연속 시 2번째가 “skip: recently\_applied”로 종료.

2. 캐시·백오프 파라미터 노출

* 목적: 운영 유연성.
* 조치: `edits_safety`의 성공 재적용 차단 윈도우(기본 60m), 실패 백오프 규칙(기본 3회/30m)을 `prefs`와 ENV로 설정화(`EDITS_SUCCESS_TTL_MIN`, `EDITS_FAIL_WINDOW_MIN`, `EDITS_FAIL_THRESHOLD`).
* 검증: 파라미터 변경 즉시 동작 반영.

3. 통합 로깅 단일화

* 목적: 단일 진실 공급원.
* 조치: `runner.run_command(check=False)` 경로도 usage.db에 실패 이벤트 기록. `edits_manager.record_result`가 usage.db와 `.agents/edits_state.json`을 동시 업데이트. 선택적 사람친화 로그 `.agents/edits_log.md` append.
* 검증: 동일 실패가 콘솔/DB/MD 세 경로에서 모두 확인 가능.

4. 스킵 사유 표준 메시지·코드

* 목적: 에이전트 오판 방지.
* 조치: `should_apply=False` 시 표준화된 원인코드 출력(`recently_applied`, `backoff_due_to_failures`)과 프로세스 종료코드 0(스킵), 2(백오프) 구분.
* 검증: 파이프라인에서 사유 파싱 가능.

5. textops 안전출력 확장

* 목적: 상위 판단 용이.
* 조치: `textops.py`에 `--dry-run`, `--json` 추가(치환 후보 수, 실제 치환 수, 라인엔딩 감지 결과 출력). 0건 치환은 종료코드 0 유지.
* 검증: `--dry-run`으로 파일 미변경, JSON 키 검증.

6. 우회 토글 제공

* 목적: 정당한 재적용 필요시 사용.
* 조치: `prefs.set edits_enforce false` 또는 `--no-enforce`로 캐시 무시 옵션. 사용 시 경고 배너 출력.
* 검증: 토글 시 즉시 재적용 허용.

7. 상태 관리 유틸

* 목적: 현장 운영 편의.
* 조치: `invoke edits.state show|purge|forget --key <diff_hash>|--file <path>` 구현.
* 검증: 특정 키 또는 파일 단위로 캐시 제거 가능.

8. 동시성 안전성

* 목적: 상태파일 경합 방지.
* 조치: `.agents/edits_state.json` 쓰기 시 파일락 또는 원자적 쓰기 헬퍼 적용 범위 확대.
* 검증: 병렬 5회 apply에서도 상태 손상 없음.

9. 테스트 스위트

* 목적: 회귀 방지.
* 조치: 단위: `should_apply`(성공 TTL, 실패 윈도우, 임계). 통합: capture→propose→diff→apply happy/skip/backoff 경로.
* 검증: CI에서 전경로 통과.

10. CLI 사용 패턴 가드

* 목적: 나쁜 호출 패턴 억제.
* 조치: `invoke text.replace` 실행 시 경고와 대안 제시(자동으로 edits 경로 사용 권고). 반복 호출 감지 시 안내 후 차단.
* 검증: 1분 내 동일 파라미터 2회 시 경고 노출.

11. HUB/리포트 연동

* 목적: 가시성 확보.
* 조치: HUB.md에 “Recent Edit Skips/Failures” 섹션 자동 갱신. 마지막 N건과 사유코드 요약.
* 검증: 작업 후 HUB에서 즉시 확인.

12. 문서화 패치

* 목적: 온보딩 단축.
* 조치: AGENTS.md와 P1-2 제안 문서에 표준 경로, 파라미터, 메시지 코드, 우회 절차, 유틸 사용법 추가.
* 검증: 신규 엔지니어가 문서만 보고 재현 가능.

### 실행 예시

* 제안 경로:
  `invoke edits.capture --file app.py` → `invoke edits.propose --file app.py --from proposal/app.py` → `invoke edits.diff` → `invoke edits.apply --yes`
* 상태 점검:
  `invoke edits.state show --file app.py`
* 캐시 우회 1회:
  `invoke edits.apply --yes --no-enforce`

### 완료 기준(DoD)

* 동일 diff 해시 재시도 시 2번째 요청이 100% 스킵 처리.
* 30분 내 동일 실패 3회 후 백오프 발동, 이후 윈도우 종료 전 모든 재시도 자동 차단.
* usage.db 질의로 최근 스킵·백오프 사유와 타임스탬프 확인 가능.
* CI 테스트 전경로 녹색.

추가 요청이 있으시면 알려주세요.
