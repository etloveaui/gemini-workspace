## 지시서: Gemini CLI UX 향상 작업 (invoke doctor / quickstart / help)

**코드명:** `[P1]UX_01_Doctor_Quickstart_Help`
**작성일:** 2025-07-28
**목표 브랜치:** `p1/ux_doctor_quickstart` → `main` 머지

---

### 1. 목적 & 배경

* P0에서 안정성 확보 완료. 이제 사용자가 **쉽게 진입하고 문제를 스스로 진단**할 수 있는 창구 필요.
* 핵심 진입점:

  1. `invoke doctor` : 환경/설정 점검 및 해결 가이드 출력
  2. `invoke quickstart` : 신규 사용자 온보딩용 빠른 시작 안내
  3. `invoke help [section]` : 문서/명령어/흐름별 도움말 조회

---

### 2. 산출물(Deliverables)

1. **scripts/doctor.py** – 환경 점검 스크립트
2. **scripts/quickstart.py** – 온보딩 안내 스크립트
3. **scripts/help.py** – 도움말 라우터/렌더러
4. **docs/HELP.md** – 전체 도움말 문서(섹션별 앵커 포함)
5. **tests/test\_ux\_enhancements.py** – 새 기능 테스트
6. **tasks.py 수정** – `doctor`, `quickstart`, `help` 태스크 추가
7. `.no_delete_list` 업데이트 – 새 파일 보호
8. (선택) `docs/QUICKSTART.md` 별도 분리 시 추가

---

### 3. 작업 순서 (체크리스트)

#### 3.1 브랜치 준비

* [ ] `git checkout -b p1/ux_doctor_quickstart`
* [ ] `pytest -vv`로 현 상태 PASS 확인

#### 3.2 파일 생성/수정

* [ ] **scripts/doctor.py**

  * 점검 항목:

    * Python 버전 (>=3.10 권장)
    * Invoke 설치&버전
    * Git 설치&버전
    * venv 활성화 여부
    * `usage.db` 존재/쓰기 가능
    * `.no_delete_list` 존재
    * `GEMINI.md` 존재
    * (선택) rank\_bm25 등 필수 라이브러리 존재 여부
  * 출력 포맷: `[PASS] 항목명` / `[FAIL] 항목명 - 해결 팁`
  * 마지막에 요약: `총 N개 중 M개 FAIL` / 다음 액션 제시
  * 예외 처리: 각 체크 try/except로 감싸고 실패 시 FAIL 등록

* [ ] **scripts/quickstart.py**

  * 출력: 번호/불릿 기반 단계 안내 (백틱으로 명령어 표시)

    1. venv 생성&활성화
    2. `pip install -r requirements.txt`
    3. `invoke start` (세션 인덱싱/브리핑)
    4. `invoke test` (검증)
    5. `invoke help` 로 더 보기
  * 단순 print로 충분 (컬러 출력 필요 시 colorama 등은 선택)

* [ ] **scripts/help.py**

  * 인자: `section` (기본 all)
  * 동작:

    * `docs/HELP.md` 읽고, `## 섹션명` 기준으로 파싱 후 해당 부분 출력
    * section이 all이면 전체 출력
  * fallback: 섹션 없으면 유효 섹션 목록 출력

* [ ] **docs/HELP.md**

  * 섹션 예시:

    * Getting Started
    * Commands Overview (invoke XXX)
    * Troubleshooting (doctor 결과 대응표)
    * FAQ
    * Conventions & Policies (GEMINI.md 요약 링크)
  * 문서 내부 앵커(`#getting-started`, `#doctor`)로 help.py에서 부분 추출 가능하도록 구조화

* [ ] **tasks.py**

  * 추가 태스크:

    ```python
    @task
    def doctor(c):
        c.run(f"{sys.executable} scripts/doctor.py", pty=False)

    @task
    def quickstart(c):
        c.run(f"{sys.executable} scripts/quickstart.py", pty=False)

    @task
    def help(c, section="all"):
        c.run(f"{sys.executable} scripts/help.py {section}", pty=False)
    ```
  * `import sys` 필요

* [ ] **tests/test\_ux\_enhancements.py**

  * 케이스 1: `invoke doctor` 정상 실행 & `[PASS]` 또는 `[FAIL]` 문자열 포함 확인
  * 케이스 2: `invoke quickstart` 실행 & "환영합니다" 또는 "가상 환경" 문자열 확인
  * 케이스 3(선택): `invoke help getting-started` 실행 & 해당 섹션 일부 문자열 포함 확인
  * subprocess.run 또는 runner.run\_command 활용 (shell=False)

* [ ] **.no\_delete\_list**

  * `scripts/doctor.py`, `scripts/quickstart.py`, `scripts/help.py`, `docs/HELP.md`, `tests/test_ux_enhancements.py` 추가

#### 3.3 테스트 & 머지

* [ ] `pytest -vv` 전부 PASS
* [ ] `git add -A && git commit -m "feat(p1): add doctor/quickstart/help UX entrypoints"`
* [ ] `git push -u origin p1/ux_doctor_quickstart`
* [ ] PR 생성 → 리뷰/머지 → `main`으로 병합
* [ ] (선택) 태그: `v1.0.0-p1-ux`

---

### 4. 구현 예시 스니펫

**scripts/doctor.py (요약 예시)**

```python
#!/usr/bin/env python
import shutil, sys, os
from pathlib import Path
from importlib import util

REPORT = []

def check(name, ok, hint=""):
    status = "[PASS]" if ok else "[FAIL]"
    REPORT.append((status, name, hint))

def main():
    # Python
    py_ok = sys.version_info >= (3, 10)
    check("Python >= 3.10", py_ok, "Python 3.10 이상을 설치하세요.")

    # Invoke
    invoke_ok = shutil.which("invoke") is not None
    check("Invoke installed", invoke_ok, "pip install invoke")

    # Git
    git_ok = shutil.which("git") is not None
    check("Git installed", git_ok, "https://git-scm.com/")

    # venv
    venv_ok = sys.prefix != sys.base_prefix
    check("Virtualenv active", venv_ok, "venv를 활성화하세요. source venv/bin/activate")

    # files
    root = Path(__file__).parent.parent
    usage_ok = (root / "usage.db").exists()
    check("usage.db exists", usage_ok, "invoke start 또는 log 발생 후 자동 생성됩니다.")
    no_delete_ok = (root / ".no_delete_list").exists()
    check(".no_delete_list exists", no_delete_ok, "루트에 .no_delete_list 생성하세요.")
    gemini_ok = (root / "GEMINI.md").exists()
    check("GEMINI.md exists", gemini_ok, "GEMINI.md가 삭제되었는지 확인하세요.")

    # Summary
    fails = [r for r in REPORT if r[0] == "[FAIL]"]
    for status, name, hint in REPORT:
        line = f"{status} {name}"
        if status == "[FAIL]":
            line += f" -> {hint}"
        print(line)

    print("\n---")
    if fails:
        print(f"{len(fails)}개의 문제가 발견되었습니다. 위의 해결 팁을 참고하세요.")
        sys.exit(1)
    else:
        print("모든 시스템 점검 완료. 문제 없음.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

(quickstart/help/test 코드도 동일 수준으로 작성)

---

### 5. 완료 기준 (DoD)

* 전체 테스트(`pytest -vv`) 통과
* `invoke doctor`, `invoke quickstart`, `invoke help` 정상 동작
* 새 파일 모두 `.no_delete_list`에 추가
* PR 머지 완료, HUB/README/HELP 업데이트 반영
* DeprecationWarning 등 남은 경고 0 또는 별도 티켓으로 분리

---

### 6. 리스크 & 대응

* **Windows 출력 인코딩**: `print` 시 CP949 문제 발생 시 `encoding='utf-8'` 설정 또는 PowerShell 권장
* **테스트 환경 차이**: doctor 테스트는 실제 환경 의존 → 핵심 문자열만 검증, 세부 항목별은 모킹 고려
* **Docs 파싱 복잡도**: help.py에서 Markdown 파싱 간단화(정규식) 또는 섹션 구분자 고정 사용

---

### 7. 후속(옵션)

* `invoke doctor --json` 옵션으로 JSON 리포트 출력 → CI에서 파싱 가능
* `invoke quickstart --non-interactive` 등 모드 지원
* `invoke help list` 로 섹션 목록 출력

---

## 즉시 실행 요청

1. 본 지시서에 따라 브랜치 생성 후 작업 착수
2. 구현 완료 후 전체 테스트 및 머지 진행
3. 완료 보고 (테스트 결과/커밋 ID/머지 링크 포함)

끝. 필요 시 전체 패치 파일(diffs)도 제공 가능.
