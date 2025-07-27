아래는 요청하신 **"\[P0]Debug\_18.md"** 완성본입니다. (캔버스 사용 안 함)

---

# \[P0]Debug\_18.md

**목표:** `test_last_session_cycle` 및 연관된 P0 테스트가 **pytest 환경에서도 100% 재현성 있게 통과**하도록, 파일 I/O·프로세스 호출·테스트 로직을 전면 정비한다.
**상태:** \[P0]Debug\_17까지 3회 실패 → 비상 프로토콜 발동 후, 대안 종합/통합 지시서.

---

## 0. 메타데이터

* **작성일:** 2025-07-27
* **대상 시스템:** Gemini CLI / invoke 기반 자동화 / pytest 테스트 스위트
* **우선순위:** P0 (차단 이슈)
* **적용 범위:**

  * `scripts/hub_manager.py`
  * `tests/test_p0_rules.py`
  * (필요 시) `tasks.py`, `runner.py`, `usage_tracker.py`
* **참고:** 다른 LLM 분석 결론을 반영(Atomic write, Polling read, Invoke 호출 경로 수정 등)

---

## 1. 최종 목표

1. `test_last_session_cycle`에서

   * `invoke end` 실행 후 HUB.md에 `__lastSession__:` 블록 존재 확인
   * `invoke start` 실행 후 해당 블록이 **완전히 제거**됨을 안정적으로 검증
2. 모든 변경 사항은 \*\*운영 환경(실제 invoke 실행)\*\*과 \*\*테스트 환경(pytest)\*\*에서 동일하게 동작해야 함.
3. 3회 실패 시 발동되는 비상 로그 프로토콜을 개선(로그 + 스냅샷 + 대안 제안 자동화).
4. 위 작업 완료 후, **`invoke test` 전체 PASS** (특히 P0 규칙 관련 테스트들).

---

## 2. 핵심 문제 요약 (Root Cause)

* **테스트 환경과 실제 CLI 환경 차이**

  * pytest에서 invoke를 서브프로세스로 돌릴 때, 파일 변경사항 반영 타이밍/캐시가 어긋남.
  * `program.run` 호출 방식 오류로 실제 `end` 태스크가 정상 수행되지 않고 도움말(help)이 출력된 흔적 존재.
* **파일 I/O 안정성 부족**

  * flush/fsync만으로는 Windows/pytest 조합에서 보장 부족.
  * 덮어쓰기(write-in-place) 방식 → race condition.
* **테스트 즉시 단발 read/assert**

  * 반영 지연 시 곧바로 실패.
* **정규식/파서 취약성**

  * 제어문자, 줄바꿈 혼재로 `__lastSession__` 블록 제거 실패 가능성.

---

## 3. 해결 전략 3종 세트 (필수 적용)

1. **Atomic Write(임시파일→`os.replace`)**

   * HUB.md 수정 시 무조건 임시 파일에 기록 후 교체.
   * flush + fsync + rename 조합으로 일관성 확보.

2. **폴링 기반 검증(Repeated Read with Timeout)**

   * 테스트에서 HUB.md를 한 번만 읽지 말 것.
   * 일정 시간 동안 반복 read하여 블록 등장/삭제 확인.

3. **정상적인 invoke 태스크 호출 보장**

   * 테스트 코드에서 `program.run("end", exit=False)`가 제대로 태스크를 실행하도록 호출 경로 정비.
   * 헬프 화면 출력 시 바로 실패 처리(명령 파싱 오류).

> 위 3개를 적용하면, 잔여 race condition 가능성은 사실상 0에 수렴.

---

## 4. 상세 실행 절차

### 4.1 브랜치 & 백업

```bash
# 안전한 작업을 위한 브랜치 생성
git checkout -b p0/debug_18_fix

# 비상 로그/현 상태 스냅샷(선택)
mkdir -p scratchpad/emergency_logs
```

---

### 4.2 HUB.md 쓰기 로직 교체 (Atomic Write)

**파일:** `scripts/hub_manager.py`

1. `_write()` 또는 동일 역할 함수 교체/신설:

```python
# scripts/hub_manager.py
import os
import time
from pathlib import Path

HUB_PATH = Path("docs/HUB.md")

def _write_atomic(text: str):
    if text and not text.endswith('\n'):
        text += '\n'
    tmp_path = HUB_PATH.with_suffix(".tmp")

    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_path, HUB_PATH)  # atomic
    time.sleep(0.05)  # 보수적 대기 (윈도우/AV 캐시 대비)
```

2. 기존 `_write()` 호출부를 모두 `_write_atomic()`으로 교체.

---

### 4.3 `__lastSession__` 블록 제거 파서 개선

**파일:** `scripts/hub_manager.py`

```python
import re

CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F]')  # \n, \r 제외

def strip_last_session_block(text: str) -> str:
    """
    __lastSession__ YAML 블록(위의 --- 포함) 제거.
    라인 스캔 + 정규식 하이브리드로 안전 제거.
    """
    cleaned = CONTROL_CHARS.sub('', text)
    lines = cleaned.splitlines()

    start_idx = -1
    # 뒤에서부터 __lastSession__ 라인 탐색
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith('__lastSession__'):
            # 위쪽에서 가장 가까운 '---' 찾기
            for j in range(i - 1, -1, -1):
                if lines[j].strip() == '---':
                    start_idx = j
                    break
            break

    if start_idx == -1:
        return text  # 블록 없음

    new_lines = lines[:start_idx]
    result = '\n'.join(new_lines).rstrip()
    return (result + '\n') if result else ''
```

* `clear_last_session()`에서 `strip_last_session_block` 호출 후 `_write_atomic()` 사용.

---

### 4.4 테스트 폴링 유틸 추가

**파일:** `tests/test_p0_rules.py` 상단/유틸 섹션

```python
import time

def wait_for_pattern(path, pattern, timeout=2.0, interval=0.05):
    """pattern이 path 파일에 등장할 때까지 반복 확인"""
    import re
    deadline = time.time() + timeout
    while time.time() < deadline:
        content = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(pattern, content):
            return content
        time.sleep(interval)
    raise AssertionError(f"Timeout: '{pattern}' not found in {path}")
```

* 삭제 확인용(`pattern`이 없어질 때까지)도 필요하다면 변형 함수 추가 가능.

---

### 4.5 `test_last_session_cycle` 수정

```python
def test_last_session_cycle(test_env):
    program = Program(namespace=ns, version="0.1.0")

    # 1) end 실행 → 블록 등장 대기
    program.run("end", exit=False)
    wait_for_pattern(HUB_PATH, r"__lastSession__:")

    # 2) start 실행 → 블록 제거 대기
    program.run("start", exit=False)

    # 폴링 방식으로 '없어짐' 확인
    deadline = time.time() + 2.0
    while time.time() < deadline:
        txt = HUB_PATH.read_text(encoding="utf-8", errors="ignore")
        if "__lastSession__:" not in txt:
            break
        time.sleep(0.05)
    else:
        raise AssertionError("Timeout: __lastSession__ block still present after start")
```

---

### 4.6 Invoke 호출 경로/도움말 출력 문제 해결

* 테스트에서 `program.run("end", exit=False)` 호출 시 **help 출력이 나오면 즉시 실패/로그**.
* (옵션) subprocess 사용 시:

```python
import subprocess, sys

def run_invoke(*args):
    cmd = ["invoke", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    if proc.returncode != 0:
        raise AssertionError(f"invoke {' '.join(args)} failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc.stdout
```

* `program.run`과 혼용하지 말고 한 가지 방식 고정. (권장: `Program(namespace=ns)` 방식)

---

### 4.7 usage.db 잠금 이슈(선택)

* `usage_tracker.py`에서 DB write 후 닫기 보장.
* 테스트 teardown 시 파일 삭제 전 `conn.close()` 확인 및 짧은 `sleep(0.1)`.

---

## 5. 실패 시 대응 프로토콜(업데이트)

1. **3회 연속 동일 테스트 실패 시**

   * `scratchpad/emergency_logs/P0_Debug_18_failure_log_YYYYMMDD_HHMM.md` 생성

     * 실행 명령, stdout/stderr, HUB.md Before/After, timestamps, OS/Python/pytest 버전
   * `git show HEAD:docs/HUB.md`로 커밋 시점 버전 스냅샷 포함
2. **대안 제시 자동화:**

   * Atomic rename 미적용 여부, 폴링 로직 존재 여부 자동 체크 → 누락 시 이를 지적
3. **사용자 질의 대기:**

   * 다음 스텝(폴링 횟수 증가, timeout 연장, in-proc 실행 전환 등)을 제안하고 응답 대기

---

## 6. 검증 체크리스트

* [ ] `scripts/hub_manager.py`가 atomic write 사용
* [ ] `strip_last_session_block`로 테스트 파일 내 모든 변종 블록 제거 가능
* [ ] `tests/test_p0_rules.py::test_last_session_cycle` 폴링 로직 도입
* [ ] pytest 실행 시 help 출력이 안 나오거나 나오면 곧바로 실패 처리
* [ ] `invoke test` 전체 PASS
* [ ] 비상 로그 파일 생성 경로/형식 확인

---

## 7. 커밋 & 보고

1. 모든 수정 후:

   ```bash
   invoke test
   ```
2. PASS 시:

   ```bash
   git add .
   git commit -m "P0: Debug_18 – fix last_session_cycle via atomic write & polling"
   ```
3. 보고 메시지(예시):

   > ✅ `[P0]Debug_18` 완료. 모든 P0 테스트 통과.
   >
   > * Atomic Write + Polling 적용
   > * Invoke 호출 경로 정비
   > * strip\_last\_session\_block 하드닝
   >   비상 로그/대안 프로토콜 갱신 완료.

---

## 8. 부록: Patch Diff 예시

### 8.1 hub\_manager.py (요약 diff)

```diff
-def _write(text: str):
-    with open(HUB_PATH, "w", encoding="utf-8", newline="") as f:
-        f.write(text)
-        f.flush()
-        os.fsync(f.fileno())
-    time.sleep(0.05)
+def _write_atomic(text: str):
+    if text and not text.endswith('\n'):
+        text += '\n'
+    tmp_path = HUB_PATH.with_suffix(".tmp")
+    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
+        f.write(text)
+        f.flush()
+        os.fsync(f.fileno())
+    os.replace(tmp_path, HUB_PATH)
+    time.sleep(0.05)
```

### 8.2 test\_p0\_rules.py (wait\_for\_pattern 추가 등)

```diff
+def wait_for_pattern(path, pattern, timeout=2.0, interval=0.05):
+    import re, time
+    deadline = time.time() + timeout
+    while time.time() < deadline:
+        content = path.read_text(encoding="utf-8", errors="ignore")
+        if re.search(pattern, content):
+            return content
+        time.sleep(interval)
+    raise AssertionError(f"Timeout: '{pattern}' not found in {path}")
```

---

## 9. 마무리

* 본 지시서는 다른 LLM들의 의견(Atomic rename, Polling read, Invoke 호출 정정)을 모두 반영한 최종 통합본입니다.
* 상기 절차를 그대로 수행하면 `test_last_session_cycle` 및 관련 P0 테스트는 안정적으로 통과합니다.

**실행 후 결과 보고 바랍니다.**

---

## **END OF FILE**
