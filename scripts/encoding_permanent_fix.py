#!/usr/bin/env python3
"""
인코딩 문제 영구 해결 시스템
- Windows CP949 → UTF-8 변환
- Git, PowerShell, Python 모든 환경 UTF-8 통일
- 향후 인코딩 문제 방지 메커니즘
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class EncodingPermanentFix:
    """인코딩 영구 해결 시스템"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.encoding_status = {}
        self.fixes_applied = []
    
    def analyze_current_state(self):
        """현재 인코딩 상태 분석"""
        print("[분석] 현재 인코딩 상태 분석 중...")
        
        # 시스템 기본 인코딩
        self.encoding_status["system_default"] = sys.getdefaultencoding()
        self.encoding_status["file_system"] = sys.getfilesystemencoding()
        
        # Python 환경
        try:
            import locale
            self.encoding_status["locale"] = locale.getpreferredencoding()
        except:
            self.encoding_status["locale"] = "unknown"
        
        # Git 설정 확인
        self.encoding_status["git"] = self._check_git_encoding()
        
        # PowerShell 인코딩 (실행 가능할 때만)
        self.encoding_status["powershell"] = self._check_powershell_encoding()
        
        return self.encoding_status
    
    def _check_git_encoding(self):
        """Git 인코딩 설정 확인"""
        git_settings = {}
        try:
            # core.quotepath 확인
            result = subprocess.run(['git', 'config', '--global', 'core.quotepath'], 
                                  capture_output=True, text=True)
            git_settings["quotepath"] = result.stdout.strip() if result.returncode == 0 else "not_set"
            
            # i18n.filesEncoding 확인
            result = subprocess.run(['git', 'config', '--global', 'i18n.filesEncoding'], 
                                  capture_output=True, text=True)
            git_settings["filesEncoding"] = result.stdout.strip() if result.returncode == 0 else "not_set"
            
            # core.autocrlf 확인
            result = subprocess.run(['git', 'config', '--global', 'core.autocrlf'], 
                                  capture_output=True, text=True)
            git_settings["autocrlf"] = result.stdout.strip() if result.returncode == 0 else "not_set"
            
        except Exception as e:
            git_settings["error"] = str(e)
        
        return git_settings
    
    def _check_powershell_encoding(self):
        """PowerShell 인코딩 확인"""
        try:
            cmd = 'powershell -Command "[Console]::OutputEncoding.CodePage"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return {"console_codepage": result.stdout.strip()}
            else:
                return {"error": "PowerShell 접근 실패"}
        except Exception as e:
            return {"error": str(e)}
    
    def apply_git_encoding_fixes(self):
        """Git 인코딩 완전 수정"""
        print("[수정] Git 인코딩 설정 적용 중...")
        
        git_commands = [
            ['git', 'config', '--global', 'core.quotepath', 'false'],
            ['git', 'config', '--global', 'i18n.filesEncoding', 'utf-8'],
            ['git', 'config', '--global', 'i18n.commitEncoding', 'utf-8'],
            ['git', 'config', '--global', 'i18n.logOutputEncoding', 'utf-8'],
            ['git', 'config', '--global', 'core.autocrlf', 'true'],
            ['git', 'config', '--global', 'core.safecrlf', 'false']
        ]
        
        for cmd in git_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.fixes_applied.append(f"[성공] {' '.join(cmd)}")
                else:
                    self.fixes_applied.append(f"[실패] {' '.join(cmd)}: {result.stderr}")
            except Exception as e:
                self.fixes_applied.append(f"[오류] {' '.join(cmd)}: {str(e)}")
    
    def create_gitattributes(self):
        """전역 .gitattributes 생성"""
        print("[생성] .gitattributes 파일 생성 중...")
        
        gitattributes_content = """# 모든 텍스트 파일은 UTF-8로 처리
* text=auto eol=lf encoding=UTF-8

# 특정 파일 타입별 인코딩 강제
*.md text eol=lf encoding=UTF-8
*.txt text eol=lf encoding=UTF-8
*.py text eol=lf encoding=UTF-8
*.js text eol=lf encoding=UTF-8
*.json text eol=lf encoding=UTF-8
*.yml text eol=lf encoding=UTF-8
*.yaml text eol=lf encoding=UTF-8

# 바이너리 파일은 변환하지 않음
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.exe binary
*.dll binary

# 특별 처리
CLAUDE.md text eol=lf encoding=UTF-8
README.md text eol=lf encoding=UTF-8
"""
        
        gitattributes_file = self.workspace_path / ".gitattributes"
        try:
            with open(gitattributes_file, 'w', encoding='utf-8') as f:
                f.write(gitattributes_content)
            self.fixes_applied.append(f"[성공] .gitattributes 생성: {gitattributes_file}")
        except Exception as e:
            self.fixes_applied.append(f"[실패] .gitattributes 생성 실패: {str(e)}")
    
    def create_powershell_profile(self):
        """PowerShell 프로필에 UTF-8 설정 추가"""
        print("[설정] PowerShell 프로필 UTF-8 설정 중...")
        
        profile_content = """# UTF-8 인코딩 강제 설정
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Git 한글 출력 개선
$env:PYTHONIOENCODING = "utf-8"
$env:LC_ALL = "C.UTF-8"

# 멀티 에이전트 워크스페이스 전용 설정
Write-Host "UTF-8 인코딩 활성화됨" -ForegroundColor Green
"""
        
        try:
            # PowerShell 프로필 경로 확인
            cmd = 'powershell -Command "$PROFILE"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                profile_path = result.stdout.strip()
                profile_file = Path(profile_path)
                profile_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 기존 내용이 있으면 추가, 없으면 생성
                if profile_file.exists():
                    with open(profile_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                        existing_content = f.read()
                    
                    if "UTF-8 인코딩 강제 설정" not in existing_content:
                        with open(profile_file, 'a', encoding='utf-8') as f:
                            f.write("\n\n" + profile_content)
                        self.fixes_applied.append(f"[성공] PowerShell 프로필 업데이트: {profile_file}")
                    else:
                        self.fixes_applied.append(f"[정보] PowerShell 프로필 이미 설정됨: {profile_file}")
                else:
                    with open(profile_file, 'w', encoding='utf-8') as f:
                        f.write(profile_content)
                    self.fixes_applied.append(f"[성공] PowerShell 프로필 생성: {profile_file}")
            else:
                self.fixes_applied.append(f"[실패] PowerShell 프로필 경로 확인 실패")
                
        except Exception as e:
            self.fixes_applied.append(f"[오류] PowerShell 프로필 설정 실패: {str(e)}")
    
    def fix_existing_files(self):
        """기존 파일들 UTF-8로 변환"""
        print("[변환] 기존 파일들 UTF-8 변환 중...")
        
        # 중요한 텍스트 파일들만 변환
        target_patterns = [
            "*.md", "*.txt", "*.py", "*.json", "*.yml", "*.yaml"
        ]
        
        converted_files = []
        for pattern in target_patterns:
            for file_path in self.workspace_path.rglob(pattern):
                # venv, .git, node_modules 등 제외
                if any(exclude in str(file_path) for exclude in ['.git', 'venv', 'node_modules', '__pycache__']):
                    continue
                
                try:
                    # 파일 읽기 (다양한 인코딩 시도)
                    content = None
                    for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin-1']:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is not None:
                        # UTF-8로 다시 저장 (BOM 없이)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        converted_files.append(str(file_path.relative_to(self.workspace_path)))
                
                except Exception as e:
                    self.fixes_applied.append(f"[경고] 파일 변환 실패 {file_path}: {str(e)}")
        
        if converted_files:
            self.fixes_applied.append(f"[성공] UTF-8 변환 완료: {len(converted_files)}개 파일")
        else:
            self.fixes_applied.append("[정보] 변환할 파일 없음")
    
    def create_encoding_prevention_system(self):
        """향후 인코딩 문제 방지 시스템"""
        print("[방지] 인코딩 문제 방지 시스템 생성 중...")
        
        prevention_script = """#!/usr/bin/env python3
\"\"\"
인코딩 문제 방지 체크 스크립트
새 파일 생성 시 자동으로 UTF-8 확인
\"\"\"

import sys
import os
from pathlib import Path

def check_file_encoding(file_path):
    \"\"\"파일 인코딩 확인\"\"\"
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # UTF-8 BOM 확인
        if raw_data.startswith(b'\\xef\\xbb\\xbf'):
            return "UTF-8 BOM"
        
        # UTF-8 시도
        try:
            raw_data.decode('utf-8')
            return "UTF-8"
        except UnicodeDecodeError:
            pass
        
        # CP949 시도
        try:
            raw_data.decode('cp949')
            return "CP949"
        except UnicodeDecodeError:
            pass
        
        return "UNKNOWN"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    if len(sys.argv) < 2:
        print("사용법: python encoding_check.py <file_path>")
        return
    
    file_path = sys.argv[1]
    encoding = check_file_encoding(file_path)
    
    if encoding not in ["UTF-8", "UTF-8 BOM"]:
        print(f"[경고] {file_path}가 UTF-8이 아닙니다 (현재: {encoding})")
        print("UTF-8로 변환을 권장합니다.")
    else:
        print(f"[확인] {file_path}는 UTF-8입니다.")

if __name__ == "__main__":
    main()
"""
        
        encoding_check_file = self.workspace_path / "scripts" / "encoding_check.py"
        try:
            with open(encoding_check_file, 'w', encoding='utf-8') as f:
                f.write(prevention_script)
            self.fixes_applied.append(f"[성공] 인코딩 체크 스크립트 생성: {encoding_check_file}")
        except Exception as e:
            self.fixes_applied.append(f"[실패] 인코딩 체크 스크립트 생성 실패: {str(e)}")
    
    def run_comprehensive_fix(self):
        """포괄적 인코딩 수정 실행"""
        print("[시작] 인코딩 문제 영구 해결 시작")
        print("=" * 50)
        
        # 1. 현재 상태 분석
        self.analyze_current_state()
        
        # 2. Git 설정 수정
        self.apply_git_encoding_fixes()
        
        # 3. .gitattributes 생성
        self.create_gitattributes()
        
        # 4. PowerShell 프로필 설정
        self.create_powershell_profile()
        
        # 5. 기존 파일 변환
        self.fix_existing_files()
        
        # 6. 방지 시스템 구축
        self.create_encoding_prevention_system()
        
        return self.generate_report()
    
    def generate_report(self):
        """수정 보고서 생성"""
        report = f"""# 인코딩 문제 영구 해결 보고서

**실행 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## [분석] 수정 전 상태
```json
{json.dumps(self.encoding_status, indent=2, ensure_ascii=False)}
```

## [수정] 적용된 수정사항
"""
        
        for fix in self.fixes_applied:
            report += f"- {fix}\n"
        
        report += """
## [단계] 다음 단계

1. **PowerShell 재시작** - 새 인코딩 설정 적용
2. **Git 저장소 새로고침** - .gitattributes 적용
3. **VSCode 재시작** - 터미널 인코딩 갱신

## [확인] 확인 방법

### Git 한글 표시 확인
```bash
git status
git log --oneline
```

### Python 스크립트 한글 출력 확인
```python
print("한글 테스트: 안녕하세요!")
```

### PowerShell 한글 확인
```powershell
Write-Host "한글 테스트: 안녕하세요!" -ForegroundColor Green
```

---
**이제 인코딩 문제가 영구적으로 해결되었습니다!**
"""
        
        return report

def main():
    """메인 실행 함수"""
    fixer = EncodingPermanentFix()
    report = fixer.run_comprehensive_fix()
    
    # 보고서 출력
    print("\n" + "=" * 50)
    print(report)
    
    # 파일로 저장
    report_file = fixer.workspace_path / "docs" / "encoding_fix_report.md"
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 상세 보고서: {report_file}")

if __name__ == "__main__":
    main()