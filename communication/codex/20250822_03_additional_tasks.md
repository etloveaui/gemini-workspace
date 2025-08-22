---
agent: codex
priority: P1
status: pending
created: 2025-08-22 17:54
---

# 🚀 Codex 추가 작업 - 중요도 높음

## 📋 4가지 추가 작업 (1시간 이내)

### 1️⃣ doctor_v3.py CLI 출력 표준화 (20분)
```python
# 목표: 진단 결과를 cli_style로 통일
# 현재: print("System OK")
# 변경: print(cli_style.header("System Status"))
```

### 2️⃣ environment_detector.py CLI 완성 (15분)
```python
# 현재 거의 완성됨, 마지막 출력 부분만 표준화
# cli_style.kv(), header() 등 적용
```

### 3️⃣ run_background.py 테스트 및 수정 (15분)
- 현재 인코딩 오류로 타임아웃 발생
- UTF-8 처리 완료됐지만 실제 동작 검증 필요
- 간단한 테스트 모드 추가

### 4️⃣ 토큰 사용량 실시간 모니터링 (10분)
```bash
# 목표: 자동으로 토큰 사용량 체크하는 간단한 스크립트
python scripts/token_monitor.py --watch
```

## 💡 추가 제안 작업들

### 5️⃣ VS Code tasks.json 최적화 (옵션)
- 현재 18개 태스크 정리
- 자주 사용하지 않는 것들 분류

### 6️⃣ pytest 결과 상세 분석 (옵션)  
- 현재 23 passed, 8 skipped
- skipped 테스트들 활성화 가능한지 검토

## ⚡ 우선순위 순서
1. **run_background.py 수정** (가장 중요 - 자동화 시스템)
2. **doctor_v3.py 표준화** (진단 시스템)  
3. **environment_detector.py 완성** (환경 감지)
4. **토큰 모니터링** (안전장치)

## 🎯 **즉시 시작 지시**

**Claude 명령**: run_background.py부터 시작하세요. 이게 제일 중요합니다!

---

## 진행 상황 업데이트 
- [ ] run_background.py 테스트 및 수정
- [ ] doctor_v3.py CLI 표준화  
- [ ] environment_detector.py 완성
- [ ] 토큰 모니터링 추가