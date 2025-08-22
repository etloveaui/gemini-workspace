#!/usr/bin/env python3
"""
스마트 파일 정리 시스템
- 자동 중복 파일 탐지 및 제거
- 임시 파일 정리
- 프로젝트 구조 최적화
- 아카이브 관리
"""

import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

class FileOrganizer:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        log_dir = self.workspace_path / '.agents' / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / 'file_organizer.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        config_file = self.workspace_path / '.agents' / 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
    def get_file_hash(self, file_path):
        """파일의 MD5 해시값 계산"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Hash calculation failed for {file_path}: {e}")
            return None
            
    def find_duplicate_files(self):
        """중복 파일 탐지"""
        file_hashes = {}
        duplicates = []
        
        # 제외할 디렉토리
        exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules', 
                       '.agents/backup', 'archive'}
        
        for root, dirs, files in os.walk(self.workspace_path):
            # 제외 디렉토리 건너뛰기
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in ['.py', '.md', '.json', '.txt', '.js']:
                    file_hash = self.get_file_hash(file_path)
                    if file_hash:
                        if file_hash in file_hashes:
                            duplicates.append((file_path, file_hashes[file_hash]))
                        else:
                            file_hashes[file_hash] = file_path
                            
        return duplicates
    
    def clean_temp_files(self):
        """임시 파일 정리"""
        temp_patterns = [
            '*.tmp', '*.temp', '*.log~', '*.bak', 
            'nul', '*.pyc', '__pycache__'
        ]
        
        cleaned_files = []
        
        for pattern in temp_patterns:
            for file_path in self.workspace_path.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                    elif file_path.is_dir() and pattern == '__pycache__':
                        shutil.rmtree(file_path)
                        cleaned_files.append(str(file_path))
                except Exception as e:
                    self.logger.error(f"Failed to remove {file_path}: {e}")
                    
        return cleaned_files
    
    def organize_communication_files(self):
        """communication 폴더 자동 정리"""
        comm_dir = self.workspace_path / 'communication'
        if not comm_dir.exists():
            return
            
        # 7일 이상 된 세션 파일들 아카이브
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for agent_dir in ['claude', 'gemini', 'codex']:
            agent_path = comm_dir / agent_dir
            if agent_path.exists():
                for md_file in agent_path.glob('*.md'):
                    try:
                        file_time = datetime.fromtimestamp(md_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            # 아카이브로 이동
                            archive_dir = self.workspace_path / 'archive' / 'communication' / agent_dir
                            archive_dir.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(md_file), archive_dir / md_file.name)
                            self.logger.info(f"Archived: {md_file}")
                    except Exception as e:
                        self.logger.error(f"Failed to archive {md_file}: {e}")
    
    def generate_cleanup_report(self):
        """정리 보고서 생성"""
        duplicates = self.find_duplicate_files()
        temp_files = self.clean_temp_files()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'duplicates_found': len(duplicates),
            'temp_files_cleaned': len(temp_files),
            'duplicate_details': [
                {'file1': str(dup[0]), 'file2': str(dup[1])} 
                for dup in duplicates[:10]  # 상위 10개만
            ],
            'temp_files_removed': temp_files[:20]  # 상위 20개만
        }
        
        report_file = self.workspace_path / '.agents' / 'logs' / f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return report
    
    def run_full_cleanup(self):
        """전체 정리 실행"""
        self.logger.info("Starting full workspace cleanup")
        
        # 1. 임시 파일 정리
        temp_files = self.clean_temp_files()
        print(f"✅ 임시 파일 {len(temp_files)}개 정리 완료")
        
        # 2. 중복 파일 탐지
        duplicates = self.find_duplicate_files()
        print(f"⚠️ 중복 파일 {len(duplicates)}쌍 발견")
        
        # 3. Communication 파일 정리
        self.organize_communication_files()
        print("✅ Communication 폴더 정리 완료")
        
        # 4. 보고서 생성
        report = self.generate_cleanup_report()
        print(f"📊 정리 보고서 생성: {len(temp_files)}개 임시파일, {len(duplicates)}개 중복파일")
        
        self.logger.info("Full workspace cleanup completed")
        return report

if __name__ == "__main__":
    import sys
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\etlov\multi-agent-workspace"
    organizer = FileOrganizer(workspace)
    
    if len(sys.argv) > 2 and sys.argv[2] == "--full":
        organizer.run_full_cleanup()
    else:
        report = organizer.generate_cleanup_report()
        print(f"발견된 중복 파일: {report['duplicates_found']}쌍")
        print(f"정리된 임시 파일: {report['temp_files_cleaned']}개")