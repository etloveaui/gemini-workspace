# Gemini를 위한 비밀 정보 관리 지침

이 문서는 Gemini가 새로운 비밀 정보(API 키, 토큰 등)를 발견하거나 생성했을 때, 이를 안전하게 기록하고 사용자에게 알리는 방법을 정의합니다.

## 1. 새로운 비밀 정보 발견/생성 시 절차

1.  **`secrets/my_sensitive_data.md` 파일에 기록:**
    *   발견하거나 생성한 비밀 정보를 `secrets/my_sensitive_data.md` 파일에 추가합니다.
    *   정보의 종류, 용도, 유효 기간(있는 경우) 등을 명확하게 기록합니다.
    *   예시:
        ```markdown
        ### [서비스 이름] API Key
        - **용도:** [간단한 설명]
        - **값:** `[API_KEY_VALUE]`
        - **생성일/발견일:** YYYY-MM-DD
        - **만료일 (있는 경우):** YYYY-MM-DD
        ```

2.  **사용자에게 알림:**
    *   `secrets/my_sensitive_data.md` 파일이 업데이트되었음을 사용자에게 즉시 알립니다.
    *   어떤 정보가 추가되었는지 간략하게 설명하고, 파일 내용을 확인하도록 안내합니다.
    *   **예시 메시지:** "새로운 [서비스 이름] API 키를 `secrets/my_sensitive_data.md` 파일에 기록했습니다. 파일 내용을 확인해 주세요."

## 2. `secrets/my_sensitive_data.md` 파일 접근 및 수정

*   `secrets/my_sensitive_data.md` 파일은 Git 추적에서 제외되므로, 이 파일에 대한 변경사항은 Git에 커밋되지 않습니다.
*   이 파일은 사용자님의 로컬 시스템에만 존재하며, USB 등으로 직접 백업하고 관리해야 합니다.
*   Gemini는 이 파일에 직접 접근하여 내용을 읽거나 수정할 수 있습니다.
