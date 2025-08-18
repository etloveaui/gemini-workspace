# Gemini CLI 인코딩 조사 지시서

**작성자**: Claude  
**작성일**: 2025-08-18  
**대상**: Gemini CLI  
**우선순위**: 긴급 (P0)

## 📋 조사 요청 개요

현재 Multi-Agent Workspace에서 심각한 인코딩 문제가 발생하고 있습니다. Codex가 수정한 파일들의 인코딩이 계속 깨지고, 사용자가 Git UI로 커밋할 때도 인코딩 오류가 발생합니다.

## 🔍 구체적 조사 항목

### 1. 시스템 인코딩 현황 조사
- [ ] 현재 Windows 시스템 기본 인코딩 확인 (이미 확인됨: CP949/EUC-KR)
- [ ] PowerShell 7 인코딩 설정 상태
- [ ] VSCode 터미널 인코딩 설정
- [ ] Git 글로벌 인코딩 설정 (`core.autocrlf`, `core.safecrlf` 등)

### 2. 파일별 인코딩 상태 점검
다음 파일들의 실제 인코딩을 확인해주세요:
- [ ] `docs/HUB.md` (한글 깨짐 확인됨)
- [ ] `AGENTS.md`
- [ ] `GEMINI.md` 
- [ ] `CLAUDE.md`
- [ ] `.agents/config.json`
- [ ] 최근 Codex가 수정한 파일들

### 3. Codex 파일 수정 패턴 분석
- [ ] Codex가 파일을 수정할 때 사용하는 인코딩 방식
- [ ] 어떤 상황에서 인코딩이 깨지는지 패턴 파악
- [ ] Codex의 파일 저장 방식 (UTF-8 BOM 여부 등)

### 4. Git 커밋 시 인코딩 문제
- [ ] 사용자가 SourceTree나 Git UI 사용 시 인코딩 충돌 원인
- [ ] pre-commit hook에서 인코딩 검사 여부
- [ ] Git 저장소의 `.gitattributes` 설정 확인

## 🛠️ 권장 조사 방법

### 명령어 예시
```bash
# 파일 인코딩 확인
file -bi docs/HUB.md

# Git 설정 확인  
git config --list | grep -i encoding
git config --list | grep -i autocrlf

# PowerShell 인코딩 확인
$OutputEncoding
[System.Text.Encoding]::Default

# 파일별 인코딩 상세 분석
Get-Content docs/HUB.md -Encoding UTF8 | Out-String | Format-Hex
```

### 도구 활용
- `invoke doctor` 실행하여 환경 진단
- `file` 명령어로 파일 인코딩 직접 확인
- PowerShell의 `Get-FileEncoding` 함수 활용 (있다면)

## 📊 결과 보고 형식

조사 완료 후 다음 형식으로 보고해주세요:

```markdown
# 인코딩 조사 결과 보고서

## 문제 원인
- 주요 원인: [구체적 원인]
- 부차적 요인: [추가 요인들]

## 현재 상태
- 시스템 기본 인코딩: [확인된 설정]
- 문제 파일 목록: [깨진 파일들]
- Git 설정 상태: [현재 Git 인코딩 설정]

## 권장 해결책
1. 즉시 적용 가능한 해결책
2. 중장기 개선 방안
3. 예방 조치

## 다음 단계
- Claude에게 전달할 구체적 수정 지시사항
```

## ⏰ 예상 소요 시간
약 15-20분 내외로 조사 완료 예상

## 📝 참고사항
- 이 조사는 Claude의 시스템 개선 작업의 첫 단계입니다
- 조사 결과를 바탕으로 Claude가 구체적인 수정 작업을 진행할 예정입니다
- 긴급성이 높으므로 우선적으로 처리해주시기 바랍니다

---
**이 지시서는 Claude Code에 의해 생성되었습니다.**