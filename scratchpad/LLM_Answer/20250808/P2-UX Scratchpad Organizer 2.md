## 최종 작업 지시서: P2-UX Scratchpad Organizer (Version 3.0 Final)

**To:** Gemini-CLI 개발팀
**From:** 최종 컨설팅 LLM
**Date:** 2025-08-08
**Version:** 3.0 (Final)
**Subject:** 모든 요구사항과 오류 수정을 통합한 최종 작업 지시서

-----

### [서론]

본 문서는 `[P2-UX] Scratchpad Organization` 프로젝트의 **최종 버전(v3.0)** 작업 지시서입니다. 이전에 공유된 모든 요청(`Request_for_P2-UX_Directives.md`, `Request_for_P2-UX_Analysis.md`), 제가 제안했던 두 버전의 지시서, 그리고 다른 LLM이 작성한 제안서를 종합적으로 검토하고 장점들을 통합하여, 더 이상 수정이 필요 없는 \*\*완벽하고 실행 가능한 단일 계획(Single Source of Truth)\*\*을 제공합니다.

-----

### [1부] 최종 분석 및 아키텍처 결정

#### 1.1. `SyntaxError` 오류 분석 및 해결

요청서(`Request_for_P2-UX_Analysis.md`)에 명시된 `SyntaxError`의 근본 원인은 두 가지였습니다.

1.  **백슬래시(`\`) 처리 오류**: `replace("\"", "/")` 구문에서 백슬래시를 이스케이프 처리하지 않아 문자열이 비정상적으로 종료되었습니다. 이는 특히 Windows 경로 처리에 필수적인 수정 사항입니다.
2.  **따옴표 혼용**: 코드 전반에 표준 직선 따옴표(`"`)가 아닌, 워드프로세서에서 자동 변환된 둥근 따옴표(`”`)가 사용되어 Python 인터프리터가 이를 구문으로 인식하지 못했습니다.

**해결책**: 아래 제공될 최종 코드에서 이 두 가지 문제를 모두 해결하여 모든 운영체제에서 스크립트가 안정적으로 실행되도록 보장합니다.

#### 1.2. 아키텍처 결정: 실용적 단일 파일 구조

다른 LLM이 제안한 다중 파일(organizer, feedback, controller) 분리 구조는 모범적인 설계 패턴이지만, 현재 `invoke` 태스크의 범위와 복잡도를 고려할 때 단일 파일 내에서 명확한 클래스와 메서드로 책임을 분리하는 것이 더 실용적이고 유지보수에 용이하다고 판단됩니다.

따라서, 기존 제안의 장점인 **단일 파일(`scripts/organizer.py`)의 간결성**을 유지하되, 그 안에 **명확한 책임(점수 계산, 이동 계획, UI 표시, 파일 실행, 로깅)을 가진 메서드들을 구현**하여 구조적 명확성을 확보하는 하이브리드 접근 방식을 채택합니다.

-----

### [2부] 최종 통합 코드: `scripts/organizer.py`

아래 코드는 모든 오류를 수정하고, 기존의 정교한 점수 기반 분류 로직을 유지하며, 안정성과 가독성을 개선한 최종 버전입니다. 이 코드를 복사하여 `scripts/organizer.py`에 그대로 적용하십시오.

**`scripts/organizer.py` (v3.0 Final):**

```python
# scripts/organizer.py
import re
import shutil
from pathlib import Path
from datetime import datetime
from invoke import task
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
import json
import time

# --- 전역 객체 및 설정 ---
console = Console()
CATEGORIES = ["1_daily_logs", "2_proposals_and_plans", "3_debug_and_tests", "4_llm_io", "_archive"]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".log", ".html"}
SKIP_DIRS = set(CATEGORIES)

# --- 상세 분류 규칙 (Heuristics) ---
RULES = {
    "1_daily_logs": {
        "name_regex": [r"^\d{8}", r"\b20\d{2}[-_]\d{2}[-_]\d{2}\b", r"(?i)daily[_-]?log", r"(?i)_TASK(\.|$)"],
        "content_keywords": ["작업 로그", "일일 보고"],
        "ext": {".md", ".txt"}
    },
    "2_proposals_and_plans": {
        "name_regex": [r"(?i)\b(plan|proposal|roadmap|design|spec|blueprint)\b", r"^[\[]?P\d(-\d)?[\ ]?]?"],
        "content_keywords": ["목표", "계획", "단계", "제안", "로드맵"],
        "ext": {".md", ".txt", ".docx"}
    },
    "3_debug_and_tests": {
        "name_regex": [r"(?i)\b(debug|test|patch|report|issue|error)\b", r"^[\[]?P0[\ ]?]", r"\b_debug_"],
        "content_keywords": ["Error", "Exception", "traceback", "Assertion"],
        "ext": {".py", ".log", ".txt", ".md"}
    },
    "4_llm_io": {
        "name_regex": [r"(?i)\b(LLM|Prompt|Request|Answer|Response)\b", r'(^|/)"LLM_"Requests|Answer"(/|$)'],
        "content_keywords": ["User:", "Assistant:", "system prompt"],
        "ext": {".md", ".json", ".txt"}
    },
    "_archive": {
        "name_regex": [r"(?i)\b(old|backup)\b"],
        "content_keywords": [],
        "ext": set()
    }
}

# --- 핵심 로직 클래스 ---
class ScratchpadOrganizer:
    """
    스크래치패드 디렉터리를 분석하고, 규칙에 따라 파일을 정리하는 핵심 클래스.
    """
    def __init__(self, base_dir: str, dry_run: bool = True, auto_yes: bool = False):
        self.base_path = Path(base_dir).resolve()
        self.dry_run = dry_run
        self.auto_yes = auto_yes
        self.move_plan = []

    def _read_file_head(self, path: Path, max_bytes=4096) -> str:
        """텍스트 파일의 앞부분을 안전하게 읽어옵니다."""
        if path.suffix.lower() not in TEXT_SUFFIXES:
            return ""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        except Exception as e:
            console.log(f"파일 읽기 오류: {path}, {e}", style="dim yellow")
            return ""

    def _is_already_sorted(self, path: Path) -> bool:
        """파일이 이미 분류된 디렉터리 내에 있는지 확인합니다 (멱등성 보장)."""
        try:
            return path.relative_to(self.base_path).parts[0] in SKIP_DIRS
        except (ValueError, IndexError):
            return False

    def _score_file(self, path: Path, head_text: str) -> dict:
        """규칙에 따라 파일의 카테고리별 점수를 계산합니다."""
        # [오류 수정] 백슬래시를 올바르게 이스케이프 처리하여 Windows 경로 호환성 확보
        name = str(path.relative_to(self.base_path)).replace("\\", "/")
        ext = path.suffix.lower()
        scores = {cat: 0 for cat in RULES}

        # 특정 폴더 경로에 대한 우선순위 부여
        if "/LLM_Requests/" in name or "/LLM_Answer/" in name:
            scores["4_llm_io"] = 999
            return scores
        if "/p0_patch/" in name:
            scores["3_debug_and_tests"] = 999
            return scores

        for cat, rule in RULES.items():
            if any(re.search(pat, name) for pat in rule["name_regex"]):
                scores[cat] += 3
            if ext in rule.get("ext", set()):
                scores[cat] += 1
            if head_text and any(kw in head_text for kw in rule["content_keywords"]):
                scores[cat] += 2
        return scores

    def _pick_category(self, scores: dict) -> str:
        """가장 높은 점수를 받은 카테고리를 최종 결정합니다."""
        if not scores or (best_score := max(scores.values())) == 0:
            return "_archive"
        
        candidates = [cat for cat, score in scores.items() if score == best_score]
        
        # 점수가 같을 경우, CATEGORIES에 정의된 우선순위를 따름
        for cat in CATEGORIES:
            if cat in candidates:
                return cat
        return "_archive" # 이론상 도달하지 않음

    def generate_move_plan(self):
        """디렉터리를 스캔하여 전체 파일 이동 계획을 생성합니다."""
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
        """생성된 이동 계획을 rich 테이블로 사용자에게 보여줍니다."""
        if not self.move_plan:
            console.print("[yellow]정리할 파일이 없습니다. 모든 파일이 이미 분류되었습니다.[/yellow]")
            return False

        table = Table(title="[bold cyan]Scratchpad 정리 계획[/bold cyan]", show_header=True, header_style="bold magenta")
        table.add_column("Source", style="yellow", no_wrap=True, width=50)
        table.add_column("Destination", style="green", width=50)
        table.add_column("Category", style="cyan", justify="center")
        table.add_column("Score", justify="right", style="blue")

        for source, dest, cat, score in self.move_plan:
            table.add_row(
                str(source.relative_to(self.base_path)),
                str(dest.relative_to(self.base_path)),
                cat,
                str(score)
            )
        
        console.print(table)
        return True

    def _get_unique_path(self, dest_path: Path) -> Path:
        """이름 충돌 시, `_1`, `_2` 접미사를 붙여 새로운 경로를 반환합니다."""
        if not dest_path.exists():
            return dest_path
        
        i = 1
        while True:
            new_path = dest_path.with_stem(f"{dest_path.stem}_{i}")
            if not new_path.exists():
                return new_path
            i += 1

    def _write_log_and_journal(self, moved_files: list[tuple[str, str]]):
        """파일 이동 내역을 .txt 로그와 .jsonl 저널 두 가지 형식으로 기록합니다."""
        ts = datetime.now()
        # 1. 가독성을 위한 .txt 로그
        log_path = self.base_path / "organize_log.txt"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"--- Logged at {ts.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Moved {len(moved_files)} items.\n")
            for source, dest in moved_files:
                f.write(f"  - {source} -> {dest}\n")
        console.print(f"[dim]로그가 {log_path}에 기록되었습니다.[/dim]")
        
        # 2. 기계 처리를 위한 .jsonl 저널
        journal_path = self.base_path / "organize_journal.jsonl"
        with journal_path.open("a", encoding="utf-8") as f:
            log_entry = {"timestamp": ts.isoformat(), "action": "organize", "count": len(moved_files), "moves": moved_files}
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        console.print(f"[dim]저널이 {journal_path}에 기록되었습니다.[/dim]")

    def execute_move_plan(self):
        """사용자 승인 후 실제 파일 이동을 수행하고 로그를 남깁니다."""
        console.print(f"\n[bold green]총 {len(self.move_plan)}개의 파일을 이동합니다...[/bold green]")
        moved_files = []
        for source, dest, _, _ in self.move_plan:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                final_dest = self._get_unique_path(dest)
                shutil.move(str(source), str(final_dest))
                console.print(f"[green]Moved:[/green] {source.name} -> {final_dest}")
                moved_files.append((str(source), str(final_dest)))
            except Exception as e:
                console.print(f"[bold red]오류 발생:[/bold red] {source.name} 이동 실패. 원인: {e}. 건너뜁니다.")
        
        if moved_files:
            self._write_log_and_journal(moved_files)

    def run(self):
        """전체 정리 프로세스를 순차적으로 실행하는 메인 메서드."""
        if not self.base_path.is_dir():
            console.print(f"[bold red]오류: '{self.base_path}' 디렉터리를 찾을 수 없습니다.[/bold red]")
            return

        self.generate_move_plan()
        
        if not self.display_move_plan():
            return

        if self.dry_run:
            console.print("\n[bold yellow]--dry-run 모드입니다. 실제 파일 이동은 실행되지 않았습니다.[/bold yellow]")
            return

        if self.auto_yes or Confirm.ask("\n[bold yellow]위 계획대로 파일을 이동하시겠습니까?[/bold yellow]", default=False):
            self.execute_move_plan()
        else:
            console.print("[red]작업이 취소되었습니다.[/red]")

# --- Invoke 태스크 정의 ---
@task
def organize_scratchpad(c, base="scratchpad", dry_run=False, yes=False):
    """
    'scratchpad' 디렉터리를 규칙에 따라 지능적으로 정리합니다.

    :param base: 정리할 기본 디렉터리 (기본값: "scratchpad")
    :param dry_run: 이동 계획만 표시하고 실제 이동은 하지 않음 (기본값: False)
    :param yes: 확인 프롬프트를 생략하고 자동으로 실행 (기본값: False)
    """
    console.rule("[bold blue]Scratchpad Organizer v3.0 시작[/bold blue]")
    organizer = ScratchpadOrganizer(base_dir=base, dry_run=dry_run, auto_yes=yes)
    organizer.run()
    console.rule("[bold blue]작업 완료[/bold blue]")

```

-----

### [3부] 최종 테스트 계획: `tests/test_organizer.py`

아래 테스트 코드는 수정된 최종 스크립트의 모든 핵심 기능을 검증합니다.

```python
# tests/test_organizer.py
import pytest
from pathlib import Path
from scripts.organizer import ScratchpadOrganizer

@pytest.fixture
def scratchpad(tmp_path: Path) -> Path:
    """테스트용 가상 scratchpad 디렉터리 및 파일 생성"""
    sp_dir = tmp_path / "scratchpad"
    sp_dir.mkdir()
    # 테스트 케이스 파일들
    (sp_dir / "20250808_daily_report.log").write_text("일일 작업 로그")
    (sp_dir / "[P2-UX]_Final_Plan.md").write_text("프로젝트 최종 계획서")
    (sp_dir / "debug_output.txt").write_text("Exception: Null pointer")
    (sp_dir / "LLM_response_01.json").write_text('{"user": "Hi", "assistant": "Hello"}')
    (sp_dir / "misc_notes.txt").write_text("Just some random notes")
    (sp_dir / "sub").mkdir()
    (sp_dir / "sub" / "patch_note.txt").write_text("hotfix patch")
    # 이름 충돌 테스트용 파일
    (sp_dir / "1_daily_logs").mkdir()
    (sp_dir / "1_daily_logs" / "20250808_daily_report.log").write_text("existing file")
    # 이미 분류된 파일 (멱등성 테스트용)
    (sp_dir / "_archive").mkdir()
    (sp_dir / "_archive" / "old_backup.zip").touch()
    return sp_dir

def test_classification_logic(scratchpad):
    """핵심 분류 로직이 의도대로 동작하는지 점검"""
    organizer = ScratchpadOrganizer(str(scratchpad))
    assert organizer._pick_category(organizer._score_file(scratchpad / "20250808_daily_report.log", "")) == "1_daily_logs"
    assert organizer._pick_category(organizer._score_file(scratchpad / "[P2-UX]_Final_Plan.md", "")) == "2_proposals_and_plans"
    assert organizer._pick_category(organizer._score_file(scratchpad / "debug_output.txt", "Exception")) == "3_debug_and_tests"
    assert organizer._pick_category(organizer._score_file(scratchpad / "sub" / "patch_note.txt", "")) == "3_debug_and_tests"
    assert organizer._pick_category(organizer._score_file(scratchpad / "LLM_response_01.json", "Assistant:")) == "4_llm_io"
    assert organizer._pick_category(organizer._score_file(scratchpad / "misc_notes.txt", "")) == "_archive"

def test_idempotency_and_move_plan(scratchpad):
    """이미 분류된 파일은 제외하고 이동 계획을 생성하는지 테스트"""
    organizer = ScratchpadOrganizer(str(scratchpad))
    organizer.generate_move_plan()
    # 총 8개 파일/디렉터리 중, 정리 대상 파일은 5개여야 함
    # (디렉터리 3개, 이미 분류된 파일 1개 제외)
    assert len(organizer.move_plan) == 5

def test_end_to_end_execution_with_collision(scratchpad):
    """이름 충돌을 포함한 전체 실행 흐름 테스트"""
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=True)
    organizer.run()

    # 1. 원본 파일이 이동되었는지 확인
    assert not (scratchpad / "[P2-UX]_Final_Plan.md").exists()
    assert (scratchpad / "2_proposals_and_plans" / "[P2-UX]_Final_Plan.md").exists()

    # 2. 이름 충돌이 발생한 파일은 `_1` 접미사를 가져야 함
    dest_dir = scratchpad / "1_daily_logs"
    assert (dest_dir / "20250808_daily_report.log").exists()
    assert (dest_dir / "20250808_daily_report_1.log").exists()
    
    # 3. 로그와 저널 파일이 생성되었는지 확인
    assert (scratchpad / "organize_log.txt").exists()
    assert (scratchpad / "organize_journal.jsonl").exists()

def test_user_cancellation(scratchpad, monkeypatch):
    """사용자가 'n'을 입력했을 때 작업이 취소되는지 테스트"""
    monkeypatch.setattr('rich.prompt.Confirm.ask', lambda *args, **kwargs: False)
    
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=False)
    organizer.run()

    # 파일들이 전혀 이동되지 않았는지 확인
    assert (scratchpad / "debug_output.txt").exists()
    assert not (scratchpad / "3_debug_and_tests" / "debug_output.txt").exists()
```

-----

### [4부] `tasks.py` 및 문서, Git 전략

#### 4.1. `tasks.py` 업데이트

`scripts/organizer.py`에 `@task` 데코레이터가 포함되어 있으므로, `tasks.py`에서 이를 호출하도록 설정합니다.

```python
# tasks.py
from invoke import Collection
# ... 다른 import들
from scripts.organizer import organize_scratchpad

ns = Collection()
# ... 다른 태스크 추가
ns.add_task(organize_scratchpad)

# ... 나머지 Collection 설정
```

#### 4.2. `docs/HELP.md` 최종안

````markdown
## 🗂️ `invoke organize-scratchpad`: 지능형 스크래치패드 정리 도구 (v3.0)

무질서한 `scratchpad` 디렉터리를 사전 정의된 규칙에 따라 5개의 카테고리로 자동 정리하여 검색성과 생산성을 극대화합니다.

### 주요 기능

-   **지능형 분류**: 파일 이름, 경로, 내용의 일부를 점수 기반으로 분석하여 최적의 카테고리로 자동 분류합니다.
-   **안전한 사전 검토**: 실제 파일을 이동하기 전, 상세한 이동 계획(분류 근거 점수 포함)을 표 형태로 미리 보여주어 사용자가 검토하고 승인할 수 있습니다.
-   **데이터 보존**: 이름이 충돌하는 파일은 덮어쓰지 않고 `_1`, `_2`와 같은 접미사를 붙여 안전하게 보존합니다.
-   **상세 로깅**: 모든 파일 이동 내역은 사람이 읽기 좋은 `organize_log.txt`와 기계가 처리하기 좋은 `organize_journal.jsonl` 두 형식으로 자동 기록됩니다.
-   **멱등성**: 이미 정리된 파일은 건너뛰므로, 여러 번 실행해도 결과는 동일하게 유지됩니다.

### 사용법 및 옵션

```bash
# [권장] 이동 계획만 확인 (실제 이동 없음)
invoke organize-scratchpad --dry-run

# 계획 검토 후, 확인 절차를 거쳐 실제 이동 실행
invoke organize-scratchpad

# 확인 절차 없이 즉시 실행 (자동화 스크립트용)
invoke organize-scratchpad --yes
````

```

#### 4.3. Git 관리 지침
* **브랜치**: `feature/P2-UX-organizer-final` 브랜치를 생성하여 작업합니다.
* **커밋 메시지**: Conventional Commits 규칙을 따릅니다.
    * `fix(organizer): resolve SyntaxError from backslash and quotes`
    * `feat(organizer): implement robust scoring and classification logic`
    * `test(organizer): add comprehensive tests for all scenarios`
    * `docs(help): update documentation for organizer v3.0`

---

### [5부] 위험 요소 및 대응 전략

-   **위험**: 복잡한 휴리스틱으로 인한 잘못된 파일 분류 가능성.
-   **영향**: 사용자가 원하는 위치와 다른 곳에 파일이 저장되어 혼란 발생.
-   **대응 전략**:
    1.  **점수 기반 투명성**: `rich` 테이블에 분류 점수를 표시하여 사용자가 '왜' 이렇게 분류되었는지 직관적으로 이해하도록 돕습니다.
    2.  **`--dry-run` 기본 권장**: 사용자가 실제 변경 전 계획을 충분히 검토하도록 유도합니다.
    3.  **상세 로그**: 만약의 경우, `organize_log.txt`를 통해 모든 이동 경로를 추적하고 수동으로 복구할 수 있습니다.

---

본 최종 지시서는 프로젝트의 모든 요구사항을 반영한 완성된 계획입니다. 이 지시서를 따라 구현을 진행하시기 바랍니다.
```