\[Role: Tech Expert]

## 🤔 Strategic Analysis

지금 병목은 두 가지: \*\*하드코딩 분기(OCP 위반)\*\*와 **포맷/주석 유실 리스크**. 규칙을 **클래스+자동등록**으로 표준화하고, **경계·멱등·되돌리기** 3종 안전장치를 내장. 테스트/CI/문서까지 한 번에 묶어 **48h 내 가동**.

---

## 📝 Expert Recommendation — **제미나이 CLI 작업 지시서 (P1-2 실행)**

> **목표:** `scripts/file_agent.py` 모놀리식을 **플러그인화된 규칙 프레임워크**로 전환. Windows-first, 리포 경계 강제, 표준 Exit Codes, CI 게이트 준수. **DoD: `pytest -q` green + Windows CI 통과 + 문서 반영.**

---

### 0) 산출물(DoD) & 승인 조건

* ✅ `invoke refactor --list/--explain/--dry-run/--yes` 동작.
* ✅ `rules/` 자동 스캔 & 규칙 클래스 자동등록: **메타데이터(name, summary, params, idempotent, conflicts)** 노출.
* ✅ **작업 경계 강제**(repo 내부만 수정), **멱등성 테스트**, **Undo(백업 또는 git-stash)**.
* ✅ `tests/test_p1_file_agent.py`에 **Dry-run/Apply/경계/미지규칙/문법오류/멱등성** 포함, 전부 통과.
* ✅ Exit codes `0/2/4` 준수, Windows CI green.

---

### 1) 디렉터리 생성 (프레임)

```bash
mkdir -p scripts/agents/rules scripts/utils tests docs
```

구조는 제안서와 동일 유지. `utils/diff.py` 신설.

---

### 2) **RuleBase** 설계 + 자동등록(핵심)

**`scripts/agents/rules/base.py`**

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Any

class RuleBase(ABC):
    registry: ClassVar[Dict[str, type["RuleBase"]]] = {}

    # 필수 메타데이터
    name: ClassVar[str] = ""        # CLI 표시명 (고유)
    summary: ClassVar[str] = ""     # 한 줄 설명
    params: ClassVar[Dict[str, str]] = {}  # CLI 파라미터 스키마(help 문구)
    idempotent: ClassVar[bool] = True
    conflicts: ClassVar[set[str]] = set()

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        n = getattr(cls, "name", cls.__name__)
        if not n: raise ValueError("Rule must define a non-empty 'name'")
        RuleBase.registry[n] = cls  # 자동 등록

    @abstractmethod
    def apply(self, source: str, **kwargs: Any) -> str: ...
```

**이유:** RULES 수동 등록/누락 리스크 제거, 규칙 공통 계약 강제, 향후 공통 훅(전/후검사) 제공 용이.

---

### 3) 규칙 자동 발견(내장 플러그인)

**`scripts/agents/rules/__init__.py`**

```python
import importlib, pkgutil
from .base import RuleBase

def load_rules(pkg="scripts.agents.rules"):
    mod = importlib.import_module(pkg)
    for _, name, _ in pkgutil.iter_modules(mod.__path__, prefix=mod.__name__ + "."):
        importlib.import_module(name)  # import 시 __init_subclass__로 자동 등록

def get_rule_names() -> list[str]:
    return sorted(RuleBase.registry.keys())

def get_rule(name: str) -> type[RuleBase]:
    try:
        return RuleBase.registry[name]
    except KeyError as e:
        raise SystemExit(4) from e  # 표준 ExitCodes 준수
```

**비고:** 패키징/외부 생태계 단계에서 `entry_points`로 승격 가능(로드 코드 교체만).

---

### 4) 규칙 예시 2종

**`scripts/agents/rules/add_docstrings.py`** (현재 로직 이식; 멱등성 유지)

```python
import ast
from .base import RuleBase

class AddDocstrings(RuleBase):
    name = "add_docstrings"
    summary = "함수/클래스에 누락된 docstring을 추가"
    params = {}

    def apply(self, source: str, **_: str) -> str:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], "value", None), ast.Str)):
                    node.body.insert(0, ast.Expr(value=ast.Str(s='"""TODO: Add docstring."""')))
        return ast.unparse(tree)
```

> 주: 포맷/주석 유실 우려 있으므로 **대규모/민감 규칙은 LibCST 권장**(중기 로드맵).

**`scripts/agents/rules/rename_variable.py`** (샘플 파라미터화)

```python
import ast
from .base import RuleBase

class RenameVariable(RuleBase):
    name = "rename_variable"
    summary = "변수 이름을 일치 규칙에 맞춰 변경"
    params = {"old": "기존 변수명", "new": "새 변수명"}

    def apply(self, source: str, **kw) -> str:
        old, new = kw["old"], kw["new"]
        class Renamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == old: node.id = new
                return node
        tree = Renamer().visit(ast.parse(source))
        return ast.unparse(tree)
```

---

### 5) 공통 Diff/출력 유틸

**`scripts/utils/diff.py`**

```python
import difflib
def unified(a: str, b: str, path: str) -> str:
    return "".join(difflib.unified_diff(
        a.splitlines(keepends=True),
        b.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    ))
```

**효과:** file\_agent의 중복 diff 생성 제거, 메시지 일원화.

---

### 6) **file\_agent.py** 메인 엔진 리팩토링

**핵심 변경:** if/else 제거 → **동적 로딩 + 클래스 규칙 실행**, **경계강제**, **--list/--explain/--yes** 지원.

```python
import argparse, sys
from pathlib import Path
from scripts.agents.rules import load_rules, get_rule, get_rule_names
from scripts.utils.diff import unified

ROOT = Path(__file__).resolve().parent.parent

def _assert_within_repo(final: Path):
    repo = ROOT.resolve()
    final = final.resolve()
    if repo not in final.parents and final != repo:
        print(f"Error: path '{final}' is outside workspace '{repo}'")
        sys.exit(4)  # 예외/보안 위반
# Windows-first/UTF-8/shell=False 방침은 기존 infra 준수. 

def main():
    p = argparse.ArgumentParser(description="Refactor files based on rules.")
    p.add_argument("--file", required=True)
    p.add_argument("--rule", help="rule name")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", "--apply", dest="apply", action="store_true")
    p.add_argument("--list", action="store_true")
    p.add_argument("--explain", metavar="RULE")
    args, unknown = p.parse_known_args()

    load_rules()  # rules/* import → 자동등록

    if args.list:
        for n in get_rule_names(): print(n)
        sys.exit(0)

    if args.explain:
        cls = get_rule(args.explain)
        print(f"{cls.name}: {cls.summary}\nparams: {cls.params}\nidempotent={cls.idempotent}")
        sys.exit(0)

    if not args.rule:
        print("Error: --rule is required (or use --list/--explain)")
        sys.exit(4)

    target = (ROOT / args.file)
    if not target.is_file():
        print(f"Error: File not found at {target}"); sys.exit(4)
    _assert_within_repo(target)

    source = target.read_text(encoding="utf-8")
    rule_cls = get_rule(args.rule)
    # 규칙별 파라미터 전달: --old foo --new bar → unknown 파싱은 규칙 params로 매핑
    import shlex
    kv = {}
    it = iter(unknown)
    for k in it:
        if k.startswith("--"):
            key = k[2:]; kv[key] = next(it, "")
    new_code = rule_cls().apply(source, **kv)

    diff = unified(source, new_code, args.file)
    if not diff:
        print("No changes to apply."); sys.exit(0)

    print(diff)

    if args.dry_run or not args.apply:
        # 비대화형 파이프라인/CI에서 안전: diff만 출력
        sys.exit(0)

    # 실제 적용: 백업/undo 보장
    bak = target.with_suffix(target.suffix + ".bak")
    bak.write_text(source, encoding="utf-8")
    # confirm은 invoke 대화형 경로에서 runner.confirm_action 사용 가능
    target.write_text(new_code, encoding="utf-8")
    print(f"Applied successfully: {args.file}")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

* **근거:** 기존 if/else 분기 제거 필요.
* **경계강제:** 리포 경계 밖 접근 차단(보안 원칙).

---

### 7) `tasks.py` 업데이트 (CLI UX 일관화)

현행 `invoke refactor`가 `--dry-run`만 전달하므로 `--yes/--list/--explain` pass-through 추가.

```python
@task
def refactor(c, file, rule=None, dry_run=False, yes=False, list=False, explain=None):
    cmd = [VENV_PYTHON, 'scripts/file_agent.py', '--file', file]
    if list: cmd.append('--list')
    if explain: cmd += ['--explain', explain]
    if rule: cmd += ['--rule', rule]
    if dry_run: cmd.append('--dry-run')
    if yes: cmd.append('--yes')
    run_command('refactor', cmd, check=False)
```

---

### 8) 테스트 하네스 (pytest)

**`tests/test_p1_file_agent.py`** – 최소 시나리오

```python
import subprocess, textwrap, os, sys, tempfile, pathlib, shutil

REPO = pathlib.Path(__file__).resolve().parents[1]
PY = (REPO / 'venv' / ('Scripts' if os.name=='nt' else 'bin') / 'python')
PY = PY if PY.exists() else pathlib.Path(sys.executable)

def run(args, cwd=REPO):
    return subprocess.run([str(PY), 'scripts/file_agent.py', *args],
                          cwd=str(cwd), capture_output=True, text=True)

def _tmpfile(content: str, name="m.py"):
    d = tempfile.TemporaryDirectory(); p = pathlib.Path(d.name)/name
    p.write_text(textwrap.dedent(content), encoding='utf-8'); return d, p

def test_list_and_explain():
    r = run(['--file','scripts/file_agent.py','--list'])
    assert r.returncode == 0 and 'add_docstrings' in r.stdout

def test_dry_run_no_write_and_diff_present():
    d, p = _tmpfile("def f():\n    return 1\n")
    rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p  # 보조
    r = run(['--file', str(rel), '--rule','add_docstrings','--dry-run'])
    assert r.returncode == 0 and '+++ b/' in r.stdout

def test_apply_writes_and_idempotent():
    d, p = _tmpfile("def g():\n    return 2\n")
    rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p
    _ = run(['--file', str(rel), '--rule','add_docstrings','--yes'])
    a1 = p.read_text(encoding='utf-8')
    _ = run(['--file', str(rel), '--rule','add_docstrings','--yes'])
    a2 = p.read_text(encoding='utf-8')
    assert a1 == a2  # 멱등성

def test_unknown_rule_exit4():
    d, p = _tmpfile("x=1\n")
    rel = p.relative_to(REPO) if p.is_relative_to(REPO) else p
    r = run(['--file', str(rel), '--rule','no_such_rule','--dry-run'])
    assert r.returncode == 4

def test_repo_boundary_enforced():
    r = run(['--file','..\\outside.py','--rule','add_docstrings','--dry-run'])
    assert r.returncode == 4
```

* 테스트 범주: Dry-run/Apply/멱등성/미지 규칙/경계 위반/문법 오류(의도적 깨진 코드) 포함.
* CI 게이트: Windows 필수.

---

### 9) 포맷/주석 보존 로드맵 (중기)

* **지금:** stdlib `ast` + diff 검증으로 시작(작은 변화).
* **중기:** 포맷 민감 규칙은 **LibCST**로만 허용, 규칙 템플릿 제공(Visitor/Transformer). **혼합 전략** 문서화.

---

### 10) 안전장치 3종 세트

1. **경계 보안:** `Path.resolve()` + 부모 경로 검사 → 리포 외부 차단. **필수.**
2. **멱등성 계약:** Rule 기본값 `idempotent=True`; 테스트 강제.
3. **Undo:** 적용 전 `*.bak` 저장 또는 `git stash -k` 옵션. 실패시 자동 복원.

---

### 11) 로깅/UX 일관화

* `runner.py`에 `display_diff(old,new, path)` 유틸 흡수 가능(색상/±라인 수 요약). 현행 `rich` 기반 출력 일관화.
* HUB 로그에 “규칙/대상/결과 요약(추가/삭제 라인 수)” 자동 기재(작업 회복성 프로토콜 준수).

---

### 12) 문서 & 도움말

* `docs/HELP.md`: `--list/--explain` 예시, **규칙 추가 튜토리얼(메타데이터/멱등성 체크리스트/LibCST 가이드)**.
* `invoke help` 섹션에 refactor 서브커맨드 옵션 반영.

---

### 13) CI/품질/보안 연계

* **품질 게이트**: `pytest -q` + `ruff` + `mypy` + Secret Scan; Windows CI 통과 없이는 머지 금지.
* **Exit Codes 통일**: 정상 0 / Provider 미설정 2 / 기타 예외 4. file\_agent는 0/4만 사용.
* **Secrets 규정 준수**: `.gemini/*` 커밋 금지, 누출시 회전/이력정리/HUB 기록.

---

### 14) 단계별 실행 계획 (48h 롤아웃)

**D0. 브랜치 생성**

```bash
git checkout -b feat/p1-2-plugin-file-agent
```

**D1. 프레임 구축**

* RuleBase/로더/유틸/diff 추가 → `file_agent.py` 리팩토링.
* `tasks.py` 옵션 pass-through.
* 단위 테스트 초안 작성.

**D2. 안전장치/UX**

* 경계 검사/Undo/Exit codes 일치.
* `--list/--explain` UX, diff 요약.

**D3. 테스트 & CI**

* 멱등성/경계/미지규칙/문법오류/드라이런·어플라이 완비.
* GitHub Actions Windows 워크플로 조정.

**D4. 문서/HUB**

* `docs/HELP.md` 갱신, HUB 로그에 마이그레이션/사용법 링크.

**머지 전 체크리스트**

* [ ] `pytest -q` 통과
* [ ] Windows CI green
* [ ] 문서/HUB 갱신
* [ ] 비상 롤백 스크립트 확인

---

### 15) 리스크 & 대응

* **포맷/주석 손실로 인한 대규모 diff** → LibCST 전환 규칙 가이드라인 수립, 민감 규칙은 LibCST 전용.
* **규칙 충돌**(rename→reorder 등) → Rule 메타데이터 `conflicts` 활용, 적용 순서/동시 실행 차단.
* **서드파티 플러그인 보안**(entry\_points 로드 시) → 내부 단계는 **내장 스캔만**; 외부 플러그인 도입 시 서명/샌드박스 설계.
* **경계 이탈(Path Traversal)** → `resolve()` + 부모 경로 검사로 차단, 테스트 포함.
* **대화형 confirm 의존** → CI에서는 `--yes` 필수 경로 보장(비대화형). 현행 `prompt_toolkit`은 invoke 자식 프로세스에서 정상 상호작용(설계 상 확인됨).

---

### 16) 커밋 단위(예시)

1. `feat(rule-core): add RuleBase and auto loader`
2. `refactor(file_agent): remove if/else; add --list/--explain/--yes`
3. `feat(rules): add add_docstrings, rename_variable`
4. `feat(utils): add unified diff helper`
5. `test(file_agent): add dry-run/apply/idempotency/boundary`
6. `docs: update HELP.md with plugin guide`

---

### 17) 사용 예

```bash
# 사용가능 규칙 조회
invoke refactor --file scripts/file_agent.py --list
# 규칙 설명
invoke refactor --file scripts/file_agent.py --explain add_docstrings
# 드라이런
invoke refactor --file scripts/file_agent.py --rule add_docstrings --dry-run
# 실제 적용(비대화형)
invoke refactor --file scripts/file_agent.py --rule rename_variable --yes -- --old val --new result
```

> `--` 이후 인자는 규칙 파라미터로 해석(간단 파서 구현 포함).

---

## 마무리 — 왜 이 설계가 맞나

* **OCP 해결:** 규칙 추가시 메인 미수정.
* **보안/운영 원칙 부합:** Windows-first, 리포 경계, ExitCodes/CI 게이트 준수.
* **UX/신뢰성:** `--list/--explain/--dry-run/--yes`, diff 표준화, 멱등/Undo 보장.

추가 요청이 있으시면 알려주세요.
