#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HUB 시스템 완전 통일
- docs/HUB.md -> docs/CORE/HUB_ENHANCED.md 로 완전 전환
- 88개 파일의 모든 참조 일괄 수정
"""
import re
from pathlib import Path
from typing import List, Dict

class HubUnificationSystem:
    def __init__(self):
        self.root = Path("C:/Users/eunta/multi-agent-workspace")
        self.replacements = [
            # 경로 참조 통일
            ('docs/HUB.md', 'docs/CORE/HUB_ENHANCED.md'),
            ('docs\\HUB.md', 'docs\\CORE\\HUB_ENHANCED.md'),
            ('"docs/HUB.md"', '"docs/CORE/HUB_ENHANCED.md"'),
            ("'docs/HUB.md'", "'docs/CORE/HUB_ENHANCED.md'"),
            ('`docs/HUB.md`', '`docs/CORE/HUB_ENHANCED.md`'),
            
            # 코드에서의 참조
            ('HUB_PATH = ROOT / "docs" / "HUB.md"', 'HUB_PATH = get_workspace_path("docs", "CORE", "HUB_ENHANCED.md")'),
            ('hub_path = "docs/HUB.md"', 'hub_path = "docs/CORE/HUB_ENHANCED.md"'),
            ('legacy_hub_path = "docs/HUB.md"', 'legacy_hub_path = "docs/HUB.md"'),  # 레거시는 유지
            
            # 문서에서의 언급
            ('HUB.md', 'HUB_ENHANCED.md'),
            ('hub.md', 'hub_enhanced.md'),
        ]
        
        self.modified_files = []
        self.errors = []
        
    def should_process_file(self, file_path: Path) -> bool:
        """파일 처리 여부 결정"""
        # 제외할 패턴
        exclude_patterns = [
            '.git/',
            '__pycache__/',
            'node_modules/',
            '.venv/',
            'venv/',
            '.pytest_cache/',
        ]
        
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if pattern in file_str:
                return False
                
        # 처리할 확장자
        allowed_extensions = {'.py', '.md', '.json', '.yml', '.yaml', '.txt', '.ps1', '.bat'}
        return file_path.suffix.lower() in allowed_extensions
    
    def unify_file(self, file_path: Path) -> bool:
        """단일 파일의 HUB 참조 통일"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            original_content = content
            modified = False
            
            # 특별 처리: hub_unification.py는 자기 자신 제외
            if file_path.name == 'hub_unification.py':
                return False
                
            # legacy_hub_path가 있는 줄은 건드리지 않음
            lines = content.split('\n')
            safe_content = []
            for line in lines:
                if 'legacy_hub_path' in line or 'LEGACY_HUB' in line:
                    safe_content.append(line)
                else:
                    # 일반적인 교체 수행
                    modified_line = line
                    for old_text, new_text in self.replacements:
                        if old_text in modified_line and 'legacy' not in modified_line.lower():
                            modified_line = modified_line.replace(old_text, new_text)
                            modified = True
                    safe_content.append(modified_line)
            
            content = '\n'.join(safe_content)
            
            # 변경사항이 있으면 파일 저장
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modified_files.append(str(file_path))
                return True
                
            return False
            
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            return False
    
    def execute_unification(self) -> Dict:
        """HUB 통일 실행"""
        print("🚀 HUB 시스템 완전 통일 시작...")
        
        processed_files = 0
        for file_path in self.root.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                processed_files += 1
                
                if processed_files % 50 == 0:
                    print(f"처리 중... {processed_files}개 파일 완료")
                
                if self.unify_file(file_path):
                    print(f"✅ 통일됨: {file_path}")
        
        return {
            "modified_count": len(self.modified_files),
            "error_count": len(self.errors),
            "total_processed": processed_files
        }
    
    def create_backup_legacy_hub(self):
        """레거시 HUB 백업 생성"""
        legacy_hub = self.root / "docs" / "HUB.md"
        enhanced_hub = self.root / "docs" / "CORE" / "HUB_ENHANCED.md"
        
        if enhanced_hub.exists() and legacy_hub.exists():
            # 레거시를 REFERENCE로 이동
            ref_dir = self.root / "docs" / "REFERENCE"
            ref_dir.mkdir(exist_ok=True)
            
            backup_path = ref_dir / "LEGACY_HUB.md"
            with open(legacy_hub, 'r', encoding='utf-8') as f:
                content = f.read()
            
            backup_content = f"""# LEGACY HUB (백업)

⚠️ **이 파일은 백업용입니다.**  
현재 시스템은 `docs/CORE/HUB_ENHANCED.md`를 사용합니다.

---

{content}
"""
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            
            # 원본 삭제
            legacy_hub.unlink()
            print(f"✅ 레거시 HUB 백업: {backup_path}")

def main():
    system = HubUnificationSystem()
    
    # 1. 백업 생성
    system.create_backup_legacy_hub()
    
    # 2. 통일 실행
    results = system.execute_unification()
    
    print(f"\n🎯 HUB 통일 완료!")
    print(f"   📊 수정된 파일: {results['modified_count']}개")
    print(f"   ❌ 오류 발생: {results['error_count']}개") 
    print(f"   📁 전체 처리: {results['total_processed']}개")
    
    if system.modified_files[:10]:
        print(f"\n📝 수정된 파일들 (일부):")
        for file_path in system.modified_files[:10]:
            print(f"   - {file_path}")
    
    if system.errors:
        print(f"\n⚠️ 오류 발생 파일들:")
        for error in system.errors[:5]:
            print(f"   - {error}")

if __name__ == "__main__":
    main()