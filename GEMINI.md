# GEMINI.md (v2 Final+)

## 0) 목적/범위
본 문서는 이 워크스페이스의 **운영 표준**이다. 목표는 **재현성**, **보안**, **신속한 인수인계**다. 모든 규정은 Windows 환경과 Python/Invoke 중심으로 정의한다.

## 1) 운영 원칙 (Windows-first)
- **Python 경로**: venv가 있으면 `%REPO%/venv/Scripts/python.exe`, 없으면 `sys.executable`.
- **셸/인코딩**: PowerShell 래핑 금지, 파이썬 프로세스 **직접 호출**. 표준 I/O는 **UTF-8** 고정.
- **작업 경계**: 파일 작업은 원칙적으로 **레포 경로 내부**에서 수행한다.

## 2) 디렉터리·추적 정책
- **`.gemini/`**: 설정·로컬 비밀 보관 위치.  
  - **커밋 금지**: `*.creds*.json`, `*oauth*.*`, 토큰류는 **로컬 전용(local-only)** 으로 보관하고 커밋하지 않는다.  
  - **추적 허용**: `.gemini/`에서 **`context_policy.yaml`만** 버전 추적을 허용한다.
- **`projects/`**: 로컬 전용 작업 공간. **항상 커밋 금지**(`.gitignore`에서 전면 차단).
- **pre-commit 가드**: `.githooks/pre-commit` + `scripts/hooks/precommit_secrets_guard.py`로  
  `.gemini/*(oauth|creds|token|secret|.json|.db|.sqlite|.pem|.p12|.key)` 및 `projects/` **스테이징 차단**.

## 3) 명령 표준 (Invoke)
- `invoke start` : 환경 점검(doctor) → HUB 브리핑 → 컨텍스트 인덱스 빌드  
- `invoke doctor`: 파이썬/권한/네트워크/경로/인코딩 점검  
- `invoke help [section]` : 도움말 출력  
- `invoke search -q "<질의>"` : 웹 검색 요약(기본: **ChatGPT 심층리서치 트리거**; 로컬 Provider 구현 시 동일 명령으로 동작)  
- `invoke context.build` / `invoke context.query "<q>"`  
- `invoke test` : pytest 실행  
- `invoke wip -m "<msg>"` : WIP 커밋  
- `invoke end` : 세션 종료(아카이브/로그/HUB 갱신)

**(로컬 1회 설정)** pre-commit 훅 활성화: `git config core.hooksPath .githooks`

**Exit Codes (표준)**  
- **0** 정상 / **2** Provider 미설정·불가 / **4** 예외(기타 오류)

## 4) 세션 라이프사이클
**Start**
1) `doctor` 실행 → 핵심 의존성/권한/인코딩 점검  
2) `docs/HUB.md`의 Active/Paused 요약, `git status --porcelain` 요약  
3) `context.build` 실행(인덱스 최신화)  
4) 이전 세션의 `__lastSession__` 블록이 있으면 정리 후 시작

**During**
- 동일 접근 3회 실패 시 **접근 전환(3-Strikes Rule)**  
- 결정/가정/실패 원인/수정 방향을 **즉시 로그**로 남긴다.

**End**
- `.gitignore` 상태 확인, 미커밋 변경은 `wip` 권고  
- HUB 상태 갱신(Active↔Paused), `__lastSession__` 블록에 핵심 요약 기록

## 5) 로깅·인수인계
- **중앙 허브**: `docs/HUB.md` — 상태(Active/Paused/Completed)와 각 작업 로그 링크 관리  
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
- **따옴표/인코딩**: PowerShell 래핑 대신 파이썬 직접 호출(UTF-8 보장)  
- **경로/권한**: 관리자 권한·경로 길이·파일 잠금 확인  
- **삭제 실패(Windows)**: `os.remove`/`shutil.rmtree` 우선  
- **검색 실패**: Provider 미설정 시 **Exit 2**. 기본은 **ChatGPT 심층리서치 트리거**로 안내

## 11) 변경관리
- 변경은 **게이트 승인 후** 적용(설계→리뷰→적용→검증).  
- **메타러닝 규칙**: 동일 목표 2회 실패+1회 성공 패턴은 규칙으로 제안, 3회 연속 성공 시 표준화.
