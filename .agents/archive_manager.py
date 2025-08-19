#!/usr/bin/env python3
"""
자동 아카이빙 관리자
- communication 폴더의 오래된 파일들 자동 아카이빙
- 일일/주간/월간 단위로 정리
- 중요도에 따른 보관 기간 설정
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
import zipfile
import re

class ArchiveManager:
    def __init__(self, workspace_path="."):
        self.workspace = Path(workspace_path)
        self.comm_dir = self.workspace / "communication"
        self.archive_dir = self.comm_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        # 보관 정책 (일 단위)
        self.retention_policy = {
            "P0": 365,  # P0는 1년 보관
            "P1": 180,  # P1은 6개월 보관  
            "P2": 90,   # P2는 3개월 보관
            "P3": 30,   # P3는 1개월 보관
            "default": 60  # 기본 2개월
        }
    
    def parse_frontmatter(self, file_path):
        """마크다운 frontmatter 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                return {}
            
            end = content.find('---', 3)
            if end == -1:
                return {}
            
            frontmatter = content[3:end].strip()
            metadata = {}
            
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            
            return metadata
            
        except Exception:
            return {}
    
    def should_archive(self, file_path):
        """파일이 아카이빙 대상인지 판단"""
        if not file_path.suffix == '.md':
            return False
        
        metadata = self.parse_frontmatter(file_path)
        
        # 상태가 completed인 파일만 아카이빙
        if metadata.get('status') != 'completed':
            return False
        
        # 생성일자 확인
        created = metadata.get('created', '')
        if not created:
            # 파일 수정 시간으로 대체
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        else:
            try:
                file_time = datetime.strptime(created[:10], '%Y-%m-%d')
            except:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # 보관 정책에 따른 기간 계산
        priority = metadata.get('priority', 'default')
        retention_days = self.retention_policy.get(priority, self.retention_policy['default'])
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        return file_time < cutoff_date
    
    def archive_old_files(self, dry_run=True):
        """오래된 파일들 아카이빙"""
        archived_files = []
        
        # communication 하위 폴더들 검사
        agent_dirs = ['claude', 'gemini', 'codex', 'shared']
        
        for agent_dir in agent_dirs:
            agent_path = self.comm_dir / agent_dir
            if not agent_path.exists():
                continue
            
            for md_file in agent_path.glob('*.md'):
                if self.should_archive(md_file):
                    if not dry_run:
                        # 연도별/월별 폴더로 아카이빙
                        metadata = self.parse_frontmatter(md_file)
                        created = metadata.get('created', '')
                        
                        if created:
                            try:
                                file_date = datetime.strptime(created[:10], '%Y-%m-%d')
                            except:
                                file_date = datetime.fromtimestamp(md_file.stat().st_mtime)
                        else:
                            file_date = datetime.fromtimestamp(md_file.stat().st_mtime)
                        
                        # archive/YYYY/MM 구조로 저장
                        archive_subdir = self.archive_dir / str(file_date.year) / f"{file_date.month:02d}"
                        archive_subdir.mkdir(parents=True, exist_ok=True)
                        
                        # 파일 이동
                        new_path = archive_subdir / md_file.name
                        shutil.move(str(md_file), str(new_path))
                    
                    archived_files.append(md_file)
        
        return archived_files
    
    def clean_old_archives(self, months=12):
        """오래된 아카이브 정리 (압축)"""
        cutoff_date = datetime.now() - timedelta(days=months*30)
        
        for year_dir in self.archive_dir.glob('*'):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue
            
            year = int(year_dir.name)
            if year < cutoff_date.year:
                # 1년 이상 된 폴더는 압축
                zip_path = self.archive_dir / f"archive_{year}.zip"
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in year_dir.rglob('*'):
                        if file_path.is_file():
                            zipf.write(file_path, file_path.relative_to(year_dir))
                
                # 원본 폴더 삭제
                shutil.rmtree(year_dir)
                print(f"📦 {year}년 아카이브 압축 완료: {zip_path}")
    
    def auto_archive(self, dry_run=False):
        """자동 아카이빙 실행"""
        print("🗂️ 자동 아카이빙 시작...")
        
        # 1. 오래된 파일들 아카이빙
        archived = self.archive_old_files(dry_run)
        print(f"  아카이빙 대상: {len(archived)} 파일")
        
        if not dry_run and archived:
            for file in archived:
                print(f"    📁 {file.name}")
        
        # 2. 오래된 아카이브 압축
        if not dry_run:
            self.clean_old_archives()
        
        return len(archived)
    
    def create_archive_index(self):
        """아카이브 인덱스 생성"""
        index_data = {
            "created": datetime.now().isoformat(),
            "archives": {}
        }
        
        # 압축 파일들 인덱싱
        for zip_file in self.archive_dir.glob("archive_*.zip"):
            year = zip_file.stem.split('_')[1]
            
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                files = zipf.namelist()
                index_data["archives"][year] = {
                    "zip_file": zip_file.name,
                    "file_count": len(files),
                    "size_mb": zip_file.stat().st_size / 1024 / 1024,
                    "files": files[:10]  # 처음 10개만 미리보기
                }
        
        # 현재 연도별 폴더들
        for year_dir in self.archive_dir.glob('*'):
            if year_dir.is_dir() and year_dir.name.isdigit():
                files = list(year_dir.rglob('*.md'))
                index_data["archives"][year_dir.name] = {
                    "type": "folder",
                    "file_count": len(files),
                    "files": [f.name for f in files[:10]]
                }
        
        # 인덱스 파일 저장
        index_file = self.archive_dir / "index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        return index_data

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    manager = ArchiveManager()
    
    if len(sys.argv) < 2:
        print("사용법: python archive_manager.py <command>")
        print("명령어:")
        print("  auto        - 자동 아카이빙 실행")
        print("  auto-dry    - 아카이빙 시뮬레이션")  
        print("  index       - 아카이브 인덱스 생성")
        print("  clean       - 오래된 아카이브 압축")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "auto":
        count = manager.auto_archive(dry_run=False)
        print(f"✅ 아카이빙 완료: {count} 파일")
        
    elif command == "auto-dry":
        count = manager.auto_archive(dry_run=True)
        print(f"📋 아카이빙 예상: {count} 파일")
        
    elif command == "index":
        index = manager.create_archive_index()
        print("📄 아카이브 인덱스 생성 완료")
        print(f"  연도별 아카이브: {len(index['archives'])} 개")
        
    elif command == "clean":
        manager.clean_old_archives()
        print("🧹 오래된 아카이브 정리 완료")
        
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)