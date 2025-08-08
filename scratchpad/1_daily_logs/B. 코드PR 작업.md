## B. 코드/PR 작업 (당신은 승인만)

> 한 번에 돌릴 수 있으나, **PR은 분리** 권장(롤백/검증 용이). 아래 지시문을 복붙해 에이전트에 전달하세요.

### B-1) **Serper Provider + Exit 2 폴백** (필수)

# [Agent | PR-SERPER] Standardize provider path:
# - scripts/tools/web_search.py:
#   if WEB_AGENT_TEST_MODE=1 → deterministic dummy (top_k)
#   elif SERPER_API_KEY set  → call serper.dev (POST /search), map 'organic' → [{title, url=link, snippet}]
#   else → raise ProviderNotConfigured
# - scripts/web_agent.py: catch ProviderNotConfigured → print clear message → exit(2)
# - docs/HELP.md: add ENV & Exit Codes examples
# - requirements.txt: ensure 'requests' present
# COMMIT: "feat(search): Serper provider with Exit 2 fallback; keep dummy via WEB_AGENT_TEST_MODE"
# PR TITLE: "feat(search): Serper provider + Exit 2 fallback"

### B-2) **CI 수동 실행 허용(workflow\_dispatch)** (필수)

# [Agent | PR-CI-dispatch] In .github/workflows/ci.yml add:
# on:
#   push: { branches: [ main, dev ] }
#   pull_request:
#   workflow_dispatch:
# COMMIT: "ci: enable manual workflow dispatch"
# PR TITLE: "ci: enable workflow_dispatch"

### B-3) **DPAPI 유틸 가이드 보강** (권장·짧게)

# [Agent | PR-DPAPI-doc] docs/HELP.md:
# - Add "Windows DPAPI(user-scope) encrypt/decrypt" example
# - Note: same user/machine, file move not decryptable
# COMMIT: "docs(security): add DPAPI how-to and caveats"

> **중요:** `scripts/secret_reader.py`가 마크다운에서 키를 읽어 쓰는 경로는 **Deprecated**로 지정하십시오.
> 표준: **ENV → (로컬 필요 시) DPAPI 복호 → 메모리 주입**. 파일 평문 파싱 금지.