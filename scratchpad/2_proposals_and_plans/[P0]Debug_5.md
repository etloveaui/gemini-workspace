### **현재 문제점 요약**

1. **`AttributeError` (No attribute or config key found for 'task')**:

   * `tasks.py` 내에서 `Context` 객체(`c`)의 `task` 속성에 접근할 수 없어서 발생하는 오류입니다. `invoke` 라이브러리의 `Context` 객체가 기본적으로 태스크에 대한 메타데이터를 포함하지 않기 때문에, `task` 속성에 접근하는 방식이 잘못된 것으로 추정됩니다.

2. **`log_usage` 통합 문제**:

   * `c.run()`을 감싸는 `logged_run` 함수에서 `log_usage`와 `c.run()`을 반복적으로 호출하면서 오류가 발생합니다. 또한, 로깅을 통해 `task_name`을 안정적으로 전달하는 방법에 대한 추가적인 해결책이 필요합니다.

---

### **해결 방안 제안**

1. **`AttributeError` 문제 해결**:
   `invoke`에서 `task` 이름을 직접 `Context` 객체에서 가져올 수 없기 때문에, `task_name`을 함수 인자로 전달하는 방식으로 해결할 수 있습니다. 이 방식은 `logged_run`을 호출할 때 태스크 이름을 명시적으로 전달하는 것입니다.

   예시 코드:

   ```python
   def logged_run(task_name, c, command, **kwargs):
       """c.run()을 감싸서 실행 전후로 자동으로 로그를 남기는 중앙 집중식 래퍼 함수."""
       from scripts.usage_tracker import log_usage
       
       log_usage(task_name, "command_start", description=f"Executing: {command}")
       
       result = c.run(command, **kwargs)
       
       log_usage(task_name, "command_end", description=f"Completed: {command}")
       return result
   ```

   `tasks.py` 내 `test` 태스크에서 `task_name`을 명시적으로 전달:

   ```python
   @task
   def test(c):
       """/tests 폴더의 모든 pytest 케이스를 실행하여 시스템 신뢰도를 검증합니다."""
       print("Running Autonomous Test Harness...")
       logged_run('test', c, "pytest -v")  # 명시적으로 task_name 전달
   ```

2. **`log_usage` 통합**:
   `log_usage`와 `c.run()`의 결합 문제는 `c.run()` 호출 전에 로그를 기록한 후, 그 실행이 완료되면 다시 로그를 기록하는 방식으로 해결할 수 있습니다. 이를 통해 각 명령어가 시작되기 전에 로그를 남기고, 명령어가 완료된 후에도 로그를 남길 수 있습니다.

3. **`SyntaxWarning` 해결**:
   Python f-string 내에서 백슬래시 이스케이프 문제는 `raw string`을 사용하여 해결할 수 있습니다. 이는 f-string 내에서 백슬래시를 escape 시퀀스로 인식하지 않도록 방지합니다.

   ```python
   run(r'powershell.exe -ExecutionPolicy Bypass -File ".\\scripts\\git-wip.ps1" -Message "{message}"')  # raw string 사용
   ```

---

### **다음 단계**

1. **AttributeError 문제 해결**: 위에서 제시한 대로 `task_name`을 명시적으로 전달하여 `logged_run`을 호출합니다.
2. **`log_usage` 통합**: `logged_run` 함수 내에서 각 명령을 실행하고 로그를 기록하는 방식으로 조정합니다.
3. **`SyntaxWarning` 해결**: 백슬래시 이스케이프 문제를 해결하기 위해 f-string에서 `raw string`을 사용하거나, 백슬래시를 이스케이프합니다.

이 해결책들을 적용하고 나면 `tasks.py` 내에서 발생한 문제들을 해결할 수 있을 것입니다. 추가적으로 다른 문제나 수정이 필요하다면 다시 말씀해 주세요!
