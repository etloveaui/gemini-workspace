# [System] - 비밀 정보 관리 체계 수립

## 2025-07-22

### [Initial Setup] - 목표: 민감 정보의 안전한 관리 시스템 구축

- **Action:** 민감한 정보(API 키, 토큰 등)를 안전하게 관리하기 위해 `secrets/` 폴더 생성.
- **Result:** `secrets/` 폴더는 Git에 의해 추적됨.
- **Action:** Gemini가 새로운 비밀 정보를 발견하거나 생성했을 때, 이를 `secrets/my_sensitive_data.md`에 기록하고 사용자에게 알리는 지침을 담은 `secrets/gemini_instructions.md` 파일 생성.
- **Result:** `secrets/gemini_instructions.md` 파일은 Git에 의해 추적됨.
- **Action:** 사용자님의 민감한 정보를 기록할 수 있는 `secrets/my_sensitive_data.md` 파일 생성 및 업데이트.
- **Result:** `secrets/my_sensitive_data.md` 파일은 `.gitignore`에 추가되어 Git 추적에서 제외됨. TerminalX 로그인 자격 증명, OneSignal Keys, Gemini API Key 정보 추가.
- **Action:** `projects/100xFenok/onesignal/keys.txt` 파일이 Git에 커밋되지 않도록 `.gitignore`에 추가.
