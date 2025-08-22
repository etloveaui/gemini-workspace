"""
환경별 자동 설정 시스템
집/회사 감지되면 다른 설정을 자동으로 적용
"""
import json
from pathlib import Path
import shutil
import sys
sys.path.append(str(Path(__file__).parent))
from cli_style import header, kv, status_line
from environment_detector import detect_environment, get_current_environment_summary

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / ".agents" / "environment_configs"

class EnvironmentAutoConfig:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_default_configs(self):
        """기본 환경별 설정 생성"""
        configs = {
            "company": {
                "name": "회사 환경",
                "settings": {
                    "backup_interval": 1800,  # 30분
                    "log_level": "INFO",
                    "auto_commit": False,  # 회사에서는 신중하게
                    "token_limit_warning": 0.7,  # 70%에서 경고
                    "sync_enabled": True,
                    "performance_mode": "balanced"
                },
                "vscode_settings": {
                    "terminal.integrated.fontSize": 14,
                    "editor.fontSize": 14,
                    "workbench.colorTheme": "Dark+ (default dark)"
                },
                "shortcuts": {
                    "claude": "claude --model gpt-4",
                    "codex": "codex --suggest", 
                    "gemini": "gemini --conservative"
                }
            },
            "home": {
                "name": "집 환경", 
                "settings": {
                    "backup_interval": 3600,  # 1시간
                    "log_level": "DEBUG", 
                    "auto_commit": True,  # 집에서는 편하게
                    "token_limit_warning": 0.8,  # 80%에서 경고
                    "sync_enabled": True,
                    "performance_mode": "performance"
                },
                "vscode_settings": {
                    "terminal.integrated.fontSize": 16,
                    "editor.fontSize": 16, 
                    "workbench.colorTheme": "Monokai"
                },
                "shortcuts": {
                    "claude": "claude --model gpt-4o",
                    "codex": "codex --auto-edit",
                    "gemini": "gemini --creative"
                }
            },
            "laptop": {
                "name": "노트북 환경",
                "settings": {
                    "backup_interval": 2400,  # 40분
                    "log_level": "WARN",
                    "auto_commit": False,
                    "token_limit_warning": 0.6,  # 배터리 고려해서 더 빡빡하게
                    "sync_enabled": False,  # 네트워크 절약
                    "performance_mode": "battery_saver"
                },
                "vscode_settings": {
                    "terminal.integrated.fontSize": 12,
                    "editor.fontSize": 12,
                    "workbench.colorTheme": "Light+ (default light)"
                },
                "shortcuts": {
                    "claude": "claude --model claude-3-haiku",
                    "codex": "codex --suggest",
                    "gemini": "gemini --efficient"
                }
            }
        }
        
        for env_name, config in configs.items():
            config_file = self.config_dir / f"{env_name}_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(kv(f"{env_name} 설정", f"{config_file.name} 생성"))
    
    def detect_and_apply_config(self):
        """현재 환경 감지하고 설정 적용"""
        print(header("환경별 자동 설정 적용"))
        
        # 현재 환경 감지
        env_summary = get_current_environment_summary()
        current_env = env_summary["location"]
        confidence = env_summary["confidence"]
        
        print(kv("감지된 환경", f"{current_env} ({confidence}% 확신)"))
        
        if confidence < 50:
            print(status_line(1, "WARN", "환경 감지", "확신도 낮음 - 기본 설정 유지"))
            return False
        
        # 해당 환경 설정 로드
        config_file = self.config_dir / f"{current_env}_config.json"
        if not config_file.exists():
            print(status_line(2, "ERROR", "설정 파일", f"{current_env}_config.json 없음"))
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(kv("적용할 설정", config["name"]))
        
        # 설정 적용
        self.apply_environment_config(config)
        
        # 적용 기록
        self.save_current_config(current_env, config)
        
        return True
    
    def apply_environment_config(self, config):
        """실제 설정 적용"""
        settings = config["settings"]
        
        # 1. 시스템 설정 파일 업데이트
        system_config = ROOT / ".agents" / "current_config.json"
        with open(system_config, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        print(status_line(1, "OK", "시스템 설정", "적용됨"))
        
        # 2. VS Code 설정 적용 (있으면)
        if "vscode_settings" in config:
            vscode_settings_file = ROOT / ".vscode" / "settings.json"
            if vscode_settings_file.exists():
                # 기존 설정과 병합
                try:
                    with open(vscode_settings_file, 'r', encoding='utf-8') as f:
                        existing_settings = json.load(f)
                except:
                    existing_settings = {}
                
                existing_settings.update(config["vscode_settings"])
                
                with open(vscode_settings_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_settings, f, indent=2)
                print(status_line(2, "OK", "VS Code 설정", "적용됨"))
        
        # 3. 단축 명령어 설정 (선택사항)
        if "shortcuts" in config:
            shortcuts_file = ROOT / ".agents" / "shortcuts.json"  
            with open(shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump(config["shortcuts"], f, indent=2)
            print(status_line(3, "OK", "단축 명령어", "적용됨"))
    
    def save_current_config(self, env_name, config):
        """현재 적용된 설정 기록"""
        from datetime import datetime
        
        record = {
            "environment": env_name,
            "config_name": config["name"],
            "applied_at": datetime.now().isoformat(),
            "settings": config["settings"]
        }
        
        record_file = ROOT / ".agents" / "last_applied_config.json"
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
    
    def get_current_config(self):
        """현재 적용된 설정 조회"""
        record_file = ROOT / ".agents" / "last_applied_config.json"
        if record_file.exists():
            with open(record_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

def main():
    """메인 실행"""
    import argparse
    parser = argparse.ArgumentParser(description='환경별 자동 설정')
    parser.add_argument('--init', action='store_true', help='기본 설정 생성')
    parser.add_argument('--apply', action='store_true', help='환경 감지하고 설정 적용')
    parser.add_argument('--status', action='store_true', help='현재 설정 상태')
    
    args = parser.parse_args()
    
    auto_config = EnvironmentAutoConfig()
    
    if args.init:
        print(header("기본 환경 설정 생성"))
        auto_config.create_default_configs()
    elif args.apply:
        auto_config.detect_and_apply_config()
    elif args.status:
        current = auto_config.get_current_config()
        if current:
            print(header("현재 적용된 설정"))
            print(kv("환경", current["environment"]))
            print(kv("설정명", current["config_name"]))
            print(kv("적용 시각", current["applied_at"]))
        else:
            print("적용된 설정이 없습니다.")
    else:
        auto_config.detect_and_apply_config()

if __name__ == "__main__":
    main()