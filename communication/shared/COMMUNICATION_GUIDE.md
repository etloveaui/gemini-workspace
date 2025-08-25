# Communication Quick Start (공유)

## 폴더
- `communication/codex/inbox`: 수신
- `communication/codex/outbox`: 발신
- `communication/codex/processed`: 처리완료
- `communication/codex/archive`: 보관

## 기본 규칙
- UTF-8 텍스트 파일 우선
- 파일명 `yyyymmdd_XX_topic`
- 상태 전이는 이동으로 추적(inbox → processed)

