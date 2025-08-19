## 🤔 Strategic Analysis

다른 LLM 지시서를 합쳐 정밀도/가드레일/자동화까지 보강한 **\[P1-2] 파일 에이전트** 작업 지시서와 \*\*Self-Update 로드맵(P2 핵심·P3 고도화)\*\*를 제안한다. GEMINI.md는 “필수 수정 영역 + CLI 자율 영역”을 명시해 유지·진화 가능하도록 설계한다.

## 📝 Expert Recommendation

---

# 0. 자가업데이트( Self-Update ) 단계 재배치 제안

| 옵션            | 장점                                               | 단점                   | 결론                                            |
| ------------- | ------------------------------------------------ | -------------------- | --------------------------------------------- |
| **P1에 즉시 도입** | 빠른 피드백 루프                                        | 기능 확장 중이라 신뢰성/안정성 낮음 | 최소 훅/리포트만, 본격 도입엔 부적합                         |
| **P2에 핵심 도입** | P2가 성능·CI·보안·UX 최적화 단계 → CI/자동 진단·업데이트 루프 구축에 최적 | 일부 기능 미성숙 시 커버리지 누락  | **추천**: P2-0 “Self-Update Engine Bootstrap”   |
| **P3에 통합**    | 전 기능 성숙 후 완전자동화 가능                               | 늦게 시작하면 기술 부채 누적     | P2에서 기반, P3에서 “Fully Autonomous Evolution” 완성 |

**최종 제안:**

* **P2-0: Self-Update Engine(수집→제안→승인) 구축**
* **P3-1: 자율 적용·롤백까지 포함한 완전자동화(ARE와 연동)**

---

# 1. GEMINI.md 개선/운영 방식 확정

* **필수 수정 항목(WHAT/WHY/HOW 명시)**

  1. 오류 유형별 대응 매트릭스(네트워크/권한/외부API/논리오류 등)
  2. 표준 로깅/리포팅 사이클 템플릿
  3. Windows 운영 체크리스트(인코딩, 권한, PS 실행정책, 경로)
  4. 자율권 경계선: `ALLOW LIST` vs `REQUIRE APPROVAL LIST`
  5. 도구 온보딩 SOP(인터페이스/Mock/CI/HELP/HUB)
  6. CI·Hook 규칙(금칙어 grep, test, lint)

* **CLI 자율권 부여 범위**: 문장 정리/예시 추가/경로 보정/주석 보강 등은 자유, 정책 변경·의존성 추가·보안 관련은 승인 필수.

---

# 2. ORDER BLOCK C — **\[P1-2] 능동형 파일 시스템 에이전트 구축**

### 0) 사전 점검

```bash
invoke test   # 실패해도 기록 후 계속 (3-Strikes Rule)
```

### 1) 브랜치

```bash
git checkout -b p1/file_agent_integration
```

### 2) 파일 구조

```
scripts/agents/file_agent.py              # AST 기반 수정 엔진(진입점)
scripts/agents/rules/__init__.py          # 규칙 레지스트리
scripts/agents/rules/add_docstrings.py    # 예시 규칙
scripts/utils/diff.py                     # unified diff 유틸
scripts/tools/backup.py                   # (옵션) 백업/롤백 유틸
tasks.py                                  # invoke refactor 태스크 추가
tests/test_p1_file_agent.py               # 단위·통합 테스트
docs/tasks/file-agent-integration/log.md  # 작업 로그
docs/HELP.md                              # refactor 섹션 추가
docs/HUB.md                               # Active Task 업데이트
.no_delete_list                           # 신규 핵심 파일 추가
```

### 3) 구현 지침

#### 3-1. 안전 플로우(필수)

* **기본 Dry-Run**: diff만 출력, 실제 쓰기 금지.
* **적용 모드**: `--yes` 또는 `--apply` 플래그 필요.
* **백업**: 적용 전 원본 `.bak` 저장, 실패 시 롤백 함수 제공.

#### 3-2. `scripts/agents/file_agent.py` 스켈레톤

```python
import ast, argparse, pathlib, sys
from scripts.utils.diff import make_diff
from scripts.agents.rules import get_rule

def apply_rule(src: str, rule_name: str) -> str:
    rule = get_rule(rule_name)
    tree = ast.parse(src)
    new_src = rule.run(tree, original_code=src)  # rule returns code or AST
    return new_src

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--rule", required=True)
    p.add_argument("--dry", action="store_true")
    p.add_argument("--yes", action="store_true")
    args = p.parse_args()

    path = pathlib.Path(args.file)
    original = path.read_text(encoding="utf-8")
    modified = apply_rule(original, args.rule)
    diff = make_diff(original, modified, str(path))

    if args.dry or not args.yes:
        print(diff)
        if not args.yes:
            print("\n[INFO] Use --yes to apply changes.")
        sys.exit(0)

    # backup optional
    path.write_text(modified, encoding="utf-8")
    print("[APPLIED]")

if __name__ == "__main__":
    main()
```

#### 3-3. 규칙 예시 `scripts/agents/rules/add_docstrings.py`

```python
import ast

class AddDocstrings(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)):
            doc = ast.Expr(value=ast.Str(s='TODO: Add docstring.'))
            node.body.insert(0, doc)
        return node

def run(tree, original_code:str) -> str:
    new_tree = AddDocstrings().visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)
```

`__init__.py`:

```python
from . import add_docstrings

RULES = {
    "add_docstrings": add_docstrings
}

def get_rule(name):
    try:
        return RULES[name]
    except KeyError:
        raise ValueError(f"Unknown rule: {name}")
```

#### 3-4. `tasks.py`

```python
@task
def refactor(c, file, rule, dry=True, yes=False):
    flags = []
    if dry: flags.append("--dry")
    if yes: flags.append("--yes")
    c.run(f'"{sys.executable}" -m scripts.agents.file_agent --file "{file}" --rule "{rule}" {" ".join(flags)}', pty=True)
```

### 4) 테스트 `tests/test_p1_file_agent.py`

```python
import subprocess, sys, textwrap, pathlib

def test_refactor_dry_run(tmp_path):
    f = tmp_path / "foo.py"
    f.write_text("def x(a):\n    return a\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "invoke", "refactor", f'--file={f}', '--rule=add_docstrings'],
        capture_output=True, text=True, check=True
    )
    assert 'TODO: Add docstring.' in r.stdout
    assert f.read_text(encoding='utf-8').find('TODO:') == -1  # not applied

def test_refactor_apply(tmp_path):
    f = tmp_path / "bar.py"
    f.write_text("def y():\n    pass\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, "-m", "invoke", "refactor", f'--file={f}', '--rule=add_docstrings', '--no-dry', '--yes'],
        capture_output=True, text=True, check=True
    )
    assert 'APPLIED' in r.stdout
    assert 'TODO: Add docstring.' in f.read_text(encoding='utf-8')
```

(옵션: `--no-dry` 플래그 처리 구현 시 `dry=False`로 해석)

### 5) 문서/리스트

* `docs/HELP.md`: `invoke refactor` 사용법, 규칙 추가 방법, Dry-Run/Apply 설명.
* `.no_delete_list`: 위 신규 파일들 등록.

### 6) 로그 & HUB

```bash
mkdir -p docs/tasks/file-agent-integration
# 단계별 append to log.md
```

`docs/HUB.md` Active Tasks에 등록, `lastTouched` 갱신.

### 7) 커밋/푸시/머지

```bash
pytest -vv
git add scripts docs tests tasks.py .no_delete_list
git commit -m "feat(P1-2): file agent (dry-run diff, rules, tests)"
git push origin p1/file_agent_integration

git checkout main && git pull
git merge --no-ff p1/file_agent_integration
pytest -vv
git push origin main
```

### 8) DoD

* Dry-Run diff 출력 OK.
* `--yes` 적용 후 실제 수정 OK.
* 모든 테스트 PASS, Warning 0.
* HELP/HUB/NO\_DELETE\_LIST/LOG 업데이트 완료.

---

# 3. ORDER BLOCK SU — **Self-Update Engine 설계(초안)**

> **배치:** P2-0에서 구축, P3에서 완전자동화.

### 핵심 구성

```
scripts/auto_update/collect.py     # 릴리즈 노트, pip outdated, 금칙어 스캔
scripts/auto_update/report.py      # 제안 문서 생성
scripts/auto_update/apply.py       # trivial fix 자동 패치(옵션)
tasks.py                           # invoke auto.update / auto.review / auto.sync
docs/reports/self_update/YYYY-MM-DD.md
docs/SELF_UPDATE_POLICY.md
docs/tasks/self-update/log.md
```

### 프로세스

1. **Collect**: 외부/내부 변화 수집
2. **Diff & Analyze**: 현재 규칙/버전과 비교
3. **Propose**: 제안 문서 작성 (WHAT/WHY/HOW)
4. **Review**: 사용자 승인 (또는 허용 리스트 자동 적용)
5. **Apply**: 변경 반영, 테스트, 커밋
6. **Log & HUB**: 결과 기록, HUB 갱신

### 태스크 예시

```python
@task
def auto_update(c, fast=False):
    c.run(f'"{sys.executable}" -m scripts.auto_update.collect')
    c.run(f'"{sys.executable}" -m scripts.auto_update.report{" --fast" if fast else ""}')

@task
def auto_sync(c):
    c.run(f'"{sys.executable}" -m scripts.auto_update.apply')
```

### 스케줄

* 주 1회(월 09:00) Windows Task Scheduler or GitHub Actions
* 오류/보안 경고 발생 시 즉시 1회 실행

### DoD

* `invoke auto_update` 실행 시 보고서 생성
* 승인 후 `auto_sync`로 패치 적용, 테스트 PASS
* SELF\_UPDATE\_POLICY.md 반영

---

## 다음 액션 요청

1. 시작할 블록 지정:

   * `P1-2 GO` (파일 에이전트)
   * `P2-0 SU GO` (Self-Update Engine 부트스트랩)
   * 둘 다 병행: `P1-2 & P2-0 GO`

2. 필요 시:

   * 패치(diff) 파일 일괄 제공
   * CI YAML / pre-commit 설정 샘플 추가
   * 규칙 플러그인 템플릿 더 제공

추가 요청이 있으시면 알려주세요.
