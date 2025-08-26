#!/usr/bin/env python3
"""
하드코딩 방지 시스템
- 실시간 하드코딩 검사
- 파일 생성/수정 시 자동 감지
- Git commit hook 연동
- 근본적 예방 시스템
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
from pathlib import Path
from datetime import datetime
import json
import subprocess

from environment_path_manager import get_workspace_path

class HardcodingPrevention:
    def __init__(self):
        self.workspace_root = get_workspace_path()
        self.patterns = [
            # Windows 절대 경로 패턴들
            r'C:\\Users\\[^\\]+\\multi-agent-workspace',
            r'C:/Users/[^/]+/multi-agent-workspace',
            r'C:\\\\Users\\\\[^\\\\]+\\\\multi-agent-workspace',
            
            # 특정 사용자 이름 하드코딩
            r'C:\\Users\\eunta',
            r'C:/Users/eunta',
            r'C:\\\\Users\\\\eunta',
            
            # Linux 절대 경로 패턴들
            r'/home/[^/]+/multi-agent-workspace',
            r'/Users/[^/]+/multi-agent-workspace',
        ]
        
        self.allowed_extensions = {'.py', '.js', '.ts', '.json', '.md', '.txt', '.yml', '.yaml', '.bat', '.sh', '.ps1'}
        
        self.exclude_patterns = [
            '.git/',
            '__pycache__/',
            '.pytest_cache/',
            'node_modules/',
            '.vscode/',
            '.venv/',
            'venv/',
            'archive/',
            'terminal_logs/',
            '.tmp',
            '.temp'
        ]
        
    def should_scan_file(self, file_path: Path) -> bool:
        """파일 스캔 여부 결정"""
        file_str = str(file_path)
        
        # 제외 패턴 확인
        for pattern in self.exclude_patterns:
            if pattern in file_str:
                return False
        
        # 허용된 확장자 확인
        return file_path.suffix.lower() in self.allowed_extensions
    
    def scan_file_for_hardcoding(self, file_path: Path) -> list:
        """단일 파일에서 하드코딩 검사"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern in self.patterns:
                    if re.search(pattern, line):
                        violations.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern,
                            'violation_type': 'hardcoded_path'
                        })
                        
        except Exception as e:
            violations.append({
                'file': str(file_path),
                'line': 0,
                'content': f"File read error: {e}",
                'pattern': 'file_error',
                'violation_type': 'scan_error'
            })
            
        return violations
    
    def scan_workspace_for_hardcoding(self) -> dict:
        """워크스페이스 전체 하드코딩 스캔"""
        print("🔍 하드코딩 방지 시스템 - 전체 스캔 시작")
        
        all_violations = []
        scanned_files = 0
        
        for file_path in self.workspace_root.rglob('*'):
            if file_path.is_file() and self.should_scan_file(file_path):
                scanned_files += 1
                
                if scanned_files % 100 == 0:
                    print(f"  📋 스캔 중... {scanned_files}개 파일 완료")
                
                violations = self.scan_file_for_hardcoding(file_path)
                all_violations.extend(violations)
        
        # 결과 정리
        files_with_violations = len(set(v['file'] for v in all_violations if v['violation_type'] != 'scan_error'))
        scan_errors = len([v for v in all_violations if v['violation_type'] == 'scan_error'])
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_scanned_files': scanned_files,
            'files_with_violations': files_with_violations,
            'total_violations': len(all_violations),
            'scan_errors': scan_errors,
            'violations': all_violations
        }
        
        print(f"✅ 스캔 완료: {scanned_files}개 파일, {files_with_violations}개 파일에서 위반 발견")
        
        return result
    
    def create_git_pre_commit_hook(self):
        """Git pre-commit hook 생성 (하드코딩 자동 검사)"""
        git_hooks_dir = self.workspace_root / '.git' / 'hooks'
        
        if not git_hooks_dir.exists():
            print("❌ Git 저장소가 아닙니다.")
            return False
        
        hook_path = git_hooks_dir / 'pre-commit'
        
        hook_content = '''#!/usr/bin/env python3
"""
Git Pre-commit Hook - 하드코딩 자동 검사
커밋 전에 하드코딩된 경로가 있는지 자동 확인
"""
import sys
import os
from pathlib import Path

# 워크스페이스 루트로 이동
workspace_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(workspace_root / 'scripts'))

try:
    from hardcoding_prevention_system import HardcodingPrevention
    
    # staged 파일들만 검사
    import subprocess
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True, cwd=workspace_root)
    
    if result.returncode != 0:
        print("❌ Git 상태 확인 실패")
        sys.exit(1)
    
    staged_files = result.stdout.strip().split('\\n')
    staged_files = [f for f in staged_files if f.strip()]
    
    if not staged_files:
        print("✅ staged 파일 없음")
        sys.exit(0)
    
    prevention = HardcodingPrevention()
    violations_found = False
    
    print("🔍 하드코딩 검사 중...")
    for file_name in staged_files:
        file_path = workspace_root / file_name
        
        if file_path.exists() and prevention.should_scan_file(file_path):
            violations = prevention.scan_file_for_hardcoding(file_path)
            
            if violations:
                violations_found = True
                print(f"❌ {file_name}: {len(violations)}개 하드코딩 발견")
                for v in violations[:3]:  # 최대 3개만 표시
                    print(f"    Line {v['line']}: {v['content'][:80]}...")
    
    if violations_found:
        print("\\n🚨 하드코딩된 경로가 발견되었습니다!")
        print("🔧 다음 명령어로 자동 수정하세요:")
        print("   python scripts/fix_hardcoded_paths.py")
        sys.exit(1)
    else:
        print("✅ 하드코딩 검사 통과")
        sys.exit(0)
        
except ImportError:
    print("⚠️ 하드코딩 방지 시스템을 찾을 수 없습니다.")
    sys.exit(0)
except Exception as e:
    print(f"❌ 하드코딩 검사 오류: {e}")
    sys.exit(1)
'''
        
        try:
            with open(hook_path, 'w', encoding='utf-8') as f:
                f.write(hook_content)
            
            # 실행 권한 부여 (Unix/Linux)
            if os.name != 'nt':
                os.chmod(hook_path, 0o755)
            
            print(f"✅ Git pre-commit hook 생성: {hook_path}")
            return True
            
        except Exception as e:
            print(f"❌ Git hook 생성 실패: {e}")
            return False
    
    def create_monitoring_service(self):
        """하드코딩 모니터링 서비스 생성"""
        service_path = get_workspace_path("scripts", "hardcoding_monitor.py")
        
        service_content = '''#!/usr/bin/env python3
"""
하드코딩 실시간 모니터링 서비스
파일 변경 감지 시 자동으로 하드코딩 검사 수행
"""
import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 워크스페이스 경로 설정
sys.path.append(str(Path(__file__).parent))
from hardcoding_prevention_system import HardcodingPrevention
from environment_path_manager import get_workspace_path

class HardcodingWatcher(FileSystemEventHandler):
    def __init__(self):
        self.prevention = HardcodingPrevention()
        self.last_check = {}  # 파일별 마지막 검사 시간
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        if not self.prevention.should_scan_file(file_path):
            return
        
        # 너무 자주 검사하지 않기 위한 쿨다운 (5초)
        now = time.time()
        if file_path in self.last_check:
            if now - self.last_check[file_path] < 5:
                return
        
        self.last_check[file_path] = now
        
        # 하드코딩 검사
        violations = self.prevention.scan_file_for_hardcoding(file_path)
        
        if violations:
            print(f"🚨 하드코딩 발견: {file_path.name}")
            print(f"    {len(violations)}개 위반사항")
            
            # 자동 수정 시도
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, 
                    get_workspace_path("scripts", "fix_hardcoded_paths.py"),
                    str(file_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ 자동 수정 완료: {file_path.name}")
                else:
                    print(f"⚠️ 자동 수정 실패: {file_path.name}")
                    
            except Exception as e:
                print(f"❌ 자동 수정 오류: {e}")

def start_monitoring():
    """모니터링 시작"""
    workspace_root = get_workspace_path()
    
    event_handler = HardcodingWatcher()
    observer = Observer()
    observer.schedule(event_handler, str(workspace_root), recursive=True)
    
    print(f"🔍 하드코딩 실시간 모니터링 시작: {workspace_root}")
    print("📁 감시 중인 디렉터리: scripts/, communication/, docs/")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\\n⏹️  모니터링 종료")
    
    observer.join()

if __name__ == "__main__":
    start_monitoring()
'''
        
        try:
            with open(service_path, 'w', encoding='utf-8') as f:
                f.write(service_content)
            
            print(f"✅ 하드코딩 모니터링 서비스 생성: {service_path}")
            return True
            
        except Exception as e:
            print(f"❌ 모니터링 서비스 생성 실패: {e}")
            return False
    
    def install_prevention_system(self):
        """하드코딩 방지 시스템 완전 설치"""
        print("🛠️  하드코딩 방지 시스템 설치")
        print("=" * 50)
        
        results = []
        
        # 1. Git pre-commit hook 설치
        print("📋 1. Git pre-commit hook 설치...")
        if self.create_git_pre_commit_hook():
            results.append("✅ Git hook 설치 완료")
        else:
            results.append("❌ Git hook 설치 실패")
        
        # 2. 모니터링 서비스 생성
        print("📋 2. 실시간 모니터링 서비스 생성...")
        if self.create_monitoring_service():
            results.append("✅ 모니터링 서비스 생성 완료")
        else:
            results.append("❌ 모니터링 서비스 생성 실패")
        
        # 3. 현재 상태 스캔
        print("📋 3. 현재 워크스페이스 스캔...")
        scan_result = self.scan_workspace_for_hardcoding()
        
        if scan_result['files_with_violations'] == 0:
            results.append("✅ 하드코딩 없음 - 클린 상태")
        else:
            results.append(f"⚠️  {scan_result['files_with_violations']}개 파일에서 하드코딩 발견")
        
        # 결과 요약
        print("=" * 50)
        print("📊 설치 결과:")
        for result in results:
            print(f"  {result}")
        
        if scan_result['files_with_violations'] > 0:
            print("\\n🔧 하드코딩 자동 수정:")
            print("   python scripts/fix_hardcoded_paths.py")
        
        print("\\n🚀 사용법:")
        print("   python scripts/hardcoding_monitor.py  # 실시간 모니터링 시작")
        
        return results

def main():
    import sys
    
    prevention = HardcodingPrevention()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--scan":
            prevention.scan_workspace_for_hardcoding()
        elif command == "--install":
            prevention.install_prevention_system()
        elif command == "--git-hook":
            prevention.create_git_pre_commit_hook()
        elif command == "--monitor":
            prevention.create_monitoring_service()
        else:
            print(f"알 수 없는 명령어: {command}")
    else:
        # 기본: 전체 설치
        prevention.install_prevention_system()

if __name__ == "__main__":
    main()