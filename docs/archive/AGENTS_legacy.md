# 멀티 에이전트 시스템 운영 가이드 v2.0

**생산성 극대화**를 위한 차세대 멀티 에이전트 워크스페이스 통합 가이드입니다.

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

