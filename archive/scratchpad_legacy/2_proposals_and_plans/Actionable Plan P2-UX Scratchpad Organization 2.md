## 최종 작업 지시서: [P2-UX] Scratchpad Organization

**To:** Gemini-CLI 개발팀
**From:** 최종 컨설팅 LLM
**Date:** 2025-08-08
**Version:** 2.0 (Final)
**Subject:** `[P2-UX] Scratchpad Organization` 프로젝트 구현을 위한 최종 통합 작업 지시서

-----

### [서론]

본 문서는 `[P2-UX] Scratchpad Organization` 프로젝트의 성공적인 구현을 위한 최종적이고 통합된 작업 지시서입니다. 기존에 제안된 두 가지 버전의 지시서를 검토하고, 각 버전의 장점(저의 초기 제안의 구조적 명확성과 다른 LLM의 상세한 휴리스틱 및 기능적 완성도)을 결합하여, 즉시 개발에 착수할 수 있는 가장 효율적이고 구체적인 실행 계획을 제시합니다.

-----

### [1부] 최종 구현 계획 및 코드 스켈레톤

#### 1.1. 디렉터리 구조 및 핵심 파일

단일 스크립트의 복잡성을 고려하여, 핵심 로직과 `invoke` 태스크를 하나의 파일로 통합하여 관리의 편의성을 높입니다.

  * `scripts/organizer.py`: 핵심 분류 로직, 파일 이동, 사용자 인터페이스 및 `invoke` 태스크 포함
  * `tests/test_organizer.py`: `organizer.py`의 기능 검증을 위한 `pytest` 테스트 케이스
  * `tasks.py`: `organizer.py`에 정의된 태스크를 등록
  * `docs/HELP.md`: 사용자 가이드 문서

-----

#### 1.2. `scripts/organizer.py`: 핵심 로직 및 Invoke 태스크

**설계 원칙:**

  * **멱등성(Idempotency):** 이미 분류된 디렉터리 내 파일은 스캔에서 제외하여, 스크립트를 여러 번 실행해도 안전하도록 보장합니다.
  * **상세한 휴리스틱:** 정규표현식과 파일 내용 키워드를 조합하여 분류 정확도를 극대화합니다.
  * **안전한 실행:** 사용자의 명시적 승인(`rich` 라이브러리 활용) 없이는 파일 시스템을 변경하지 않으며, 이름 충돌 시 덮어쓰지 않고 접미사(`_1`, `_2`)를 붙여 데이터를 보존합니다.
  * **로깅:** 모든 파일 이동 내역을 로그 파일(`organize_log.txt`)에 기록하여 추적 가능성을 확보합니다.
  * **사용 편의성:** `--dry-run`, `--yes`와 같은 커맨드 라인 옵션을 제공하여 유연한 사용을 지원합니다.

**최종 코드 스켈레톤 (`scripts/organizer.py`):**

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

# --- 전역 객체 및 설정 ---
console = Console()
CATEGORIES = ["1_daily_logs", "2_proposals_and_plans", "3_debug_and_tests", "4_llm_io", "_archive"]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".log"}

# --- 상세 분류 규칙 (Heuristics) ---
DEFAULT_RULES = {
    "1_daily_logs": {
        "name_any_regex": [r"^\d{8}", r"(?i)daily[_-]?log", r"(?i)_task"],
        "content_any": []
    },
    "2_proposals_and_plans": {
        "name_any_regex": [r"(?i)plan|proposal|roadmap|design|spec", r"^\[?P\d(-\d)?\]?"],
        "content_any": ["목표", "계획", "단계", "제안", "로드맵"]
    },
    "3_debug_and_tests": {
        "name_any_regex": [r"(?i)debug|test|patch|report|issue|error", r"^\[?P0\]?"],
        "content_any": ["Error", "Exception", "traceback", "assertion"]
    },
    "4_llm_io": {
        "name_any_regex": [r"(?i)llm|prompt|request|answer|response"],
        "content_any": ["User:", "Assistant:", "system prompt"]
    },
}

# --- 핵심 로직 클래스 ---
class ScratchpadOrganizer:
    def __init__(self, base_dir: str, dry_run: bool = True, auto_yes: bool = False):
        self.base_path = Path(base_dir)
        self.dry_run = dry_run
        self.auto_yes = auto_yes
        self.move_plan = []

    def _read_file_head(self, path: Path, max_bytes=4096) -> str:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            return ""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        except Exception as e:
            console.log(f"파일 읽기 오류: {path}, {e}", style="dim yellow")
            return ""

    def _is_already_sorted(self, path: Path) -> bool:
        try:
            return path.relative_to(self.base_path).parts[0] in CATEGORIES
        except (ValueError, IndexError):
            return False

    def determine_category(self, path: Path) -> str:
        file_name_str = str(path.relative_to(self.base_path))
        content_head = self._read_file_head(path)

        for cat_name in ["1_daily_logs", "2_proposals_and_plans", "3_debug_and_tests", "4_llm_io"]:
            rules = DEFAULT_RULES[cat_name]
            if any(re.search(p, file_name_str, re.IGNORECASE) for p in rules["name_any_regex"]):
                return cat_name
            if content_head and any(keyword in content_head for keyword in rules["content_any"]):
                return cat_name
        return "_archive"

    def generate_move_plan(self):
        console.print(f"[bold green]'{self.base_path}' 디렉터리 스캔 중...[/bold green]")
        for item in self.base_path.rglob("*"):
            if not item.is_file() or self._is_already_sorted(item):
                continue
            
            category = self.determine_category(item)
            target_dir = self.base_path / category
            target_path = target_dir / item.name
            
            if item.parent != target_dir:
                self.move_plan.append((item, target_path))

    def display_move_plan(self):
        if not self.move_plan:
            console.print("[yellow]정리할 파일이 없습니다.[/yellow]")
            return False

        table = Table(title="[bold cyan]Scratchpad 정리 계획[/bold cyan]")
        table.add_column("분류", style="magenta", width=15)
        table.add_column("원본 파일", style="yellow", no_wrap=True)
        table.add_column("->", style="dim")
        table.add_column("목표 경로", style="green")

        for source, dest in self.move_plan:
            category = dest.parent.name
            table.add_row(category, str(source), "→", str(dest))
        
        console.print(table)
        return True

    def _get_unique_path(self, dest_path: Path) -> Path:
        if not dest_path.exists():
            return dest_path
        
        i = 1
        while True:
            new_path = dest_path.with_stem(f"{dest_path.stem}_{i}")
            if not new_path.exists():
                return new_path
            i += 1

    def execute_move_plan(self):
        console.print(f"\n[bold green]총 {len(self.move_plan)}개의 파일을 이동합니다...[/bold green]")
        moved_files = []
        for source, dest in self.move_plan:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                final_dest = self._get_unique_path(dest)
                shutil.move(str(source), str(final_dest))
                console.print(f"[green]Moved:[/green] {source} -> {final_dest}")
                moved_files.append((source, final_dest))
            except Exception as e:
                console.print(f"[bold red]오류 발생:[/bold red] {source} 이동 실패. 원인: {e}. 건너뜁니다.")
        
        self._write_log(moved_files)

    def _write_log(self, moved_files: list):
        log_path = self.base_path / "organize_log.txt"
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"--- Logged at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Moved {len(moved_files)} items.\n")
            for source, dest in moved_files:
                f.write(f"  - {source} -> {dest}\n")
        console.print(f"[dim]로그가 {log_path}에 기록되었습니다.[/dim]")

    def run(self):
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
    'scratchpad' 디렉터리를 규칙에 따라 정리합니다.

    :param base: 정리할 기본 디렉터리 (기본값: "scratchpad")
    :param dry_run: 이동 계획만 표시하고 실제 이동은 하지 않음 (기본값: False)
    :param yes: 확인 프롬프트를 생략하고 자동으로 실행 (기본값: False)
    """
    console.rule("[bold blue]Scratchpad Organizer 시작[/bold blue]")
    organizer = ScratchpadOrganizer(base_dir=base, dry_run=dry_run, auto_yes=yes)
    organizer.run()

```

-----

### [2부] 테스트 케이스 (`pytest`)

**지침:**

  * `tmp_path` fixture를 사용하여 격리된 환경에서 파일 시스템을 테스트합니다.
  * 각 분류 규칙, 이름 충돌 시나리오, 사용자 취소, 예외 처리 등을 정밀하게 검증합니다.

**테스트 코드 스켈레톤 (`tests/test_organizer.py`):**

```python
# tests/test_organizer.py
import pytest
from pathlib import Path
from scripts.organizer import ScratchpadOrganizer, determine_category

@pytest.fixture
def scratchpad(tmp_path: Path) -> Path:
    sp_dir = tmp_path / "scratchpad"
    sp_dir.mkdir()
    # 테스트 파일 생성
    (sp_dir / "20250808_daily_report.log").write_text("Daily work log")
    (sp_dir / "[P2-UX]_Final_Plan.md").write_text("프로젝트 최종 계획서")
    (sp_dir / "debug_output.txt").write_text("Exception: Null pointer")
    (sp_dir / "LLM_response_01.json").write_text('{"user": "Hi", "assistant": "Hello"}')
    (sp_dir / "misc_notes.txt").write_text("Just some random notes")
    # 이름 충돌 테스트용 파일
    (sp_dir / "1_daily_logs").mkdir()
    (sp_dir / "1_daily_logs" / "20250808_daily_report.log").write_text("existing file")
    return sp_dir

def test_determine_category(scratchpad):
    # 각 카테고리별 분류 정확성 테스트
    assert determine_category(scratchpad / "20250808_daily_report.log") == "1_daily_logs"
    assert determine_category(scratchpad / "[P2-UX]_Final_Plan.md") == "2_proposals_and_plans"
    assert determine_category(scratchpad / "debug_output.txt") == "3_debug_and_tests"
    assert determine_category(scratchpad / "LLM_response_01.json") == "4_llm_io"
    assert determine_category(scratchpad / "misc_notes.txt") == "_archive"

def test_generate_move_plan_and_idempotency(scratchpad):
    organizer = ScratchpadOrganizer(str(scratchpad))
    organizer.generate_move_plan()
    # 정리되지 않은 4개 파일만 계획에 포함되어야 함 (1개는 이미 정렬됨)
    assert len(organizer.move_plan) == 4
    
    # 올바른 목표 경로를 가지는지 확인
    src_plan = scratchpad / "[P2-UX]_Final_Plan.md"
    dest_plan = scratchpad / "2_proposals_and_plans" / "[P2-UX]_Final_Plan.md"
    assert (src_plan, dest_plan) in organizer.move_plan

def test_name_collision_handling(scratchpad):
    # dry_run=False, auto_yes=True 로 실제 실행
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=True)
    organizer.run()

    # 충돌이 발생한 파일은 `_1` 접미사를 가져야 함
    dest_dir = scratchpad / "1_daily_logs"
    assert (dest_dir / "20250808_daily_report.log").exists()
    assert (dest_dir / "20250808_daily_report_1.log").exists()

def test_user_cancellation(scratchpad, monkeypatch):
    # 사용자가 'n'을 입력하도록 Confirm.ask를 패치
    monkeypatch.setattr('rich.prompt.Confirm.ask', lambda *args, **kwargs: False)
    
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=False)
    organizer.run()

    # 파일이 이동되지 않았는지 확인
    assert (scratchpad / "debug_output.txt").exists()
    assert not (scratchpad / "3_debug_and_tests").exists()
```

-----

### [3부] `tasks.py` 및 `docs/HELP.md` 업데이트

#### 3.1. `tasks.py` 업데이트

**지침:** `scripts/organizer.py`에 정의된 태스크를 `invoke`가 인식할 수 있도록 등록합니다.

**코드 (`tasks.py`):**

```python
from invoke import Collection, task
from scripts.organizer import organize_scratchpad

# ... 다른 기존 task들 ...

ns = Collection()
# ... 다른 ns.add_task ...

# organize_scratchpad 태스크 추가
ns.add_task(organize_scratchpad, name="organize-scratchpad")
```

#### 3.2. `docs/HELP.md` 문서화

**지침:** 사용자가 새로운 기능의 강력함과 안전성을 쉽게 이해할 수 있도록 상세한 가이드를 제공합니다.

**`docs/HELP.md` 추가 내용:**

````markdown
## 🗂️ `invoke organize-scratchpad`: 지능형 스크래치패드 정리 도구

무질서한 `scratchpad` 디렉터리를 사전 정의된 규칙에 따라 5개의 카테고리로 자동 정리하여 검색성과 생산성을 극대화합니다.

### 주요 기능

-   **지능형 분류:** 파일 이름, 경로, 내용의 일부를 분석하여 최적의 카테고리로 자동 분류합니다.
-   **안전한 사전 검토:** 실제 파일을 이동하기 전, 상세한 이동 계획을 표 형태로 미리 보여주어 사용자가 검토하고 승인할 수 있습니다.
-   **데이터 보존:** 이름이 충돌하는 파일은 덮어쓰지 않고 `_1`, `_2`와 같은 접미사를 붙여 안전하게 보존합니다.
-   **작업 로그:** 모든 파일 이동 내역은 `scratchpad/organize_log.txt`에 자동으로 기록됩니다.
-   **멱등성:** 이미 정리된 파일은 건너뛰므로, 여러 번 실행해도 결과는 동일하게 유지됩니다.

### 사용법 및 옵션

```bash
# [추천] 이동 계획만 확인 (실제 이동 없음)
invoke organize-scratchpad --dry-run

# 계획 검토 후, 확인 절차를 거쳐 실제 이동 실행
invoke organize-scratchpad

# 확인 절차 없이 즉시 실행 (자동화 스크립트용)
invoke organize-scratchpad --yes
```

### 분류 체계 및 규칙 (요약)

-   **`1_daily_logs`**: `20250808`, `daily_log`, `_task` 등 날짜/로그 패턴
-   **`2_proposals_and_plans`**: `plan`, `proposal`, `P1-UX` 등 기획/설계 패턴
-   **`3_debug_and_tests`**: `debug`, `test`, `error`, `Exception` 등 테스트/오류 패턴
-   **`4_llm_io`**: `llm`, `prompt`, `response`, `User:` 등 LLM 입출력 패턴
-   **`_archive`**: 위 규칙에 해당하지 않는 모든 기타 파일
````

-----

### [4부] Git 관리 및 다음 단계

#### 4.1. Git 관리 지침

  * **브랜치:** `feature/P2-UX-organizer` 브랜치를 생성하여 모든 작업을 진행하고, 완료 후 `develop` 브랜치로 Pull Request를 요청합니다.
  * **커밋 메시지:** Conventional Commits 규칙을 따릅니다.
      * `feat(organizer): add core logic for file classification and move planning`
      * `test(organizer): add pytest cases for collision and cancellation`
      * `docs(help): update HELP.md with new organizer usage and options`

#### 4.2. 권장 작업 순서 (Action Plan)

1.  **브랜치 생성:** `git checkout -b feature/P2-UX-organizer`
2.  **파일 작성:** 위 스켈레톤 코드를 기반으로 `scripts/organizer.py`와 `tests/test_organizer.py`를 작성합니다.
3.  **단위 테스트:** `pytest tests/test_organizer.py`를 실행하여 모든 테스트가 통과하는지 확인합니다.
4.  **`invoke` 연동:** `tasks.py`를 수정하여 새로운 태스크를 등록합니다.
5.  **실행 및 검증:**
      * `invoke organize-scratchpad --dry-run`을 실행하여 실제 `scratchpad`에 대한 이동 계획을 신중하게 검토합니다.
      * 계획이 완벽하다고 판단되면, `invoke organize-scratchpad`를 실행하여 최종 정리를 수행합니다.
6.  **문서화:** `docs/HELP.md`를 업데이트합니다.
7.  **Pull Request 생성:** 모든 변경 사항을 커밋하고 `develop` 브랜치로 PR을 제출합니다.

-----

본 최종 작업 지시서가 `[P2-UX] Scratchpad Organization` 프로젝트의 성공적인 완수에 기여할 것이라 확신합니다. 추가 질문이 있으시면 언제든지 문의하십시오.