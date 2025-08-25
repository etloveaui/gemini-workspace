#!/usr/bin/env python3
"""
환경별 경로 관리 시스템
- 모든 환경에서 동적으로 올바른 경로 생성
- 하드코딩된 경로 문제 완전 해결
"""
import os
import platform
from pathlib import Path
from typing import Dict, Optional
import json
import socket

class EnvironmentPathManager:
    def __init__(self):
        self.current_user = self._get_current_user()
        self.hostname = socket.gethostname()
        self.platform = platform.system()
        self.workspace_root = self._find_workspace_root()
        self.environment_id = self._generate_environment_id()
        
        # 환경별 프로필 로드
        self.profile = self._load_environment_profile()
        
    def _get_current_user(self) -> str:
        """현재 사용자 이름 가져오기"""
        return os.environ.get('USERNAME') or os.environ.get('USER') or 'unknown'
    
    def _find_workspace_root(self) -> Path:
        """워크스페이스 루트 디렉터리 찾기"""
        # 현재 스크립트 위치에서 상위로 올라가며 찾기
        current = Path(__file__).resolve()
        
        # 최대 5단계까지 상위 디렉터리 검색
        for _ in range(5):
            current = current.parent
            if (current / '.agents').exists() or (current / 'ma.py').exists():
                return current
                
        # 못 찾으면 현재 사용자의 multi-agent-workspace 추정
        if self.platform == "Windows":
            return Path(f"C:/Users/{self.current_user}/multi-agent-workspace")
        else:
            return Path(f"/home/{self.current_user}/multi-agent-workspace")
    
    def _generate_environment_id(self) -> str:
        """환경 고유 ID 생성 (hostname-user)"""
        return f"{self.hostname}-{self.current_user}"
    
    def _load_environment_profile(self) -> Dict:
        """환경별 프로필 로드"""
        profile_path = self.workspace_root / ".agents" / "environment_profiles" / f"{self.hostname}.json"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 기본 프로필 생성
        return {
            "system": {
                "hostname": self.hostname,
                "user": self.current_user,
                "working_directory": str(self.workspace_root),
                "platform": self.platform
            },
            "paths": {
                "workspace_root": str(self.workspace_root),
                "user_home": str(Path.home()),
                "temp_dir": str(Path.home() / "temp" / "multi_agent_workspace")
            }
        }
    
    def get_workspace_path(self, *subpaths) -> Path:
        """워크스페이스 내 경로 생성"""
        return self.workspace_root.joinpath(*subpaths)
    
    def get_user_path(self, *subpaths) -> Path:
        """사용자 홈 디렉터리 기반 경로"""
        return Path.home().joinpath(*subpaths)
    
    def get_temp_path(self, *subpaths) -> Path:
        """임시 디렉터리 경로 (환경별 분리)"""
        import tempfile
        base_temp = Path(tempfile.gettempdir()) / "multi_agent_workspace" / self.environment_id
        base_temp.mkdir(parents=True, exist_ok=True)
        return base_temp.joinpath(*subpaths)
    
    def get_reports_path(self, *subpaths) -> Path:
        """리포트 디렉터리 경로"""
        reports_dir = self.get_workspace_path("reports")
        reports_dir.mkdir(exist_ok=True)
        return reports_dir.joinpath(*subpaths)
    
    def get_logs_path(self, *subpaths) -> Path:
        """로그 디렉터리 경로"""
        logs_dir = self.get_workspace_path("logs")
        logs_dir.mkdir(exist_ok=True)
        return logs_dir.joinpath(*subpaths)
    
    def replace_hardcoded_path(self, path_str: str) -> str:
        """하드코딩된 경로를 현재 환경에 맞게 변경"""
        if not isinstance(path_str, str):
            return path_str
            
        # Windows 경로 패턴들
        patterns = [
            r'C:\\Users\\etlov\\multi-agent-workspace',
            r'C:\Users\eunta\multi-agent-workspace', 
            r'C:\Users\eunta\multi-agent-workspace',
            # 다른 사용자 이름도 대응
            r'C:\\Users\\[^\\]+\\multi-agent-workspace',
            r'C:\Users\[^\]+\multi-agent-workspace'
        ]
        
        # 현재 워크스페이스 경로로 교체
        result = path_str
        import re
        
        # 정확한 패턴 매칭으로 교체
        old_patterns = [
            'C:\\\\Users\\\\eunta\\\\multi-agent-workspace',
            'C:\\\\Users\\\\etlov\\\\multi-agent-workspace',
            'C:/Users/eunta/multi-agent-workspace'
        ]
        
        for pattern in old_patterns:
            if pattern in result:
                result = result.replace(pattern, str(self.workspace_root))
        
        return result
    
    def create_environment_profile(self) -> None:
        """현재 환경 프로필 생성/업데이트"""
        profile_dir = self.get_workspace_path(".agents", "environment_profiles")
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_path = profile_dir / f"{self.hostname}.json"
        
        profile_data = {
            "system": {
                "timestamp": str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now()),
                "hostname": self.hostname,
                "platform": platform.platform(),
                "user": self.current_user,
                "working_directory": str(self.workspace_root),
                "local_ip": self._get_local_ip()
            },
            "paths": {
                "workspace_root": str(self.workspace_root),
                "user_home": str(Path.home()),
                "temp_dir": str(self.get_temp_path()),
                "reports_dir": str(self.get_reports_path()),
                "logs_dir": str(self.get_logs_path())
            },
            "environment_id": self.environment_id
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] 환경 프로필 생성: {profile_path}")
    
    def _get_local_ip(self) -> str:
        """로컬 IP 주소 가져오기"""
        try:
            # 임시 소켓으로 로컬 IP 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "unknown"
    
    def get_environment_info(self) -> Dict:
        """현재 환경 정보 반환"""
        return {
            "environment_id": self.environment_id,
            "user": self.current_user,
            "hostname": self.hostname,
            "platform": self.platform,
            "workspace_root": str(self.workspace_root),
            "profile_loaded": bool(self.profile)
        }

# 전역 인스턴스 (다른 스크립트에서 import하여 사용)
path_manager = EnvironmentPathManager()

def get_workspace_path(*subpaths):
    """전역 함수: 워크스페이스 경로 획득"""
    return path_manager.get_workspace_path(*subpaths)

def get_reports_path(*subpaths):
    """전역 함수: 리포트 경로 획득"""  
    return path_manager.get_reports_path(*subpaths)

def get_logs_path(*subpaths):
    """전역 함수: 로그 경로 획득"""
    return path_manager.get_logs_path(*subpaths)

def replace_hardcoded_path(path_str):
    """전역 함수: 하드코딩된 경로 교체"""
    return path_manager.replace_hardcoded_path(path_str)

if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    # CLI 실행 모드
    if len(sys.argv) > 1 and sys.argv[1] == "--create-profile":
        path_manager.create_environment_profile()
    
    # 환경 정보 출력
    info = path_manager.get_environment_info()
    print("=== 환경 경로 관리 시스템 ===")
    print(f"환경 ID: {info['environment_id']}")
    print(f"사용자: {info['user']}")
    print(f"호스트: {info['hostname']}")
    print(f"워크스페이스: {info['workspace_root']}")
    print(f"프로필 로드: {'OK' if info['profile_loaded'] else 'FAILED'}")