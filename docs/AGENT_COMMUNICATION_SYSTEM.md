# 멀티 에이전트 파일 기반 소통 시스템

**작성일**: 2025-08-21  
**작성자**: Claude (총감독관)  
**버전**: v1.0

## 🎯 시스템 개요

각 AI 에이전트가 파일을 통해 비동기적으로 소통할 수 있는 체계적인 시스템입니다.

## 📁 디렉토리 구조

```
communication/
├── claude/           # Claude 전용 폴더
├── gemini/          # Gemini 전용 폴더  
├── codex/           # Codex 전용 폴더
├── shared/          # 공유 작업 공간
└── templates/       # 템플릿 파일들
```

## 📝 메시지 포맷

### 기본 템플릿
```markdown
---
from: [발신자 에이전트]
to: [수신자 에이전트] 
date: YYYY-MM-DD HH:MM
subject: [제목]
priority: [P0|P1|P2|P3]
---

# [발신자] → [수신자] 메시지

## 📋 요청 내용
[구체적 요청사항]

## 📊 배경 정보  
[관련 컨텍스트]

## 🎯 기대 결과
[원하는 결과물]

---
[발신자] 🤖
```

## 🔄 소통 워크플로우

### 1. 메시지 작성
- 해당 에이전트 폴더에 날짜_제목.md 파일 생성
- 표준 템플릿 사용

### 2. 상태 추적
```markdown
status: [pending|in_progress|completed|cancelled]
```

### 3. 응답 처리
- 같은 파일에 응답 섹션 추가
- 또는 별도 응답 파일 생성

## 💡 활용 예시

### Claude → Codex 작업 요청
```markdown
# communication/codex/20250821_code_review.md

---
from: Claude
to: Codex  
date: 2025-08-21 12:00
subject: TerminalX 브라우저 제어 코드 리뷰 요청
priority: P2
---

## 📋 요청 내용
1. browser_controller.py 코드 리뷰
2. 성능 최적화 제안
3. 에러 처리 개선점 분석
```

### Gemini → Claude 분석 결과 공유
```markdown
# communication/claude/20250821_analysis_report.md

---
from: Gemini
to: Claude
date: 2025-08-21 12:30  
subject: 시스템 사용 패턴 분석 결과
priority: P1
---

## 📊 분석 결과
[상세 분석 내용]
```

## 🎯 장점

1. **비동기 협업**: 실시간 응답 불필요
2. **기록 보존**: 모든 소통 내역 파일로 보존
3. **체계적 관리**: 폴더 구조로 정리
4. **검색 가능**: Git 히스토리 및 파일 검색
5. **확장성**: 새로운 에이전트 쉽게 추가

## 📋 사용 규칙

### 필수 사항
- [ ] 표준 템플릿 사용
- [ ] 명확한 제목 작성  
- [ ] 우선순위 명시
- [ ] 완료 후 상태 업데이트

### 권장 사항
- 파일명: `YYYYMMDD_작업명.md`
- 간결하고 구체적인 요청
- 관련 파일 경로 명시
- 예상 소요시간 표기

## 🔧 자동화 도구

### 워처 스크립트 활용
```bash
# communication 폴더 모니터링
python scripts/watch_file.py communication --recursive --include *.md

# 특정 에이전트 폴더만 감시
python scripts/watch_file.py communication/claude --include *.md
```

### 알림 시스템 (선택사항)
- 새 메시지 감지시 로그 기록
- 우선순위별 알림 차등화
- 응답 대기 시간 추적

## 📈 확장 계획

### Phase 1: 기본 소통 (현재)
- 파일 기반 메시지 교환
- 표준 템플릿 적용

### Phase 2: 자동화 강화  
- 메시지 상태 자동 추적
- 워크플로우 자동화
- 응답 템플릿 제안

### Phase 3: 인텔리전트 라우팅
- 작업 유형별 자동 에이전트 배정
- 우선순위 기반 스케줄링
- 성과 측정 및 최적화

---

**💡 이 시스템으로 멀티 에이전트 협업이 더욱 체계적이고 효율적으로 이루어집니다!**