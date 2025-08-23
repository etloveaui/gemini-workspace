---
agent: codex
priority: P1
status: pending
created: 2025-08-22 16:45
token_limit_warning: true
---

# 🎯 CODEX 계속 진행 작업 지시 - 토큰 관리하며 CLI 표준화

## 📊 현재 토큰 상황
- **현재 사용량**: 8,693,688 토큰 (39% 사용)
- **토큰 한도**: ~22,000,000 토큰 추정
- **안전 마진**: 60% 이하 유지 권장
- **⚠️ 주의**: 사용량을 지속적으로 모니터링하며 작업

## 🚀 계속 진행할 CLI 표준화 작업

### 우선순위 P1 작업들
1. **environment_detector.py** CLI 출력 표준화
   - 현재 상태: 미완성
   - scripts.cli_style 모듈 활용
   - 추정 토큰: ~50,000

2. **usage_limit_monitor.py** CLI 출력 표준화  
   - 현재 상태: 미완성
   - 토큰 사용량 모니터링 관련
   - 추정 토큰: ~40,000

3. **doctor_v3.py** CLI 출력 표준화
   - 현재 상태: 미완성
   - 진단 시스템 출력 정리
   - 추정 토큰: ~80,000

### 작업 방식
- **토큰 효율성**: 각 파일당 최소한의 수정만
- **검증 단계**: 수정 후 즉시 테스트
- **진행 보고**: 각 파일 완료 시마다 상태 업데이트

## 🛡️ 토큰 안전 가이드라인

### 즉시 중단 조건
- 토큰 사용률 55% 초과 시
- 에러가 연속 3회 발생 시
- 예상 토큰과 실제 차이가 50% 초과 시

### 안전 작업 방법
1. 한 번에 하나의 파일만 작업
2. 수정 전후 토큰 사용량 체크
3. 복잡한 리팩토링 금지 (단순 출력 표준화만)
4. 새 기능 추가 금지

## 📋 작업 순서

### 1단계: environment_detector.py
```python
# 목표: scripts.cli_style 모듈로 출력 통일
# 변경 예시:
# print("Current environment: Windows")  
# → print(cli_style.kv("Environment", "Windows"))
```

### 2단계: usage_limit_monitor.py  
```python
# 목표: 토큰 사용량 출력 표준화
# 변경 예시:
# print("Token usage: 50%")
# → print(cli_style.status_line(1, "INFO", "Token Usage", "50%"))
```

### 3단계: doctor_v3.py
```python
# 목표: 진단 결과 출력 표준화  
# 변경 예시:
# print("System OK")
# → print(cli_style.header("System Status"))
```

## 🔄 진행 상황 보고

작업 완료 시 이 파일에 다음 형식으로 업데이트:

```
## 진행 상황 - [날짜/시간]
- [파일명]: 완료/진행중/중단
- 토큰 사용량: [현재]/[이전] ([증가량])
- 발생 이슈: [있다면 기록]
- 다음 작업: [계획]
```

## ⚡ 즉시 시작 지시

**Claude의 명령**:
1. 토큰 사용량 확인 (현재 39%)
2. environment_detector.py부터 시작
3. 30분 단위로 진행상황 업데이트
4. 55% 도달 시 즉시 작업 중단하고 Claude에게 보고

**시작하세요!**