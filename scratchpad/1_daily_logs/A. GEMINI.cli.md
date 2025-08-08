### 0) 현황 핵심 메모

* `GEMINI.md v2`는 원칙·추적정책·Exit Codes·DoD가 일관됩니다(좋음). 다만 **훅 활성화(로컬 1회)**, **“PR 병합=CI 통과”** 두 문장만 추가하면 완결에 가깝습니다.
* 작업 로그에는 `scripts/*` 신규 모듈, CI/Serper/DPAPI 추가가 기재되어 있습니다. 원격에 현재 모두 반영된 것으로 보이지만, **CI 실행 기록(0회)** 과 **Serper 동작 경로/Exit 2 반환**은 반드시 **로컬에서 검증**해야 합니다.
* 민감정보는 **절대 평문 보관 금지**. 현재 구조(마크다운 파일에 키 보관 후 모듈이 읽어 사용)는 **설계상 위험**이므로, **ENV/DPAPI**로 전환하고 파일은 **로컬 전용·암호화**로 고정합니다.

---

## A. GEMINI.cli — **당신이 지금 바로 실행할 지시서** (선택 없음 · 복붙용)

> 경로: `C:\Users\eunta\gemini-workspace` / 셸: PowerShell

### A1) 보안 핫픽스 (필수)

powershell
cd C:\Users\eunta\gemini-workspace

# 1) secrets/ 디렉터리 보장 및 민감파일 이동(로컬만; Git 추적 금지 경로)
mkdir secrets -Force
# (my_sensitive_data.md가 레포 루트/다른 경로에 있다면)
if (Test-Path .\my_sensitive_data.md) { Move-Item .\my_sensitive_data.md .\secrets\my_sensitive_data.md -Force }

# 2) .gitignore에 secrets/ 제외 확인(없으면 추가 후 커밋)
#   줄:  'secrets/'  또는 'secrets/**'
#   이미 있다면 건너뜀
notepad .gitignore
git add .gitignore
git commit -m "chore(security): ignore secrets/ directory"  # 변경 없으면 스킵

# 3) 혹시 과거에 잘못 추적된 비밀이 있으면 인덱스에서 제거(있을 때만)
git rm --cached -r secrets  # tracked였다면
git commit -m "chore(security): remove secrets from index"  # 변경 없으면 스킵

> **즉시 권고:** `secrets/my_sensitive_data.md`에 기록된 **모든 키/토큰은 회전(재발급·폐기)** 하십시오. (Google API/OAuth, Serper, GitHub PAT, 타 서비스 계정 등)
> **원칙:** 실행 시에는 **ENV 우선**, 파일은 \*\*로컬 암호화(아래 DPAPI)\*\*로만 보관.

### A2) CI 1회 성공(증빙 확보)

powershell
# 빈 커밋으로 트리거
git commit --allow-empty -m "ci: trigger"
git push
# GitHub Actions에서 "CI (Windows)"가 Success로 1회 찍히는지 확인

### A3) 검색 Provider 경로 검증

powershell
# (1) 더미 모드 검증
$env:WEB_AGENT_TEST_MODE="1"
invoke search -q "hello"      # 5±1 결과 요약 기대 (정상=Exit 0)
$LASTEXITCODE

# (2) 실 Provider 검증 (Serper)
Remove-Item Env:\WEB_AGENT_TEST_MODE -ErrorAction SilentlyContinue
$env:SERPER_API_KEY="<YOUR_KEY>"
invoke search -q "gemini workspace"
$LASTEXITCODE                 # 정상=0, 미설정/불가=2, 예외=4  → 2 규약 준수 확인

* **규약 미충족 시**(예: 미설정인데 4 반환): 아래 **B-1 에이전트 패치**로 즉시 교정.

### A4) 훅/가드 자가시험(각 PC 1회)

powershell
git config core.hooksPath .githooks
git update-index --chmod=+x .githooks/pre-commit

Set-Content .gemini\google.creds-local.json "{}"
git add .gemini\google.creds-local.json   # ← pre-commit이 차단되어야 정상

Set-Content projects\do-not-commit.txt "x"
git add projects\do-not-commit.txt        # ← 차단되어야 정상


### A5) HUB 반영(증빙 필수)

* `docs/HUB.md`에서 **\[P1-1] Web Search Tool** → **Completed** 이동
* `__lastSession__`에 아래 **4가지 증빙** 한 줄씩 기록

  1. `pytest -q` 통과
  2. `invoke search` 더미/실 Provider 결과 정상
  3. pre-commit 훅 차단 작동
  4. CI 1회 성공 기록

powershell
git add docs\HUB.md
git commit -m "docs(hub): complete P1-1 with test/search/hook/CI evidence"
git push
