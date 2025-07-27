두 군데 모두 “원인 → 최소 수정 패치 → 재현/검증” 순서로 정리합니다.

---

## 1) `test_commit_protocol_integration` (Executor 초기화)

**원인**

* `invoke.Executor`의 시그니처는 `Executor(collection, config=None)` 입니다.
* `Program` 객체엔 `collection` 속성이 없고, 실제 컬렉션은 `program.namespace`(또는 테스트 코드에서 이미 가지고 있는 `ns`) 입니다.

**패치(테스트 코드 쪽)**

```diff
# tests/test_p0_rules.py
@@ 79,7 79,7 @@
 program = Program(namespace=ns, version="0.1.0")
 config = Config(overrides={'program': program})
- executor = Executor(collection=program.collection, config=config)
+ executor = Executor(collection=program.namespace, config=config)  # or simply ns
 result = executor.execute("wip --message='Test commit via protocol'")
 assert result.ok, f"invoke wip command failed: {result.stderr}"
```

> 만약 `program.namespace`도 없다면, 그냥 `Executor(collection=ns, config=config)`로 넣으면 됩니다.

---

## 2) `test_last_session_cycle` (**lastSession** 블록 미삭제)

### 2-1. 진짜 원인 먼저 짚기

* **`tasks.start()` 안에서 **lastSession** 제거 로직(handle\_last\_session/clear\_last\_session)을 안 부르고 있습니다.**
  테스트는 `start` 실행 후 HUB.md에서 블록이 사라져 있어야 한다고 가정합니다. strip 함수 품질 문제 이전에, 애초에 호출이 안 되면 당연히 안 지워집니다.

### 2-2. 최소 수정

**tasks.py**

```diff
# tasks.py (start 태스크 상단)
-from invoke import task, Collection, Program
+from invoke import task, Collection, Program
+from scripts.hub_manager import handle_last_session  # ← 추가

 @task
 def start(c):
     """[Intelligent Engine Start] 컨텍스트 엔진을 통해 세션을 시작하고 브리핑합니다."""
-    log_usage("session", "start", description="Intelligent session started")
+    log_usage("session", "start", description="Intelligent session started")
+
+    # 0. 지난 세션 블록 처리
+    handle_last_session()  # ← 가장 먼저 호출

     print("▶️ Starting intelligent session...")
```

이 한 줄로 테스트는 대부분 통과할 겁니다.

### 2-3. 그래도 strip이 헷갈리면, 더 견고한 버전으로 바꿔두세요

```python
# scripts/hub_manager.py
import re

CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F]')
BLOCK_RE = re.compile(
    r'^\s*---\s*\n__lastSession__:\s*(?:.*?)(?=^\s*---\s*$|\Z)',
    flags=re.MULTILINE | re.DOTALL
)

def strip_last_session_block(text: str) -> str:
    cleaned = CTRL.sub('', text.replace('\r\n', '\n').replace('\r', '\n'))
    new = re.sub(BLOCK_RE, '', cleaned).rstrip()
    return (new + '\n') if new else ''
```

`clear_last_session()`에서 이 함수 호출 후 반드시 `utf-8`로 다시 써 주세요.

---

## 3) 실행/검증 순서

```bash
# 1. 코드 수정 후
invoke start   # 블록이 지워지는지 수동 확인 가능
invoke end     # 블록이 다시 생기는지 확인

# 2. 테스트
invoke test
```

---

## 4) usage.db 잠금 경고(WinError 32)

테스트 셋업/티어다운에서 파일을 rename/delete하려다 잠금된 상태. 큰 실패는 아니지만 깔끔히 하려면:

* `scripts/usage_tracker.py`에서 커넥션을 항상 `with sqlite3.connect(DB_PATH) as conn:` 형태로 열고 자동 close.
* 테스트 셋업 전에 `conn.close()` 보장 or `os.environ["SQLITE_BUSY_TIMEOUT"]="1000"` 등 설정.
* 테스트에서 굳이 rename 하지 말고 `tempfile.NamedTemporaryFile`로 별도 DB를 쓰게 override.

(지금은 경고 수준이라 우선순위 낮음.)

---
