# COMMUNICATION_GUIDE.md

## 빠른 시작
1. `communication/codex/`에 오늘자 파일 생성: `yyyymmdd_01_subject.md`
2. 목적/요약/할 일/차기 액션/요청 사항을 10줄 내로 정리
3. 저장하면 워처가 감지하여 로그 출력

## 템플릿
```
# 제목(간결하게)
- 날짜: 2025-08-23
- 에이전트: Codex
- 목적: 
- 컨텍스트: 
- TODO:
  - [ ] 
- 차기 액션: 
- 요청/의존성: 
```

## 인코딩 트러블슈팅(Windows)
- 반드시 UTF-8로 저장하세요. VS Code: 하단 상태바 인코딩 → UTF-8 선택.
- 자동 추정 활성화: `.vscode/settings.json`에 `files.autoGuessEncoding: true` 설정.
- 파일이 이미 깨졌다면, 원문을 다시 붙여넣고 UTF-8로 재저장하세요.
