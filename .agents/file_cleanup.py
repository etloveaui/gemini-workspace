#!/usr/bin/env python3
"""
불필요한 파일 정리 및 최적화 도구
- 임시 파일, 캐시 파일, 중복 파일 제거
- 로그 파일 정리
- 디스크 공간 최적화
"""

import os
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
import json
import hashlib

class FileCleanup:
    def __init__(self, workspace_path="."):
        self.workspace = Path(workspace_path)
        self.cleaned_files = []
        self.saved_space = 0
        
    def find_temp_files(self):
        """임시 파일 찾기"""
        temp_patterns = [
            "*.tmp", "*.temp", "*.swp", "*.swo",
            "*~", "*.bak", "*.orig", "*.cache",
            "thumbs.db", ".DS_Store", "desktop.ini"
        ]
        
        temp_files = []
        for pattern in temp_patterns:
            temp_files.extend(self.workspace.rglob(pattern))
        
        return temp_files
    
    def find_duplicate_files(self):
        """중복 파일 찾기 (해시 기반)"""
        file_hashes = {}
        duplicates = []
        
        # Python, 텍스트 파일만 검사
        for file_path in self.workspace.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix in ['.py', '.txt', '.md', '.json'] and
                file_path.stat().st_size > 100):  # 100바이트 이상만
                
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        duplicates.append((file_path, file_hashes[file_hash]))
                    else:
                        file_hashes[file_hash] = file_path
                except:
                    continue
        
        return duplicates
    
    def find_old_logs(self, days=30):
        """오래된 로그 파일 찾기"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_logs = []
        
        log_dirs = [
            self.workspace / "logs",
            self.workspace / "terminal_logs", 
            self.workspace / ".agents" / "backup"
        ]
        
        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.rglob("*"):
                    if (log_file.is_file() and 
                        datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date):
                        old_logs.append(log_file)
        
        return old_logs
    
    def find_empty_directories(self):
        """빈 디렉토리 찾기"""
        empty_dirs = []
        
        for dir_path in self.workspace.rglob("*"):
            if (dir_path.is_dir() and 
                not any(dir_path.iterdir()) and
                dir_path.name not in ['.git', '.vscode', '.agents']):
                empty_dirs.append(dir_path)
        
        return empty_dirs
    
    def find_large_files(self, size_mb=10):
        """큰 파일 찾기 (MB 단위)"""
        size_bytes = size_mb * 1024 * 1024
        large_files = []
        
        for file_path in self.workspace.rglob("*"):
            if (file_path.is_file() and 
                file_path.stat().st_size > size_bytes and
                not str(file_path).startswith(str(self.workspace / '.git'))):
                large_files.append((file_path, file_path.stat().st_size))
        
        return sorted(large_files, key=lambda x: x[1], reverse=True)
    
    def clean_pycache(self):
        """Python 캐시 파일 정리"""
        pycache_dirs = list(self.workspace.rglob("__pycache__"))
        pyc_files = list(self.workspace.rglob("*.pyc"))
        
        for cache_dir in pycache_dirs:
            if cache_dir.is_dir():
                try:
                    shutil.rmtree(cache_dir)
                    self.cleaned_files.append(str(cache_dir))
                except:
                    pass
        
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
                self.cleaned_files.append(str(pyc_file))
            except:
                pass
        
        return len(pycache_dirs) + len(pyc_files)
    
    def analyze_workspace(self):
        """워크스페이스 전체 분석"""
        analysis = {
            "temp_files": self.find_temp_files(),
            "duplicates": self.find_duplicate_files(),
            "old_logs": self.find_old_logs(),
            "empty_dirs": self.find_empty_directories(),
            "large_files": self.find_large_files(),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
    
    def clean_safe(self, dry_run=True):
        """안전한 정리 (임시 파일, 캐시만)"""
        if not dry_run:
            print("🧹 실제 정리 시작...")
        else:
            print("🔍 정리 시뮬레이션 (dry run)...")
        
        # 1. Python 캐시 정리
        pycache_count = 0 if dry_run else self.clean_pycache()
        print(f"  Python 캐시: {len(list(self.workspace.rglob('__pycache__')))} 개")
        
        # 2. 임시 파일 정리  
        temp_files = self.find_temp_files()
        print(f"  임시 파일: {len(temp_files)} 개")
        if not dry_run:
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                    self.cleaned_files.append(str(temp_file))
                except:
                    pass
        
        # 3. 빈 디렉토리 정리
        empty_dirs = self.find_empty_directories()
        print(f"  빈 디렉토리: {len(empty_dirs)} 개")
        if not dry_run:
            for empty_dir in empty_dirs:
                try:
                    empty_dir.rmdir()
                    self.cleaned_files.append(str(empty_dir))
                except:
                    pass
        
        # 4. 30일 이상 된 백업 정리
        old_backups = []
        backup_dir = self.workspace / ".agents" / "backup"
        if backup_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=30)
            for backup in backup_dir.glob("backup_*.zip"):
                if datetime.fromtimestamp(backup.stat().st_mtime) < cutoff_date:
                    old_backups.append(backup)
        
        print(f"  오래된 백업: {len(old_backups)} 개")
        if not dry_run:
            for old_backup in old_backups:
                try:
                    old_backup.unlink()
                    self.cleaned_files.append(str(old_backup))
                except:
                    pass
        
        total_cleaned = len(temp_files) + len(empty_dirs) + len(old_backups)
        if not dry_run:
            total_cleaned += pycache_count
        
        print(f"\n{'✅ 정리 완료' if not dry_run else '📋 정리 예상'}: {total_cleaned} 항목")
        
        return {
            "cleaned_count": total_cleaned,
            "temp_files": len(temp_files),
            "empty_dirs": len(empty_dirs), 
            "old_backups": len(old_backups),
            "pycache": pycache_count if not dry_run else len(list(self.workspace.rglob("__pycache__")))
        }
    
    def generate_report(self):
        """정리 보고서 생성"""
        analysis = self.analyze_workspace()
        
        report = f"""# 워크스페이스 정리 보고서
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🗂️ 파일 분석

### 임시 파일: {len(analysis['temp_files'])} 개
{chr(10).join(f"- {f}" for f in analysis['temp_files'][:10])}
{'...' if len(analysis['temp_files']) > 10 else ''}

### 중복 파일: {len(analysis['duplicates'])} 쌍
{chr(10).join(f"- {dup[0]} ↔ {dup[1]}" for dup in analysis['duplicates'][:5])}
{'...' if len(analysis['duplicates']) > 5 else ''}

### 큰 파일 (10MB+): {len(analysis['large_files'])} 개
{chr(10).join(f"- {f[0]} ({f[1]/1024/1024:.1f}MB)" for f in analysis['large_files'][:5])}
{'...' if len(analysis['large_files']) > 5 else ''}

### 오래된 로그: {len(analysis['old_logs'])} 개
{chr(10).join(f"- {f}" for f in analysis['old_logs'][:10])}
{'...' if len(analysis['old_logs']) > 10 else ''}

## 📁 빈 디렉토리: {len(analysis['empty_dirs'])} 개

## 💡 권장사항
- 임시 파일과 Python 캐시는 안전하게 삭제 가능
- 중복 파일은 수동으로 검토 후 삭제
- 큰 파일들은 필요성 검토
- 30일 이상 된 로그는 아카이브 고려
"""
        
        return report

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    cleaner = FileCleanup()
    
    if len(sys.argv) < 2:
        print("사용법: python file_cleanup.py <command>")
        print("명령어:")
        print("  analyze     - 워크스페이스 분석")
        print("  clean       - 안전한 정리 실행")
        print("  clean-dry   - 정리 시뮬레이션")
        print("  report      - 상세 보고서 생성")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        analysis = cleaner.analyze_workspace()
        print("📊 워크스페이스 분석 결과:")
        print(f"  임시 파일: {len(analysis['temp_files'])} 개")
        print(f"  중복 파일: {len(analysis['duplicates'])} 쌍") 
        print(f"  큰 파일: {len(analysis['large_files'])} 개")
        print(f"  빈 디렉토리: {len(analysis['empty_dirs'])} 개")
        print(f"  오래된 로그: {len(analysis['old_logs'])} 개")
        
    elif command == "clean-dry":
        result = cleaner.clean_safe(dry_run=True)
        
    elif command == "clean":
        result = cleaner.clean_safe(dry_run=False)
        
    elif command == "report":
        report = cleaner.generate_report()
        report_file = Path("workspace_cleanup_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 보고서 생성: {report_file}")
        
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)