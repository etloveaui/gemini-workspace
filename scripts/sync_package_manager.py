#!/usr/bin/env python3
"""
Sync Package 관리 시스템
- Git 추적하지 않지만 환경에 필수인 파일들 관리
- ZIP으로 패키징하여 동기화
- 자동화된 백업 및 복원 시스템
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import zipfile
import json
import hashlib
from pathlib import Path
from datetime import datetime
import shutil

from environment_path_manager import get_workspace_path

class SyncPackageManager:
    def __init__(self):
        self.workspace_root = get_workspace_path()
        self.sync_package_dir = get_workspace_path("sync_package")
        self.sync_package_dir.mkdir(exist_ok=True)
        
        # Git 추적하지 않지만 동기화가 필요한 파일들
        self.sync_files = {
            # 환경 설정 파일들
            ".env": "환경 변수",
            ".vscode/settings.json": "VSCode 설정",
            ".vscode/tasks.json": "VSCode 태스크",
            ".editorconfig": "에디터 설정",
            ".gitattributes": "Git 속성",
            
            # 에이전트 설정
            ".gemini/context_policy.yaml": "Gemini 컨텍스트 정책",
            ".claude/settings.json": "Claude 설정",
            ".codex/preferences.json": "Codex 설정",
            
            # 개인 스크립트 및 도구
            "scripts/user_config.py": "사용자 설정",
            "scripts/cli_style.py": "CLI 스타일",
            
            # 중요 문서 (개인화된 내용)
            "MULTI_ENVIRONMENT_SYNC_GUIDE.md": "멀티 환경 동기화 가이드",
            
            # 시스템 상태 파일
            ".agents/environment_profiles/*.json": "환경 프로필",
            "secrets/my_sensitive_data.md": "민감 정보 (암호화)",
        }
        
        self.last_sync_file = self.sync_package_dir / "last_sync.json"
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return "0"
    
    def get_current_state(self) -> dict:
        """현재 파일 상태 조사"""
        current_state = {}
        
        for pattern, description in self.sync_files.items():
            if '*' in pattern:
                # glob 패턴 처리
                base_path = self.workspace_root / pattern.replace('*', '')
                parent_dir = base_path.parent
                
                if parent_dir.exists():
                    glob_pattern = pattern.split('/')[-1]
                    for file_path in parent_dir.glob(glob_pattern):
                        rel_path = str(file_path.relative_to(self.workspace_root))
                        current_state[rel_path] = self.calculate_file_hash(file_path)
            else:
                file_path = self.workspace_root / pattern
                if file_path.exists():
                    current_state[pattern] = self.calculate_file_hash(file_path)
        
        return current_state
    
    def get_last_sync_state(self) -> dict:
        """마지막 동기화 상태 로드"""
        if self.last_sync_file.exists():
            try:
                with open(self.last_sync_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_sync_state(self, state: dict) -> None:
        """동기화 상태 저장"""
        with open(self.last_sync_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def detect_changes(self) -> dict:
        """변경사항 감지"""
        current_state = self.get_current_state()
        last_state = self.get_last_sync_state()
        
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "unchanged_files": []
        }
        
        # 새로 생성된 파일과 수정된 파일
        for file_path, current_hash in current_state.items():
            if file_path not in last_state:
                changes["new_files"].append(file_path)
            elif last_state[file_path] != current_hash:
                changes["modified_files"].append(file_path)
            else:
                changes["unchanged_files"].append(file_path)
        
        # 삭제된 파일
        for file_path in last_state:
            if file_path not in current_state:
                changes["deleted_files"].append(file_path)
        
        return changes
    
    def create_sync_package(self) -> tuple:
        """동기화 패키지 생성"""
        print("📦 동기화 패키지 생성 중...")
        
        # 변경사항 감지
        changes = self.detect_changes()
        
        total_changes = (len(changes["new_files"]) + 
                        len(changes["modified_files"]) + 
                        len(changes["deleted_files"]))
        
        if total_changes == 0:
            print("✅ 변경사항 없음 - 패키지 생성 건너뛰기")
            return True, "no_changes"
        
        # ZIP 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"settings_sync_{timestamp}.zip"
        zip_path = self.sync_package_dir / zip_filename
        
        # 패키지 생성
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                current_state = self.get_current_state()
                
                # 메타데이터 추가
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    "platform": os.name,
                    "hostname": os.environ.get('COMPUTERNAME') or os.environ.get('HOSTNAME'),
                    "user": os.environ.get('USERNAME') or os.environ.get('USER'),
                    "changes": changes,
                    "file_count": len(current_state)
                }
                
                zipf.writestr("_sync_metadata.json", 
                            json.dumps(metadata, indent=2, ensure_ascii=False))
                
                # 파일들 추가
                files_added = 0
                for file_rel_path in current_state:
                    file_path = self.workspace_root / file_rel_path
                    
                    if file_path.exists():
                        # 민감 정보는 암호화
                        if "sensitive_data" in file_rel_path:
                            # 간단한 인코딩 (실제 환경에서는 더 강력한 암호화 필요)
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            encoded_content = content.encode('utf-8').hex()
                            zipf.writestr(file_rel_path + ".encrypted", encoded_content)
                        else:
                            zipf.write(file_path, file_rel_path)
                        
                        files_added += 1
                
                print(f"✅ 패키지 생성 완료: {zip_filename}")
                print(f"   - 포함된 파일: {files_added}개")
                print(f"   - 새 파일: {len(changes['new_files'])}개")
                print(f"   - 수정 파일: {len(changes['modified_files'])}개")
                print(f"   - 삭제 파일: {len(changes['deleted_files'])}개")
                
                # 현재 상태 저장
                self.save_sync_state(current_state)
                
                return True, str(zip_path)
                
        except Exception as e:
            print(f"❌ 패키지 생성 실패: {e}")
            return False, str(e)
    
    def restore_from_package(self, zip_path: Path) -> tuple:
        """패키지에서 복원"""
        print(f"📥 패키지에서 복원: {zip_path.name}")
        
        if not zip_path.exists():
            return False, "패키지 파일이 존재하지 않음"
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # 메타데이터 확인
                if "_sync_metadata.json" in zipf.namelist():
                    metadata_str = zipf.read("_sync_metadata.json").decode('utf-8')
                    metadata = json.loads(metadata_str)
                    
                    print(f"📋 패키지 정보:")
                    print(f"   - 생성일: {metadata.get('created_at', '알 수 없음')}")
                    print(f"   - 생성자: {metadata.get('user', '알 수 없음')}")
                    print(f"   - 파일 수: {metadata.get('file_count', 0)}개")
                
                # 파일 복원
                restored_count = 0
                for file_info in zipf.infolist():
                    if file_info.filename == "_sync_metadata.json":
                        continue
                    
                    target_path = self.workspace_root / file_info.filename
                    
                    # 디렉터리 생성
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 암호화된 파일 처리
                    if file_info.filename.endswith(".encrypted"):
                        original_filename = file_info.filename[:-10]  # .encrypted 제거
                        original_path = self.workspace_root / original_filename
                        
                        # 간단한 디코딩
                        encoded_content = zipf.read(file_info.filename).decode('utf-8')
                        content = bytes.fromhex(encoded_content).decode('utf-8')
                        
                        with open(original_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        restored_count += 1
                    else:
                        # 일반 파일 복원
                        with open(target_path, 'wb') as f:
                            f.write(zipf.read(file_info.filename))
                        
                        restored_count += 1
                
                print(f"✅ 복원 완료: {restored_count}개 파일")
                
                # 복원 후 상태 업데이트
                current_state = self.get_current_state()
                self.save_sync_state(current_state)
                
                return True, f"{restored_count}개 파일 복원 완료"
                
        except Exception as e:
            return False, f"복원 실패: {e}"
    
    def list_packages(self) -> list:
        """사용 가능한 패키지 목록"""
        packages = []
        
        for zip_file in self.sync_package_dir.glob("settings_sync_*.zip"):
            try:
                stat = zip_file.stat()
                packages.append({
                    "filename": zip_file.name,
                    "path": str(zip_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception:
                continue
        
        # 최신순 정렬
        packages.sort(key=lambda x: x["created"], reverse=True)
        
        return packages
    
    def auto_backup(self) -> dict:
        """자동 백업 실행"""
        print("🔄 자동 백업 시작...")
        
        # 변경사항 확인
        changes = self.detect_changes()
        total_changes = (len(changes["new_files"]) + 
                        len(changes["modified_files"]) + 
                        len(changes["deleted_files"]))
        
        if total_changes == 0:
            return {
                "status": "skipped",
                "reason": "no_changes",
                "message": "변경사항 없음"
            }
        
        # 패키지 생성
        success, result = self.create_sync_package()
        
        # 오래된 백업 정리 (최대 10개 유지)
        packages = self.list_packages()
        if len(packages) > 10:
            for old_package in packages[10:]:
                old_path = Path(old_package["path"])
                if old_path.exists():
                    old_path.unlink()
                    print(f"🗑️  오래된 백업 삭제: {old_package['filename']}")
        
        return {
            "status": "success" if success else "failed",
            "result": result,
            "changes": changes,
            "total_changes": total_changes
        }
    
    def status_report(self) -> dict:
        """상태 리포트"""
        changes = self.detect_changes()
        packages = self.list_packages()
        
        return {
            "sync_status": {
                "new_files": len(changes["new_files"]),
                "modified_files": len(changes["modified_files"]),
                "deleted_files": len(changes["deleted_files"]),
                "unchanged_files": len(changes["unchanged_files"])
            },
            "packages": {
                "total_count": len(packages),
                "latest_package": packages[0] if packages else None
            },
            "tracked_files": len(self.get_current_state())
        }

def main():
    import sys
    
    manager = SyncPackageManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--backup":
            result = manager.auto_backup()
            print(f"백업 결과: {result}")
            
        elif command == "--restore":
            if len(sys.argv) > 2:
                zip_name = sys.argv[2]
                zip_path = manager.sync_package_dir / zip_name
                success, message = manager.restore_from_package(zip_path)
                print(f"복원 {'성공' if success else '실패'}: {message}")
            else:
                packages = manager.list_packages()
                if packages:
                    print("📦 사용 가능한 패키지:")
                    for i, pkg in enumerate(packages[:5]):
                        print(f"  {i+1}. {pkg['filename']} ({pkg['created'][:10]})")
                else:
                    print("❌ 사용 가능한 패키지 없음")
                    
        elif command == "--list":
            packages = manager.list_packages()
            print(f"📦 패키지 목록 ({len(packages)}개):")
            for pkg in packages:
                size_mb = pkg['size'] / 1024 / 1024
                print(f"  - {pkg['filename']}")
                print(f"    크기: {size_mb:.1f}MB, 생성: {pkg['created'][:16]}")
                
        elif command == "--status":
            status = manager.status_report()
            print("📊 동기화 상태:")
            print(f"  - 새 파일: {status['sync_status']['new_files']}개")
            print(f"  - 수정 파일: {status['sync_status']['modified_files']}개")
            print(f"  - 삭제 파일: {status['sync_status']['deleted_files']}개")
            print(f"  - 추적 파일: {status['tracked_files']}개")
            print(f"  - 백업 패키지: {status['packages']['total_count']}개")
            
        elif command == "--changes":
            changes = manager.detect_changes()
            print("🔄 변경사항 상세:")
            
            if changes["new_files"]:
                print(f"📁 새 파일 ({len(changes['new_files'])}개):")
                for f in changes["new_files"]:
                    print(f"  + {f}")
            
            if changes["modified_files"]:
                print(f"✏️  수정 파일 ({len(changes['modified_files'])}개):")
                for f in changes["modified_files"]:
                    print(f"  * {f}")
            
            if changes["deleted_files"]:
                print(f"🗑️  삭제 파일 ({len(changes['deleted_files'])}개):")
                for f in changes["deleted_files"]:
                    print(f"  - {f}")
        else:
            print(f"알 수 없는 명령어: {command}")
    else:
        # 기본: 자동 백업 실행
        manager.auto_backup()

if __name__ == "__main__":
    main()