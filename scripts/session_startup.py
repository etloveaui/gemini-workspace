"""Codex 세션 스타트업 스크립트

기능:
- communication 폴더(특히 codex 하위) 기본 디렉터리 생성
- 임시 파일(.tmp) 안전 보관(archive) 이동
- 필수 문서/가이드가 없으면 최소 템플릿 생성
- 실행 결과 리포트를 communication/codex/startup_reports에 기록

주의:
- 모든 I/O는 UTF-8 사용
- 파괴적 삭제 없음(보관 폴더로만 이동)
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def ensure_dirs(paths: List[Path]) -> List[Path]:
    created = []
    for p in paths:
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            created.append(p)
    return created


def ensure_files(files: List[Tuple[Path, str]]) -> List[Path]:
    created = []
    for path, content in files:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(path)
    return created


def safe_archive_tmp(codex_dir: Path) -> Tuple[int, List[Path]]:
    archive = codex_dir / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    moved = []
    count = 0
    for p in codex_dir.rglob("*.tmp"):
        if p.is_file():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = archive / f"{p.stem}_{ts}{p.suffix}"
            try:
                shutil.move(str(p), str(dest))
                moved.append(dest)
                count += 1
            except Exception:
                # 보존: 실패해도 중단하지 않음
                pass
    return count, moved


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")

    # 필수 디렉터리
    docs_core = repo_root / "docs" / "CORE"
    comm_root = repo_root / "communication"
    codex_root = comm_root / "codex"
    shared_root = comm_root / "shared"
    inbox = codex_root / "inbox"
    outbox = codex_root / "outbox"
    processed = codex_root / "processed"
    startup_reports = codex_root / "startup_reports"

    created_dirs = ensure_dirs([
        docs_core,
        shared_root,
        codex_root,
        inbox,
        outbox,
        processed,
        startup_reports,
    ])

    # 필수 파일(없을 때만 템플릿 생성)
    checklist_md = docs_core / "AGENTS_CHECKLIST.md"
    hub_md = docs_core / "HUB_ENHANCED.md"
    comm_guide = shared_root / "COMMUNICATION_GUIDE.md"
    system_md = repo_root / "docs" / "AGENT_COMMUNICATION_SYSTEM.md"

    today = now.strftime("%Y-%m-%d")
    files_created = ensure_files([
        (
            checklist_md,
            f"# AGENTS 체크리스트\n\n"
            f"- 생성: {today}\n- 목적: 세션 시작 시 필수 확인 항목 정리\n\n"
            "## 시작 체크\n- 문서 확인(HUB_ENHANCED.md)\n- 통신 폴더 상태 확인\n- 스타트업 스크립트 실행 기록 확인\n",
        ),
        (
            hub_md,
            f"# HUB_ENHANCED (초기 템플릿)\n\n"
            f"- 생성: {today}\n- 설명: 확장된 중앙 허브 문서(실제 운영 규칙으로 업데이트 필요)\n\n"
            "## 핵심\n- 에이전트 역할과 책임\n- 작업 라우팅 흐름\n- 품질 게이트/검토 절차\n",
        ),
        (
            comm_guide,
            f"# Communication Quick Start (공유)\n\n"
            f"- 생성: {today}\n- 목적: 파일 기반 비동기 소통 흐름 빠른 안내\n\n"
            "## 폴더\n- communication/codex/inbox: 수신\n- communication/codex/outbox: 발신\n- communication/codex/processed: 처리완료\n- communication/codex/archive: 보관\n\n"
            "## 규칙\n- 모든 파일 UTF-8\n- yyyymmdd_XX_topic 네이밍 권장\n",
        ),
        (
            system_md,
            f"# AGENT 통신 시스템 (초기 템플릿)\n\n"
            f"- 생성: {today}\n- 설명: 파일 기반 비동기 통신 명세(상세화 필요)\n\n"
            "## 이벤트\n- NEW_MESSAGE: inbox 투입\n- PROCESSED: processed 이동\n",
        ),
        (
            codex_root / "README.md",
            "# Codex 통신 영역\n\n- inbox/outbox/processed/archive 폴더를 사용합니다.\n- 임시파일(.tmp)은 스타트업에서 archive로 이동됩니다.\n",
        ),
    ])

    # 통신 폴더 .tmp 안전 보관
    tmp_moved, moved_paths = safe_archive_tmp(codex_root)

    # 리포트 작성
    report_path = startup_reports / f"{now.strftime('%Y%m%d_%H%M%S')}.log"
    report_lines = [
        "Codex Session Startup Report",
        f"timestamp: {ts}",
        f"repo_root: {repo_root}",
        "",
        "[created_dirs]",
    ]
    report_lines += [f"- {p}" for p in created_dirs] or ["- (none)"]
    report_lines += ["", "[created_files]"]
    report_lines += [f"- {p}" for p in files_created] or ["- (none)"]
    report_lines += ["", f"[archived_tmp_files] count={tmp_moved}"]
    report_lines += [f"- {p}" for p in moved_paths] or ["- (none)"]

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    # 콘솔 출력 요약
    print("[Codex Startup] 완료")
    print(f"- 생성 디렉터리: {len(created_dirs)}")
    print(f"- 생성 파일: {len(files_created)}")
    print(f"- 보관된 .tmp: {tmp_moved}")
    print(f"- 리포트: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

