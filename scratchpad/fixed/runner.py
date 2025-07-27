# /scripts/runner.py
import subprocess
from scripts.usage_tracker import log_usage

def run_command(task_name: str, args: list[str], **kwargs):
    """인자를 리스트로 받아 안전하게 실행하고 로그를 남기는 새로운 표준 실행기."""
    command_str = " ".join(args)
    log_usage(task_name, "command_start", details=f"Executing: {command_str}")
    
    # kwargs에서 'check' 및 'hide' 인자를 추출하고 기본값 설정
    check_param = kwargs.pop('check', True)
    hide_param = kwargs.pop('hide', False)

    try:
        # 셸 파싱을 피하기 위해 shell=False가 기본값
        result = subprocess.run(args, text=True, capture_output=True, encoding="utf-8", errors="replace", check=check_param, **kwargs)
        log_usage(task_name, "command_end", details=f"Success: {result.stdout[:200]}")
        return result
    except subprocess.CalledProcessError as e:
        log_usage(task_name, "command_error", details=f"Failed: {e.stderr[:200]}")
        # check=False일 경우 예외를 발생시키지 않고 result 반환
        if not check_param:
            # check=False일 경우 예외를 발생시키지 않고 CompletedProcess 객체 반환
            return subprocess.CompletedProcess(
                args=e.cmd,
                returncode=e.returncode,
                stdout=e.stdout,
                stderr=e.stderr
            )
        raise e