# 🚨 URGENT: Codex 인코딩 대량 복구 작업 지시서

## 📋 작업 개요
**목표**: d4f6efe 커밋에서 깨진 520여개 파일의 인코딩을 Git 히스토리를 통해 일괄 복구

**작업 방식**: 별도 브랜치에서 작업 → Claude 검토 → main 머지

## 🎯 문제 상황 정확한 이해

### 원인 분석
1. **d4f6efe 커밋**에서 `scripts/encoding_permanent_fix.py` 스크립트가 520개 파일을 "CP949→UTF-8 변환"한다며 실제로는 **정상 파일들을 깨뜨림**
2. **정상 한글**: "시스템에서 작업" → **깨진 문자**: "?쒖뒪?쒖뿉???묒뾽"
3. **정상 상태 커밋**: 26bb83d (2025-08-15) - 대부분 파일이 정상이었던 시점

### 이미 해결된 부분 (Claude 완료)
- ✅ 문제 스크립트 완전 제거
- ✅ pre-commit 훅 비활성화  
- ✅ GEMINI.md, CLAUDE.md 복구 완료
- ✅ 근본 원인 커밋 완료 (3b58b47)

## 🔧 Codex 수행 작업

### STEP 1: 브랜치 생성 및 작업 환경 준비
```bash
# 새 브랜치 생성
git checkout -b encoding-bulk-recovery

# 작업 디렉토리 확인  
pwd  # C:\Users\eunta\multi-agent-workspace 인지 확인

# 현재 브랜치 확인
git branch
```

### STEP 2: 깨진 파일들 전체 식별
```bash
# 한글 깨진 패턴으로 파일 검색
grep -r "?쒖뒪?쒖뿉\|硫붿씤 泥댁젣\|筌ㅼ뮇\|獄?\|揶쏆뮇\|餓?" . --include="*.md" --include="*.py" --include="*.txt" --include="*.json" | cut -d: -f1 | sort -u > damaged_files_list.txt

# 검색된 파일 개수 확인
wc -l damaged_files_list.txt

# 검색 결과 확인 (처음 20개)  
head -20 damaged_files_list.txt
```

### STEP 3: Git 히스토리에서 정상 버전 확인
각 깨진 파일에 대해 언제부터 정상이었는지 확인:
```bash
# 주요 확인 포인트 커밋들
echo "확인할 커밋 포인트들:"
echo "26bb83d - 2025-08-15 (대부분 정상)"  
echo "95dd94b - 2025-08-15 (인코딩 하드닝 이전)"
echo "69400fa - CLAUDE.md 정상 버전"

# 샘플 파일로 테스트
git show 26bb83d:GEMINI.md | head -5
git show 26bb83d:docs/CORE/HUB_ENHANCED.md | head -5
```

### STEP 4: 자동 복구 스크립트 생성
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대량 인코딩 복구 스크립트
Git 히스토리에서 정상 버전을 가져와 현재 깨진 파일들을 복구
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, capture=True):
    """안전한 명령어 실행"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            result = subprocess.run(cmd, shell=True, encoding='utf-8')
            return "", "", result.returncode
    except Exception as e:
        print(f"명령어 실행 오류: {cmd}")
        print(f"오류 내용: {e}")
        return "", str(e), 1

def check_file_in_commit(file_path, commit_hash):
    """특정 커밋에서 파일이 존재하고 정상인지 확인"""
    cmd = f'git show {commit_hash}:"{file_path}"'
    stdout, stderr, returncode = run_command(cmd)
    
    if returncode != 0:
        return False, f"파일이 해당 커밋에 없음: {stderr}"
        
    # 깨진 문자 패턴 확인
    broken_patterns = ["?쒖뒪?쒖뿉", "硫붿씤 泥댁젣", "筌ㅼ뮇", "獄?", "揶쏆뮇", "餓?"]
    for pattern in broken_patterns:
        if pattern in stdout:
            return False, f"해당 커밋에서도 파일이 깨져있음"
    
    return True, "정상"

def restore_file_from_commit(file_path, commit_hash):
    """Git 히스토리에서 파일 복구"""
    # 임시 파일로 복구
    temp_file = f"{file_path}.recovered"
    cmd = f'git show {commit_hash}:"{file_path}" > "{temp_file}"'
    
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        print(f"❌ 복구 실패: {file_path} from {commit_hash}")
        print(f"   오류: {stderr}")
        return False
        
    # 원본 파일 교체
    try:
        if os.path.exists(temp_file):
            os.replace(temp_file, file_path)
            print(f"✅ 복구 완료: {file_path}")
            return True
        else:
            print(f"❌ 임시 파일 생성 실패: {temp_file}")
            return False
    except Exception as e:
        print(f"❌ 파일 교체 실패: {file_path}")
        print(f"   오류: {e}")
        return False

def main():
    # 깨진 파일 목록 읽기
    if not os.path.exists("damaged_files_list.txt"):
        print("❌ damaged_files_list.txt 파일이 없습니다.")
        return
        
    with open("damaged_files_list.txt", 'r', encoding='utf-8') as f:
        damaged_files = [line.strip() for line in f if line.strip()]
    
    print(f"📋 총 {len(damaged_files)}개 파일 복구 시작")
    
    # 복구 시도할 커밋 순서 (최신부터 과거로)
    commit_candidates = [
        "26bb83d",  # 대부분 정상
        "95dd94b",  # 인코딩 하드닝 이전  
        "69400fa",  # Claude 통합 시점
        "6fa2776",  # 더 이전 버전
    ]
    
    success_count = 0
    failed_files = []
    
    for file_path in damaged_files:
        # 현재 워크스페이스 기준 상대경로로 변환
        if file_path.startswith("C:\\Users\\etlov\\multi-agent-workspace\\"):
            relative_path = file_path[35:].replace("\\", "/")
        else:
            relative_path = file_path.replace("\\", "/")
            
        print(f"\n🔄 복구 중: {relative_path}")
        
        recovered = False
        for commit in commit_candidates:
            is_normal, message = check_file_in_commit(relative_path, commit)
            if is_normal:
                if restore_file_from_commit(relative_path, commit):
                    print(f"   📍 복구 소스: {commit}")
                    recovered = True
                    success_count += 1
                    break
                    
        if not recovered:
            print(f"❌ 복구 실패: {relative_path}")
            failed_files.append(relative_path)
    
    # 결과 리포트
    print(f"\n📊 복구 결과:")
    print(f"   ✅ 성공: {success_count}개")
    print(f"   ❌ 실패: {len(failed_files)}개")
    
    if failed_files:
        print(f"\n❌ 복구 실패 파일들:")
        for failed_file in failed_files[:10]:  # 처음 10개만 표시
            print(f"   - {failed_file}")
        if len(failed_files) > 10:
            print(f"   ... 및 {len(failed_files) - 10}개 더")
    
    # 복구 완료된 파일들을 Git에 스테이징
    if success_count > 0:
        print(f"\n📝 Git 스테이징 중...")
        cmd = "git add ."
        stdout, stderr, returncode = run_command(cmd, False)
        if returncode == 0:
            print("✅ Git 스테이징 완료")
        else:
            print(f"❌ Git 스테이징 실패: {stderr}")

if __name__ == "__main__":
    main()
```

### STEP 5: 복구 스크립트 실행
```bash
# 복구 스크립트 저장
cat > bulk_recovery.py << 'EOF'
[위의 Python 스크립트 내용 전체 붙여넣기]
EOF

# 실행 권한 부여 및 실행
python bulk_recovery.py

# 결과 확인
git status
git diff --name-only
```

### STEP 6: 복구 결과 검증
```bash
# 주요 파일들이 정상 복구되었는지 확인
echo "=== GEMINI.md 확인 ==="
head -5 GEMINI.md

echo "=== HUB_ENHANCED.md 확인 ==="  
head -5 docs/CORE/HUB_ENHANCED.md

echo "=== 깨진 패턴 잔존 확인 ==="
grep -r "?쒖뒪?쒖뿉\|硫붿씤 泥댁젣" . --include="*.md" --include="*.py" | head -5

# 복구 통계
echo "=== 복구된 파일 개수 ==="
git diff --name-only | wc -l
```

### STEP 7: 커밋 및 푸시
```bash
# 커밋 메시지 작성
cat > COMMIT_MSG.tmp << 'EOF'
fix(encoding): Git 히스토리를 통한 520개 파일 대량 인코딩 복구

- d4f6efe 커밋에서 깨진 파일들을 Git 히스토리에서 복구
- 복구 소스: 26bb83d, 95dd94b, 69400fa 등 정상 상태 커밋
- 정상 한글 복원: "?쒖뒪?쒖뿉???묒뾽" → "시스템에서 작업"
- encoding_permanent_fix.py 피해 완전 복구

🤖 Generated with Codex
🔄 브랜치: encoding-bulk-recovery → Claude 검토 후 main 머지 예정

Co-Authored-By: Codex <noreply@anthropic.com>
EOF

# 커밋 실행
git commit -F COMMIT_MSG.tmp
rm COMMIT_MSG.tmp

# 브랜치 푸시
git push -u origin encoding-bulk-recovery
```

## 🔍 Claude 검토 대기 메시지

복구 완료 후 다음 메시지를 남겨주세요:

```markdown
## 📋 Codex 대량 인코딩 복구 완료 보고

### 작업 결과
- 📦 **브랜치**: `encoding-bulk-recovery`
- 🔢 **복구 파일 수**: XXX개 (총 520개 중)
- ✅ **성공률**: XX%
- ❌ **실패 파일**: XX개

### 검증 완료 항목
- [ ] GEMINI.md 정상 한글 표시 확인
- [ ] HUB_ENHANCED.md 정상 한글 표시 확인  
- [ ] 깨진 패턴 (?쒖뒪?쒖뿉 등) 잔존 여부 확인
- [ ] Git diff 결과 검토
- [ ] 주요 Python/Markdown 파일 샘플링 검토

### 다음 단계
**Claude님, 검토 후 문제없으면 main 브랜치 머지 승인 부탁드립니다.**

브랜치 확인 명령어:
git checkout encoding-bulk-recovery
git log --oneline -3
git diff main..encoding-bulk-recovery --name-only
```

## ⚠️ 중요 주의사항

1. **절대 main 브랜치에서 직접 작업하지 말 것**
2. **각 단계마다 결과를 확인하고 다음 진행**
3. **복구 실패 시 원본 파일 백업 있는지 확인**
4. **Git 상태를 수시로 확인하여 예상치 못한 변경 방지**
5. **520개 파일 중 일부만 복구되어도 성공으로 간주**

## 🎯 성공 기준

- **80% 이상 파일 복구 성공**
- **주요 문서 파일들 (*.md) 정상 한글 표시**  
- **깨진 문자 패턴 95% 이상 제거**
- **Git 히스토리 손상 없음**

---
**작업 완료 후 Claude 검토 → main 머지 → 인코딩 문제 완전 해결**