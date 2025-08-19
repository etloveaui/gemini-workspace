> 한 번에 돌릴 수 있지만, **PR은 분리**(A→B→C) 권장.
> 에이전트가 코드 수정·커밋·PR 생성까지 처리합니다.

#### A) **CI 도입(PR-CI)** — Windows + pytest + Gitleaks (공통 적용을 위해 커밋)

# [Agent | PR-CI] Add Windows CI with pytest + Gitleaks

REPO: etloveaui/gemini-workspace
BRANCH: ci/windows-gitleaks
CHANGES:
- Add .github/workflows/ci.yml (Windows runner, setup-python@v5, pip cache, pytest -q, gacts/gitleaks@v1 with fetch-depth: 0)
- Add .github/gitleaks.toml (allowlist: ignore .gemini/** except .gemini/context_policy.yaml)

FILES:
/.github/workflows/ci.yml
--------------------------------
name: CI (Windows)
on:
  push: { branches: [ main, dev ] }
  pull_request:
jobs:
  build-test-and-scan:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: requirements.txt
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest -q
      - name: Gitleaks scan
        uses: gacts/gitleaks@v1
        with:
          config-path: .github/gitleaks.toml

/.github/gitleaks.toml
--------------------------------
[allowlist]
description = "Ignore .gemini except policy"
paths = [ "^\\.gemini/(?!context_policy\\.yaml)" ]

COMMIT: "ci(windows): add pytest + gitleaks on windows-latest"
PR TITLE: "ci(windows): add pytest + gitleaks"
PR BODY: 목적/변경사항/검증 포인트 요약

#### B) **실 Provider 전환(PR-SERPER)** — Serper.dev 기본 + 안전 폴백

# [Agent | PR-SERPER] Add Serper provider with safe fallback & docs

REPO: etloveaui/gemini-workspace
BRANCH: feature/serper-provider
GOAL: SERPER_API_KEY가 있으면 Serper(dev)로 검색. 없거나 실패 시 Exit Code=2로 종료(명확한 안내). 테스트/오프라인은 더미 유지(ENV: WEB_AGENT_TEST_MODE=1).

CHANGES:
1) scripts/tools/web_search.py
   - Implement search(query, top_k) that:
     - if os.getenv("WEB_AGENT_TEST_MODE") == "1": return deterministic dummy results (top_k)
     - elif SERPER_API_KEY set: call POST https://google.serper.dev/search with {"q": query, "num": top_k}
       map 'organic' -> [{title, url (link), snippet}]
     - else: raise ProviderNotConfigured
2) scripts/web_agent.py
   - try/except ProviderNotConfigured: print
     "Search provider not configured. Set SERPER_API_KEY or enable WEB_AGENT_TEST_MODE=1"
     and exit(2).
3) requirements.txt
   - ensure 'requests' is present (add if missing).
4) docs/HELP.md
   - add env setup section for SERPER_API_KEY and Exit Codes(0/2/4).
   - show example: invoke search -q "hello"

COMMIT: "feat(search): integrate Serper provider with Exit 2 fallback; keep dummy via WEB_AGENT_TEST_MODE"
PR TITLE: "feat(search): Serper provider + Exit 2 fallback"
PR BODY: 변경 요약, 동작 예시, 실패 시 메시지, 테스트 로그 첨부

#### C) **로컬 비밀 보호(PR-DPAPI)** — DPAPI 유틸 도입(윈도우 전용)

# [Agent | PR-DPAPI] Add Windows DPAPI utility for local secret encryption

REPO: etloveaui/gemini-workspace
BRANCH: feat/dpapi-utils
CHANGES:
1) scripts/utils/dpapi.py  (new)
--------------------------------
import win32crypt  # pywin32
from pathlib import Path
def encrypt_to_file(plaintext: bytes, path: str) -> None:
    blob = win32crypt.CryptProtectData(plaintext, None, None, None, None, 0)
    Path(path).write_bytes(blob)
def decrypt_from_file(path: str) -> bytes:
    blob = Path(path).read_bytes()
    _, data = win32crypt.CryptUnprotectData(blob, None, None, None, None, 0)
    return data
# NOTE: user-scope 기본. 동일 PC/동일 사용자에서만 복호 가능.

2) requirements.txt
   - add 'pywin32' (if missing)

3) docs/HELP.md
   - HowTo: ".gemini/*-local.json 내용을 secret.dat로 암호화/복호" 섹션 추가
   - 예시 코드와 주의점(user-scope, 이동 불가) 기재

COMMIT: "feat(security): add DPAPI utils (Windows user-scope) and HELP"
PR TITLE: "feat(security): Windows DPAPI utils for local secrets"
PR BODY: 목적/코드/주의점/샘플 커맨드

> 위 3개 PR이 병합되면, **운영 자동검증 + 실 Provider + 로컬 보안**까지 **완결**입니다.
> (에이전트가 질문하면 “레포=etloveaui/gemini-workspace, write 권한 사용”만 재확인해 주시면 됩니다.)