"""
자동 환경 동기화 시스템
- Git 관리 안되는 중요 파일들 자동 ZIP
- 변경 감지시 즉시 새 ZIP 생성
- 타임스탬프 포함 파일명으로 변경사항 표시
"""
import zipfile
import hashlib
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line

ROOT = Path(__file__).resolve().parent.parent

# Git 관리 안되는 중요 파일들 (MULTI_ENVIRONMENT_SYNC_GUIDE.md 기준)
SYNC_TARGETS = {
    '.vscode/': 'VS Code 워크스페이스 설정',
    '.env': '환경변수 파일',
    'secrets/': '모든 민감 정보', 
    '*.log': '로그 파일들',
    'usage.db': '토큰 사용량 데이터베이스',
    '.claude*/': 'Claude 개인 설정',
    '.agents/': '에이전트 설정 일부'
}

def calculate_folder_hash(folder_path):
    """폴더 내용의 해시값 계산"""
    hash_md5 = hashlib.md5()
    
    if folder_path.is_file():
        with open(folder_path, 'rb') as f:
            hash_md5.update(f.read())
    elif folder_path.is_dir():
        for file_path in sorted(folder_path.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    hash_md5.update(f.read())
                hash_md5.update(str(file_path).encode())
    
    return hash_md5.hexdigest()

def create_sync_zip():
    """동기화용 ZIP 파일 생성"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    zip_filename = f"environment_sync_{timestamp}.zip"
    zip_path = ROOT / zip_filename
    
    print(header("환경 동기화 ZIP 생성"))
    
    # 현재 해시 상태 계산
    current_hashes = {}
    files_to_sync = []
    
    for target, description in SYNC_TARGETS.items():
        if target == '*.log':
            # 로그 파일들 찾기
            log_files = list(ROOT.glob('**/*.log'))
            files_to_sync.extend(log_files)
            for log_file in log_files:
                current_hashes[str(log_file)] = calculate_folder_hash(log_file)
        else:
            target_path = ROOT / target.rstrip('/')
            if target_path.exists():
                files_to_sync.append(target_path)
                current_hashes[str(target_path)] = calculate_folder_hash(target_path)
    
    # ZIP 파일 생성
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_sync:
            if file_path.is_file():
                arcname = file_path.relative_to(ROOT)
                zipf.write(file_path, arcname)
            elif file_path.is_dir():
                for sub_file in file_path.rglob('*'):
                    if sub_file.is_file():
                        arcname = sub_file.relative_to(ROOT)
                        zipf.write(sub_file, arcname)
        
        # 해시 정보도 ZIP에 포함
        hash_info = json.dumps(current_hashes, indent=2)
        zipf.writestr('_sync_hashes.json', hash_info)
    
    print(kv("생성된 ZIP", zip_filename))
    print(kv("파일 크기", f"{zip_path.stat().st_size:,} bytes"))
    print(kv("포함 파일 수", len(files_to_sync)))
    
    # .gitignore에 ZIP 파일 제외 패턴 추가
    gitignore_path = ROOT / '.gitignore'
    try:
        gitignore_content = gitignore_path.read_text(encoding='utf-8') if gitignore_path.exists() else ""
    except UnicodeDecodeError:
        gitignore_content = gitignore_path.read_text(encoding='cp949') if gitignore_path.exists() else ""
    
    if 'environment_sync_*.zip' not in gitignore_content:
        with open(gitignore_path, 'a') as f:
            f.write('\n# Environment sync files\n')
            f.write('environment_sync_*.zip\n')
        print(status_line(1, "UPDATE", ".gitignore", "ZIP 파일 제외 패턴 추가"))
    
    return zip_path

def check_changes():
    """변경사항 확인"""
    print(header("환경 파일 변경사항 확인"))
    
    # 이전 해시 정보 로드
    latest_zip = None
    for zip_file in ROOT.glob('environment_sync_*.zip'):
        if latest_zip is None or zip_file.stat().st_mtime > latest_zip.stat().st_mtime:
            latest_zip = zip_file
    
    if not latest_zip:
        print(status_line(1, "INFO", "초기 실행", "이전 ZIP 없음 - 새로 생성"))
        return True
    
    # 이전 해시와 현재 해시 비교
    try:
        with zipfile.ZipFile(latest_zip, 'r') as zipf:
            hash_data = zipf.read('_sync_hashes.json').decode()
            previous_hashes = json.loads(hash_data)
    except:
        print(status_line(2, "WARNING", "해시 로드 실패", "새로 생성 필요"))
        return True
    
    changes_found = False
    for target, description in SYNC_TARGETS.items():
        if target == '*.log':
            continue  # 로그는 항상 변경됨
            
        target_path = ROOT / target.rstrip('/')
        if target_path.exists():
            current_hash = calculate_folder_hash(target_path)
            previous_hash = previous_hashes.get(str(target_path))
            
            if current_hash != previous_hash:
                print(status_line(3, "CHANGED", target, description))
                changes_found = True
            else:
                print(status_line(4, "OK", target, "변경사항 없음"))
    
    return changes_found

def auto_sync():
    """자동 동기화 실행"""
    if check_changes():
        zip_path = create_sync_zip()
        print(header("동기화 완료"))
        print(f"새로운 동기화 파일: {zip_path.name}")
        print("집/회사에서 이 ZIP 파일을 복사하여 압축 해제하세요.")
        return True
    else:
        print(status_line(1, "OK", "동기화 불필요", "변경사항 없음"))
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='환경 동기화')
    parser.add_argument('--check', action='store_true', help='변경사항만 확인')
    parser.add_argument('--force', action='store_true', help='강제 ZIP 생성')
    
    args = parser.parse_args()
    
    if args.check:
        check_changes()
    elif args.force:
        create_sync_zip()
    else:
        auto_sync()