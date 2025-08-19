
> **목표:** 마지막 남은 실패 테스트(`tests/test_p0_rules.py::test_runner_error_logging`)를 100% 안정적으로 통과시키고, 같은 유형의 문제가 재발하지 않도록 구조를 고도화한다.

---

## 0. TL;DR (즉시 실행 요약)

1. **DB 경로 주입 방식으로 전환(A-안, 권장)**

   * `runner.py`/`usage_tracker.py`의 모든 DB 접근 함수에 `db_path` 인자를 추가.
   * 기본값은 환경변수(`GEMINI_USAGE_DB_PATH`) → 없으면 `usage.db`.
   * 테스트에서는 `tmp_path`를 넘겨 완전 분리.

2. **테이블 이름/스키마 단일화**

   * 테스트가 기대하는 테이블명(`usage` or `usage_logs`) 확인 후 **통일**.
   * 생성은 `CREATE TABLE IF NOT EXISTS ...`로 항상 선보장.

3. **테스트 수정**

   * `test_runner_error_logging`에서 **환경변수 세팅 + importlib.reload** 또는 **db\_path 직접 인자 전달**로 확실한 경로 고정.
   * monkeypatch 순서 문제 제거.

4. **검증/롤백/체크리스트 수행**

   * `pytest -k test_runner_error_logging -vv` → PASS 확인
   * `pytest -vv` 전체 통과
   * 변경 파일 커밋 + 문서 보호 재검증

---

## 1. 문제 정의

* **실패 테스트:** `tests/test_p0_rules.py::test_runner_error_logging`
* **오류:** `sqlite3.OperationalError: no such table: usage`
* **근본 원인:**

  * DB 초기화/접근이 **모듈 전역 변수**(`DB_PATH`)와 **import 시점**에 의존.
  * pytest `monkeypatch`로 경로 변경해도 이미 로드된 모듈/함수는 **옛 경로 또는 테이블 미생성 상태** 참조.
  * 결과: 테스트가 바라보는 DB엔 테이블이 없어서 OperationalError.

---

## 2. 목표(Outcome)

* `test_runner_error_logging` **1회 시도에 PASS**.
* DB 로깅 로직이 **테스트/운영 환경 어디서든 확실히 동작**.
* 이후 새로운 테스트/기능 추가 시에도 DB 경로/스키마로 인한 실패 재발 방지.

---

## 3. 해결 전략 옵션

### ✅ **A-안 (권장): “DB 경로 인자화 + 환경변수 기반”**

* 모든 DB 관련 함수에 `db_path` 인자를 추가하고 기본값은 `os.environ["GEMINI_USAGE_DB_PATH"]` → 없으면 루트 `usage.db`.
* 테스트는 `tmp_path`를 넘기거나 env 설정 후 `importlib.reload`로 반영.

### ⚠️ B-안 (우회): “monkeypatch + importlib.reload”만으로 해결

* 기존 설계 그대로 두고 테스트에서 monkeypatch 후 `importlib.reload(runner)`
* 단기 응급 처치 가능하지만, 다시 같은 문제 재발할 가능성 큼.

### 🚫 C-안 (권장하지 않음): “테스트에서 CREATE TABLE 직접 실행”

* SELECT 전에 매번 CREATE TABLE 실행 → 침투적, 구조적으로 부정확.

---

## 4. 구체 작업 지시 (A-안 구현)

### 4.1 공통 상수/환경

* **환경변수 키:** `GEMINI_USAGE_DB_PATH`
* **기본 DB 경로:** `Path(__file__).parent.parent / "usage.db"`

```python
# 공통 패턴 예시
import os
from pathlib import Path

DEFAULT_DB_PATH = Path(os.getenv("GEMINI_USAGE_DB_PATH", Path(__file__).parent.parent / "usage.db"))
```

---

### 4.2 `scripts/runner.py` 수정

1. **DB 유틸 함수 정리** (필요 시 `scripts/db_utils.py`로 분리 가능)

```python
# scripts/runner.py (발췌/대체)
import sqlite3
from datetime import datetime
from pathlib import Path
import os
import subprocess

DEFAULT_DB_PATH = Path(os.getenv("GEMINI_USAGE_DB_PATH", Path(__file__).parent.parent / "usage.db"))

def _ensure_db(db_path: Path = DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            command TEXT,
            stdout TEXT,
            stderr TEXT
        )
    """)
    conn.commit()
    conn.close()

def _log_event(task_name: str, event_type: str, command: str, stdout: str, stderr: str, db_path: Path = DEFAULT_DB_PATH):
    _ensure_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usage (timestamp, task_name, event_type, command, stdout, stderr)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), task_name, event_type, command, stdout, stderr))
    conn.commit()
    conn.close()

def run_command(task_name: str, args: list[str], cwd=None, check=True, db_path: Path = DEFAULT_DB_PATH):
    _ensure_db(db_path)
    try:
        cp = subprocess.run(
            args,
            cwd=str(Path(cwd).resolve()) if cwd else None,
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=check,
            shell=False
        )
        return cp
    except subprocess.CalledProcessError as e:
        _log_event(task_name, "command_error", " ".join(args), e.stdout, e.stderr, db_path)
        raise
```

> **주의:** 기존 `usage_tracker.py`가 있다면, 스키마/테이블명/컬럼명을 일치시키거나, 위 runner용 테이블만 유지해도 됨(테스트가 runner의 로깅만 본다면).

---

### 4.3 (선택) `scripts/usage_tracker.py` 동기화

* 동일한 DB/테이블을 사용한다면, **스키마/테이블명을 runner.py와 맞춤**.
* `init_db()` → `_ensure_db()` 동일 시그니처로 정리.

---

### 4.4 테스트 코드 수정 (`tests/test_p0_rules.py`)

#### 4.4.1 테스트 픽스처

```python
# tests/conftest.py (또는 해당 파일 상단)
import importlib
import os
import sqlite3
import pytest
from pathlib import Path

@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "usage.db"
    monkeypatch.setenv("GEMINI_USAGE_DB_PATH", str(db))
    # 모듈 리로드로 환경변수 반영
    from scripts import runner
    importlib.reload(runner)
    yield db
```

#### 4.4.2 실제 테스트

```python
def test_runner_error_logging(isolated_db):
    from scripts import runner
    import subprocess, sqlite3

    with pytest.raises(subprocess.CalledProcessError):
        runner.run_command("test_error", ["python", "-c", "import sys; sys.exit(1)"])

    # 검증
    conn = sqlite3.connect(isolated_db)
    cur = conn.cursor()
    cur.execute("""
        SELECT task_name, event_type, command, stderr
        FROM usage
        ORDER BY id DESC LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()

    assert row is not None, "usage 테이블에 기록이 없습니다."
    assert row[0] == "test_error"
    assert row[1] == "command_error"
    assert "sys.exit(1)" in (row[2] or "")
```

> **테이블명/컬럼명은 실제 runner.py 구현에 맞게 조정하세요.**

---

## 5. 검증 절차

1. 단일 테스트 먼저:

   ```bash
   pytest -k test_runner_error_logging -vv
   ```

   * PASS 확인

2. 전체 테스트:

   ```bash
   pytest -vv         # or invoke test
   ```

   * 기존 11개(9 pass / 1 skip / 1 fail) → **모두 pass (skip 유지 가능)**

3. DB 내용 수동 확인:

   ```python
   sqlite3 /path/to/usage.db "select * from usage limit 3;"
   ```

   * 에러 로그 레코드 존재 확인

4. 문서 삭제 방지/훅 재확인

   * `[P0]Debug_21.md`를 `.no_delete_list`에 추가
   * pre-commit 훅 동작 테스트

---

## 6. 롤백 및 백업

* 수정 전 `runner.py`, `usage_tracker.py` 백업: `*.bak`
* 문제가 생기면 `git checkout HEAD~1 scripts/runner.py` 등으로 복원
* DB 스키마 변경 시 기존 `usage.db` 백업

---

## 7. 재발 방지 체크리스트

* [ ] DB 접근 함수 모두 **인자 주입/환경변수** 기반
* [ ] `CREATE TABLE IF NOT EXISTS`로 테이블 생성 보장
* [ ] 테스트마다 **독립 DB 파일** 사용 (tmp\_path)
* [ ] `shell=False + list` 원칙 준수(이미 적용)
* [ ] 문서 보호 훅 유지(이미 적용)
* [ ] 테스트 후 CLI 상태/로그 정리 태스크(`invoke clean-cli`) 정상 동작 확인

---

## 8. 추가 비상 대응(Plan B/C)

* **Plan B:** 모듈 리로드 + monkeypatch 조합 유지(빠른 핫픽스)
* **Plan C:** 테스트 시작 시 `sqlite3.connect()`로 직접 DDL 실행
* **Plan D:** DB I/O 모듈화(`db.py`) 후 runner/usage\_tracker 모두 해당 모듈만 사용

---

## 9. 보고/커밋

1. 수정 파일 목록/커밋 메시지 예:

   ```
   feat(p0): finalize Debug_21 – parametric DB path & fix test_runner_error_logging
   ```
2. 테스트 결과 캡처 첨부
3. usage.db 스키마 확인 결과 첨부:

   ```sql
   SELECT sql FROM sqlite_master WHERE name='usage';
   ```

---

### 끝.

필요 시 세부 diff/패치 파일 분리, 또는 다른 LLM/엔지니어에게 넘길 **핸드오버 노트** 형태로 요약본 추가 가능합니다.
**더 필요하면 바로 말해. 이번엔 실패 없이 끝내자.** 💥
