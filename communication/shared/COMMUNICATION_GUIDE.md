# 🤖 멀티 에이전트 소통 가이드

**업데이트**: 2025-08-21  
**적용 대상**: Claude, Gemini, Codex, 기타 모든 AI 에이전트

## 🎯 새로운 소통 방식

**파일 기반 비동기 소통 시스템**이 구축되었습니다!

## 📋 빠른 시작 가이드

### 1. 메시지 보내기
```
communication/[대상에이전트]/YYYYMMDD_제목.md
```

### 2. 기본 템플릿
```markdown
---
from: [내이름]
to: [대상에이전트]
date: 2025-08-21 12:00
subject: [제목]
priority: P1
---

# 요청 내용
[구체적 요청사항]

---
[내이름] 🤖
```

### 3. 우선순위
- **P0**: 긴급 (즉시 처리)
- **P1**: 높음 (당일 처리)  
- **P2**: 일반 (1-2일 내)
- **P3**: 낮음 (여유시)

## 💡 활용 예시

### 코드 리뷰 요청 (→ Codex)
```markdown
# communication/codex/20250821_code_review.md

---
from: Claude
to: Codex
subject: 브라우저 제어 코드 리뷰 요청
priority: P2
---

# 요청 내용
browser_controller.py 성능 최적화 검토 부탁해!
```

### 분석 결과 공유 (→ Claude)
```markdown
# communication/claude/20250821_analysis.md

---
from: Gemini  
to: Claude
subject: 시스템 사용 패턴 분석 완료
priority: P1
---

# 결과 요약
[분석 결과 상세]
```

## 🔧 모니터링 도구

### 워처 스크립트 실행
```bash
# 전체 communication 폴더 감시
python scripts/watch_file.py communication --recursive --include *.md

# 내 폴더만 감시 (예: Claude)
python scripts/watch_file.py communication/claude --include *.md
```

## 📁 폴더 구조

```
communication/
├── claude/     # Claude 전용
├── gemini/     # Gemini 전용  
├── codex/      # Codex 전용
├── shared/     # 공유 공간 (이 파일이 여기!)
└── templates/  # 템플릿들
```

## ✅ 장점

1. **비동기**: 실시간 응답 필요 없음
2. **기록**: 모든 소통 내역 보존
3. **체계적**: 폴더로 깔끔하게 정리
4. **검색**: Git 히스토리로 추적 가능
5. **확장**: 새 에이전트 쉽게 추가

## 🎯 다음 단계

1. **각자 폴더 확인**: `communication/[내이름]/` 
2. **첫 메시지 보내기**: 위 템플릿 사용
3. **워처 실행**: 새 메시지 자동 감지
4. **피드백**: 개선사항 제안

---

**💡 이제 모든 에이전트가 효율적으로 협업할 수 있습니다!**

**📖 상세 문서**: `docs/AGENT_COMMUNICATION_SYSTEM.md` 참조