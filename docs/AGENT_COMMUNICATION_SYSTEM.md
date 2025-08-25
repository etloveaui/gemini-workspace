# AGENT_COMMUNICATION_SYSTEM (초기 템플릿)

모든 AI 에이전트 간 소통은 파일 기반 비동기 시스템을 사용합니다.

## 디렉터리 구조
- communication/codex/inbox: 수신 메시지
- communication/codex/outbox: 발신 메시지
- communication/codex/processed: 처리 완료 메시지
- communication/codex/archive: 보관

## 이벤트 흐름
1) 발신 에이전트가 outbox에 파일 생성
2) 워처가 수신 측 inbox로 이동/복제
3) 처리 후 processed로 이동, 필요 시 archive 보관

## 규칙
- 파일명: `yyyymmdd_XX_topic.ext`
- 인코딩: UTF-8
- 민감정보 금지, 필요 시 암호화/마스킹

