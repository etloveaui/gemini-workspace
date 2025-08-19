# 📡 Communication System v2.1

**멀티 에이전트 워크스페이스 통합 소통 시스템**

토큰 최적화와 워크플로우 효율성을 동시에 달성하는 차세대 소통 시스템입니다.

## 📁 디렉토리 구조

```
communication/
├── claude/           # Claude와의 대화 로그
├── gemini/          # Gemini와의 대화 로그  
├── codex/           # Codex와의 대화 로그
├── shared/          # 공통 참조 자료
└── templates/       # 표준 템플릿들
```

## 📝 파일 명명 규칙

### 세션 파일
- `YYYYMMDD_session_N.md` (N은 해당 날짜의 세션 번호)
- 예: `20250819_session_1.md`, `20250819_session_2.md`

### 태스크 파일  
- `YYYYMMDD_task_[task_name].md`
- 예: `20250819_task_ui_improvement.md`

### 긴급 요청
- `YYYYMMDD_urgent_[description].md`
- 예: `20250819_urgent_system_fix.md`

## 🏷️ 표준 태그 시스템

각 파일 헤더에 다음 정보를 포함:

```markdown
---
agent: claude|gemini|codex
priority: P0|P1|P2|P3
status: pending|in_progress|completed|blocked
tags: [feature, bugfix, optimization, etc.]
created: YYYY-MM-DD HH:MM
updated: YYYY-MM-DD HH:MM
---
```

## 🎯 우선순위 가이드

- **P0**: 시스템 크리티컬 (즉시 처리)
- **P1**: 높은 우선순위 (24시간 내) 
- **P2**: 일반 작업 (일주일 내)
- **P3**: 백로그 (유연한 일정)

## 💡 사용 팁

1. **구체적 제목**: "버그 수정" → "로그인 폼 validation 오류 수정"
2. **명확한 요구사항**: 원하는 결과를 구체적으로 명시
3. **컨텍스트 제공**: 관련 파일, 이전 작업 등 참조 정보 포함
4. **진행 상황 업데이트**: 상태 변경 시 파일 업데이트