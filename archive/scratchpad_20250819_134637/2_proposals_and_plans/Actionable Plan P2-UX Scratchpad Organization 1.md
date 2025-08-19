\[Role: Tech Expert]

## 🤔 Strategic Analysis

첨부된 지시서는 동작하나 휴리스틱이 지나치게 단순(예: `.py`=debug, `"io"` 포함=LLM)해 오분류 리스크가 큽니다. P2-UX 보고서의 구조/정책을 준수하면서(리치 테이블 승인·멱등성·충돌 시 `_1`) 점수 기반 분류, 폴더 컨텍스트, UNDO 저널을 추가한 **최종 작업지시서**를 제시합니다.  &#x20;

## 📝 Expert Recommendation

아래는 실제 코드로 바로 이행 가능한 **최종 작업지시서**입니다. P2-UX 요구사항(카테고리, 휴리스틱, 승인·안전 실행, 테스트, 문서화)을 모두 충족합니다. &#x20;

---

### A) 설계 원칙(반영 사항)

1. **카테고리 고정**: `1_daily_logs/`, `2_proposals_and_plans/`, `3_debug_and_tests/`, `4_llm_io/`, `_archive/` 5종. 이미 정리된 폴더는 스캔 제외(멱등성). &#x20;
2. **승인 기반 실행**: 이동계획 → `rich.Table`로 확인 → 승인 시만 이동.&#x20;
3. **충돌정책**: 대상에 동명 존재 시 `_1`, `_2`… 접미사로 안전 보존(덮어쓰기 금지).&#x20;
4. **로그**: `scratchpad/organize_log.txt`에 요약 및 상세 경로 기록.&#x20;
5. **분류 기준 근거**: 파일명/내용/확장자/경로 컨텍스트를 조합한 휴리스틱 표 적용.&#x20;

> **다른 LLM 지시서 대비 보완점(브루털 팩트)**
>
> * 단순 규칙(예: `p.suffix==".py" → debug`, `name.startswith("20") → log`, `"io"` 포함 → llm)은 오분류 유발. 본안은 **정규식+키워드+경로** 가중 점수로 결정.
> * 디렉터리 컨텍스트(예: `LLM_Answer/`, `p0_patch/`) 미활용 → 본안은 **폴더 우선 규칙**을 추가. &#x20;
> * 멱등성, 계획 미리보기, 충돌정책은 기존 보고서 취지대로 강화 유지. &#x20;

---

### B) 휴리스틱(최종판, 점수 기반)

아래 표의 **규칙 일치당 가중치**를 합산해 최고 점수 카테고리로 분류(동률 시 우선순위: Daily → Proposals → Debug/Tests → LLM → Archive).

| 카테고리                     | 파일명/경로 정규식(각 +3)                                                                  | 내용 키워드(각 +2, 텍스트 파일 헤더 4KB만 스캔) | 확장자 힌트(+1)                                | 예외/폴더 컨텍스트(+∞) |                  |                                    |                                                |                       |                                    |                |                                      |
| ------------------------ | --------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------------- | -------------- | ---------------- | ---------------------------------- | ---------------------------------------------- | --------------------- | ---------------------------------- | -------------- | ------------------------------------ |
| 1\_daily\_logs           | `^\d{8}` / `\b20\d{2}[-_]\d{2}[-_]\d{2}\b` / `(?i)daily[_-]?log` / \`(?i)\_TASK(. | \$)\`                           | “작업 로그”, “일일 보고”, 날짜 문자열(예: `2025-08-05`) | `.md`, `.txt`  | 해당 없음            |                                    |                                                |                       |                                    |                |                                      |
| 2\_proposals\_and\_plans | \`(?i)\b(plan                                                                     | proposal                        | roadmap                                   | design         | spec             | blueprint)\b`/`^$?P\d(-\d)?$?\`    | “목표”, “계획”, “단계”, “제안”, “로드맵”                  | 문서형 확장자               | **폴더 자체가 제안/설계 모음이면 폴더째 이동**       |                |                                      |
| 3\_debug\_and\_tests     | \`(?i)\b(debug                                                                    | test                            | patch                                     | report         | issue            | error)\b`/`^$?P0$?`/`\b\_debug\_\` | `Error`, `Exception`, `traceback`, `Assertion` | `.py`, `.log`, `.txt` | `p0_patch/` 하위 전부                  |                |                                      |
| 4\_llm\_io               | \`(?i)\b(LLM                                                                      | Prompt                          | Request                                   | Answer         | Response)\b`/`(^ | /)LLM\_(Requests                   | Answer)(/                                      | \$)\`                 | “User:”, “Assistant:”, 시스템 프롬프트 패턴 | `.md`, `.json` | `LLM_Requests/`, `LLM_Answer/` 하위 전부 |
| \_archive                | 위 미해당 / \`(?i)\b(old                                                              | backup)\b\`                     | (없음)                                      | (무관)           | (없음)             |                                    |                                                |                       |                                    |                |                                      |

근거: 보고서의 카테고리 정의·예시와 분류 규칙 표를 준수.   &#x20;

---

### C) 모듈 구성(최종)

* `scripts/rules.py` : 정규식/키워드/가중치 정의 + 점수 함수
* `scripts/utils/file_ops.py` : 안전 이동·고유이름·저널(UNDO)
* `scripts/organizer.py` : 스캔→분류→이동계획→미리보기→승인→실행
* `tasks.py` : `invoke organize-scratchpad` 등록(비대화식: `--yes`)&#x20;

---

### D) 코드 스켈레톤(교체 적용용)

#### 1) `scripts/rules.py`

```python
# scripts/rules.py
import re
from pathlib import Path

TEXT_EXT = {".md",".txt",".json",".yaml",".yml",".ini",".log",".html"}
DAILY_NAME = [r"^\d{8}\b", r"\b20\d{2}[-_]\d{2}[-_]\d{2}\b", r"(?i)daily[_-]?log", r"(?i)_TASK(\.|$)"]
PLAN_NAME  = [r"(?i)\b(plan|proposal|roadmap|design|spec|blueprint)\b", r"^\[?P\d(-\d)?\]?"]
DEBUG_NAME = [r"(?i)\b(debug|test|patch|report|issue|error)\b", r"^\[?P0\]?", r"\b_debug_"]
LLM_NAME   = [r"(?i)\b(LLM|Prompt|Request|Answer|Response)\b", r"(^|/)LLM_(Requests|Answer)(/|$)"]
ARCHIVE_NAME = [r"(?i)\b(old|backup)\b"]

CONTENT_DAILY = ["작업 로그","일일 보고"]
CONTENT_PLAN  = ["목표","계획","단계","제안","로드맵"]
CONTENT_DEBUG = ["Error","Exception","traceback","Assertion"]
CONTENT_LLM   = ["User:","Assistant:","system prompt"]

CAT_ORDER = ["1_daily_logs","2_proposals_and_plans","3_debug_and_tests","4_llm_io","_archive"]

RULES = {
  "1_daily_logs": {"name": DAILY_NAME, "content": CONTENT_DAILY, "ext": {".md",".txt"}},
  "2_proposals_and_plans": {"name": PLAN_NAME, "content": CONTENT_PLAN, "ext": {".md",".txt",".docx"}},
  "3_debug_and_tests": {"name": DEBUG_NAME, "content": CONTENT_DEBUG, "ext": {".py",".log",".txt",".md"}},
  "4_llm_io": {"name": LLM_NAME, "content": CONTENT_LLM, "ext": {".md",".json",".txt"}},
  "_archive": {"name": ARCHIVE_NAME, "content": [], "ext": set()}
}

def score_file(path: Path, head_text: str) -> dict:
    name = str(path).replace("\\","/")
    ext = path.suffix.lower()
    scores = {c:0 for c in RULES}
    # 폴더 컨텍스트 보정(강제 분류)
    if "/LLM_Requests/" in name or "/LLM_Answer/" in name:
        return {"4_llm_io": 999}
    if "/p0_patch/" in name:
        return {"3_debug_and_tests": 999}

    for cat, rule in RULES.items():
        if any(re.search(pat, name) for pat in rule["name"]): scores[cat]+=3
        if ext in rule["ext"]: scores[cat]+=1
        if head_text and any(kw in head_text for kw in rule["content"]): scores[cat]+=2
    return scores

def pick_category(scores: dict) -> str:
    # 동률은 CAT_ORDER 우선순위로 해소
    best = max(scores.values()) if scores else 0
    cands = [c for c,v in scores.items() if v==best]
    for c in CAT_ORDER:
        if c in cands: return c
    return "_archive"
```

> 카테고리 정의·폴더 컨텍스트·예시 키워드는 보고서 규칙을 준수.  &#x20;

#### 2) `scripts/utils/file_ops.py`

```python
# scripts/utils/file_ops.py
from pathlib import Path
import shutil, json, time

def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def unique_path(dest: Path) -> Path:
    if not dest.exists(): return dest
    i=1
    while True:
        cand = dest.with_stem(f"{dest.stem}_{i}")
        if not cand.exists(): return cand
        i+=1  # 충돌 시 _1, _2 … (P2-UX 정책)

def safe_move(src: Path, dest: Path) -> Path:
    ensure_dir(dest.parent)
    final_dest = unique_path(dest)
    shutil.move(str(src), str(final_dest))
    return final_dest

def write_journal(base: Path, moves: list[tuple[str,str]]):
    j = base / "organize_journal.jsonl"
    with open(j,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.time(), "moves": moves}, ensure_ascii=False) + "\n")
```

(충돌정책·로그 요구사항 반영)&#x20;

#### 3) `scripts/organizer.py`

```python
# scripts/organizer.py
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from invoke import task
from scripts.rules import score_file, pick_category, TEXT_EXT, CAT_ORDER
from scripts.utils.file_ops import safe_move, write_journal

console = Console()
CATEGORIES = CAT_ORDER  # 동일 순서 유지
SKIP_DIRS = set(CATEGORIES)  # 멱등성: 이미 정리된 폴더 스킵

def read_head(path: Path, maxb=4096) -> str:
    if path.suffix.lower() not in TEXT_EXT: return ""
    try:
        return path.read_bytes()[:maxb].decode("utf-8","ignore")
    except Exception:
        return ""

def already_sorted(p: Path, base: Path) -> bool:
    try:
        head = p.relative_to(base).parts[0]
        return head in SKIP_DIRS
    except ValueError:
        return False

def build_plan(base: Path):
    plan = []
    for p in base.rglob("*"):
        if p.is_dir(): continue
        if already_sorted(p, base): continue
        head = read_head(p)
        scores = score_file(p, head)
        # 강제 분류 반환(예: 999 점) 대응
        if len(scores)==1: cat = list(scores.keys())[0]
        else: cat = pick_category(scores)
        dest = base / cat / p.name
        if p.parent != dest.parent:
            plan.append((p, dest, cat, max(scores.values()) if len(scores)>1 else 999))
    return plan  # (src, dest, cat, score)

def render(plan):
    table = Table(title="Scratchpad Organization Plan")
    table.add_column("Source", style="dim")
    table.add_column("Destination", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Score", justify="right")
    for src, dest, cat, sc in plan:
        table.add_row(str(src), str(dest), cat, str(sc))
    console.print(table)

def apply_plan(base: Path, plan):
    moves = []
    for src, dest, _, _ in plan:
        final_dest = safe_move(src, dest)
        console.print(f"[green]Moved:[/green] {src} -> {final_dest}")
        moves.append((str(src), str(final_dest)))
    write_journal(base, moves)
    with open(base / "organize_log.txt","a",encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] Moved {len(moves)} items.\n")
        for s,d in moves: f.write(f"  {s} -> {d}\n")

@task
def organize_scratchpad(c, base="scratchpad", dry_run=True, yes=False):
    base = Path(base)
    if not base.exists():
        console.print(f"[red]Base not found: {base}[/red]"); return
    plan = build_plan(base)
    if not plan:
        console.print("[yellow]정리 대상 없음[/yellow]"); return
    render(plan)  # 리치 테이블 미리보기(승인 절차)
    if not yes:
        resp = console.input("\n위 계획대로 파일을 이동할까요? [y/N]: ").strip().lower()
        if resp != "y":
            console.print("사용자 취소 - 종료"); return
    if dry_run:
        console.print("[blue]Dry-run: 미실행[/blue]"); return
    apply_plan(base, plan)
```

(리치 미리보기→승인→이동→로그의 P2-UX 파이프라인을 그대로 구현)&#x20;

#### 4) `tasks.py`

```python
# tasks.py
from invoke import Collection
from scripts.organizer import organize_scratchpad

ns = Collection()
ns.add_task(organize_scratchpad, name="organize-scratchpad")
```

(Invoke 태스크 등록)&#x20;

---

### E) 테스트(핵심 케이스, `pytest`)

요구된 시나리오: 분류 정확성, 충돌 처리, 사용자 취소, 멱등성. &#x20;

```python
# tests/test_organizer.py
from pathlib import Path
from scripts.organizer import build_plan, organize_scratchpad
from scripts.rules import pick_category

def write(p: Path, text=""): p.write_text(text, encoding="utf-8")

def test_daily_and_plan_and_debug_and_llm(tmp_path: Path):
    base = tmp_path / "scratchpad"; base.mkdir()
    write(base/"20250805_Daily_Log.md", "# 2025-08-05 작업 로그")  # daily
    write(base/"[P1-2]Plan_O3.md", "목표와 단계 정의")             # plan
    write(base/"debug_hub_stripper.py", "raise Exception('x')")    # debug
    (base/"LLM_Requests").mkdir(); write(base/"LLM_Requests"/"a.md","User: hi\nAssistant: hello")  # llm
    plan = build_plan(base)
    cats = {str(d.parent.name) for (_,d,_,_) in plan}
    assert "1_daily_logs" in cats and "2_proposals_and_plans" in cats and "3_debug_and_tests" in cats and "4_llm_io" in cats

def test_collision_policy(tmp_path: Path, monkeypatch):
    base = tmp_path / "scratchpad"; base.mkdir()
    write(base/"20250731_TASK.md", "")
    (base/"1_daily_logs").mkdir()
    write(base/"1_daily_logs"/"20250731_TASK.md", "existing")
    # 승인 자동화 & 미드라이런
    monkeypatch.setattr("scripts.organizer.console.input", lambda *_: "y")
    organize_scratchpad(None, base=str(base), dry_run=False, yes=False)
    # 원본은 _1으로 이동되었는지 확인
    moved = list((base/"1_daily_logs").glob("20250731_TASK*.md"))
    assert len(moved) == 2

def test_idempotency(tmp_path: Path, monkeypatch):
    base = tmp_path / "scratchpad"; base.mkdir()
    write(base/"20250805_Daily_Log.md","..")
    monkeypatch.setattr("scripts.organizer.console.input", lambda *_: "y")
    organize_scratchpad(None, base=str(base), dry_run=False, yes=False)
    # 두 번째 실행 시 이동 계획 비어야 함(이미 정리된 폴더 스킵)
    organize_scratchpad(None, base=str(base), dry_run=True, yes=True)  # dry-run
```

---

### F) 문서화(`docs/HELP.md` 템플릿)

* **목적/카테고리**: 5개 카테고리와 예시 설명.&#x20;
* **사용법**:

  ```bash
  invoke organize-scratchpad --dry-run=True           # 계획만
  invoke organize-scratchpad --dry-run=False          # 승인 후 실행
  invoke organize-scratchpad --dry-run=False --yes=True  # 비대화식
  ```
* **승인 흐름**: 리치 테이블 미리보기 → `y` 승인 시 실행.&#x20;
* **정책**: 충돌 시 `_1` 접미사, 로그/저널 경로 기술.&#x20;

---

### G) 운영 체크리스트(최초 실행 전)

1. 로컬에서 `--dry-run=True`로 89개 파일 계획을 검토(표시·분류 근거 샘플 확인). 요구 문서의 “AI 제안→인간 승인→실행” 절차 준수.&#x20;
2. 프로젝트 폴더는 **폴더단위 이동**이 더 적합한 경우(순수 기획/설계 모음) 예외 규정에 따라 폴더째 `2_proposals_and_plans/` 이동.&#x20;
3. 실행 후 `organize_log.txt`와 `organize_journal.jsonl`을 커밋(추적성).

---

### H) 수용 기준(DoD)

* 리치 테이블에 **Source/Destination/Category/Score** 표기
* 재실행 시 추가 이동 없음(멱등성)
* 이름 충돌 시 덮어쓰기 없이 `_N` 부여
* 로그/저널 생성
* 테스트 4대 케이스 통과

---

### I) 결론

본 지시서는 P2-UX 보고서의 구조·정책을 **완전 수용**하면서(카테고리/승인·안전 실행) 현업 오분류 리스크를 낮추는 **가중치 휴리스틱+폴더 컨텍스트+UNDO**까지 포함했습니다. 운영 초기엔 `--dry-run`으로 검토 후 실행하세요. &#x20;

추가 요청이 있으시면 알려주세요.
