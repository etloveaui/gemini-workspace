#!/usr/bin/env python3
"""
설정 동기화 시스템 - ZIP 자동 압축 및 변경 감지
집/회사 간에 설정 파일들을 쉽게 옮길 수 있게 해드립니다.
"""
import os
import zipfile
import hashlib
import json
from pathlib import Path
from datetime import datetime

class SettingsSync:
    def __init__(self):
        self.root = Path("C:/Users/eunta/multi-agent-workspace")
        self.sync_files = [
            # VS Code 설정
            ".vscode/tasks.json",
            ".vscode/settings.json", 
            ".vscode/launch.json",
            
            # 환경 설정
            ".env",
            ".editorconfig",
            ".gitattributes",
            
            # 에이전트 설정 (민감하지 않은 것만)
            ".gemini/context_policy.yaml",
            
            # 스크립트 설정
            "scripts/cli_style.py",
            "MULTI_ENVIRONMENT_SYNC_GUIDE.md"
        ]
        
        self.sync_dir = self.root / "sync_package"
        self.sync_dir.mkdir(exist_ok=True)
        
        self.hash_file = self.sync_dir / "last_sync.json"
    
    def create_sync_package(self):
        """동기화 패키지 생성"""
        print("🎒 설정 동기화 패키지 생성 중...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"settings_sync_{timestamp}.zip"
        zip_path = self.sync_dir / zip_name
        
        # 현재 해시 계산
        current_hashes = {}
        files_to_sync = []
        
        for file_path in self.sync_files:
            full_path = self.root / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    current_hashes[file_path] = file_hash
                    files_to_sync.append((file_path, full_path))
        
        # 이전 해시와 비교
        changes_detected = self._check_changes(current_hashes)
        
        if not changes_detected:
            print("✅ 변경사항 없음 - 새 패키지 생성 스킵")
            return None
        
        # ZIP 파일 생성
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for rel_path, full_path in files_to_sync:
                zip_file.write(full_path, rel_path)
                print(f"  📄 {rel_path}")
            
            # 메타데이터 추가
            metadata = {
                "created": datetime.now().isoformat(),
                "files": list(current_hashes.keys()),
                "hashes": current_hashes,
                "hostname": os.environ.get('COMPUTERNAME', 'unknown'),
                "user": os.environ.get('USERNAME', 'unknown')
            }
            
            zip_file.writestr("sync_metadata.json", json.dumps(metadata, indent=2))
        
        # 해시 저장
        with open(self.hash_file, 'w') as f:
            json.dump(current_hashes, f, indent=2)
        
        print(f"📦 패키지 생성 완료: {zip_name}")
        print(f"   파일: {len(files_to_sync)}개")
        print(f"   크기: {zip_path.stat().st_size / 1024:.1f}KB")
        
        return str(zip_path)
    
    def _check_changes(self, current_hashes):
        """변경사항 확인"""
        if not self.hash_file.exists():
            return True  # 처음 실행
        
        try:
            with open(self.hash_file, 'r') as f:
                old_hashes = json.load(f)
            
            # 해시 비교
            for file_path, current_hash in current_hashes.items():
                if file_path not in old_hashes or old_hashes[file_path] != current_hash:
                    print(f"🔄 변경 감지: {file_path}")
                    return True
            
            # 새 파일 확인
            for file_path in current_hashes:
                if file_path not in old_hashes:
                    print(f"📄 새 파일: {file_path}")
                    return True
            
            return False
            
        except:
            return True  # 오류시 안전하게 생성
    
    def apply_sync_package(self, zip_path):
        """동기화 패키지 적용"""
        print(f"📥 동기화 패키지 적용: {Path(zip_path).name}")
        
        if not os.path.exists(zip_path):
            print(f"❌ 파일 없음: {zip_path}")
            return False
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # 메타데이터 확인
                if "sync_metadata.json" in zip_file.namelist():
                    metadata_content = zip_file.read("sync_metadata.json").decode('utf-8')
                    metadata = json.loads(metadata_content)
                    print(f"  생성일: {metadata.get('created', 'unknown')}")
                    print(f"  생성자: {metadata.get('user', 'unknown')}@{metadata.get('hostname', 'unknown')}")
                
                # 파일 추출
                applied_count = 0
                for file_info in zip_file.infolist():
                    if file_info.filename == "sync_metadata.json":
                        continue
                    
                    target_path = self.root / file_info.filename
                    target_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    with zip_file.open(file_info) as source:
                        with open(target_path, 'wb') as target:
                            target.write(source.read())
                    
                    print(f"  ✅ {file_info.filename}")
                    applied_count += 1
                
                print(f"📦 적용 완료: {applied_count}개 파일")
                return True
                
        except Exception as e:
            print(f"❌ 적용 실패: {e}")
            return False
    
    def list_packages(self):
        """사용 가능한 패키지 목록"""
        packages = list(self.sync_dir.glob("settings_sync_*.zip"))
        
        if not packages:
            print("📦 사용 가능한 동기화 패키지 없음")
            return []
        
        print("📦 사용 가능한 동기화 패키지:")
        for i, package in enumerate(sorted(packages, reverse=True), 1):
            size_kb = package.stat().st_size / 1024
            mtime = datetime.fromtimestamp(package.stat().st_mtime)
            print(f"  {i}) {package.name} ({size_kb:.1f}KB, {mtime.strftime('%m-%d %H:%M')})")
        
        return packages
    
    def auto_check_and_sync(self):
        """자동 체크 및 동기화"""
        print("🔄 자동 설정 동기화 체크...")
        
        # 변경 감지 및 패키지 생성
        package_path = self.create_sync_package()
        
        if package_path:
            print(f"🎯 새 패키지 생성됨: {Path(package_path).name}")
            print("💡 이 ZIP 파일을 다른 환경으로 복사하여 사용하세요:")
            print(f"   python scripts/settings_sync.py apply {Path(package_path).name}")
        
        return package_path

def main():
    import sys
    
    sync = SettingsSync()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            sync.create_sync_package()
        elif command == "apply" and len(sys.argv) > 2:
            zip_name = sys.argv[2]
            zip_path = sync.sync_dir / zip_name
            sync.apply_sync_package(str(zip_path))
        elif command == "list":
            sync.list_packages()
        elif command == "auto":
            sync.auto_check_and_sync()
        else:
            print("사용법:")
            print("  python settings_sync.py create     - 새 패키지 생성")
            print("  python settings_sync.py apply <파일명> - 패키지 적용")
            print("  python settings_sync.py list      - 패키지 목록")
            print("  python settings_sync.py auto      - 자동 체크")
    else:
        # 기본: 자동 체크
        sync.auto_check_and_sync()

if __name__ == "__main__":
    main()