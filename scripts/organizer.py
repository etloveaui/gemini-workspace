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
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.yaml', '.yml', '.py', '.log', '.html'}
SKIP_DIRS = set(CATEGORIES)

# --- 상세 분류 규칙 (정규식/키워드/확장자) ---
RULES = {
    "1_daily_logs": {
        "name_regex": [
            r"^\d{8}$\b",                    # 20250805...
            r"\b20\d{2}[-_]\d{2}[-_]\d{2}\b",  # 2025-08-05 / 2025_08_05
            r"(?i)daily[_-]?log",
            r"(?i)_TASK(\.|$)",
        ],
        "content_keywords": ["작업 로그", "일일 보고"],
        "ext": {'.md', '.txt'},
    },
    "2_proposals_and_plans": {
        "name_regex": [
            r"(?i)\b(plan|proposal|roadmap|design|spec|blueprint)\b",
            r"^\(?P\d(?:-\d)?\)?"  # [P1], [P1-2], P1, P1-2
        ],
        "content_keywords": ["목표", "계획", "단계", "제안", "로드맵"],
        "ext": {'.md', '.txt', '.docx'},
    },
    "3_debug_and_tests": {
        "name_regex": [
            r"(?i)\b(debug|test|patch|report|issue|error)\b",
            r"^\(?P0\)?",  # [P0], P0
            r"\b_debug_",
        ],
        "content_keywords": ["Error", "Exception", "traceback", "Assertion"],
        "ext": {'.py', '.log', '.txt', '.md'},
    },
    "4_llm_io": {
        "name_regex": [
            r"(?i)\b(LLM|Prompt|Request|Answer|Response)\b",
            r"(^|/)" + "LLM_" + "(Requests|Answer)" + "(/|$)",  # 폴더 컨텍스트
        ],
        "content_keywords": ["User:", "Assistant:", "system prompt"],
        "ext": {'.md', '.json', '.txt'},
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
        console.print(f"[bold green]'{{self.base_path}}' 디렉터리 스캔 중...[/bold green]")
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
            f.write(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " ---" + "\n")
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