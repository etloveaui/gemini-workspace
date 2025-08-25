#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HUB 경로 중앙 관리 시스템
- 하드코딩된 HUB 경로 문제 해결
- 동적 경로 관리로 유연성 확보
"""
import json
import os
from pathlib import Path
from typing import Optional

# 환경 경로 관리 시스템 사용
import sys
sys.path.append(str(Path(__file__).parent))
from environment_path_manager import get_workspace_path

class HubPathManager:
    def __init__(self):
        self.workspace_root = get_workspace_path()
        self.config_file = get_workspace_path(".agents", "config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 기본 설정과 병합
                default = self._default_config()
                default.update(config)
                return default
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")
                return self._default_config()
        else:
            return self._default_config()
    
    def _default_config(self) -> dict:
        """기본 설정"""
        return {
            "active": "gemini",
            "hub_path": "docs/CORE/HUB_ENHANCED.md",
            "legacy_hub_path": "docs/HUB.md",
            "paths": {
                "hub_primary": "docs/CORE/HUB_ENHANCED.md",
                "hub_legacy": "docs/HUB.md",
                "agents_checklist": "docs/CORE/AGENTS_CHECKLIST.md"
            }
        }
    
    def get_hub_path(self, use_legacy: bool = False) -> Path:
        """HUB 파일 경로 가져오기"""
        if use_legacy:
            # legacy=True는 실제로는 현재 표준인 HUB_ENHANCED.md를 의미
            hub_path = self.config.get("hub_path", "docs/CORE/HUB_ENHANCED.md")
        else:
            hub_path = self.config.get("hub_path", "docs/CORE/HUB_ENHANCED.md")
        
        return get_workspace_path(hub_path)
    
    def get_primary_hub_path(self) -> Path:
        """주 HUB 파일 경로"""
        return get_workspace_path(self.config["paths"]["hub_primary"])
    
    def get_legacy_hub_path(self) -> Path:
        """레거시 HUB 파일 경로"""
        return get_workspace_path(self.config["paths"]["hub_legacy"])
    
    def sync_hub_files(self) -> bool:
        """HUB 파일들 동기화 (primary -> legacy)"""
        try:
            primary_path = self.get_primary_hub_path()
            legacy_path = self.get_legacy_hub_path()
            
            if primary_path.exists():
                # 주 파일의 내용을 레거시 파일에 복사
                with open(primary_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 레거시 파일에 호환성 메모 추가
                sync_note = f"""
---

**⚠️ 참고**: 이 파일은 임시 호환성을 위한 파일입니다. 
실제 시스템 표준은 `{self.config["paths"]["hub_primary"]}`를 참조하세요.
자동 동기화 시간: {Path(__file__).stat().st_mtime}
"""
                
                with open(legacy_path, 'w', encoding='utf-8') as f:
                    f.write(content + sync_note)
                
                print(f"HUB 파일 동기화 완료: {primary_path} -> {legacy_path}")
                return True
            else:
                print(f"주 HUB 파일이 존재하지 않음: {primary_path}")
                return False
                
        except Exception as e:
            print(f"HUB 파일 동기화 실패: {e}")
            return False
    
    def update_config(self, new_config: dict) -> bool:
        """설정 업데이트"""
        try:
            self.config.update(new_config)
            
            # 설정 파일 디렉터리 생성
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"설정 업데이트 완료: {self.config_file}")
            return True
        except Exception as e:
            print(f"설정 업데이트 실패: {e}")
            return False
    
    def get_agents_checklist_path(self) -> Path:
        """에이전트 체크리스트 경로"""
        return get_workspace_path(self.config["paths"]["agents_checklist"])
    
    def get_all_hub_paths(self) -> dict:
        """모든 HUB 관련 경로 반환"""
        return {
            "primary": str(self.get_primary_hub_path()),
            "legacy": str(self.get_legacy_hub_path()),
            "checklist": str(self.get_agents_checklist_path()),
            "workspace_root": str(self.workspace_root)
        }

# 전역 인스턴스
hub_manager = HubPathManager()

def get_hub_path(use_legacy: bool = False) -> Path:
    """전역 함수: HUB 경로 가져오기"""
    return hub_manager.get_hub_path(use_legacy=use_legacy)

def sync_hub_files():
    """전역 함수: HUB 파일 동기화"""
    return hub_manager.sync_hub_files()

def get_all_hub_paths():
    """전역 함수: 모든 HUB 경로"""
    return hub_manager.get_all_hub_paths()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            success = sync_hub_files()
            sys.exit(0 if success else 1)
        elif command == "paths":
            paths = get_all_hub_paths()
            print("=== HUB 경로 정보 ===")
            for key, path in paths.items():
                print(f"{key}: {path}")
        elif command == "test":
            # 경로 테스트
            primary = hub_manager.get_primary_hub_path()
            legacy = hub_manager.get_legacy_hub_path()
            print(f"Primary HUB: {primary} (exists: {primary.exists()})")
            print(f"Legacy HUB: {legacy} (exists: {legacy.exists()})")
    else:
        print("사용법:")
        print("  python scripts/hub_path_manager.py sync   # HUB 파일 동기화")
        print("  python scripts/hub_path_manager.py paths  # 경로 정보 출력")
        print("  python scripts/hub_path_manager.py test   # 경로 테스트")