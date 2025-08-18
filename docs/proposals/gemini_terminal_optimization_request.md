# Gemini CLI VSCode 터미널 환경 최적화 지시서

**작성자**: Claude  
**작성일**: 2025-08-18  
**대상**: Gemini CLI  
**우선순위**: 중요 (P1)

## 📋 조사 및 최적화 요청 개요

VSCode PowerShell 7 터미널 환경에서 발생하는 다음 문제들을 조사하고 해결 방안을 제시해주세요:

## 🔍 구체적 조사 및 해결 항목

### 1. 터미널 새 창 글씨 문제 🖥️
- **문제 설명**: 터미널을 새 창으로 열었을 때 글씨가 안 보이는 현상
- **조사 대상**:
  - [ ] VSCode 터미널 폰트 설정
  - [ ] PowerShell 7 폰트 및 색상 설정
  - [ ] Windows Terminal vs VSCode 통합 터미널 차이점
  - [ ] 다중 모니터 환경에서의 DPI 스케일링 문제

### 2. Codex 스크롤 문제 📜
- **문제 설명**: Codex가 긴 출력을 생성할 때 스크롤 넘어가면 내용이 삭제됨
- **조사 대상**:
  - [ ] PowerShell 버퍼 크기 설정
  - [ ] VSCode 터미널 스크롤백 설정
  - [ ] Codex 출력 방식 문제점 분석
  - [ ] 대용량 출력 처리 방법

### 3. 환경별 일관성 확보 🌐
- **목표**: 집, 회사, 노트북에서 동일한 터미널 환경
- **조사 대상**:
  - [ ] VSCode 설정 동기화 방법
  - [ ] PowerShell 프로필 표준화
  - [ ] 폰트 및 테마 통합 관리
  - [ ] 환경 변수 및 PATH 설정 통일

### 4. UTF-8 인코딩 완전 적용 🔤
- **목표**: 모든 터미널 환경에서 UTF-8 완전 지원
- **조사 대상**:
  - [ ] PowerShell $OutputEncoding 영구 설정
  - [ ] VSCode 터미널 인코딩 설정
  - [ ] 콘솔 앱 기본 인코딩 설정
  - [ ] 시스템 로케일 vs 터미널 인코딩

## 🛠️ 권장 조사 방법

### 현재 환경 진단
```powershell
# PowerShell 환경 정보
$PSVersionTable
$OutputEncoding
[Console]::OutputEncoding
Get-Host | Select-Object Name, Version

# VSCode 터미널 설정 확인
code --list-extensions | grep -i terminal
```

### 폰트 및 색상 검사
```powershell
# 현재 콘솔 설정
[Console]::WindowWidth
[Console]::WindowHeight
[Console]::BufferWidth
[Console]::BufferHeight

# 색상 테스트
Write-Host "Color Test: " -NoNewline
Write-Host "Red" -ForegroundColor Red -NoNewline
Write-Host " Green" -ForegroundColor Green -NoNewline  
Write-Host " Blue" -ForegroundColor Blue
```

### 다중 환경 설정 점검
- 홈 PC, 회사 PC, 노트북에서 각각 동일한 진단 실행
- 차이점 문서화

## 📊 결과 보고 형식

```markdown
# VSCode 터미널 환경 최적화 보고서

## 문제 원인 분석
### 1. 새 창 글씨 문제
- 원인: [구체적 원인]
- 영향 범위: [어떤 상황에서 발생]

### 2. 스크롤 문제  
- 원인: [구체적 원인]
- 재현 조건: [문제 재현 방법]

### 3. 환경 불일치
- 차이점: [환경별 차이점 목록]
- 주요 원인: [불일치 원인]

## 해결 방안
### 즉시 적용 가능한 해결책
1. [VSCode 설정 수정 방법]
2. [PowerShell 프로필 설정]
3. [폰트 및 색상 최적화]

### 환경 통합 방안
1. [설정 파일 동기화 방법]
2. [표준 설정 템플릿]
3. [자동 환경 구성 스크립트]

### 예방 조치
1. [정기 점검 항목]
2. [설정 백업 방법]

## 다음 단계
- Claude에게 전달할 구체적 설정 파일
- 적용 순서 및 주의사항
```

## ⏰ 예상 소요 시간
약 20-30분 내외로 조사 및 해결 방안 도출 예상

## 📝 특별 요청사항

1. **실용적 해결책**: 이론보다는 즉시 적용 가능한 실용적 방법 우선
2. **설정 파일 제공**: 권장 설정을 복사-붙여넣기 가능한 형태로 제공
3. **자동화 스크립트**: 가능하면 환경 설정 자동화 스크립트도 포함
4. **호환성 검증**: Windows 10/11, VSCode 최신 버전에서 검증된 방법

## 🎯 성공 기준

- [ ] 모든 환경에서 터미널 글씨가 정상 표시
- [ ] Codex 긴 출력도 스크롤로 확인 가능
- [ ] 집/회사/노트북 환경이 동일하게 동작
- [ ] UTF-8 인코딩이 완벽하게 지원
- [ ] 설정 적용이 5분 이내 완료 가능

---
**이 지시서는 Claude Code에 의해 생성되었습니다.**