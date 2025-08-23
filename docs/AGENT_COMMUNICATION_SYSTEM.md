# AGENT_COMMUNICATION_SYSTEM.md

본 시스템은 파일 기반 비동기 커뮤니케이션을 표준으로 합니다.

## 디렉터리 구조
- `communication/codex/`: Codex 발신/수신 메시지 및 작업 노트
- `communication/shared/`: 공통 가이드 및 템플릿

## 메시지 작성 규칙
- 파일명: `yyyymmdd_XX_short-title.md` (예: `20250823_01_setup.md`)
- 내용: 목적, 컨텍스트, TODO, 차기 액션, 담당자
- 인코딩: UTF-8

## 워크플로우
1. Codex가 메시지/노트 작성 → 저장
2. 워처(`scripts/watch_file.py`)가 변경 감지 → 로그 출력
3. 타 에이전트는 해당 파일을 읽고 응답 파일 생성

## 주의사항
- 민감정보 포함 금지. 필요 시 환경변수/별도 설정 사용
- projects/ 내부 변경 사항을 루트 Git에 포함 금지

