from scripts.usage_tracker import log_usage

def logged_run(task_name, c, command, **kwargs):
    """c.run()을 감싸서 실행 전후로 자동으로 로그를 남기는 중앙 집중식 래퍼 함수."""
    log_usage(task_name, "command_start", description=f"Executing: {command}")
    
    result = c.run(command, encoding='utf-8', hide=True, warn=True, **kwargs)
    
    log_usage(task_name, "command_end", description=f"Completed: {command}")
    return result