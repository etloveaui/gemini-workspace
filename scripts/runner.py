# /scripts/runner.py
import subprocess
from scripts.usage_tracker import log_usage

def run_command(task_name: str, args: list[str], **kwargs):
    """인자를 리스트로 받아 안전하게 실행하고 로그를 남기는 새로운 표준 실행기."""
    command_str = " ".join(args)
    log_usage(task_name, "command_start", details=f"Executing: {command_str}")
    try:
        # 셸 파싱을 피하기 위해 shell=False가 기본값
        result = subprocess.run(args, text=True, capture_output=True, encoding="utf-8", check=True, **kwargs)
        log_usage(task_name, "command_end", details=f"Success: {result.stdout[:200]}")
        return result
    except subprocess.CalledProcessError as e:
        log_usage(task_name, "command_error", details=f"Failed: {e.stderr[:200]}")
        # 실패 시 예외를 다시 발생시켜 상위 태스크에서 인지하도록 함
        raise e