# 다중 환경 동기화 가이드

## 🚨 Git 관리 안되는 중요 파일들

### 1️⃣ **에이전트 개인 설정 폴더**
```
.claude*/     ← Claude Code 개인 설정  
.gemini/      ← Gemini 개인 설정 (context_policy.yaml 제외)
.agents/      ← 일부 파일만 Git 관리됨
```

### 2️⃣ **개발 환경 설정**
```
.vscode/      ← VS Code 워크스페이스 설정
.env          ← 환경변수 파일
venv/         ← 가상환경
```

### 3️⃣ **민감 정보**
```
secrets/      ← 모든 민감 정보
usage.db      ← 토큰 사용량 데이터베이스  
*.log         ← 로그 파일들
```

### 4️⃣ **프로젝트 독립 공간**
```
projects/     ← 독립적인 Git 프로젝트들
```

### 5️⃣ **임시/캐시 파일**
```
__pycache__/
*.tmp
*.temp
.pytest_cache/
reports/      ← 일일 리포트들
```

## 🔄 **환경 간 동기화 방법**

### ✅ **자동으로 해야 할 것들**
1. **VS Code 설정 (.vscode/)**
   ```bash
   # 수동으로 복사 필요
   cp -r .vscode/ /다른환경/
   ```

2. **환경변수 (.env)**
   ```bash
   # 템플릿 파일 생성하여 Git 관리
   cp .env .env.template  # 민감정보 제거 후
   ```

3. **에이전트 설정 일부**
   ```bash
   # .gemini/context_policy.yaml만 Git 관리됨
   # 나머지는 수동 동기화 필요
   ```

### ⚠️ **주의할 것들**
- **secrets/** 폴더는 절대 Git에 넣지 말 것
- **usage.db**는 각 환경별로 독립 관리
- **projects/**는 별도 Git 저장소

## 🤖 **자동 동작 시스템 답변**

### 1️⃣ **"지금 터미널에 있으면 알아서 동작?"**
**→ 아직 아닙니다!** 수동 실행 필요:

```bash
# 백그라운드 자동화 시작
python run_background.py

# 또는 일회성 실행
python scripts/auto_status_updater.py
```

### 2️⃣ **"터미널 켜두고 똑같이 작업하면 됨?"**
**→ YES!** 다음 명령어 실행 후:

```bash
python run_background.py
```

그러면:
- 10분마다 상태 자동 업데이트
- 1시간마다 성능 최적화  
- 사용자는 신경쓸 필요 없음

## 📝 **환경별 설정 체크리스트**

### 새로운 환경 설정시:
- [ ] `.env` 파일 복사 (민감정보 수정)
- [ ] `.vscode/` 폴더 복사
- [ ] `python run_background.py` 실행
- [ ] `secrets/` 폴더 재생성
- [ ] 가상환경 재생성 (`python -m venv venv`)
- [ ] `pip install -r requirements.txt`

### 정기 동기화:
- [ ] VS Code 설정 변경사항 수동 복사
- [ ] 새로운 secrets 파일들 수동 이동
- [ ] .agents/ 폴더 일부 파일 동기화

## 🎯 **권장 동기화 전략**

1. **Git으로 관리되는 것**: 자동 동기화 ✅
2. **설정 파일들**: 주기적 수동 동기화 📋  
3. **민감 정보**: 암호화된 별도 저장소 🔐
4. **로그/캐시**: 환경별 독립 관리 🗂️