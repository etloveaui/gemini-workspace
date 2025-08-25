#!/usr/bin/env python3
"""
긴급 시스템 정리 스크립트 - 비대해진 워크스페이스 최적화
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def emergency_cleanup():
    """긴급 정리 실행"""
    root = Path("C:/Users/eunta/multi-agent-workspace")
    removed_files = []
    saved_space = 0
    
    print("🚨 긴급 시스템 정리 시작...")
    
    # 1. .bak 파일 정리 (communication 폴더 제외하고)
    print("\n📁 .bak 파일 정리...")
    for bak_file in root.rglob("*.bak"):
        if "communication" not in str(bak_file):
            try:
                size = bak_file.stat().st_size
                bak_file.unlink()
                removed_files.append(f"BAK: {bak_file.name}")
                saved_space += size
            except Exception as e:
                print(f"  ❌ {bak_file}: {e}")
    
    # 2. 오래된 로그 파일 정리 (7일 이상)
    print("\n📝 오래된 로그 파일 정리...")
    cutoff_date = datetime.now() - timedelta(days=7)
    for log_file in root.rglob("*.log"):
        try:
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                # 중요한 로그가 아닌 경우만
                if not any(word in str(log_file).lower() for word in ['master', 'critical', 'error']):
                    size = log_file.stat().st_size
                    log_file.unlink()
                    removed_files.append(f"LOG: {log_file.name}")
                    saved_space += size
        except Exception as e:
            print(f"  ❌ {log_file}: {e}")
    
    # 3. 임시 파일 정리
    print("\n🗑️ 임시 파일 정리...")
    temp_patterns = ["*.tmp", "*.temp", "*~", "*.swp"]
    for pattern in temp_patterns:
        for temp_file in root.rglob(pattern):
            try:
                size = temp_file.stat().st_size
                temp_file.unlink()
                removed_files.append(f"TEMP: {temp_file.name}")
                saved_space += size
            except Exception as e:
                print(f"  ❌ {temp_file}: {e}")
    
    # 4. 빈 디렉토리 정리
    print("\n📂 빈 디렉토리 정리...")
    def remove_empty_dirs(path):
        for item in path.iterdir():
            if item.is_dir():
                remove_empty_dirs(item)
                try:
                    if not any(item.iterdir()):  # 비어있으면
                        item.rmdir()
                        removed_files.append(f"DIR: {item.name}")
                except:
                    pass
    
    # 안전한 디렉토리만 정리
    safe_dirs = [root / "logs", root / "temp", root / ".agents" / "cache"]
    for safe_dir in safe_dirs:
        if safe_dir.exists():
            remove_empty_dirs(safe_dir)
    
    # 5. 중복 파일 감지 및 정리 (간단한 버전)
    print("\n🔍 중복 파일 감지...")
    file_hashes = {}
    duplicates = []
    
    for file_path in root.rglob("*"):
        if file_path.is_file() and file_path.stat().st_size > 1024:  # 1KB 이상만
            try:
                # 간단한 해시 (파일 크기 + 수정 시간)
                simple_hash = f"{file_path.stat().st_size}_{file_path.stat().st_mtime}"
                if simple_hash in file_hashes:
                    duplicates.append((file_path, file_hashes[simple_hash]))
                else:
                    file_hashes[simple_hash] = file_path
            except:
                pass
    
    # 중복 파일 중 덜 중요한 것 제거 (backup, temp 우선)
    for dup_file, original in duplicates[:10]:  # 안전하게 10개만
        if any(word in str(dup_file).lower() for word in ['backup', 'temp', 'copy']):
            try:
                size = dup_file.stat().st_size
                dup_file.unlink()
                removed_files.append(f"DUP: {dup_file.name}")
                saved_space += size
            except:
                pass
    
    # 결과 보고
    print(f"\n✅ 정리 완료!")
    print(f"   📊 제거된 파일: {len(removed_files)}개")
    print(f"   💾 절약된 공간: {saved_space / (1024*1024):.1f}MB")
    
    if len(removed_files) <= 20:
        print(f"\n📋 제거된 파일들:")
        for file in removed_files:
            print(f"   - {file}")
    else:
        print(f"\n📋 제거된 파일 종류별:")
        types = {}
        for file in removed_files:
            file_type = file.split(":")[0]
            types[file_type] = types.get(file_type, 0) + 1
        for file_type, count in types.items():
            print(f"   - {file_type}: {count}개")
    
    return len(removed_files), saved_space

if __name__ == "__main__":
    emergency_cleanup()