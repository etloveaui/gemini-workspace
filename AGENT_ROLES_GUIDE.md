# 🤖 멀티 에이전트 시스템 통합 가이드 v2.1

**생산성 극대화**를 위한 차세대 멀티 에이전트 워크스페이스 완전 가이드입니다.

## 🎯 에이전트별 전문 영역

### 🧠 **Claude (수석 설계자)**
**전문분야**: 시스템 아키텍처, 복잡한 로직, 멀티파일 작업, 보안

**언제 사용?**
- 복잡한 시스템 설계가 필요할 때
- 여러 파일을 동시에 수정해야 할 때  
- 보안이 중요한 코드 작업 시
- 전체적인 프로젝트 구조 검토 시

**사용법**:
```
communication/claude/YYYYMMDD_작업명.md 파일에 작성
- 복잡한 요구사항도 자세히 설명 가능
- 단계별 계획 수립 후 체계적 실행
- 다른 에이전트 작업 조율 가능
```

### ⚡ **Gemini (빠른 실행자)**  
**전문분야**: 빠른 구현, 데이터 처리, 검색, 단순 반복 작업

**언제 사용?**
- 빠른 프로토타입이 필요할 때
- 대량의 데이터 처리가 필요할 때
- 빠른 검색/조사 작업 시
- 단순하지만 반복적인 작업 시

**사용법**:
```
communication/gemini/quick_task.md 또는 daily_log.md 사용
- 간단명료한 지시사항으로 빠른 결과
- 대량 파일 처리나 반복 작업에 특화
- 실시간 작업 상황 공유
```

### 💻 **Codex (코딩 전문가)**
**전문분야**: 특정 언어 최적화, 디버깅, 코드 리뷰, 성능 튜닝

**언제 사용?**
- 특정 프로그래밍 언어 최적화가 필요할 때
- 복잡한 버그 수정이 필요할 때
- 코드 성능 개선이 필요할 때  
- 특정 알고리즘 구현이 필요할 때

**사용법**:
```
communication/codex/code_task.md 사용
- 구체적인 코딩 요구사항 명시
- 성능 목표나 제약사항 포함
- 기존 코드 스타일 유지 요청
```

---

## 🔄 협업 패턴

### Pattern 1: **순차 작업**
1. **Claude**: 전체 설계 및 계획 수립
2. **Gemini**: 빠른 기초 구현  
3. **Codex**: 코드 최적화 및 완성

### Pattern 2: **병렬 작업**
- **Claude**: 핵심 모듈 개발
- **Gemini**: 데이터 처리 스크립트
- **Codex**: 유틸리티 함수 최적화

### Pattern 3: **긴급 모드**
- **Claude**: 긴급 상황 분석 및 대응책 수립
- **Gemini**: 빠른 임시 해결책 구현
- **Codex**: 코드 수정 및 배포

---

## 📝 효율적인 소통 방법

### 빠른 작업 요청
```markdown
# Quick Task
Agent: gemini
Priority: P1

파일 100개에서 "old_function" -> "new_function" 일괄 변경해줘
```

### 복잡한 프로젝트
```markdown
# 복합 프로젝트  
Agent: claude
Priority: P0

새로운 인증 시스템 구축
- OAuth2 + JWT 토큰
- 3단계 보안 검증
- 기존 시스템과 호환성 유지
```

### 성능 최적화
```markdown
# Performance Tuning
Agent: codex  
Priority: P2

database.py의 쿼리 성능 50% 개선 필요
현재 응답시간: 2.3초 → 목표: 1.0초 이하
```

---

## ⚡ 즉시 사용 가능한 템플릿

### 일반 작업 요청
```
communication/templates/quick_template.md 복사 → 수정 → 해당 에이전트 폴더에 저장
```

### 프로젝트 시작
```  
communication/templates/session_template.md 복사 → 프로젝트명으로 수정
```

### 버그 수정
```
communication/templates/task_template.md 복사 → "버그 수정" 태그 추가
```

---

## 🚀 효율성 극대화 팁

1. **적재적소 활용**: 각 에이전트의 강점에 맞는 작업 배정
2. **명확한 소통**: 구체적인 요구사항과 제약조건 명시  
3. **템플릿 활용**: 일관된 형식으로 빠른 작업 지시
4. **우선순위 관리**: P0(긴급) ~ P3(백로그) 체계적 관리
5. **결과 공유**: 완료 후 다른 에이전트가 참고할 수 있도록 문서화

---

**💡 핵심**: 각 에이전트의 특성을 이해하고 적절히 활용하면 기존 Claude Code 대비 **정말로 10배** 빠른 생산성을 경험할 수 있습니다!

---

## 🚀 고성능 워크플로우 (병렬 처리)
1. **시작** → `python .agents/multi_agent_manager.py status` - 에이전트 상태 확인
2. **작업 할당** → `python .agents/multi_agent_manager.py add-task <task_id> [priority] [agent]`
3. **동시 실행** → 3개 에이전트가 독립적 영역에서 병렬 작업
4. **실시간 모니터링** → Context7 MCP + 성능 지표 추적
5. **테스트** → `pytest` - 통합 테스트 자동 실행
6. **통합 커밋** → `invoke commit_safe` - 원자적 변경사항 적용
7. **작업 완료** → 자동 아카이브 및 성과 기록

## 🎛️ 시스템 설정 (차세대 아키텍처)
- **동시실행 제한**: `.agents/config.json`에서 `concurrent_limit: 3` 설정
- **작업 우선순위**: P0(긴급), P1(높음), P2(일반), P3(백로그) 자동 관리
- **Context7 MCP**: 실시간 문서/지식 통합으로 생산성 10배 향상
- **성능 모니터링**: SQLite 기반 실시간 에이전트 상태 추적
- **충돌 방지**: Git 기반 원자적 작업 영역 분할

## 🔧 고급 제어 명령어
- **에이전트 전환**: `invoke agent.set --name claude|gemini|codex`
- **긴급 모드**: `.agents/emergency.json`의 `enabled` 필드 토글
- **Context7 검색**: `python .agents/context7_mcp.py search <library> [function]`
- **성능 통계**: `python .agents/multi_agent_manager.py stats`
- **캐시 관리**: Context7 캐시 자동 정리 (1시간 TTL)
- **우선순위 조정**: 작업 큐에서 P0~P3 우선순위 동적 변경

## 🛡️ 보안 및 최적화
- **민감정보 보호**: `.gemini/*`, `secrets/*`, `.agents/locks/*` 커밋 차단
- **토큰 최적화**: Context7 캐시로 30% 토큰 절약
- **메모리 효율성**: 동시실행 시 60% 미만 CPU 사용률 유지
- **에러 복구**: 자동 잠금 해제 및 작업 재할당 시스템