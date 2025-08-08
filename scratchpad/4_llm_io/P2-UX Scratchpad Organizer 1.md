\[Role: Tech Expert]

## 🤔 Strategic Analysis

핵심 문제는 \*\*잘못된 문자열 리터럴·따옴표 문자(굽은 따옴표)\*\*와 **깨진 정규식** 때문에 `scripts/organizer.py`가 import 시점에 `SyntaxError`를 내면서 `invoke` 전체를 멈추는 것입니다. 또한 LLM이 생성한 규칙 중 **LLM 경로 정규식**·**P 패턴**이 오타로 무의미해져 분류 정확도를 해치고 있었습니다. 아래에 **원인 → 수정 → 재발 방지**까지 포함한 완전 지시서와 **교체 가능한 최종 코드**를 제공합니다.

---

## 📝 Expert Recommendation

### 0) 결론 먼저 (TL;DR)

* **즉시 수정 포인트**

  * `"\", "/"` → `"\\", "/"` (백슬래시 이스케이프)
  * 모든 굽은 따옴표(” “ ‘ ’) → 표준 따옴표(" ')
  * 깨진 정규식 교정

    * `r"^[\[]?P\d(-\d)?[\ ]?]?"` → `r"^\[?P\d(?:-\d)?\]?"`
    * `r"^[\[]?P0[\ ]?]"` → `r"^\[?P0\]?"`
    * `r'(^|/)"LLM_"Requests|Answer"(/|$)'` → `r'(^|/)LLM_(Requests|Answer)(/|$)'`
* **기능 수용**: 점수 기반 휴리스틱(파일명/내용/확장자/경로 컨텍스트), Rich 테이블 승인, 멱등성(정리 폴더 스킵), 이름 충돌 시 `_1` 증분, 로그/저널 기록 — 전부 유지·강화.
* **아래 “최종 스크립트”를 그대로 교체**하고, **스모크 테스트** 절차로 검증하세요.

---

### 1) 교체 적용용 최종 코드

#### `scripts/organizer.py` (최종본/교체 용)

```python
# scripts/organizer.py
from __future__ import annotations

import re
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
from invoke import task
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

# --- 전역 설정 ---
console = Console()
CATEGORIES = ["1_daily_logs", "2_proposals_and_plans", "3_debug_and_tests", "4_llm_io", "_archive"]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".log", ".html"}
SKIP_DIRS = set(CATEGORIES)

# --- 상세 분류 규칙 (정규식/키워드/확장자) ---
RULES = {
    "1_daily_logs": {
        "name_regex": [
            r"^\d{8}\b",                    # 20250805...
            r"\b20\d{2}[-_]\d{2}[-_]\d{2}\b",  # 2025-08-05 / 2025_08_05
            r"(?i)daily[_-]?log",
            r"(?i)_TASK(\.|$)",
        ],
        "content_keywords": ["작업 로그", "일일 보고"],
        "ext": {".md", ".txt"},
    },
    "2_proposals_and_plans": {
        "name_regex": [
            r"(?i)\b(plan|proposal|roadmap|design|spec|blueprint)\b",
            r"^\[?P\d(?:-\d)?\]?",  # [P1], [P1-2], P1, P1-2
        ],
        "content_keywords": ["목표", "계획", "단계", "제안", "로드맵"],
        "ext": {".md", ".txt", ".docx"},
    },
    "3_debug_and_tests": {
        "name_regex": [
            r"(?i)\b(debug|test|patch|report|issue|error)\b",
            r"^\[?P0\]?",  # [P0], P0
            r"\b_debug_",
        ],
        "content_keywords": ["Error", "Exception", "traceback", "Assertion"],
        "ext": {".py", ".log", ".txt", ".md"},
    },
    "4_llm_io": {
        "name_regex": [
            r"(?i)\b(LLM|Prompt|Request|Answer|Response)\b",
            r"(^|/)LLM_(Requests|Answer)(/|$)",  # 폴더 컨텍스트
        ],
        "content_keywords": ["User:", "Assistant:", "system prompt"],
        "ext": {".md", ".json", ".txt"},
    },
    "_archive": {
        "name_regex": [r"(?i)\b(old|backup)\b"],
        "content_keywords": [],
        "ext": set(),
    },
}

class ScratchpadOrganizer:
    def __init__(self, base_dir: str, dry_run: bool = True, auto_yes: bool = False):
        self.base_path = Path(base_dir).resolve()
        self.dry_run = dry_run
        self.auto_yes = auto_yes
        self.move_plan: list[tuple[Path, Path, str, int]] = []

    # --- 유틸 ---
    def _read_file_head(self, path: Path, max_bytes=4096) -> str:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            return ""
        try:
            # 텍스트 파일 헤더만 확인
            return path.read_bytes()[:max_bytes].decode("utf-8", errors="ignore")
        except Exception as e:
            console.log(f"파일 읽기 오류: {path}, {e}", style="dim yellow")
            return ""

    def _is_already_sorted(self, path: Path) -> bool:
        try:
            return path.relative_to(self.base_path).parts[0] in SKIP_DIRS
        except (ValueError, IndexError):
            return False

    # --- 점수 기반 스코어링 ---
    def _score_file(self, path: Path, head_text: str) -> dict[str, int]:
        # Windows 백슬래시 → 슬래시 정규화
        name = str(path.relative_to(self.base_path)).replace("\\", "/")
        ext = path.suffix.lower()
        scores = {cat: 0 for cat in RULES}

        # 폴더 컨텍스트 강제 분류(최우선)
        if "/LLM_Requests/" in name or "/LLM_Answer/" in name:
            return {"4_llm_io": 999}
        if "/p0_patch/" in name:
            return {"3_debug_and_tests": 999}

        for cat, rule in RULES.items():
            if any(re.search(pat, name) for pat in rule["name_regex"]):
                scores[cat] += 3
            if ext in rule.get("ext", set()):
                scores[cat] += 1
            if head_text and any(kw in head_text for kw in rule["content_keywords"]):
                scores[cat] += 2
        return scores

    def _pick_category(self, scores: dict[str, int]) -> str:
        if not scores:
            return "_archive"
        best = max(scores.values())
        if best <= 0:
            return "_archive"
        # 동점자는 우선순위 CATEGORIES 순으로 결정
        candidates = {c for c, v in scores.items() if v == best}
        for cat in CATEGORIES:
            if cat in candidates:
                return cat
        return "_archive"

    # --- 플로우 ---
    def generate_move_plan(self):
        console.print(f"[bold green]'{self.base_path}' 디렉터리 스캔 중...[/bold green]")
        for item in self.base_path.rglob("*"):
            if not item.is_file() or self._is_already_sorted(item):
                continue
            head = self._read_file_head(item)
            scores = self._score_file(item, head)
            category = self._pick_category(scores)
            target_dir = self.base_path / category
            target_path = target_dir / item.name
            if item.parent.resolve() != target_dir.resolve():
                score_val = max(scores.values()) if scores else 0
                self.move_plan.append((item, target_path, category, score_val))

    def display_move_plan(self) -> bool:
        if not self.move_plan:
            console.print("[yellow]정리할 파일이 없습니다.[/yellow]")
            return False
        table = Table(title="[bold cyan]Scratchpad 정리 계획[/bold cyan]")
        table.add_column("Source", style="yellow", no_wrap=True)
        table.add_column("Destination", style="green")
        table.add_column("Category", style="magenta")
        table.add_column("Score", justify="right", style="cyan")
        for src, dest, cat, score in self.move_plan:
            table.add_row(
                str(src.relative_to(self.base_path)),
                str(dest.relative_to(self.base_path)),
                cat,
                str(score),
            )
        console.print(table)
        return True

    def _unique_path(self, dest_path: Path) -> Path:
        if not dest_path.exists():
            return dest_path
        i = 1
        while True:
            cand = dest_path.with_stem(f"{dest_path.stem}_{i}")
            if not cand.exists():
                return cand
            i += 1

    def execute_move_plan(self):
        console.print(f"\n[bold green]총 {len(self.move_plan)}개의 파일을 이동합니다...[/bold green]")
        moved: list[tuple[str, str]] = []
        for src, dest, _, _ in self.move_plan:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                final_dest = self._unique_path(dest)
                shutil.move(str(src), str(final_dest))
                console.print(f"[green]Moved:[/green] {src} -> {final_dest}")
                moved.append((str(src), str(final_dest)))
            except Exception as e:
                console.print(f"[bold red]오류:[/bold red] {src} 이동 실패 → {e} (건너뜀)")
        self._write_log(moved)
        self._write_journal(moved)

    def _write_log(self, moved_files: list[tuple[str, str]]):
        log_path = self.base_path / "organize_log.txt"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Moved {len(moved_files)} items.\n")
            for s, d in moved_files:
                f.write(f"  - {s} -> {d}\n")
        console.print(f"[dim]로그 기록: {log_path}[/dim]")

    def _write_journal(self, moves: list[tuple[str, str]]):
        j_path = self.base_path / "organize_journal.jsonl"
        with j_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "moves": moves}, ensure_ascii=False) + "\n")
        console.print(f"[dim]저널 기록: {j_path}[/dim]")

    def run(self):
        if not self.base_path.is_dir():
            console.print(f"[bold red]오류: '{self.base_path}' 디렉터리를 찾을 수 없습니다.[/bold red]")
            return
        self.generate_move_plan()
        if not self.display_move_plan():
            return
        if self.dry_run:
            console.print("\n[bold yellow]--dry-run: 이동 미실행[/bold yellow]")
            return
        if self.auto_yes or Confirm.ask("\n[bold yellow]위 계획대로 이동할까요?[/bold yellow]", default=False):
            self.execute_move_plan()
        else:
            console.print("[red]사용자 취소[/red]")

# --- Invoke 태스크 ---
@task
def organize_scratchpad(c, base="scratchpad", dry_run=False, yes=False):
    """
    scratchpad 디렉터리를 휴리스틱 규칙에 따라 정리합니다.
    """
    console.rule("[bold blue]Scratchpad Organizer[/bold blue]")
    ScratchpadOrganizer(base_dir=base, dry_run=dry_run, auto_yes=yes).run()
```

---

### 2) 스모크 테스트 & 재발 방지 Check-list

#### A. 즉시 스모크 테스트

```bash
# 1) 문법 오류 사전 확인(Import 시점 에러 탐지)
python -c "import importlib.util, sys; spec=importlib.util.spec_from_file_location('org','scripts/organizer.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK')"

# 2) Dry-run 계획 출력
invoke organize-scratchpad --base="scratchpad" --dry-run=True

# 3) 실제 실행(비대화식)
invoke organize-scratchpad --base="scratchpad" --dry-run=False --yes=True
```

#### B. 재발 방지(소스 위생)

* **굽은 따옴표 제거 스윕(1회 실행):**

  ```python
  # tools/fix_quotes.py
  from pathlib import Path
  import re
  ROOT = Path(".")
  bad = ["“","”","‘","’"]
  for p in ROOT.rglob("*.py"):
      t = p.read_text(encoding="utf-8", errors="ignore")
      nt = t
      for b in bad:
          nt = nt.replace(b, '"' if b in ["“","”"] else "'")
      if t != nt:
          p.write_text(nt, encoding="utf-8")
          print("fixed", p)
  ```
* **사전 CI 훅**: `python -m py_compile scripts/organizer.py`를 pre-commit 또는 CI에 추가 → 구문 오류 사전 차단.
* **정규식 회귀 테스트**: 아래 테스트 추가로 규칙 오타 재발 방지.

---

### 3) 실행 가능한 테스트 (pytest)

`tests/test_organizer_basic.py`

```python
from pathlib import Path
import importlib.util

def import_file(path: Path):
    spec = importlib.util.spec_from_file_location("org", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_import_ok(tmp_path):
    # 문법 오류/따옴표 문제 사전 감지
    m = import_file(Path("scripts/organizer.py"))
    assert hasattr(m, "ScratchpadOrganizer")

def test_regex_and_scoring(tmp_path):
    base = tmp_path / "scratchpad"; base.mkdir()
    # 샘플 파일 생성
    (base / "20250805_Daily_Log.md").write_text("# 2025-08-05 작업 로그")
    (base / "[P1-2]Plan_O3.md").write_text("목표와 계획 단계")
    (base / "debug_hub_stripper.py").write_text("raise Exception('x')")
    (base / "LLM_Requests").mkdir()
    (base / "LLM_Requests" / "foo.md").write_text("User: hi\nAssistant: hello")
    # 모듈 import 및 계획 생성
    m = import_file(Path("scripts/organizer.py"))
    org = m.ScratchpadOrganizer(str(base), dry_run=True)
    org.generate_move_plan()
    cats = {cat for *_ , cat, _ in org.move_plan}
    assert {"1_daily_logs","2_proposals_and_plans","3_debug_and_tests","4_llm_io"}.issubset(cats)

def test_collision_suffix(tmp_path, monkeypatch):
    base = tmp_path / "scratchpad"; base.mkdir()
    (base / "20250731_TASK.md").write_text("..")
    (base / "1_daily_logs").mkdir()
    (base / "1_daily_logs" / "20250731_TASK.md").write_text("existing")
    m = import_file(Path("scripts/organizer.py"))
    monkeypatch.setattr(m.Confirm, "ask", lambda *a, **k: True)
    org = m.ScratchpadOrganizer(str(base), dry_run=False, auto_yes=True)
    org.run()
    matches = list((base/"1_daily_logs").glob("20250731_TASK*.md"))
    assert len(matches) == 2  # 원본 + _1
```

---

### 4) 요구사항 충족 점검 (체크리스트)

* ✅ **Windows-first**: 경로 조작은 `pathlib` 사용, `replace("\\", "/")`로 정규화. `subprocess` 미사용(본 스크립트), `shell=True` 금지 원칙 준수.
* ✅ **점수 기반 분류**: 파일명 정규식(+3) / 확장자(+1) / 내용 키워드(+2) / 폴더 컨텍스트(999) → 최고점 카테고리 선택, 동점 시 `CATEGORIES` 우선순위.
* ✅ **Rich UI**: 계획을 `rich.table.Table`로 가독성 있게 출력, dry-run/승인 플로우.
* ✅ **멱등성**: 이미 분류된 상위 폴더(`1_…`, `2_…`, …, `_archive`) 하위는 스킵.
* ✅ **충돌 정책**: 대상 위치에 동명 존재 시 `_1`, `_2` … 부여(덮어쓰기 방지).
* ✅ **로깅**: 이동 요약은 `organize_log.txt`, 상세 저널은 JSONL(`organize_journal.jsonl`).
* ✅ **Invoke 진입점**: `@task organize_scratchpad` 제공. `tasks.py`에 등록되어 있으면 즉시 사용 가능.

---

### 5) `tasks.py` 등록(확인)

이미 다음과 같이 등록되어 있어야 합니다. 없으면 추가하세요.

```python
# tasks.py (발췌)
from invoke import Collection
from scripts.organizer import organize_scratchpad

ns = Collection()
ns.add_task(organize_scratchpad, name="organize-scratchpad")
```

---

### 6) 운영 팁(현장 적용)

* 첫 실행은 반드시 `--dry-run=True`로 계획 검토 → 승인 적용.
* 대규모 이동 직전 git 커밋 스냅샷 생성 권장:

  ```bash
  git add -A && git commit -m "chore(organizer): pre-move snapshot"
  ```
* 이동 후 `organize_log.txt`와 `organize_journal.jsonl`을 커밋해 변경 추적성을 확보.

---

### 7) 왜 이게 “최종판”인가 (브루털 팩트)

* 기존 지시서의 **핵심 오류 3종**(백슬래시 이스케이프, 굽은 따옴표, 오타 난 정규식)을 실사용 코드 기준으로 전부 교정.
* 분류 로직은 **규칙 중복/동점/컨텍스트**까지 안전하게 해소.
* 실패 내성: 파일 읽기 오류/이동 실패는 **건너뛰고 계속** + **로그/저널 기록**으로 사후 추적 용이.
* Windows-first 제약 하에서 **표준 라이브러리+Rich+Invoke**만 사용, 네트워크 비의존.

---

필요하시면 위 코드로 바로 PR 생성용 패치(diff)도 만들어 드릴게요.
추가 요청이 있으시면 알려주세요.
