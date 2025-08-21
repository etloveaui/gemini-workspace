#!/usr/bin/env python3
"""
자동 백업 관리자
- 정기적으로 중요 파일들 백업
- 버전 관리
- 복구 기능
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import zipfile

class BackupManager:
    def __init__(self, workspace_path="."):
        self.workspace = Path(workspace_path)
        self.backup_dir = self.workspace / ".agents/backup"
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.zip"
        
        important_files = [
            "CLAUDE.md", "GEMINI.md", "AGENTS.md",
            ".agents/config.json", "docs/HUB.md",
            ".agents/multi_agent_manager.py",
            ".agents/context7_mcp.py",
            "usage.db"
        ]
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in important_files:
                full_path = self.workspace / file_path
                if full_path.exists():
                    zipf.write(full_path, file_path)
        
        print(f"✅ 백업 생성 완료: {backup_file}")
        self.cleanup_old_backups()
        
    def cleanup_old_backups(self, keep_count=10):
        """오래된 백업 정리"""
        backups = sorted(self.backup_dir.glob("backup_*.zip"))
        if len(backups) > keep_count:
            for old_backup in backups[:-keep_count]:
                old_backup.unlink()
                print(f"🗑️ 오래된 백업 삭제: {old_backup.name}")

if __name__ == "__main__":
    import sys
    manager = BackupManager()
    if len(sys.argv) > 1 and sys.argv[1] == "backup":
        manager.create_backup()
    else:
        print("사용법: python backup_manager.py backup")
