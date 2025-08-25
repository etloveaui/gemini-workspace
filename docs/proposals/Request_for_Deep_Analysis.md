# 분석 요청서: Gemini-CLI의 파일 시스템 에이전트 프레임워크 전환 프로젝트

**To:** GPT-4 심층 리서치 모델
**From:** Gemini-CLI 개발팀
**Date:** 2025-08-07
**Version:** 1.0

## [서론] 분석의 목표

당신은 Python 아키텍처 설계 및 리팩토링 전문가입니다. 우리는 현재 단일 스크립트로 구현된 파일 에이전트 프로토타입을, **확장 가능한 플러그인 기반 프레임워크로 업그레이드**하는 중대한 기로에 서 있습니다.

이 문서에 제공된 모든 정보를 바탕으로, 우리의 계획을 검증하고, 더 나은 대안을 제시하며, 잠재적 위험을 분석하여 이 프로젝트가 성공적으로 완수될 수 있도록 도와주십시오. 당신의 분석은 우리 시스템의 비약적인 발전을 이끌어낼 핵심적인 역할을 할 것입니다.

---


## [1부] 프로젝트의 헌법: GEMINI.md

*모든 분석과 제안은 아래에 명시된 우리 프로젝트의 핵심 운영 원칙, 보안 정책, 품질 기준을 반드시 준수해야 합니다. 이 문서는 우리 프로젝트의 모든 의사결정의 기반이 되는 '가치관'입니다.*

# GEMINI.md (v2 Final+)

## 0) 목적/범위
본 문서는 이 워크스페이스의 **운영 표준**이다. 목표는 **재현성**, **보안**, **신속한 인수인계**다. 모든 규정은 Windows 환경과 Python/Invoke 중심으로 정의한다.

## 1) 운영 원칙 (Windows-first)
- **Python 경로**: venv가 있으면 `%REPO%/venv/Scripts/python.exe`, 없으면 `sys.executable`.
- **셸/인코딩**: PowerShell 래핑 금지, 파이썬 프로세스 **직접 호출**. 표준 I/O는 **UTF-8** 고정.
- **작업 경계**: 파일 작업은 원칙적으로 **레포 경로 내부**에서 수행한다.

## 2) 디렉터리·추적 정책
- **`.gemini/`**: 설정·로컬 비밀 보관 위치.  
  - **커밋 금지**: `*.creds*.json`, `*oauth*.*`, 토큰류는 **로컬 전용(local-only)** 으로 보관하고 커밋하지 않는다.  
  - **추적 허용**: `.gemini/`에서 **`context_policy.yaml`만** 버전 추적을 허용한다.
- **`projects/`**: 로컬 전용 작업 공간. **항상 커밋 금지**(`.gitignore`에서 전면 차단).
- **pre-commit 가드**: `.githooks/pre-commit` + `scripts/hooks/precommit_secrets_guard.py`로  
  `.gemini/*(oauth|creds|token|secret|.json|.db|.sqlite|.pem|.p12|.key)` 및 `projects/` **스테이징 차단**.

## 3) 명령 표준 (Invoke & GitHub Actions)
- **Invoke (로컬)**:
  - `invoke start`: 환경 점검(doctor) → HUB 브리핑 → 컨텍스트 인덱스 빌드
  - `invoke doctor`: 파이썬/권한/네트워크/경로/인코딩 점검
  - `invoke help [section]`: 도움말 출력
  - `invoke search -q "<질의>"`: 웹 검색 요약
  - `invoke context.build` / `invoke context.query "<q>"`
  - `invoke test`: pytest 실행
  - `invoke wip -m "<msg>"`: WIP 커밋
  - `invoke end`: 세션 종료(아카이브/로그/HUB 갱신)
- **GitHub Actions (원격)**:
  - `@gemini-cli <요청>`: PR 또는 이슈의 댓글을 통해 원격 AI 어시스턴트에게 작업을 지시합니다. (예: `@gemini-cli 이 코드 리뷰해줘`)

**(로컬 1회 설정)** pre-commit 훅 활성화: `git config core.hooksPath .githooks`

**Exit Codes (표준)**
- **0** 정상 / **2** Provider 미설정·불가 / **4** 예외(기타 오류)

## 4) 세션 라이프사이클
**Start**
1) `doctor` 실행 → 핵심 의존성/권한/인코딩 점검  
2) `docs/CORE/HUB_ENHANCED.md`의 Active/Paused 요약, `git status --porcelain` 요약  
3) `context.build` 실행(인덱스 최신화)  
4) 이전 세션의 `__lastSession__` 블록이 있으면 정리 후 시작

**During (작업 회복성 프로토콜)**
- **작업 분할:** 복잡한 작업은 명확한 하위 목표로 분할하여 순차적으로 실행한다.
- **사전/사후 로그:** 모든 도구 실행(특히 파일 수정, 명령어 실행) 전후로 의도와 결과를 즉시 로그로 기록한다.
- **실패 시 즉시 전환:** 동일한 접근으로 2회 연속 실패 시, 즉시 다른 해결책을 모색한다 (기존 3-Strikes Rule 강화).
- **가정 명시:** 불확실한 상황에서는 명시적으로 가정을 설정하고, 검증 계획을 함께 제시한다.

**End**
- `.gitignore` 상태 확인, 미커밋 변경은 `wip` 권고  
- HUB 상태 갱신(Active↔Paused), `__lastSession__` 블록에 핵심 요약 기록

## 5) 로깅·인수인계
- **중앙 허브**: `docs/CORE/HUB_ENHANCED.md` — 상태(Active/Paused/Completed)와 각 작업 로그 링크 관리  
- **작업 로그**: `docs/tasks/<task_id>/log.md` — 시간순 **Append-only**(정정은 하단에 추가)  
- **권장 주기**: Detailed | Standard(기본) | Minimal 중 선택

## 6) 정책 파일 (context_policy.yaml)
- **위치/추적**: `.gemini/context_policy.yaml`만 **버전 추적 허용**.  
- **화이트리스트 스키마**: `sources`, `tokens`, `context_limits` 만 유효 키로 간주한다.  
- **[Unwired Config] 규정**: 코드에서 **실사용 참조 없는 키는 Deprecated**로 분류하고 **차기 마이너 릴리스에서 제거**한다. Unknown key는 로드 시 **경고**만 남기고 **무시**한다.

## 7) 보안 / Secrets
- **레포 내 자격증명 커밋 금지**: `.gemini/*` 내 비밀 파일은 **로컬 전용**이며 커밋 금지.  
- **보관 위치**: 기본 `%APPDATA%\gemini-workspace\secrets\` 또는 **환경변수/시크릿 매니저**.  
- **노출 대응 절차**  
  1) **키 회전**(재발급·기존 폐기)  
  2) **Git 이력 정리**(예: `git filter-repo`로 해당 경로 제거)  
  3) 영향권 스캔/폐기 및 HUB에 사고·조치 로그 기록

## 8) 품질 게이트
- **필수**: `pytest -q` 통과.  
- **도입**: 정적 분석(`ruff`/`mypy`)과 Secret Scan을 CI에 추가한다.  
- **병합 조건**: **모든 PR은 Windows CI 통과가 필수**다.

## 9) P1-1: Web Search Tool (DoD)
- **즉시 구현(더미 Provider)**  
  - 함수 시그니처: `search(query: str, top_k: int = 5) -> List[Dict[str,str]]`  
  - **결정적·비네트워크·`top_k` 준수**. 각 item은 `title/url/snippet` 포함, `title/snippet`에 `query` 반영, 최소 1개 결과 보장.
- **실 Provider(병행)**  
  - Serper.dev(권장) 또는 Google CSE/SerpAPI로 구현하되 **동일 시그니처·Exit Codes**를 적용한다.  
- **완료 기준(DoD)**  
  - `invoke search -q "test"` 실행 시 약 5개 결과 요약 출력 **및** 관련 테스트 통과 → HUB의 **[P1-1]**을 **Completed**로 이동한다.

## 10) 트러블슈팅 (Quick)
- **`git push` 권한 오류**: 워크플로우(.github/workflows) 수정 등 높은 권한이 필요한 Push 실패 시, `C:\Users\eunta\gemini-workspace\secrets\my_sensitive_data.md` 파일에 기록된 GitHub PAT를 자동으로 적용한다.
- **따옴표/인코딩**: PowerShell 래핑 대신 파이썬 직접 호출(UTF-8 보장)
- **경로/권한**: 관리자 권한·경로 길이·파일 잠금 확인
- **삭제 실패(Windows)**: `os.remove`/`shutil.rmtree` 우선
- **검색 실패**: Provider 미설정 시 **Exit 2**. 기본은 **ChatGPT 심층리서치 트리거**로 안내

## 11) 변경관리 및 워크플로우
- **통합 워크플로우**: 로컬(Gemini CLI)과 원격(GitHub Action)의 역할을 명확히 분리하여 시너지를 창출합니다.
  1. **로컬 개발 (Gemini CLI)**: 사용자와의 대화를 통해 로컬 환경에서 신속하게 코드를 작성, 수정, 테스트합니다.
  2. **원격 Push 및 PR 생성 (Gemini CLI)**: 로컬 개발이 완료되면, 변경사항을 원격 저장소에 Push하고 Pull Request를 생성합니다.
  3. **자동 리뷰 및 분석 (GitHub Action)**: PR이 생성되면 `run-gemini-cli` Action이 자동으로 코드 리뷰, 분석 등 설정된 작업을 수행합니다.
  4. **피드백 반영 및 병합**: Action의 피드백을 바탕으로 로컬에서 추가 수정을 진행하고, 최종적으로 PR을 병합합니다.
- **게이트 승인**: 모든 변경은 위 워크플로우에 따른 코드 리뷰 및 자동화된 검증(CI)을 거친 후 적용됩니다.
- **메타러닝 규칙**: 동일 목표 2회 실패+1회 성공 패턴은 규칙으로 제안, 3회 연속 성공 시 표준화합니다.

## 12) 작업 회복성 프로토콜
- **작업 분할:** 복잡한 작업은 명확한 하위 목표로 분할하여 순차적으로 실행한다.
- **사전/사후 로그:** 모든 도구 실행(특히 파일 수정, 명령어 실행) 전후로 의도와 결과를 즉시 로그로 기록한다.
- **실패 시 즉시 전환:** 동일한 접근으로 2회 연속 실패 시, 즉시 다른 해결책을 모색한다 (기존 3-Strikes Rule 강화).
- **가정 명시:** 불확실한 상황에서는 명시적으로 가정을 설정하고, 검증 계획을 함께 제시한다.

---


## [2부] 현재 시스템 상태 (As-Is)

*현재 시스템이 어떻게 동작하는지 이해하기 위한 핵심 코드입니다.*

### 2.1. `tasks.py` (사용자 인터페이스)
*사용자는 `invoke refactor` 명령을 통해 파일 에이전트를 호출합니다.*

from invoke import task, Collection, Program
import tempfile
from pathlib import Path
from scripts.runner import run_command as _runner_run_command
from scripts.usage_tracker import log_usage
import sys
from scripts import hub_manager
import subprocess, os
ROOT = Path(__file__).resolve().parent
if os.name == 'nt':
    _venv_candidate = ROOT / 'venv' / 'Scripts' / 'python.exe'
else:
    _venv_candidate = ROOT / 'venv' / 'bin' / 'python'
if _venv_candidate.exists():
    VENV_PYTHON = str(_venv_candidate)
else:
    VENV_PYTHON = sys.executable
__all__ = ['run_command']

def run_command(task_name, args, cwd=ROOT, check=True):
    '''"""TODO: Add docstring."""'''
    return _runner_run_command(task_name, args, cwd, check)

# ... (중략) ...

@task
def refactor(c, file, rule, dry_run=False):
    """Refactors a file based on a given rule."""
    command = [VENV_PYTHON, 'scripts/file_agent.py', '--file', file, '--rule', rule]
    if dry_run:
        command.append('--dry-run')
    run_command('refactor', command, check=False)

# ... (중략) ...

ns = Collection()
# ...
ns.add_task(refactor)
# ...
program = Program(namespace=ns)


### 2.2. `scripts/runner.py` (핵심 의존성)
*`file_agent.py`는 명령어 실행 및 사용자 확인을 위해 이 모듈에 의존합니다.*

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

console = Console()

def confirm_action(message: str, choices: list[str], default: str = None) -> str:
    """
    Presents an interactive prompt to the user for confirmation.
    """
    # ... (구현 생략) ...

def run_command(task_name: str, args: list[str], cwd=None, check=True, db_path: Path = DEFAULT_DB_PATH):
    """
    명령어를 실행하고, 실패 시 오류를 DB에 로깅합니다.
    - shell=False 원칙 유지
    - cwd는 Path 객체 또는 str로 받을 수 있음
    """
    # ... (구현 생략) ...


### 2.3. `scripts/file_agent.py` (분석 대상 프로토타입)
*이 파일이 바로 우리가 개선하려는 대상입니다. **특히 `main` 함수의 `if/else` 구조가 핵심 문제입니다.***

import argparse
import sys
from pathlib import Path
import ast
import difflib

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def add_docstrings(source_code):
    tree = ast.parse(source_code)
    new_tree = tree
    for node in ast.walk(new_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)):
                docstring = ast.Expr(value=ast.Str(s='"""TODO: Add docstring."""'))
                node.body.insert(0, docstring)
    return ast.unparse(new_tree)

def main():
    parser = argparse.ArgumentParser(description="Refactor files based on rules.")
    parser.add_argument("--file", required=True, help="The file to refactor.")
    parser.add_argument("--rule", required=True, help="The refactoring rule to apply.")
    parser.add_argument("--dry-run", action="store_true", help="If set, shows the changes without applying them.")
    args = parser.parse_args()

    file_path = ROOT / args.file
    if not file_path.is_file():
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    source_code = file_path.read_text(encoding='utf-8')

    # [!!! 핵심 문제점 !!!] 새로운 규칙을 추가하려면 이 if/else 블록을 계속 수정해야 합니다.
    # 이는 확장성을 저해하는 안티패턴입니다.
    if args.rule == "add_docstrings":
        new_code = add_docstrings(source_code)
    else:
        print(f"Error: Unknown rule '{args.rule}'")
        sys.exit(1)

    if args.dry_run:
        diff = difflib.unified_diff(
            source_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile=f"a/{args.file}",
            tofile=f"b/{args.file}",
        )
        sys.stdout.writelines(diff)
    else:
        from scripts.runner import confirm_action
        diff = difflib.unified_diff(
            source_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile=f"a/{args.file}",
            tofile=f"b/{args.file}",
        )
        diff_output = "".join(diff)

        if diff_output:
            print("The following changes will be applied:")
            sys.stdout.writelines(diff_output)
            
            confirmation = confirm_action("Apply these changes?", ["yes", "no"], default="no")
            if confirmation == "yes":
                file_path.write_text(new_code, encoding='utf-8')
                print(f"Successfully refactored {args.file}")
            else:
                print("Refactoring cancelled.")
        else:
            print("No changes to apply.")

if __name__ == "__main__":
    main()


---


## [3부] 우리의 개선 계획 및 구체적인 질문 (To-Be)

*우리가 생각하는 해결책과, 당신에게 얻고 싶은 자문에 대한 내용입니다.*

### 3.1. 목표: 플러그인 기반 프레임워크로의 전환

**프로젝트 비전:** 현재의 단일 파일 스크립트를, 새로운 코드 수정 규칙을 플러그인처럼 쉽게 추가하고 안전하게 테스트할 수 있는, 확장 가능한 "지능형 코드베이스 관리 프레임워크"로 진화시키는 것입니다.

**목표 아키텍처:**

scripts/
├── agents/
│   ├── __init__.py
│   ├── file_agent.py         # 메인 엔진 (수정됨)
│   └── rules/
│       ├── __init__.py         # 규칙 레지스트리
│       ├── add_docstrings.py   # 규칙 1 (모듈화됨)
│       └── rename_variable.py  # 규칙 2 (새로 추가될 예시)
└── utils/
    └── diff.py


**동작 흐름:**
1. `invoke refactor --rule <rule_name>` 실행
2. `file_agent.py`는 `scripts/agents/rules/__init__.py`의 `get_rule` 함수를 호출합니다.
3. `get_rule` 함수는 `RULES` 딕셔너리에서 `<rule_name>`에 해당하는 규칙 모듈을 찾아 반환합니다.
4. `file_agent.py`는 반환된 모듈의 `run` 함수를 실행하여 리팩토링을 수행합니다.

### 3.2. 구체적인 실행 계획 (Action Plan)

1.  **디렉터리 구조 생성:** `scripts/agents/` 및 `scripts/agents/rules/` 디렉터리를 생성합니다.
2.  **규칙 레지스트리 구현:** `scripts/agents/rules/__init__.py`에 `RULES` 딕셔너리와 `get_rule` 함수를 구현합니다.
3.  **기존 규칙 모듈화:** `file_agent.py`에 있던 `add_docstrings` 로직을 `scripts/agents/rules/add_docstrings.py` 파일로 분리하고, `run(tree)` 인터페이스를 준수하도록 수정합니다.
4.  **메인 엔진 리팩토링:** `file_agent.py`의 `main` 함수에서 `if/else` 분기문을 제거하고, `get_rule(args.rule).run(tree)`를 호출하여 동적으로 규칙을 적용하도록 수정합니다.
5.  **안전장치 강화:** 사용자의 명시적 동의 없이는 파일이 수정되지 않도록, `--apply` 또는 `--yes` 플래그가 있을 때만 실제 파일 쓰기를 수행하는 로직을 추가합니다.
6.  **테스트 하네스 구축:** `tests/test_p1_file_agent.py`를 생성하고, Dry-run, Apply, 규칙 로딩, 예외 처리 등 상세 계획에 명시된 모든 케이스를 검증하는 `pytest` 코드를 작성합니다.
7.  **문서화:** `docs/HELP.md`에 새로운 프레임워크의 사용법과 **"새로운 리팩토링 규칙을 추가하는 방법"**에 대한 상세한 가이드를 추가합니다.

### 3.3. 핵심 질문 (당신의 전문 지식이 필요합니다)

1.  **(아키텍처)** 제시된 플러그인 아키텍처(규칙 레지스트리 패턴)보다 더 효율적이거나 Pythonic한 설계 패턴이 있다면 제안해 주십시오. (예: `setuptools`의 `entry_points` 활용, 클래스 기반 규칙 상속 구조 등)
2.  **_AST 조작)_** Python의 `ast` 모듈을 직접 다룰 때 발생할 수 있는 잠재적 위험(예: 주석, 빈 줄, 기존 포맷팅 유실)을 최소화하기 위한 Best Practice나 추천 라이브러리(`libcst` 등)가 있다면 알려주십시오.
3.  **_미래 확장성)_** 향후 "이 함수를 비동기로 바꿔줘"와 같은 자연어 명령을 AST 변환 규칙으로 자동 생성하는 기능을 구현하려면, 현재 설계에서 어떤 점을 미리 고려해야 합니까? (예: 규칙 생성 프롬프트 템플릿, AST 노드 타입과 자연어 매핑 등)

---


## [4부] 요청 결과물 (Deliverable)

위 모든 정보를 바탕으로, 다음 4개 섹션으로 구성된 상세한 분석 보고서를 작성해 주십시오.

1.  **아키텍처 검토:** 우리가 제안한 플러그인 아키텍처에 대한 평가와, 더 나은 대안이 있다면 그에 대한 구체적인 설명 및 코드 예시.
2.  **핵심 질문에 대한 답변:** 3.3절의 3가지 질문에 대한 상세하고 실행 가능한 답변.
3.  **코드 레벨의 개선 제안:** 현재 `file_agent.py`와 우리가 계획 중인 `rules` 모듈에 대해, 더 견고하고 효율적인 코드로 개선할 수 있는 구체적인 제안.
4.  **잠재적 위험 분석:** 이 프로젝트를 진행하면서 발생할 수 있는 기술적, 논리적 위험 요소들과 그에 대한 대비책 제안.
