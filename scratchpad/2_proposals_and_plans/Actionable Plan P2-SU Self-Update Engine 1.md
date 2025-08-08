\[Role: Tech Expert]

## 🤔 Strategic Analysis

핵심: \*\*P2-SU는 P1-2 파일 에이전트의 “자동 고객”\*\*입니다. 흐름은 **scanner → proposer → file\_agent(invoke refactor) → tester → committer/report**이며, 모든 자동 적용은 **`SELF_UPDATE_POLICY.md` + `--dry-run` → `--yes` 2단계**를 강제합니다.  &#x20;

---

## 📝 Expert Recommendation — **\[최종 작업 지시서] P2-SU Self-Update Engine 구축**

### A) 디렉터리·원칙

```
scripts/auto_update/
  ├── scanner.py      # 변화 감지
  ├── proposer.py     # 제안/명령 생성
  ├── apply.py        # 정책 기반 자동 적용(+롤백)
  └── __init__.py
docs/
  ├── proposals/auto_update_YYYYMMDD.md
  └── SELF_UPDATE_POLICY.md
```

* **운영원칙**: Windows-first, `shell=False`, UTF-8, **레포 경계 내부만 접근**(경로 `.resolve()` 후 하위 여부 검증). 모든 변경은 테스트 통과 전제.&#x20;
* **시스템 흐름**: scanner → proposer → **invoke refactor** → test → commit/report.&#x20;

---

### B) 모듈별 구현 지침 & 스켈레톤

#### B-1) `scanner.py` — 변화 수집/정규화

**목표**: (1) `pip list --outdated` (JSON) 수집, (2) `pytest`에서 `DeprecationWarning` 추출 → **정규화된 Finding** 목록 반환.&#x20;

스키마:

```python
# scripts/auto_update/scanner.py
from __future__ import annotations
import json, re, subprocess, sys
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Finding:
    kind: Literal["update_dependency","replace_deprecated"]
    payload: dict          # 예: {"name":"requests","current":"2.25.1","latest":"2.28.1"}
    evidence: str          # 원문 한 줄/요약
    file_hint: str|None    # "requirements.txt" 또는 추정 타겟 파일

def scan_outdated_packages() -> list[Finding]:
    cmd = [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=False)
    items = json.loads(res.stdout or "[]")
    return [
      Finding("update_dependency",
              {"name": it["name"], "current": it["version"], "latest": it["latest_version"]},
              f"pip: {it['name']} {it['version']} -> {it['latest_version']}",
              "requirements.txt")
      for it in items
    ]

def scan_deprecations(pytest_args: list[str]|None=None) -> list[Finding]:
    args = ["pytest","-q","-W","default","-rA"] + (pytest_args or [])
    res = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", shell=False)
    pat = re.compile(r"DeprecationWarning: (?P<msg>.+)")
    return [Finding("replace_deprecated", {"message": m.group("msg")}, m.group(0), None)
            for m in pat.finditer(res.stdout + res.stderr)]

def run() -> list[Finding]:
    return scan_outdated_packages() + scan_deprecations()
```

> 주기/소스는 **pip outdated + DeprecationWarnings**가 1차 범위. 향후 릴리즈 노트·규칙 위반 스캔으로 확장.&#x20;

---

#### B-2) `proposer.py` — 제안서/명령 생성

**목표**: Finding → 정책 해석 → **제안서 MD**와 **`invoke refactor` 명령**(우선 `--dry-run`) 생성. **자동 승인**이면 `--yes` 재실행을 지시.&#x20;

정책 파서 & 매핑:

```python
# scripts/auto_update/proposer.py
from __future__ import annotations
import datetime as dt
from pathlib import Path
from .scanner import Finding, run as scan_run

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT/"docs/SELF_UPDATE_POLICY.md"
PROPOSALS = ROOT/"docs/proposals"

def load_policy(md_path: Path) -> dict[str, dict]:
    text = md_path.read_text(encoding="utf-8")
    rows = {}
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    for ln in lines[2:]:
        cols = [c.strip() for c in ln.strip("|").split("|")]
        if len(cols) < 6: continue
        rule = cols[0].strip("* ")
        rows[rule] = {
            "risk_level": cols[2],
            "auto_approve": cols[3].lower().startswith(("y","t")),
            "test_required": cols[4].lower().startswith(("y","t")),
            "desc": cols[5],
        }
    return rows

def map_to_commands(findings: list[Finding], policy: dict) -> list[dict]:
    cmds=[]
    for f in findings:
        if f.kind=="update_dependency":
            p = policy.get("update_dependency", {})
            cmds.append({
              "how": f"invoke refactor --file requirements.txt --rule update_dependency "
                     f"--package {f.payload['name']} --version {f.payload['latest']} --dry-run",
              "auto": p.get("auto_approve", False), "test_required": p.get("test_required", True),
              "evidence": f.evidence
            })
        elif f.kind=="replace_deprecated":
            p = policy.get("replace_deprecated", {})
            cmds.append({
              "how": "invoke refactor --file <detect_target>.py --rule replace_api "
                     "--old-name OldFunc --new-name NewFunc --dry-run",
              "auto": p.get("auto_approve", False), "test_required": p.get("test_required", True),
              "evidence": f.evidence
            })
    return cmds

def write_proposal(cmds: list[dict]) -> Path:
    PROPOSALS.mkdir(parents=True, exist_ok=True)
    path = PROPOSALS / f"auto_update_{dt.datetime.now():%Y%m%d}.md"
    lines = ["# Auto-Update Proposal", "## Items"]
    for c in cmds:
        lines += [
          f"- Evidence: {c['evidence']}",
          f"- Auto-Approve: {c['auto']} / TestRequired: {c['test_required']}",
          f"- HOW: `{c['how']}`"
        ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

def run() -> Path:
    policy = load_policy(POLICY)
    cmds = map_to_commands(scan_run(), policy)
    return write_proposal(cmds)
```

> **명령 포맷**은 반드시 `invoke refactor --file <파일> --rule <규칙> [옵션]`을 따릅니다. `--dry-run`→(정책 허용 시)`--yes` 재실행.&#x20;

---

#### B-3) `apply.py` — 정책 기반 자동 적용 (+테스트/롤백)

**목표**: 제안서 내 `HOW` 라인 반복 실행. 1) `--dry-run` 실행·로그, 2) **테스트 필요**면 `pytest` 실행, 3) 통과 시 동일 명령을 `--yes`로 재실행 및 커밋, 4) 실패 시 **롤백**.&#x20;

```python
# scripts/auto_update/apply.py
from __future__ import annotations
import subprocess, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROPOSALS = ROOT/"docs/proposals"

def _run(args: list[str]) -> int:
    return subprocess.run(args, cwd=ROOT, shell=False).returncode

def apply_from_md(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.search(r"- HOW: `(invoke refactor .+?)`", line)
        if not m: continue
        dry = m.group(1)
        # 1) dry-run
        if _run(dry.split()) != 0:
            print(f"[SKIP] dry-run failed: {dry}"); continue
        # 2) 정책상 테스트 필요 여부 감지(상위 블록 파싱/간단 규칙)
        need_test = "TestRequired: True" in text
        if need_test and _run(["pytest","-q"]) != 0:
            print("[ROLLBACK] tests failed; reverting"); _run(["git","reset","--hard","HEAD"]); continue
        # 3) 확정 적용
        yes = dry.replace("--dry-run","--yes")
        if _run(yes.split()) == 0:
            _run(["git","add","-A"])
            _run(["git","commit","-m","chore(p2-su): auto-apply policy-approved change"])
        else:
            print(f"[ERROR] apply failed: {yes}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv)>1 else PROPOSALS/"auto_update_latest.md"
    apply_from_md(Path(target))
```

> `--dry-run`으로 diff 산출 후 **정책 허용 + 테스트 통과** 시에만 `--yes` 확정. 테스트 실패 시 자동 승인도 철회 → 수동 검토로 강등. &#x20;

---

### C) `tasks.py` 통합

**필수 태스크**: `auto.scan`, `auto.propose`, `auto.apply`. &#x20;

```python
from invoke import task
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

@task
def auto_scan(c):
    c.run(f"{sys.executable} scripts/auto_update/scanner.py", pty=False)

@task
def auto_propose(c):
    c.run(f"{sys.executable} scripts/auto_update/proposer.py", pty=False)

@task
def auto_apply(c, proposal="latest"):
    target = f"docs/proposals/{proposal}" if proposal.endswith(".md") else "docs/proposals/auto_update_latest.md"
    c.run(f"{sys.executable} scripts/auto_update/apply.py {target}", pty=False)
```

---

### D) 정책/문서

#### D-1) `docs/SELF_UPDATE_POLICY.md` **초안**

정책은 **표 형식 메타데이터**로 자동 해석됩니다(규칙, 위험도, 자동 승인, 테스트 필요…).&#x20;

```
# Self-Update Engine Policy v1
| Rule ID            | Category | Risk Level | Auto Approve | Test Required | Description                     |
|--------------------|----------|------------|--------------|---------------|---------------------------------|
| update_dependency  | deps     | Low        | Yes          | Yes           | Patch/minor upgrade only        |
| replace_deprecated | upkeep   | Medium     | Yes          | Yes           | Replace deprecated API          |
| lint_fix           | style    | Low        | Yes          | No            | Lint/format only (no logic)     |
| add_docstrings     | docs     | Low        | Yes          | No            | Add missing docstrings          |
```

> 위 기준은 다른 LLM 보고서 수용 사항과 일치. 필요 시 조정. &#x20;

#### D-2) `GEMINI.md` 업데이트

* “Self-Update Protocol” 항목 신설: **주기/흐름/정책/롤백** 명시 및 `docs/SELF_UPDATE_POLICY.md` 참조.&#x20;

---

### E) 테스트 전략 (pytest 예시)

#### E-1) `scanner` 단위

* 가짜 `pip --outdated` JSON·가짜 `pytest` 출력 모킹 → Finding 생성 검증.&#x20;

#### E-2) `proposer` 단위

* 정책 파싱으로 `auto_approve`/`test_required` 변화가 명령 플래그에 반영되는지 검증. **실제 수정은 금지**(dry-run/mocks).&#x20;

#### E-3) `apply` 단위

* `--dry-run` 성공 후 `--yes` 재실행, 테스트 실패 시 **git reset --hard** 롤백 확인. ‘자동 승인’이라도 테스트 불합격 시 자동 철회 로그 확인.&#x20;

#### E-4) 통합(E2E)

* 임시 리포(예: `requests==2.27.0`) 구성 → `auto.scan → auto.propose → auto.apply` → 버전 상향/테스트 통과/커밋 여부 검증. 실패 시 보류/보고 동작 확인. &#x20;

---

### F) Git/운영

* **브랜치**: `chore/p2-su/<topic>` (자동 적용), `feat/p2-su/<topic>` (기능 추가)
* **커밋**: `chore(p2-su): auto-apply update_dependency: requests 2.28.2`
* **롤백**: 실패 시 `git reset --hard HEAD` / 필요 시 `revert`로 복구.
* **리포팅**: 자동 적용=Applied, 보류=Pending Review로 마킹하여 HUB/콘솔에 요약 표시.&#x20;

---

### G) 안전장치(필수)

1. **경계 경로 차단**: 모든 파일 접근은 **레포 내부**만. `.resolve()` 후 하위 여부 확인. (P1-2와 정책 일관)&#x20;
2. **`--yes` 게이트**: 자동 반영은 정책+테스트 통과 후에만 `--yes`. 기본은 **`--dry-run`**.&#x20;
3. **정책 준수 테스트**: `auto_approve=False` 전환 시 diff만 출력되는지 등 **설정-테스트** 포함.&#x20;

---

## 부록 — 실행 체크리스트

* [ ] `scripts/auto_update/{scanner,proposer,apply}.py` 생성
* [ ] `docs/SELF_UPDATE_POLICY.md` 작성(표 메타데이터)&#x20;
* [ ] `tasks.py`에 `auto.scan / auto.propose / auto.apply` 추가&#x20;
* [ ] E2E 테스트: requests 패치/마이너 업그레이드 시나리오 통과 확인&#x20;
* [ ] HUB/리포트에 Applied/Pending 집계 출력(보류 항목 수동 명령 가이드 포함)&#x20;

---

필요 시, `replace_api`, `lint_fix`, `add_docstrings` 등 **P1-2 규칙 플러그인**을 더 추가하여 proposer 매핑 범위를 확장하세요. 명령 포맷과 `--dry-run/--yes` 절차는 동일합니다.&#x20;

추가 요청이 있으시면 알려주세요.
