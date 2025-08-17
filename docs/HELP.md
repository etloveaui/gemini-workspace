# Gemini CLI 도움말

> 간단한 워크플로우는 루트의 `AGENTS.md`(Slim+Automation 가이드)를 참고하세요.

## 시작하기

이 섹션에서는 Gemini CLI를 시작하는 방법에 대한 정보를 제공합니다.

## 명령어 개요

사용 가능한 명령어에 대한 개요입니다:

* `invoke doctor`: 환경 설정을 확인합니다.
* `invoke quickstart`: 빠른 시작 가이드를 확인합니다.
* `invoke help [section]`: 도움말 정보를 표시합니다.
* `invoke search "<query>"`: 웹 검색을 수행하고 결과를 요약합니다.
* `invoke refactor`: 코드 리팩토링 프레임워크를 사용합니다. (아래 상세 설명 참조)

## `invoke refactor` 상세 가이드

`refactor` 태스크는 플러그인 기반의 강력한 코드 리팩토링 프레임워크를 제공합니다. AST(추상 구문 트리)를 기반으로 코드를 안전하게 분석하고 수정할 수 있습니다.

### 사용법

- **사용 가능한 규칙 목록 보기:**
  ```bash
  invoke refactor --list-rules
  ```

- **특정 규칙에 대한 설명 보기:**
  ```bash
  invoke refactor --explain <규칙명>
  ```
  *예시: `invoke refactor --explain add_docstrings`*

- **리팩토링 Dry-Run (변경 사항 미리보기):**
  ```bash
  invoke refactor --file <파일경로> --rule <규칙명> --dry-run
  ```
  *이 명령은 실제 파일을 수정하지 않고, 변경될 내용(diff)만 터미널에 출력합니다.*

- **리팩토링 실제 적용:**
  ```bash
  invoke refactor --file <파일경로> --rule <규칙명> --yes
  ```
  *`--yes` 플래그를 사용하면 확인 절차 없이 즉시 파일에 변경 사항이 적용됩니다.*

### 새로운 리팩토링 규칙 추가하기

이 프레임워크의 가장 큰 장점은 새로운 리팩토링 규칙을 매우 쉽게 추가할 수 있다는 점입니다.

1.  **규칙 파일 생성:**
    - `scripts/agents/rules/` 디렉터리에 새로운 Python 파일을 생성합니다. (예: `my_new_rule.py`)

2.  **`RuleBase` 상속:**
    - 생성한 파일 안에서 `scripts.agents.rules.base`의 `RuleBase` 클래스를 상속받는 새로운 클래스를 정의합니다.

3.  **필수 클래스 변수 정의:**
    - `name`: CLI에서 사용될 규칙의 고유한 이름 (예: `my_new_rule`)
    - `summary`: 규칙에 대한 한 줄 설명

4.  **`apply` 메소드 구현:**
    - `apply(self, source: str, **kwargs) -> str` 메소드를 구현합니다. 이 메소드는 원본 소스 코드를 문자열로 받아, 수정한 코드를 문자열로 반환합니다.
    - `ast` 모듈을 사용하여 소스 코드를 파싱하고, 원하는 대로 수정한 후 `ast.unparse()`를 사용하여 다시 문자열로 변환합니다.

5.  **자동 등록:**
    - 위 과정을 마치면 프레임워크가 자동으로 새로운 규칙을 인식합니다. 별도의 등록 절차는 필요 없습니다. `invoke refactor --list-rules`를 실행하여 규칙이 추가되었는지 바로 확인할 수 있습니다.

**예시 (`my_new_rule.py`):**
# Gemini CLI 도움말

## 시작하기

이 섹션에서는 Gemini CLI를 시작하는 방법에 대한 정보를 제공합니다.

## 명령어 개요

사용 가능한 명령어에 대한 개요입니다:

* `invoke doctor`: 환경 설정을 확인합니다.
* `invoke quickstart`: 빠른 시작 가이드를 확인합니다.
* `invoke help [section]`: 도움말 정보를 표시합니다.
* `invoke search "<query>"`: 웹 검색을 수행하고 결과를 요약합니다.
* `invoke refactor`: 코드 리팩토링 프레임워크를 사용합니다. (아래 상세 설명 참조)
* `invoke organize-scratchpad`: `scratchpad` 디렉터리를 정리합니다. (아래 상세 설명 참조)

## `invoke refactor` 상세 가이드

`refactor` 태스크는 플러그인 기반의 강력한 코드 리팩토링 프레임워크를 제공합니다. AST(추상 구문 트리)를 기반으로 코드를 안전하게 분석하고 수정할 수 있습니다.

### 사용법

- **사용 가능한 규칙 목록 보기:**
  ```bash
  invoke refactor --list-rules
  ```

- **특정 규칙에 대한 설명 보기:**
  ```bash
  invoke refactor --explain <규칙명>
  ```
  *예시: `invoke refactor --explain add_docstrings`*

- **리팩토링 Dry-Run (변경 사항 미리보기):**
  ```bash
  invoke refactor --file <파일경로> --rule <규칙명> --dry-run
  ```
  *이 명령은 실제 파일을 수정하지 않고, 변경될 내용(diff)만 터미널에 출력합니다.*

- **리팩토링 실제 적용:**
  ```bash
  invoke refactor --file <파일경로> --rule <규칙명> --yes
  ```
  *`--yes` 플래그를 사용하면 확인 절차 없이 즉시 파일에 변경 사항이 적용됩니다.*

### 새로운 리팩토링 규칙 추가하기

이 프레임워크의 가장 큰 장점은 새로운 리팩토링 규칙을 매우 쉽게 추가할 수 있다는 점입니다.

1.  **규칙 파일 생성:**
    - `scripts/agents/rules/` 디렉터리에 새로운 Python 파일을 생성합니다. (예: `my_new_rule.py`)

2.  **`RuleBase` 상속:**
    - 생성한 파일 안에서 `scripts.agents.rules.base`의 `RuleBase` 클래스를 상속받는 새로운 클래스를 정의합니다.

3.  **필수 클래스 변수 정의:**
    - `name`: CLI에서 사용될 규칙의 고유한 이름 (예: `my_new_rule`)
    - `summary`: 규칙에 대한 한 줄 설명

4.  **`apply` 메소드 구현:**
    - `apply(self, source: str, **kwargs) -> str` 메소드를 구현합니다. 이 메소드는 원본 소스 코드를 문자열로 받아, 수정한 코드를 문자열로 반환합니다.
    - `ast` 모듈을 사용하여 소스 코드를 파싱하고, 원하는 대로 수정한 후 `ast.unparse()`를 사용하여 다시 문자열로 변환합니다.

5.  **자동 등록:**
    - 위 과정을 마치면 프레임워크가 자동으로 새로운 규칙을 인식합니다. 별도의 등록 절차는 필요 없습니다. `invoke refactor --list-rules`를 실행하여 규칙이 추가되었는지 바로 확인할 수 있습니다.

**예시 (`my_new_rule.py`):**
```python
import ast
from .base import RuleBase

class MyNewRule(RuleBase):
    """새로운 리팩토링 규칙 예시입니다."""
    
    name = "my_new_rule"
    summary = "모든 'pass' 구문을 'print(\"Hello World\")'로 변경합니다."

    def apply(self, source: str, **kwargs) -> str:
        tree = ast.parse(source)
        
        class PassReplacer(ast.NodeTransformer):
            def visit_Pass(self, node):
                return ast.Expr(value=ast.Call(
                    func=ast.Name(id='print', ctx=ast.Load()),
                    args=[ast.Constant(value='Hello World')],
                    keywords=[]
                ))
        
        new_tree = PassReplacer().visit(tree)
        return ast.unparse(new_tree)
```

## 🗂️ `invoke organize-scratchpad`: 지능형 스크래치패드 정리 도구 (v3.0)

무질서한 `scratchpad` 디렉터리를 사전 정의된 규칙에 따라 5개의 카테고리로 자동 정리하여 검색성과 생산성을 극대화합니다.

### 주요 기능

-   **지능형 분류**: 파일 이름, 경로, 내용의 일부를 점수 기반으로 분석하여 최적의 카테고리로 자동 분류합니다.
-   **안전한 사전 검토**: 실제 파일을 이동하기 전, 상세한 이동 계획(분류 근거 점수 포함)을 표 형태로 미리 보여주어 사용자가 검토하고 승인할 수 있습니다.
-   **데이터 보존**: 이름이 충돌하는 파일은 덮어쓰지 않고 `_1`, `_2`와 같은 접미사를 붙여 안전하게 보존합니다.
-   **상세 로깅**: 모든 파일 이동 내역은 사람이 읽기 좋은 `organize_log.txt`와 기계가 처리하기 좋은 `organize_journal.jsonl` 두 형식으로 자동 기록됩니다.
-   **멱등성**: 이미 정리된 파일은 건너뛰므로, 여러 번 실행해도 결과는 동일하게 유지됩니다.

### 사용법 및 옵션

```bash
# [권장] 이동 계획만 확인 (실제 이동 없음)
invoke organize-scratchpad --dry-run

# 계획 검토 후, 확인 절차를 거쳐 실제 이동 실행
invoke organize-scratchpad

# 확인 절차 없이 즉시 실행 (자동화 스크립트용)
invoke organize-scratchpad --yes
```

## 환경 변수

* `SERPER_API_KEY`: Serper.dev API 키. 웹 검색 기능을 사용하려면 이 변수를 설정해야 합니다.

## 종료 코드 (Exit Codes)

* `0`: 정상 종료.
* `1`: 일반적인 오류.
* `2`: Provider 미설정 또는 사용 불가 (예: `SERPER_API_KEY`가 설정되지 않았거나 유효하지 않은 경우).
* `4`: 기타 예외 오류 (파일 없음, 규칙 없음, 경계 위반 등).

## 문제 해결

이 섹션에서는 문제 해결 팁을 제공합니다.

## 로컬 비밀 보호 (Windows DPAPI)

Windows DPAPI를 사용하여 로컬 비밀을 암호화하고 복호화할 수 있습니다. 이는 `pywin32` 라이브러리를 사용하며, 동일한 PC의 동일 사용자만 복호화할 수 있습니다.

**사용 방법:**

1.  `scripts/utils/dpapi.py` 모듈을 임포트합니다.
2.  `encrypt_to_file(plaintext: bytes, path: str)` 함수를 사용하여 평문 데이터를 파일에 암호화하여 저장합니다.
3.  `decrypt_from_file(path: str)` 함수를 사용하여 암호화된 파일에서 데이터를 복호화합니다.

**예시:**

```python
from scripts.utils.dpapi import encrypt_to_file, decrypt_from_file

# 암호화
plaintext_data = b"my_secret_api_key"
encrypt_to_file(plaintext_data, "./.gemini/my_secret.dat")

# 복호화
decrypted_data = decrypt_from_file("./.gemini/my_secret.dat")
print(decrypted_data.decode())
```

**주의점:**

*   이 기능은 **Windows 전용**이며, `pywin32` 라이브러리가 필요합니다.
*   암호화된 데이터는 **동일한 PC의 동일 사용자 계정**에서만 복호화할 수 있습니다. 다른 PC나 다른 사용자 계정에서는 복호화할 수 없습니다.
*   암호화된 파일을 다른 시스템으로 이동해도 복호화할 수 없습니다.

## 자주 묻는 질문

자주 묻는 질문입니다.

## 규칙 및 정책

자세한 규칙 및 정책은 `GEMINI.md`를 참조하십시오.


## 환경 변수

* `SERPER_API_KEY`: Serper.dev API 키. 웹 검색 기능을 사용하려면 이 변수를 설정해야 합니다.

## 종료 코드 (Exit Codes)

* `0`: 정상 종료.
* `1`: 일반적인 오류.
* `2`: Provider 미설정 또는 사용 불가 (예: `SERPER_API_KEY`가 설정되지 않았거나 유효하지 않은 경우).
* `4`: 기타 예외 오류 (파일 없음, 규칙 없음, 경계 위반 등).

## 문제 해결

이 섹션에서는 문제 해결 팁을 제공합니다.

## 로컬 비밀 보호 (Windows DPAPI)

Windows DPAPI를 사용하여 로컬 비밀을 암호화하고 복호화할 수 있습니다. 이는 `pywin32` 라이브러리를 사용하며, 동일한 PC의 동일 사용자만 복호화할 수 있습니다.

**사용 방법:**

1.  `scripts/utils/dpapi.py` 모듈을 임포트합니다.
2.  `encrypt_to_file(plaintext: bytes, path: str)` 함수를 사용하여 평문 데이터를 파일에 암호화하여 저장합니다.
3.  `decrypt_from_file(path: str)` 함수를 사용하여 암호화된 파일에서 데이터를 복호화합니다.

**예시:**

```python
from scripts.utils.dpapi import encrypt_to_file, decrypt_from_file

# 암호화
plaintext_data = b"my_secret_api_key"
encrypt_to_file(plaintext_data, "./.gemini/my_secret.dat")

# 복호화
decrypted_data = decrypt_from_file("./.gemini/my_secret.dat")
print(decrypted_data.decode())
```

**주의점:**

*   이 기능은 **Windows 전용**이며, `pywin32` 라이브러리가 필요합니다.
*   암호화된 데이터는 **동일한 PC의 동일 사용자 계정**에서만 복호화할 수 있습니다. 다른 PC나 다른 사용자 계정에서는 복호화할 수 없습니다.
*   암호화된 파일을 다른 시스템으로 이동해도 복호화할 수 없습니다.

## 자주 묻는 질문

자주 묻는 질문입니다.

## 규칙 및 정책

자세한 규칙 및 정책은 `GEMINI.md`를 참조하십시오.
