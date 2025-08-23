#!/usr/bin/env python3
"""
PowerShell 프로필 문제 수정 및 GitHub Desktop 커밋 문제 해결
"""
import os
import shutil
from pathlib import Path

def fix_powershell_profile():
    """
    손상된 PowerShell 프로필을 수정하고 올바른 UTF-8 설정 적용
    """
    print("[시작] PowerShell 프로필 문제 수정 중...")
    
    # PowerShell 프로필 경로들
    profile_paths = [
        Path(os.path.expandvars(r"%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1")),
        Path(os.path.expandvars(r"%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1")),
        Path(os.path.expandvars(r"D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"))
    ]
    
    # 올바른 UTF-8 설정
    correct_profile_content = """# Claude Code 최적화 PowerShell 프로필
# UTF-8 인코딩 영구 설정

try {
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    
    # 코드페이지 UTF-8로 설정 (조용히)
    chcp 65001 > $null 2>&1
} catch {
    # 오류 발생시 조용히 넘어감
}

# Claude Code 작업 디렉토리 단축키
function goto-workspace {
    Set-Location "C:\\Users\\etlov\\multi-agent-workspace"
}
Set-Alias -Name cw -Value goto-workspace
"""
    
    fixed_count = 0
    
    for profile_path in profile_paths:
        if profile_path.exists():
            try:
                # 백업 생성
                backup_path = profile_path.with_suffix('.ps1.backup')
                shutil.copy2(profile_path, backup_path)
                print(f"[백업] {profile_path} -> {backup_path}")
                
                # 새로운 올바른 내용으로 교체
                with open(profile_path, 'w', encoding='utf-8') as f:
                    f.write(correct_profile_content)
                
                print(f"[수정] {profile_path} 프로필 수정 완료")
                fixed_count += 1
                
            except Exception as e:
                print(f"[오류] {profile_path} 수정 실패: {e}")
    
    print(f"[완료] {fixed_count}개 PowerShell 프로필 수정 완료")
    return fixed_count > 0

def fix_github_desktop_commit():
    """
    GitHub Desktop 커밋 문제 해결 - Git 설정 최적화
    """
    print("\n[시작] GitHub Desktop 커밋 문제 해결 중...")
    
    workspace_path = Path(__file__).parent.parent
    os.chdir(workspace_path)
    
    # Git 설정 최적화 명령어들
    git_commands = [
        'git config core.autocrlf true',
        'git config core.filemode false', 
        'git config core.ignorecase true',
        'git config core.precomposeunicode true',
        'git config core.quotepath false',
        'git config i18n.commitencoding utf-8',
        'git config i18n.logoutputencoding utf-8',
        'git config gui.encoding utf-8'
    ]
    
    success_count = 0
    
    for cmd in git_commands:
        try:
            result = os.system(cmd)
            if result == 0:
                success_count += 1
                print(f"[설정] {cmd}")
            else:
                print(f"[실패] {cmd}")
        except Exception as e:
            print(f"[오류] {cmd} - {e}")
    
    # GitHub Desktop용 커밋 스크립트 생성
    commit_script = workspace_path / "scripts" / "github_desktop_helper.bat"
    
    commit_script_content = """@echo off
chcp 65001 > nul
echo GitHub Desktop 커밋 도우미
echo ========================

REM UTF-8 환경 설정
set PYTHONIOENCODING=utf-8

REM 작업 디렉토리로 이동
cd /d "%~dp0\\.."

REM Git 상태 확인
echo [상태 확인]
git status

echo.
echo [설정 확인]
git config --list | findstr encoding
git config --list | findstr autocrlf

echo.
echo 이제 GitHub Desktop에서 커밋을 진행할 수 있습니다.
echo 만약 여전히 문제가 있다면 관리자 권한으로 실행하세요.

pause
"""
    
    with open(commit_script, 'w', encoding='utf-8') as f:
        f.write(commit_script_content)
    
    print(f"[생성] GitHub Desktop 도우미 스크립트: {commit_script}")
    print(f"[완료] {success_count}개 Git 설정 적용 완료")
    
    return commit_script

def main():
    """메인 실행 함수"""
    print("=== PowerShell & GitHub Desktop 문제 해결 ===")
    print("=" * 50)
    
    # 1. PowerShell 프로필 수정
    ps_fixed = fix_powershell_profile()
    
    # 2. GitHub Desktop 커밋 문제 해결
    commit_script = fix_github_desktop_commit()
    
    print("\n" + "=" * 50)
    print("해결 완료!")
    print("\n다음 단계:")
    if ps_fixed:
        print("1. PowerShell을 다시 시작하세요 (인코딩 문제 해결됨)")
    print("2. GitHub Desktop 사용 전 다음 스크립트를 실행하세요:")
    print(f"   {commit_script}")
    print("3. 이제 집에서도 정상적으로 커밋할 수 있습니다!")

if __name__ == "__main__":
    main()