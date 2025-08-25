# Codex용 시스템 정리 지시사항

**작성일**: 2025-08-18  
**작성자**: Claude Code  
**대상 에이전트**: Codex  
**작업 우선순위**: 최고 (시스템 안정화)  

---

## 📋 승인된 시스템 정리 작업 목록

사용자로부터 다음 작업들이 **승인**되었습니다:

### 1. 🗂️ claude_code 폴더 삭제
- **위치**: `C:\Users\eunta\multi-agent-workspace\claude_code\`
- **이유**: 불필요한 중복 폴더로 시스템 혼란 야기
- **방법**: Python `shutil.rmtree()` 사용 권장 (Windows 안정성)

### 2. ⚙️ .agents/config.json 설정 수정
- **파일 위치**: `.agents/config.json`
- **수정 내용**: 
  - `active` 에이전트를 `codex`로 고정
  - 불필요한 설정 제거 및 정리
- **목적**: 에이전트 설정 일관성 확보

### 3. 📦 config.json 백업 및 보관
- **대상**: 루트 디렉터리의 `config.json` 파일들
- **작업**: `archives/configs/` 디렉터리로 이동
- **백업명**: `config_backup_20250818.json` 형식

### 4. 🧹 *.bak 파일 정리
- **대상**: 모든 `.bak` 확장자 파일
- **스캔 범위**: 전체 워크스페이스
- **작업**: 불필요한 백업 파일 삭제 (중요 파일은 확인 후)

---

## 🔧 구체적 실행 방법

### Python 삭제 스크립트 예시:
```python
import os
import shutil
from pathlib import Path

# 1. claude_code 폴더 삭제
claude_code_path = Path("C:/Users/eunta/multi-agent-workspace/claude_code")
if claude_code_path.exists():
    try:
        shutil.rmtree(claude_code_path)
        print(f"[성공] {claude_code_path} 삭제 완료")
    except Exception as e:
        print(f"[오류] 삭제 실패: {e}")

# 2. *.bak 파일 스캔 및 정리
workspace = Path("C:/Users/eunta/multi-agent-workspace")
bak_files = list(workspace.glob("**/*.bak"))
for bak_file in bak_files:
    print(f"백업 파일 발견: {bak_file}")
    # 필요시 삭제: bak_file.unlink()
```

### .agents/config.json 수정:
```json
{
  "active": "codex",
  "last_update": "2025-08-18T17:30:00Z",
  "cleanup_completed": true
}
```

---

## ⚠️ 중요 주의사항

1. **안전한 삭제**: 삭제 전 해당 디렉터리/파일이 정말 불필요한지 재확인
2. **백업 우선**: 중요해 보이는 설정 파일은 삭제 전 백업
3. **로그 기록**: 모든 작업 내용을 상세히 기록
4. **단계별 확인**: 각 작업 완료 후 사용자에게 보고

---

## 📝 완료 보고 형식

각 작업 완료 시 다음 형식으로 보고해 주세요:

```
[완료] 작업명: 구체적 결과
- 삭제된 파일/폴더: 경로와 크기
- 수정된 설정: 변경 내용 요약  
- 발견된 문제: 있다면 기록
```

---

**이 지시사항은 사용자의 명시적 승인을 받았으며, 시스템 안정화를 위한 최우선 작업입니다.**