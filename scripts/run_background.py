#!/usr/bin/env python3
"""
비동기 백그라운드 실행 유틸리티
- UTF-8 인코딩 강제, 윈도우 콘솔 창 최소화/비표시 옵션
- 표준 출력/에러를 logs/background/<ts>_<name>_{out,err}.log 에 기록
- 테스트 모드(--test) 제공: 간단한 Python 작업을 백그라운드로 실행해 검증
"""
import argparse
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 출력 스타일
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, item


def ensure_logs_dir() -> Path:
    root = Path(__file__).resolve().parents[1]
    bg_dir = root / "logs" / "background"
    bg_dir.mkdir(parents=True, exist_ok=True)
    return bg_dir


def build_env() -> dict:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


def run_bg(cmd: str, name: str = "task", cwd: str | None = None) -> dict:
    logs_dir = ensure_logs_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{ts}_{name}"
    out_path = logs_dir / f"{prefix}_out.log"
    err_path = logs_dir / f"{prefix}_err.log"

    env = build_env()

    # 윈도우 전용 창 숨김 옵션
    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    with open(out_path, "wb") as out_f, open(err_path, "wb") as err_f:
        # shell=True 로 단일 문자열 커맨드 실행을 단순화
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd or str(Path(__file__).resolve().parents[1]),
            stdout=out_f,
            stderr=err_f,
            env=env,
            creationflags=creationflags,
            startupinfo=startupinfo,
        )

    return {"pid": proc.pid, "out": str(out_path), "err": str(err_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="비동기 백그라운드 실행 유틸리티")
    parser.add_argument("--cmd", help="백그라운드로 실행할 전체 커맨드 문자열", default=None)
    parser.add_argument("--name", help="로그 파일 접두어 이름", default="task")
    parser.add_argument("--cwd", help="작업 디렉터리", default=None)
    parser.add_argument("--test", action="store_true", help="테스트 모드 실행")

    args = parser.parse_args()

    print(header("Run Background"))

    if args.test and not args.cmd:
        # 간단한 파이썬 테스트 태스크: 시작/대기/종료 메시지 출력
        py = sys.executable
        test_code = (
            "import sys,time;"
            "print('BG_START');sys.stdout.flush();"
            "time.sleep(1);"
            "print('BG_END')"
        )
        cmd = f'"{py}" -c "{test_code}"'
        info = run_bg(cmd, name=args.name or "test", cwd=args.cwd)
        print(item(1, kv("mode", "test")))
        print(item(2, kv("pid", info["pid"])))
        print(item(3, kv("stdout", info["out"])))
        print(item(4, kv("stderr", info["err"])))
        sys.exit(0)

    if not args.cmd:
        print("ERROR: --cmd 또는 --test 중 하나는 필요합니다")
        sys.exit(2)

    info = run_bg(args.cmd, name=args.name, cwd=args.cwd)
    print(item(1, kv("pid", info["pid"])))
    print(item(2, kv("stdout", info["out"])))
    print(item(3, kv("stderr", info["err"])))
    sys.exit(0)


if __name__ == "__main__":
    main()

