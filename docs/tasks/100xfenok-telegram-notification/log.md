# [100xFenok] Telegram Notification Integration - 작업 로그

## 1. 목표
- `100xFenok` 프로젝트에 새로운 포스팅이 올라가면, 텔레그램 봇을 통해 사용자에게 알림을 보내는 시스템을 구축한다.
- 기존 OneSignal 기반 알림 시스템은 유지한 채, 텔레그램 알림을 병행하여 추가한다.
- 향후 다른 기능(예: 로그인)으로 확장할 수 있도록 견고한 구조로 설계한다.

## 2. 실행 계획

### 1단계: 환경 설정 및 인증
1.  **라이브러리 추가:** `requirements.txt`에 Google Sheets 및 Telegram API 요청에 필요한 라이브러리(`google-api-python-client`, `requests` 등)를 추가하고 설치한다.
2.  **인증 정보 관리:** Telegram 봇 토큰과 Google Sheets API 접근을 위한 서비스 계정 인증 정보를 `secrets` 폴더에서 안전하게 읽어오도록 구현한다.

### 2단계: 핵심 기능 모듈 개발 (예: `telegram_notifier.py`)
1.  **Google Sheets 연동:**
    *   `ChatIDs` 시트에서 알림을 받을 사용자들의 Chat ID 목록을 읽어오는 기능을 구현한다.
    *   알림 발송 결과를 기록할 새로운 로그용 시트(예: `100xFenok_Logs`)에 "시간, 발송상태, 상세내용" 등을 기록하는 기능을 구현한다.
2.  **Telegram 메시지 발송:**
    *   입력받은 Chat ID와 메시지 내용을 바탕으로, Telegram 봇 API를 통해 실제 알림을 보내는 기능을 구현한다.

### 3단계: 프로젝트에 통합
1.  **알림 트리거:** `100xfenok` 프로젝트의 메인 스크립트에서 최종 `데일리랩.html` 파일이 성공적으로 생성되는 시점을 찾아, 위에서 만든 알림 모듈을 호출하는 코드를 추가한다.
2.  **수동/자동 실행:** 이 알림 기능이 수동으로도 실행될 수 있고, 향후 자동화 흐름에도 쉽게 통합될 수 있도록 설계한다.

## 3. 전제 조건 (Prerequisites)
- **Google Service Account JSON 키 파일:** Google Sheets API에 접근하기 위한 서비스 계정의 JSON 키 파일이 필요하다. 사용자가 추후 이 파일을 제공해야 실제 구현을 진행할 수 있다.
