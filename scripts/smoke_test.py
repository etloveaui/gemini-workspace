from __future__ import annotations

"""간단 스모크 테스트: 로깅/트레이싱이 동작하는지 확인.

사용:
  venv/Scripts/python.exe scripts/smoke_test.py
"""

import json
import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, "scripts/demo_task.py", "--message", "hello", "--repeat", "2", "--log-level", "DEBUG"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if proc.returncode != 0:
        print("[smoke] demo_task failed")
        print(proc.stderr)
        return 1

    # 출력이 JSON 라인인지 대략 검증
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    try:
        parsed = [json.loads(ln) for ln in lines[:3]]
    except Exception:  # noqa: BLE001
        print("[smoke] output is not JSON lines: ")
        print(proc.stdout)
        return 2

    keys_ok = all("ts" in d and "level" in d and "msg" in d for d in parsed)
    if not keys_ok:
        print("[smoke] missing keys in logs")
        print(parsed)
        return 3

    print("[smoke] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

