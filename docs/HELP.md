# Gemini CLI 도움말

## 시작하기

이 섹션에서는 Gemini CLI를 시작하는 방법에 대한 정보를 제공합니다.

## 명령어 개요

사용 가능한 명령어에 대한 개요입니다:

* `invoke doctor`: 환경 설정을 확인합니다.
* `invoke quickstart`: 빠른 시작 가이드를 확인합니다.
* `invoke help [section]`: 도움말 정보를 표시합니다.
* `invoke search "<query>"`: 웹 검색을 수행하고 결과를 요약합니다.

## 환경 변수

* `SERPER_API_KEY`: Serper.dev API 키. 웹 검색 기능을 사용하려면 이 변수를 설정해야 합니다.

## 종료 코드 (Exit Codes)

* `0`: 정상 종료.
* `1`: 일반적인 오류.
* `2`: Provider 미설정 또는 사용 불가 (예: `SERPER_API_KEY`가 설정되지 않았거나 유효하지 않은 경우).
* `4`: 기타 예외 오류.

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