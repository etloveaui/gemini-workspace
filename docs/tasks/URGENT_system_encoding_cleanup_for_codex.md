# 🚨 URGENT: 시스템 인코딩 문제 및 스크립트 정리 (Codex 긴급 지시사항)

**작성일**: 2025-08-18  
**작성자**: Claude Code  
**대상 에이전트**: Codex  
**우선순위**: 🔥 최고 긴급 (시스템 마비 상태)  

---

## 🚨 현재 상황: 시스템 마비 상태

**인코딩 문제가 시스템 전체를 마비시키고 있음:**
- `UnicodeDecodeError` 지속 발생 (`'cp949' codec can't decode`)  
- `invoke review` 완전 실패
- Git 작업 불가능 상태
- Python 스크립트들 상호 충돌

**근본 원인:**
1. **Git 속성 파일 설정에도 불구하고 CP949 고착화**
2. **scripts 폴더에 57개 Python 파일 - 너무 많아서 충돌**
3. **중복/불필요 스크립트들이 시스템 혼란 가중**

---

## 🔧 긴급 실행 지시사항 (순서대로 필수 실행)

### 1단계: Python 스크립트 대폭 정리 (57개 → 10개)

**현재 상태**: `scripts/` 폴더에 57개 Python 파일
**목표**: 핵심 기능만 10개 이하로 정리

**삭제 대상 (즉시 삭제):**
- `scripts/encoding_*` 관련 중복 파일들 (여러 개 존재)  
- `scripts/*_backup.py`, `scripts/*_old.py` 등 백업 파일들
- `scripts/auto_update/` 폴더 내 실험적 스크립트들
- `scripts/usage_*` 관련 중복 파일들
- `scripts/git_*` 관련 중복 파일들 (기능이 겹치는 것들)

**보존해야 할 핵심 스크립트 (10개 이하):**
1. `tasks.py` (메인 Invoke 태스크)
2. `encoding_permanent_fix.py` (최종 인코딩 수정용)
3. `git_commit_easy.py` (pre-commit 우회용)
4. `error_prevention_simple.py` (에러 방지)
5. `usage_limit_monitor.py` (사용량 모니터링)
6. 그 외 **정말 필요한 것만 5개 이하**

### 2단계: Git 저장소 완전 초기화 및 UTF-8 강제 적용

**실행 명령어 (순서대로):**
```bash
# 1. 환경변수 강제 설정 (영구적)
setx PYTHONIOENCODING "utf-8"
setx PYTHONLEGACYWINDOWSFSENCODING "utf-8"

# 2. Git 설정 재적용
git config --global core.quotepath false
git config --global i18n.filesEncoding utf-8  
git config --global i18n.commitEncoding utf-8
git config --global core.autocrlf false

# 3. Git 캐시 완전 초기화
git rm --cached -r .
git add .
git reset --hard HEAD

# 4. 코드페이지 강제 변경
chcp 65001
```

### 3단계: 인코딩 문제 파일들 강제 수정

**대상 파일들:**
- `GEMINI.md` - 현재 완전히 깨짐
- `HUB.md` - 일부 깨짐  
- 모든 `.md` 파일들
- Python 스크립트 내 한글 주석들

**방법:**
- Python `open()` 함수에 `encoding='utf-8'` 명시적 지정
- 깨진 파일들은 백업 후 새로 작성

### 4단계: 시스템 검증

**확인사항:**
1. `git status` 한글 파일명 정상 출력
2. `python -c "print('한글테스트')"` 정상 출력  
3. `invoke` 명령어 정상 작동
4. 모든 스크립트에서 `UnicodeEncodeError` 미발생

---

## ⚠️ 중요 주의사항

1. **백업 필수**: 중요해 보이는 스크립트는 `_archive/` 폴더로 이동 (삭제 말고)
2. **단계별 검증**: 각 단계 완료 후 `git status` 및 `python` 테스트
3. **즉시 보고**: 각 단계 완료 시 결과 보고
4. **실패 시 중단**: 오류 발생 시 즉시 중단하고 상황 보고

---

## 📝 예상 결과

**성공 시:**
- `scripts/` 폴더: 57개 → 10개 이하 파일
- Git 작업 정상화  
- 모든 한글 파일/출력 정상 표시
- `invoke` 명령어 정상 작동

**실패 시:**
- 현재보다 더 악화될 수 있음
- 즉시 중단하고 다른 방법 모색

---

## 🎯 최종 목표

**"더 이상 인코딩 때문에 작업을 할 수 없는 상황" 완전 해결**

이 작업은 **시스템 생존을 위한 필수 작업**입니다. 
다른 모든 작업보다 **절대 우선순위**로 처리해 주세요.

---

**이 지시사항 완료 후 즉시 결과 보고 요청**