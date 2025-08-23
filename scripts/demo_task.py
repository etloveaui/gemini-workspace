from __future__ import annotations

"""
데모 작업 스크립트: 메시지를 받아 처리하고 구조적 로깅/트레이싱 시연.

사용:
  venv/Scripts/python.exe scripts/demo_task.py --message "hello" --repeat 2
"""

import argparse
import random
import time
from typing import Any

from utils.logging import get_logger, init_logging, trace, with_correlation


@trace
def _work_once(msg: str) -> str:
    # 가벼운 처리 시뮬레이션
    time.sleep(random.uniform(0.02, 0.08))
    return msg.upper()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--message", default="ping")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args(argv)

    init_logging(level=args.log_level)
    log = get_logger(__name__)

    with with_correlation() as cid:
        log.info("demo_start", extra={"extra": {"repeat": args.repeat, "correlation_id": cid}})
        outputs: list[str] = []
        for _ in range(args.repeat):
            outputs.append(_work_once(args.message))
        log.info("demo_done", extra={"extra": {"outputs": outputs}})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

