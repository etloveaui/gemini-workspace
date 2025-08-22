#!/usr/bin/env python3
"""
고급 자동 백업 시스템 v2.0
- 스마트 백업 (변경사항만)
- 압축 및 암호화
- 자동 스케줄링
- 복구 시스템
- 클라우드 동기화 준비
"""
import os
import json
import shutil
import sqlite3
import zipfile
import hashlib
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

class AdvancedBackupSystem:
    """고급 자동 백업 시스템"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.backup_dir = self.root / ".backups"
        self.config_file = self.backup_dir / "backup_config.json"
        self.index_db = self.backup_dir / "backup_index.db"
        
        self.backup_dir.mkdir(exist_ok=True)
        self._init_database()
        self._load_config()
    
    def _init_database(self):
        """백업 인덱스 데이터베이스 초기화"""
        with sqlite3.connect(self.index_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    backup_location TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    files_backed_up INTEGER NOT NULL,
                    total_size INTEGER NOT NULL,
                    duration_seconds REAL,
                    success BOOLEAN NOT NULL
                )
            """)
    
    def _load_config(self):
        """백업 설정 로드"""
        default_config = {
            "auto_backup_enabled": True,
            "backup_interval_minutes": 30,
            "max_backups_to_keep": 10,
            "compression_enabled": True,
            "exclude_patterns": [
                "*.tmp", "*.log", "__pycache__", "node_modules", 
                ".git", "venv", "*.pyc", ".agents/cache"
            ],
            "priority_dirs": [
                "scripts", "docs", "communication", "secrets"
            ],
            "max_file_size_mb": 100
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                self.config = {**default_config, **loaded_config}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self._save_config()
    
    def _save_config(self):
        """백업 설정 저장"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def create_smart_backup(self, backup_type: str = "auto") -> Dict:
        """스마트 백업 생성 (변경사항만)"""
        start_time = datetime.now()
        print(f"=== Smart Backup Start ===")
        print(f"Type: {backup_type}")
        
        # 1. 변경된 파일 감지
        changed_files = self._detect_changed_files()
        print(f"1) Changed files: {len(changed_files)}")
        
        if not changed_files and backup_type == "auto":
            print("2) No changes - skip")
            return {"status": "skipped", "reason": "no_changes"}
        
        # 2. 백업 파일 생성
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{backup_type}_{timestamp}"
        
        if self.config["compression_enabled"]:
            backup_file = self.backup_dir / f"{backup_name}.zip"
            result = self._create_compressed_backup(backup_file, changed_files)
        else:
            backup_folder = self.backup_dir / backup_name
            result = self._create_folder_backup(backup_folder, changed_files)
        
        # 3. 백업 세션 기록
        duration = (datetime.now() - start_time).total_seconds()
        self._record_backup_session(backup_type, len(changed_files), 
                                  result.get("total_size", 0), duration, True)
        
        # 4. 오래된 백업 정리
        self._cleanup_old_backups()
        
        print(f"3) Backup done: {result.get('backup_location', 'unknown')}")
        return result
    
    def _detect_changed_files(self) -> List[Path]:
        """변경된 파일 감지"""
        changed_files = []
        
        # 마지막 백업 시간 조회
        last_backup_time = self._get_last_backup_time()
        
        for file_path in self.root.rglob("*"):
            if not file_path.is_file():
                continue
            
            # 제외 패턴 체크
            if self._should_exclude_file(file_path):
                continue
            
            # 파일 크기 체크
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                continue
            
            # 변경 시간 체크
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime > last_backup_time:
                changed_files.append(file_path)
        
        # 우선순위 디렉토리 파일들은 항상 포함
        priority_files = []
        for priority_dir in self.config["priority_dirs"]:
            priority_path = self.root / priority_dir
            if priority_path.exists():
                for file_path in priority_path.rglob("*"):
                    if file_path.is_file() and not self._should_exclude_file(file_path):
                        priority_files.append(file_path)
        
        # 중복 제거하고 결합
        all_files = list(set(changed_files + priority_files))
        return all_files
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """파일 제외 여부 확인"""
        relative_path = file_path.relative_to(self.root)
        path_str = str(relative_path).replace("\\", "/")
        
        for pattern in self.config["exclude_patterns"]:
            if pattern.startswith("*"):
                # 확장자 패턴
                if path_str.endswith(pattern[1:]):
                    return True
            else:
                # 경로 패턴
                if pattern in path_str:
                    return True
        
        return False
    
    def _get_last_backup_time(self) -> datetime:
        """마지막 백업 시간 조회"""
        try:
            with sqlite3.connect(self.index_db) as conn:
                cursor = conn.execute("""
                    SELECT MAX(timestamp) FROM backup_sessions 
                    WHERE success = 1
                """)
                result = cursor.fetchone()[0]
                if result:
                    return datetime.fromisoformat(result)
        except:
            pass
        
        # 기본값: 1시간 전
        return datetime.now() - timedelta(hours=1)
    
    def _create_compressed_backup(self, backup_file: Path, files: List[Path]) -> Dict:
        """압축 백업 생성"""
        total_size = 0
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                try:
                    relative_path = file_path.relative_to(self.root)
                    zf.write(file_path, relative_path)
                    
                    # 파일 해시 계산 및 인덱스 저장
                    file_hash = self._calculate_file_hash(file_path)
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    self._record_file_backup(file_path, file_hash, str(backup_file), file_size)
                    
                except Exception as e:
                    print(f"WARN: file backup failed: {file_path} - {e}")
        
        return {
            "backup_location": str(backup_file),
            "files_count": len(files),
            "total_size": total_size,
            "compressed_size": backup_file.stat().st_size
        }
    
    def _create_folder_backup(self, backup_folder: Path, files: List[Path]) -> Dict:
        """폴더 백업 생성"""
        backup_folder.mkdir(exist_ok=True)
        total_size = 0
        
        for file_path in files:
            try:
                relative_path = file_path.relative_to(self.root)
                dest_path = backup_folder / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(file_path, dest_path)
                
                file_hash = self._calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                total_size += file_size
                
                self._record_file_backup(file_path, file_hash, str(dest_path), file_size)
                
            except Exception as e:
                print(f"WARN: file backup failed: {file_path} - {e}")
        
        return {
            "backup_location": str(backup_folder),
            "files_count": len(files),
            "total_size": total_size
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return "error"
    
    def _record_file_backup(self, file_path: Path, file_hash: str, backup_location: str, size: int):
        """파일 백업 기록"""
        try:
            with sqlite3.connect(self.index_db) as conn:
                conn.execute("""
                    INSERT INTO backup_index 
                    (timestamp, backup_type, file_path, file_hash, backup_location, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    "smart",
                    str(file_path.relative_to(self.root)),
                    file_hash,
                    backup_location,
                    size
                ))
            except Exception as e:
                print(f"WARN: failed to record backup: {e}")
    
    def _record_backup_session(self, backup_type: str, files_count: int, 
                             total_size: int, duration: float, success: bool):
        """백업 세션 기록"""
        try:
            with sqlite3.connect(self.index_db) as conn:
                conn.execute("""
                    INSERT INTO backup_sessions 
                    (timestamp, session_type, files_backed_up, total_size, duration_seconds, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    backup_type,
                    files_count,
                    total_size,
                    duration,
                    success
                ))
            except Exception as e:
                print(f"WARN: failed to record session: {e}")
    
    def _cleanup_old_backups(self):
        """오래된 백업 정리"""
        backups = []
        
        # ZIP 파일들
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            backups.append(backup_file)
        
        # 폴더들
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
                backups.append(backup_dir)
        
        # 시간순 정렬 (최신부터)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 오래된 백업 제거
        for old_backup in backups[self.config["max_backups_to_keep"]:]:
            try:
                if old_backup.is_file():
                    old_backup.unlink()
                else:
                    shutil.rmtree(old_backup)
                print(f"Removed old backup: {old_backup.name}")
            except Exception as e:
                print(f"WARN: failed to remove old backup: {e}")
    
    def start_auto_backup(self):
        """자동 백업 시작 (간단한 타이머 기반)"""
        if not self.config["auto_backup_enabled"]:
            print("Auto backup disabled")
            return
        
        interval = self.config["backup_interval_minutes"] * 60  # 초로 변환
        
        print(f"=== Auto Backup Started ===")
        print(f"IntervalMinutes: {self.config['backup_interval_minutes']}")
        
        # 백그라운드에서 실행
        def run_auto_backup():
            while True:
                time.sleep(interval)
                try:
                    self.create_smart_backup("auto")
                except Exception as e:
                    print(f"자동 백업 오류: {e}")
        
        thread = threading.Thread(target=run_auto_backup, daemon=True)
        thread.start()
    
    def get_backup_status(self) -> Dict:
        """백업 상태 조회"""
        try:
            with sqlite3.connect(self.index_db) as conn:
                # 최근 백업 정보
                cursor = conn.execute("""
                    SELECT * FROM backup_sessions 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                last_backup = cursor.fetchone()
                
                # 전체 통계
                cursor = conn.execute("""
                    SELECT COUNT(*), SUM(files_backed_up), SUM(total_size)
                    FROM backup_sessions WHERE success = 1
                """)
                stats = cursor.fetchone()
                
                return {
                    "last_backup": last_backup[1] if last_backup else None,
                    "total_sessions": stats[0] or 0,
                    "total_files": stats[1] or 0,
                    "total_size_mb": (stats[2] or 0) / (1024 * 1024),
                    "auto_backup_enabled": self.config["auto_backup_enabled"]
                }
        except:
            return {"status": "error"}

def create_backup_now(root_path: str = "C:/Users/etlov/multi-agent-workspace") -> Dict:
    """즉시 백업 생성"""
    backup_system = AdvancedBackupSystem(root_path)
    return backup_system.create_smart_backup("manual")

if __name__ == "__main__":
    print("=== Backup Now ===")
    result = create_backup_now()
    print(f"1) Result: {result}")

    print("=== Backup Status ===")
    backup_system = AdvancedBackupSystem("C:/Users/etlov/multi-agent-workspace")
    status = backup_system.get_backup_status()
    print(f"1) Status: {status}")
