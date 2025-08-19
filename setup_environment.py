#!/usr/bin/env python3
"""
멀티 에이전트 워크스페이스 환경 자동 설정
- 집/직장/노트북 어디서나 동일한 환경 구성
- 필요한 패키지 자동 설치
- MCP 서버 설정 자동화
"""

import sys
import os
import json
import subprocess
import platform
from pathlib import Path

class EnvironmentSetup:
    def __init__(self):
        self.workspace_path = Path.cwd()
        self.system_info = {
            "os": platform.system(),
            "python_version": sys.version_info,
            "platform": platform.platform()
        }
        
    def check_requirements(self):
        """필수 요구사항 확인"""
        print("🔍 시스템 요구사항 확인 중...")
        
        # Python 버전 확인
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 이상이 필요합니다.")
        
        # Git 확인
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("✅ Git 설치됨")
        except:
            raise RuntimeError("Git이 설치되지 않았습니다.")
        
        # 필수 디렉토리 생성
        essential_dirs = [
            ".agents", ".agents/locks", ".agents/queue", 
            ".agents/context7_cache", ".agents/backup",
            "docs/tasks", "secrets"
        ]
        
        for dir_path in essential_dirs:
            (self.workspace_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ 디렉토리 구조 생성 완료")
    
    def install_packages(self):
        """필수 패키지 설치"""
        print("📦 필수 패키지 설치 중...")
        
        packages = [
            "pytest>=8.0.0",
            "psutil>=5.9.0", 
            "invoke>=2.0.0",
            "requests>=2.31.0",
            "sqlite3"  # 내장 모듈이지만 확인용
        ]
        
        for package in packages:
            try:
                if package == "sqlite3":
                    import sqlite3
                    continue
                    
                print(f"  설치 중: {package}")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"⚠️ {package} 설치 실패: {e}")
            except ImportError:
                print(f"⚠️ {package} 가져오기 실패")
        
        print("✅ 패키지 설치 완료")
    
    def setup_mcp_servers(self):
        """무료 MCP 서버 설정"""
        print("🔌 MCP 서버 설정 중...")
        
        mcp_config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", 
                            str(self.workspace_path)],
                    "description": "파일시스템 전체 접근"
                },
                "sqlite": {
                    "command": "npx", 
                    "args": ["-y", "@modelcontextprotocol/server-sqlite",
                            str(self.workspace_path / "usage.db")],
                    "description": "SQLite 데이터베이스 관리"
                },
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "description": "GitHub 리포지토리 관리",
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
                    }
                }
            }
        }
        
        # Claude Desktop 설정 파일 경로 찾기
        config_paths = []
        if self.system_info["os"] == "Windows":
            config_paths = [
                Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",
                Path.home() / ".config/claude/claude_desktop_config.json"
            ]
        elif self.system_info["os"] == "Darwin":  # macOS
            config_paths = [
                Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
            ]
        else:  # Linux
            config_paths = [
                Path.home() / ".config/claude/claude_desktop_config.json"
            ]
        
        # 설정 파일 업데이트
        for config_path in config_paths:
            if config_path.parent.exists():
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                existing_config = {}
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            existing_config = json.load(f)
                    except:
                        pass
                
                # 기존 설정과 병합
                existing_config.update(mcp_config)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ MCP 설정 업데이트: {config_path}")
                break
        else:
            print("⚠️ Claude Desktop 설정 파일 위치를 찾을 수 없습니다.")
    
    def create_cross_platform_scripts(self):
        """크로스 플랫폼 실행 스크립트 생성"""
        print("🖥️ 크로스 플랫폼 스크립트 생성 중...")
        
        # ma.py - 통합 CLI 래퍼
        ma_script = '''#!/usr/bin/env python3
"""멀티 에이전트 워크스페이스 통합 CLI"""
import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("사용법: python ma.py <command> [args...]")
        print("명령어:")
        print("  status    - 에이전트 상태")
        print("  add <task> - 작업 추가") 
        print("  search <query> - Context7 검색")
        print("  backup    - 백업 실행")
        return
    
    command = sys.argv[1]
    workspace = Path(__file__).parent
    
    if command == "status":
        subprocess.run([sys.executable, workspace / ".agents/multi_agent_manager.py", "status"])
    elif command == "add":
        if len(sys.argv) < 3:
            print("사용법: ma.py add <task_name> [priority] [agent]")
            return
        args = ["add-task"] + sys.argv[2:]
        subprocess.run([sys.executable, workspace / ".agents/multi_agent_manager.py"] + args)
    elif command == "search":
        if len(sys.argv) < 3:
            print("사용법: ma.py search <query>")
            return
        args = ["search"] + sys.argv[2:]
        subprocess.run([sys.executable, workspace / ".agents/context7_mcp.py"] + args)
    elif command == "backup":
        subprocess.run([sys.executable, workspace / ".agents/backup_manager.py", "backup"])
    else:
        print(f"알 수 없는 명령어: {command}")

if __name__ == "__main__":
    main()
'''
        
        with open(self.workspace_path / "ma.py", 'w', encoding='utf-8') as f:
            f.write(ma_script)
        
        # Windows 배치 파일
        if self.system_info["os"] == "Windows":
            bat_script = f'@echo off\npython "{self.workspace_path}/ma.py" %*'
            with open(self.workspace_path / "ma.bat", 'w') as f:
                f.write(bat_script)
        
        # Unix 셸 스크립트
        else:
            sh_script = f'#!/bin/bash\npython3 "{self.workspace_path}/ma.py" "$@"'
            sh_path = self.workspace_path / "ma.sh"
            with open(sh_path, 'w') as f:
                f.write(sh_script)
            sh_path.chmod(0o755)
        
        print("✅ 크로스 플랫폼 스크립트 생성 완료")
    
    def setup_natural_language_processor(self):
        """자연어 명령 처리 시스템 기초 설정"""
        print("🗣️ 자연어 처리 시스템 설정 중...")
        
        nl_processor = '''#!/usr/bin/env python3
"""
자연어 명령 처리기
사용자의 자연어를 시스템 명령으로 변환
"""
import re
import json

class NaturalLanguageProcessor:
    def __init__(self):
        self.patterns = {
            r"상태.*확인|어떻게.*되|진행.*상황": "status",
            r"작업.*추가|새.*작업|할일.*추가": "add_task",
            r"검색|찾아|알아봐": "search",
            r"백업|저장": "backup",
            r"테스트|확인": "test"
        }
    
    def process(self, text: str) -> dict:
        """자연어 텍스트를 명령으로 변환"""
        for pattern, command in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    "command": command,
                    "original_text": text,
                    "confidence": 0.8
                }
        
        return {
            "command": "unknown", 
            "original_text": text,
            "confidence": 0.0
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        processor = NaturalLanguageProcessor()
        result = processor.process(" ".join(sys.argv[1:]))
        print(json.dumps(result, ensure_ascii=False, indent=2))
'''
        
        with open(self.workspace_path / ".agents/nl_processor.py", 'w', encoding='utf-8') as f:
            f.write(nl_processor)
        
        print("✅ 자연어 처리 시스템 기초 설정 완료")
    
    def create_backup_system(self):
        """자동 백업 시스템 생성"""
        print("💾 백업 시스템 생성 중...")
        
        backup_manager = '''#!/usr/bin/env python3
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
'''
        
        with open(self.workspace_path / ".agents/backup_manager.py", 'w', encoding='utf-8') as f:
            f.write(backup_manager)
        
        print("✅ 백업 시스템 생성 완료")
    
    def run_setup(self):
        """전체 설정 실행"""
        print("🚀 멀티 에이전트 워크스페이스 환경 설정 시작\n")
        
        try:
            self.check_requirements()
            self.install_packages()
            self.setup_mcp_servers()
            self.create_cross_platform_scripts()
            self.setup_natural_language_processor()
            self.create_backup_system()
            
            print("\n🎉 환경 설정 완료!")
            print(f"시스템: {self.system_info['os']} {self.system_info['platform']}")
            print("사용법:")
            print("  python ma.py status    - 상태 확인")
            print("  python ma.py add 작업명 - 작업 추가")
            print("  python ma.py search 검색어 - 검색")
            
        except Exception as e:
            print(f"❌ 설정 중 오류 발생: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup = EnvironmentSetup()
    setup.run_setup()