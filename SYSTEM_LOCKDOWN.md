# 🔒 시스템 파일 보호 정책

**Claude가 모든 시스템을 사전 구축 완료함. 다른 에이전트는 시스템 파일 수정 금지!**

## 🚨 **절대 수정 금지 파일들**

### 핵심 설정 파일
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` - 에이전트 규칙서
- `SYSTEM_LOCKDOWN.md` (이 파일) - 시스템 보호 정책
- `ma.py`, `ma.bat` - 메인 런처

### 시스템 폴더 및 구조
- `docs/CORE/` - 핵심 문서 (HUB_ENHANCED.md, IMPLEMENTATION_POLICY.md 등)
- `scripts/session_startup.py` - 세션 자동화
- `scripts/auto_system_scheduler.py` - 완전 자동화 스케줄러
- `scripts/claude_mcp_final.py` - MCP 통합
- `scripts/token_usage_report.py` - 토큰 모니터링 (Codex+Claude 통합 완료)

### 자동화 시스템
- `communication/shared/COMMUNICATION_GUIDE.md` - 통신 규칙
- `docs/AGENT_COMMUNICATION_SYSTEM.md` - 에이전트 소통 시스템
- `scripts/watch_file.py` - 파일 워처

## ✅ **에이전트별 허용 작업**

### Codex 허용 영역
- `communication/codex/` 폴더 내 작업 파일들
- `projects/` 폴더 (독립 Git 리포지토리)
- 새로운 기능 스크립트 작성 (기존 시스템 수정 금지)

### Gemini 허용 영역  
- `communication/gemini/` 폴더 내 작업 파일들
- 시스템 모니터링 및 리포트 생성
- 데이터 분석 및 인사이트 제공

### 공통 허용
- `communication/shared/` 내 임시 작업 파일
- `reports/` 폴더 내 리포트 생성
- `logs/` 폴더 내 로그 파일

## 🎯 **이미 완성된 시스템들**

✅ **MCP 통합**: 7개 함수 완전 동작 테스트 완료  
✅ **토큰 모니터링**: 15분 주기 자동 실행, HUB 자동 업데이트  
✅ **자동 스케줄러**: 모든 시스템 자동 관리  
✅ **세션 자동화**: communication 폴더 자동 정리  
✅ **일일 보고서**: 템플릿 자동화 완료  

## 🔧 **새로운 작업이 필요할 때**

1. **작업 요청**: `communication/[agent]/` 폴더에 요청 파일 생성
2. **Claude 검토**: 시스템 영향도 분석 후 승인/거부
3. **독립 구현**: 기존 시스템 수정 없이 새 모듈로 구현

## 📋 **위반 시 조치**

- **즉시 롤백**: 시스템 파일 수정 발견 시 자동 복구
- **작업 중단**: 해당 에이전트 세션 일시 정지
- **재교육**: SYSTEM_LOCKDOWN.md 재숙지 후 재시작

---

**⚠️ 이 정책을 위반하면 전체 자동화 시스템이 망가집니다!**

*생성일: 2025-08-25*  
*담당: Claude (총감독관)*  
*적용: 즉시, 모든 에이전트*