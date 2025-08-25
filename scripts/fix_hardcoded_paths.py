#!/usr/bin/env python3
"""
하드코딩된 경로 일괄 수정 도구
모든 파일에서 C:\\Users\\eunta 등의 하드코딩된 경로를 동적 경로로 교체
"""
import os
import re
from pathlib import Path
from typing import List, Dict
import json

class PathFixer:
    def __init__(self):
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.current_user = os.environ.get('USERNAME') or os.environ.get('USER')
        
        # 수정할 패턴들 (간단한 문자열 교체 방식)
        self.replacements = [
            # Windows 패턴들
            (r'C:\Users\eunta\multi-agent-workspace', str(self.workspace_root)),
            (r'C:\Users\eunta\multi-agent-workspace', str(self.workspace_root)),
            ('C:/Users/eunta/multi-agent-workspace', str(self.workspace_root).replace('\\', '/')),
            ('C:/Users/eunta/multi-agent-workspace', str(self.workspace_root).replace('\\', '/')),
        ]
        
        # 수정 결과 저장
        self.fixed_files = []
        self.skipped_files = []
        self.errors = []
    
    def should_process_file(self, file_path: Path) -> bool:
        """파일 처리 여부 결정"""
        # 제외할 파일들
        exclude_patterns = [
            '.git/',
            '__pycache__/',
            '.pytest_cache/',
            'node_modules/',
            '.vscode/',
            '.venv/',
            'venv/',
            '.tmp',
            '.temp'
        ]
        
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if pattern in file_str:
                return False
                
        # 처리할 확장자들
        allowed_extensions = {'.py', '.json', '.md', '.txt', '.yml', '.yaml', '.bat', '.sh', '.ps1'}
        return file_path.suffix.lower() in allowed_extensions
    
    def fix_file(self, file_path: Path) -> bool:
        """단일 파일의 하드코딩된 경로 수정"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"읽기 실패 {file_path}: {e}")
            return False
        
        original_content = content
        modified = False
        
        # 패턴별로 교체 (문자열 교체 방식)
        for old_text, new_text in self.replacements:
            if old_text in content:
                content = content.replace(old_text, new_text)
                modified = True
        
        # 변경사항이 있으면 파일 저장
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                return True
            except Exception as e:
                self.errors.append(f"쓰기 실패 {file_path}: {e}")
                return False
        
        return False
    
    def scan_and_fix_directory(self, directory: Path = None) -> Dict:
        """디렉터리 내 모든 파일의 하드코딩 경로 수정"""
        if directory is None:
            directory = self.workspace_root
        
        print(f"스캔 시작: {directory}")
        
        processed_files = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                processed_files += 1
                
                if processed_files % 50 == 0:
                    print(f"처리 중... {processed_files}개 파일 완료")
                
                if self.fix_file(file_path):
                    print(f"수정됨: {file_path}")
                else:
                    self.skipped_files.append(str(file_path))
        
        return {
            "fixed_count": len(self.fixed_files),
            "skipped_count": len(self.skipped_files),  
            "error_count": len(self.errors),
            "total_processed": processed_files
        }
    
    def get_summary(self) -> Dict:
        """수정 결과 요약"""
        return {
            "summary": {
                "fixed_files": len(self.fixed_files),
                "errors": len(self.errors),
                "total_files_checked": len(self.fixed_files) + len(self.skipped_files)
            },
            "fixed_files": self.fixed_files[:10],  # 처음 10개만 표시
            "errors": self.errors[:5]  # 처음 5개 에러만 표시
        }

def main():
    import sys
    
    print("=== 하드코딩된 경로 일괄 수정 도구 ===")
    
    fixer = PathFixer()
    print(f"현재 사용자: {fixer.current_user}")
    print(f"워크스페이스: {fixer.workspace_root}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("\n[DRY RUN] 모드 - 파일을 실제로 수정하지 않습니다")
        # dry-run 로직 구현 가능
        return
    
    # 실제 수정 실행
    print("\n[START] 하드코딩된 경로 수정 시작...")
    
    results = fixer.scan_and_fix_directory()
    summary = fixer.get_summary()
    
    print(f"\n[SUCCESS] 수정 완료!")
    print(f"- 수정된 파일: {results['fixed_count']}개")
    print(f"- 에러 발생: {results['error_count']}개") 
    print(f"- 전체 처리: {results['total_processed']}개")
    
    if summary["fixed_files"]:
        print(f"\n[FILES] 수정된 파일들 (일부):")
        for file_path in summary["fixed_files"]:
            print(f"  - {file_path}")
    
    if summary["errors"]:
        print(f"\n[ERRORS] 에러 발생 파일들:")
        for error in summary["errors"]:
            print(f"  - {error}")

if __name__ == "__main__":
    main()