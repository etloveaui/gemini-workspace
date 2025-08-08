### GLOBAL META RULES (CLI가 반드시 준수)

* **중단 금지 원칙**: 개별 단계 FAIL 시에도 전체 플로우 중단 금지. 단, 같은 원인으로 3회 연속 실패 시 “PAUSE & REPORT” → 원인/대안 제시 후 다음 단계 진행 여부 재확인.
* **로그 사이클**: 모든 주요 액션 후 `docs/tasks/<task>/log.md`에 Append. HUB.md `lastTouched` 갱신.
* **가드레일**:

  * `datetime.utcnow()` 재등장 금지 (pre-commit/CI grep).
  * 핵심 문서/스크립트 `.no_delete_list` 반영.
  * 테스트 100% PASS를 출고 기준으로 삼되, Warning은 0건 유지(UTC 등).
* **윈도우 환경 우선 고려**: 경로 표기는 `C:\Users\etlov\gemini-workspace\...` 기준, 쉘은 PowerShell/Invoke 기본.
* **패치 묶음 제공**: 주요 변경 후 `git diff > patches/<task>.patch` 저장(선택).
* **문서 업데이트 순서**: 작업파일 → 테스트 → 로그 → HUB.md → `.no_delete_list` → 커밋/푸시.

---

# ORDER BLOCK A — **\[P1-0-GMD] `GEMINI.md` v2 업그레이드**

### 0. 사전 점검

```bash
invoke test
```

* 결과 PASS/FAIL 여부만 기록(`docs/tasks/gemini-md-v2/log.md` 시작).

### 1. 브랜치 생성

```bash
git checkout -b p1/gemini_md_v2
```

### 2. 개정 범위 확정 (명시 + 자율권 정의)

**명시적으로 반드시 수정해야 할 섹션/내용 (WHAT & WHY & HOW):**

1. **메타인지/실패복구 프로토콜 세분화**

   * WHAT: 현재 “오류 진단→패치→재시도” 규칙을 유형별(네트워크/권한/외부API/로컬IO/논리오류) 체크리스트로 분리.
   * WHY: 재현성/자동화 가능성 제고, 중복진단 감소.
   * HOW: `GEMINI.md`에 “Error Matrix” 표 삽입. 예:

     * 네트워크 실패 → 재시도 N회, 백오프, Proxy 확인
     * 권한 실패 → 관리자 권한 체크, 파일 잠금 해제 스크립트 안내
     * 외부 API 실패 → Mock fallback or cached data 사용
     * …

2. **로깅/리포팅 사이클 구체화**

   * WHAT: “표준 로깅 사이클”을 단계별(Plan→Exec→Log→Commit)로 명문화하고, 각 단계에서 최소 기록 항목 지정.
   * WHY: HUB/log 일관성, 추적성 강화.
   * HOW: 예시 템플릿을 `GEMINI.md`에 바로 삽입(표 또는 코드블럭).

3. **Windows 특화 운영 규칙 추가**

   * WHAT: 경로/인코딩/권한/PowerShell vs cmd 차이/venv 활성화 등 OS별 포인트를 별도 섹션.
   * WHY: 실제 운영환경이 Windows여서 빈번히 발생하는 이슈 예방.
   * HOW: “Windows Ops Checklist” 섹션 추가. 예: CodePage 65001, git config core.autocrlf, PSExecutionPolicy 등.

4. **자율성 vs 통제권 경계선 명시**

   * WHAT: CLI(에이전트)가 자율로 수정 가능한 범위(예: 주석/문서 보강, 경로 정규화, 테스트 보조코드)와 반드시 사용자 승인 필요한 범위(예: API Key 처리, 보안 정책 변경, 의존성 추가/제거) 구분.
   * WHY: 안전한 자율 실행.
   * HOW: `ALLOW LIST` / `REQUIRE APPROVAL LIST` 두 리스트를 GEMINI.md에 테이블로.

5. **도구 온보딩 SOP**

   * WHAT: 새 도구(웹 검색, 파일 변환기 등) 추가 시 체크리스트(Interface 정의, Mock 테스트, CI 등록, HELP/HUB 업데이트).
   * WHY: 확장 시 일관성 유지.
   * HOW: “New Tool Integration SOP” 섹션 추가.

6. **CI/Hook 연계 규칙**

   * WHAT: pre-commit / GitHub Actions / local CI 스크립트에서 최소 실행 세트 명시(pytest, lint, forbidden patterns grep).
   * WHY: 품질 자동 보증.
   * HOW: 해당 섹션에 예시 YAML/Hook 스크립트 삽입.

> **자율권 부여**: 위 6개 항목 외 세부 문장 구성, 문서 구조 재배열, 용어 통일, 예시 코드/표 추가는 CLI 재량. 단, 삭제는 금지(기존 규칙 보존).

### 3. 실행 단계

#### 3-1. Phase 1 — 외부 컨설트 프롬프트 준비(옵션)

* 파일: `docs/proposals/GEMINI_MD_v2_PROMPT.md`
* 내용: 현재 GEMINI.md 전문 + 개선 질문 리스트.
* 사용자 OK 시 다른 LLM/모델에 투입 후 결과 수집.

> **시간 단축 시**: 외부 컨설트 생략 가능. 단, 생략 시 “생략 사유” log에 기록.

#### 3-2. Phase 2 — Draft 작성

```bash
mkdir -p docs/proposals/gemini-md-v2
```

* 파일: `docs/proposals/gemini-md-v2/DRAFT.md`

  * 구조: 섹션별 `현재 내용 / 제안 변경 / 근거(Why)`
  * 위 6개 필수항목 + 외부 컨설트 제안 통합

#### 3-3. Phase 3 — 본문 반영

* 사용자 승인 후 `GEMINI.md` 수정.
* “CHANGELOG” 섹션에 버전/날짜/주요 변경점 기록.

### 4. 테스트/가드 추가

* `.githooks/pre-commit.utc_guard` 유사하게 `pre-commit.gemini_guard` 생성:

  * 금지 패턴(예: `datetime.utcnow`, `print(` 디버그 잔재, `TODO:` 미정리) 검출 시 커밋 차단.
* CI(YAML) 템플릿 (`.github/workflows/ci.yml` or `.ci/ci.ps1`) 작성은 선택, 초안만 두어도 됨.

### 5. 문서 & 리스트

* `.no_delete_list`에 다음 추가(중복 시 무시):

  ```
  GEMINI.md
  docs/proposals/gemini-md-v2/DRAFT.md
  docs/tasks/gemini-md-v2/log.md
  .githooks/pre-commit.gemini_guard
  ```
* `docs/HUB.md` Active Tasks → `[P1-0-GMD] GEMINI.md v2` 등록.

### 6. 커밋 & 푸시

```bash
git add GEMINI.md docs/proposals/gemini-md-v2 docs/tasks/gemini-md-v2 .no_delete_list .githooks
git commit -m "feat(P1-0-GMD): GEMINI.md v2 upgrade (meta rules, SOP, guardrails)"
git push origin p1/gemini_md_v2
```

### 7. 머지

```bash
git checkout main && git pull
git merge --no-ff p1/gemini_md_v2
pytest -vv
git push origin main
```

### 8. DoD (Definition of Done)

* GEMINI.md v2 반영 + CHANGELOG 기재.
* 필수 6개 항목 반영 확인.
* Guard 훅/CI 템플릿 도입.
* 테스트/doctor PASS, Warning 0.
* HUB/HELP/NO\_DELETE\_LIST 업데이트 완료.

---

# ORDER BLOCK B — **\[P1-1] Web Agent Integration**

### 0. 사전 점검

```bash
invoke test
```

* 결과를 `docs/tasks/web-agent-integration/log.md`에 기록.

### 1. 브랜치

```bash
git checkout -b p1/web_agent_integration
```

### 2. 구조/파일

```
scripts/tools/web_search.py         # 검색 추상화(search(query, top_k=5))
scripts/web_agent.py                # 검색→요약 파이프라인 main
scripts/summarizer.py               # 없으면 생성, 기존 엔진 재사용 가능
tasks.py                            # invoke search 태스크
tests/test_p1_web_tool.py           # 모킹 테스트
docs/tasks/web-agent-integration/log.md
docs/HELP.md                        # invoke search 섹션 추가
docs/HUB.md                         # Active Task 반영
.no_delete_list                     # 위 신규 핵심 파일 등록
```

### 3. 구현 상세

#### 3-1. `scripts/tools/web_search.py`

```python
# pseudo-code
import os

def search(query: str, top_k: int = 5) -> list[dict]:
    """
    Return: [{ "title": "...", "url": "...", "snippet": "..." }, ...]
    Real API call abstracted; in tests use monkeypatch to mock this function.
    """
    # TODO: implement real call or placeholder
    raise NotImplementedError
```

#### 3-2. `scripts/web_agent.py`

```python
import sys
from scripts.tools.web_search import search
from scripts.summarizer import summarize

def main():
    # args: --query "..." --top_k 5 ...
    q = _parse_args(sys.argv)   # implement simple parser or argparse
    results = search(q, top_k=5)
    merged = "\n\n".join(r["snippet"] for r in results)
    summary = summarize(merged, max_tokens=400)
    print(summary)

if __name__ == "__main__":
    main()
```

#### 3-3. `tasks.py`

```python
import sys
from invoke import task

@task
def search(c, q):
    """invoke search \"<query>\" : web search + summarize"""
    c.run(f'"{sys.executable}" -m scripts.web_agent --query "{q}"', pty=True)
```

#### 3-4. `summarizer.py`

* 기존 컨텍스트 엔진 있으면 래핑. 없으면 간단 요약(문장 상위 N개) 임시 구현 가능.
* 추후 LLM요약으로 교체하기 쉽게 인터페이스 분리.

### 4. 테스트 (`tests/test_p1_web_tool.py`)

```python
import subprocess, sys
from unittest.mock import patch

DUMMY_RESULTS = [
    {"title": "Python", "url": "https://python.org", "snippet": "Python official website."},
    {"title": "Docs", "url": "https://docs.python.org", "snippet": "Documentation for Python."},
]

def test_web_agent_with_mocked_search(tmp_path, monkeypatch):
    monkeypatch.setattr("scripts.tools.web_search.search", lambda q, top_k=5: DUMMY_RESULTS)
    r = subprocess.run([sys.executable, "-m", "scripts.web_agent", "--query", "Python"], text=True, capture_output=True, check=True)
    assert "Python official website" in r.stdout or "Documentation" in r.stdout

def test_invoke_search_task(monkeypatch):
    monkeypatch.setattr("scripts.tools.web_search.search", lambda q, top_k=5: DUMMY_RESULTS)
    r = subprocess.run([sys.executable, "-m", "invoke", "search", "Python"], text=True, capture_output=True, check=True)
    assert "Python official website" in r.stdout
```

### 5. 문서화/보호

* `docs/HELP.md`: “invoke search” 설명/예시 추가.
* `.no_delete_list` 갱신.
* `docs/HUB.md` Active Task 업데이트.

### 6. 커밋/푸시/머지

```bash
git add scripts docs tests tasks.py .no_delete_list
git commit -m "feat(P1-1): web agent integration (search tool, summarize, tests)"
git push origin p1/web_agent_integration

git checkout main && git pull
git merge --no-ff p1/web_agent_integration
pytest -vv
git push origin main
```

### 7. DoD

* `invoke search "Python official website"` → 요약 출력.
* 모든 테스트 PASS / Warning 0.
* HUB/HELP/NO\_DELETE\_LIST 반영.
* Log 파일에 전 과정 기록.

---

## 추가 권장(선택)

* **CI 파이프라인 초안**: `.github/workflows/ci.yml` or `.ci/ci.ps1`

  * Steps: setup-python → pip install → invoke test → grep forbidden patterns.
* **pre-commit config**: `.pre-commit-config.yaml`에 ruff/flake8/forbidden-string hook 등록.
* **Patch exporter**: `git diff main...HEAD > patches/P1-1.patch`

---

끝. 다음 액션 키워드만 주면 된다:

* `P1-0-GMD GO` → GEMINI.md v2 작업 시작
* `P1-1 GO` → Web Agent 통합 시작

추가 요청이 있으시면 알려주세요.
