"""간단한 파일 변경 워처 (폴링 기반)

사용법:
  venv/Scripts/python.exe scripts/watch_file.py --dir communication/codex/inbox --interval 1.0

의존성: 표준 라이브러리만 사용
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Dict


def scan(dir_path: Path) -> Dict[Path, float]:
    state: Dict[Path, float] = {}
    for p in dir_path.rglob("*"):
        if p.is_file():
            try:
                state[p] = p.stat().st_mtime
            except FileNotFoundError:
                continue
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="폴링 기반 파일 변경 감지기")
    parser.add_argument("--dir", dest="target", default="communication/codex/inbox", help="감시 디렉터리")
    parser.add_argument("--interval", type=float, default=1.0, help="폴링 주기(초)")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)

    print(f"[watch] start: {target}")
    prev = scan(target)
    try:
        while True:
            time.sleep(args.interval)
            curr = scan(target)

            # 신규
            for p in curr.keys() - prev.keys():
                print(f"[created] {p}")
            # 변경
            for p in curr.keys() & prev.keys():
                if curr[p] != prev[p]:
                    print(f"[modified] {p}")
            # 삭제
            for p in prev.keys() - curr.keys():
                print(f"[deleted] {p}")

            prev = curr
    except KeyboardInterrupt:
        print("[watch] stop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

