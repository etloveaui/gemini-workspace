## 0. 준비

```powershell
cd C:\Users\etlov\gemini-workspace
.\venv\Scripts\activate    # 가상환경 사용 시
```

---

## 1. 패치 파일 반영

### 한 번에 복사

```powershell
robocopy .\scratchpad\p0_patch . /E /NFL /NDL /NJH /NJS /NC /NS
```

> 실패 시 관리자 권한 PowerShell에서 다시 실행하거나, 개별 파일만 수동 복사하세요.

### (선택) 적용 스크립트 저장용

```powershell
@'
robocopy .\scratchpad\p0_patch . /E /NFL /NDL /NJH /NJS /NC /NS
git add -A
git commit -m "P0 patch applied"
'@ | Set-Content .\apply_p0_patch.ps1
```

---

## 2. 불필요 테스트 제거/무시

pytest가 `scratchpad/fixed`를 수집하지 않도록 합니다.

* **방법 A(추천):** `pytest.ini`에 다음이 들어있나 확인

  ```ini
  [pytest]
  testpaths = tests
  ```
* **방법 B:** `scratchpad/fixed/*.py`를 삭제하거나 `_bak.py` 등으로 변경.

---

## 3. invoke/pytest 동작 확인

```powershell
invoke test            # 내부에서 pytest tests/ -v 실행되도록 수정됨
# 또는
pytest tests/ -v
```

* 실패 시 메시지 확인 →

  * `test_commit_protocol*` : invoke 인자 전달/Executor 생성 방식 확인
  * `test_last_session_cycle` : HUB.md 블록 제거 확인 (hub\_manager.py 정규식)

---

## 4. 세션 사이클 최종 점검

```powershell
invoke start
# HUB.md 에 __lastSession__ 블록 없어야 함

invoke end -t general  # 혹은 invoke end
# HUB.md 맨 끝에 __lastSession__ 블록 생성되는지 확인
```

---

## 5. 커밋 프로토콜 검증

```powershell
invoke wip -m "check commit protocol"   # scripts/git-wip.ps1 가 -F 사용 중인지 확인
git log -1 -p                            # 커밋 메시지가 임시파일 기반으로 들어갔는지 확인
```

---

## 6. 마무리 커밋

```powershell
git add -A
git commit -m "[P0] Integrity verified & patch applied"
```

---

### 문제 발생 시 빠른 체크리스트

* `ImportError: tasks`:  현재 경로가 프로젝트 루트인지, `tasks.py`가 루트에 있는지 확인.
* `Program.run() got an unexpected keyword`: invoke는 CLI 스타일 인자 전달 (`"--option" "value"`)인지 확인.
* `__lastSession__` 잔존: `hub_manager.strip_last_session_block()` 정규식 범위가 `---` 포함 블록 전체를 커버하는지 확인. HUB.md에 제어문자(`\x01` 등) 없는지 재검사.
* `usage.db` 잠금: 테스트 끝난 뒤 `gc.collect()` + `time.sleep(0.1)` 로 파일 핸들 해제. 삭제 대신 rename.

