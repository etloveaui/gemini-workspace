#!/usr/bin/env python3
"""
Git Push 최적화 시스템
- 작업 진행에 따른 자동 push 주기 관리
- 중요 변경사항 감지 및 즉시 push 권장
- 작업 세션별 push 패턴 분석 및 최적화
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

class GitPushOptimizer:
    """Git Push 최적화 시스템"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.config_file = self.workspace_path / ".agents" / "git_push_config.json"
        self.push_log_file = self.workspace_path / "logs" / "git_push_optimizer.log"
        
        # 기본 설정
        self.default_config = {
            "auto_push_enabled": True,
            "push_intervals": {
                "normal_work": 1800,      # 30분 (일반 작업)
                "critical_work": 300,     # 5분 (중요 작업)
                "experimental": 600,      # 10분 (실험적 작업)
                "documentation": 3600     # 1시간 (문서 작업)
            },
            "critical_files": [
                "CLAUDE.md",
                "GEMINI.md",
                "tasks.py",
                "main_generator.py",
                "*.py",
                "docs/HUB.md"
            ],
            "critical_changes": [
                "add new feature",
                "fix critical bug",
                "complete task",
                "system integration",
                "encoding fix",
                "pytest fix"
            ],
            "max_uncommitted_time": 7200,  # 2시간 (최대 미푸시 시간)
            "file_count_threshold": 10,     # 파일 변경 수 임계값
            "size_threshold_mb": 5          # 변경 크기 임계값 (MB)
        }
        
        self.config = self.load_config()
        self.last_push_time = None
        self.uncommitted_changes = []
        self.work_session_type = "normal_work"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉터리 생성"""
        self.config_file.parent.mkdir(exist_ok=True)
        self.push_log_file.parent.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 기본 설정과 병합
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
            else:
                # 기본 설정 파일 생성
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            self._log(f"설정 로드 오류, 기본값 사용: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log(f"설정 저장 오류: {e}")
    
    def _log(self, message: str, level: str = "INFO"):
        """로깅"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        try:
            with open(self.push_log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"로그 기록 실패: {e}")
    
    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Git 명령어 실행"""
        try:
            result = subprocess.run(
                command,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip() if result.stdout else result.stderr.strip()
        except Exception as e:
            return False, str(e)
    
    def get_git_status(self) -> Dict:
        """Git 상태 정보 수집"""
        status_info = {
            "has_changes": False,
            "staged_files": [],
            "unstaged_files": [],
            "untracked_files": [],
            "total_files": 0,
            "last_commit_time": None,
            "current_branch": "unknown"
        }
        
        # Git 상태 확인
        success, output = self._run_git_command(["git", "status", "--porcelain"])
        if success:
            lines = output.split('\n') if output else []
            for line in lines:
                if line.strip():
                    status_info["has_changes"] = True
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                        status_info["staged_files"].append(file_path)
                    if status_code[1] in ['M', 'D']:
                        status_info["unstaged_files"].append(file_path)
                    if status_code == "??":
                        status_info["untracked_files"].append(file_path)
        
        status_info["total_files"] = (
            len(status_info["staged_files"]) + 
            len(status_info["unstaged_files"]) + 
            len(status_info["untracked_files"])
        )
        
        # 현재 브랜치 확인
        success, output = self._run_git_command(["git", "branch", "--show-current"])
        if success and output:
            status_info["current_branch"] = output
        
        # 마지막 커밋 시간 확인
        success, output = self._run_git_command(["git", "log", "-1", "--format=%ct"])
        if success and output:
            try:
                timestamp = int(output)
                status_info["last_commit_time"] = datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                pass
        
        return status_info
    
    def analyze_changes(self, status_info: Dict) -> Dict:
        """변경사항 분석"""
        analysis = {
            "criticality": "low",
            "change_types": [],
            "critical_files_changed": [],
            "size_estimate_mb": 0,
            "requires_immediate_push": False,
            "recommended_interval": self.config["push_intervals"]["normal_work"]
        }
        
        all_changed_files = (
            status_info["staged_files"] + 
            status_info["unstaged_files"] + 
            status_info["untracked_files"]
        )
        
        # 중요 파일 변경 확인
        critical_patterns = self.config["critical_files"]
        for file_path in all_changed_files:
            for pattern in critical_patterns:
                if pattern.replace("*", "") in file_path or file_path.endswith(pattern.replace("*", "")):
                    analysis["critical_files_changed"].append(file_path)
                    analysis["criticality"] = "high"
        
        # 파일 수 기반 분석
        if status_info["total_files"] >= self.config["file_count_threshold"]:
            analysis["criticality"] = "medium" if analysis["criticality"] == "low" else analysis["criticality"]
        
        # 마지막 커밋 이후 시간 확인
        if status_info["last_commit_time"]:
            time_since_commit = datetime.now() - status_info["last_commit_time"]
            if time_since_commit.total_seconds() > self.config["max_uncommitted_time"]:
                analysis["requires_immediate_push"] = True
                analysis["criticality"] = "high"
        
        # 권장 push 간격 설정
        if analysis["criticality"] == "high":
            analysis["recommended_interval"] = self.config["push_intervals"]["critical_work"]
        elif analysis["criticality"] == "medium":
            analysis["recommended_interval"] = self.config["push_intervals"]["experimental"]
        
        return analysis
    
    def should_push_now(self, force_check: bool = False) -> Tuple[bool, str]:
        """현재 push가 필요한지 판단"""
        if not self.config["auto_push_enabled"] and not force_check:
            return False, "자동 push가 비활성화됨"
        
        status_info = self.get_git_status()
        if not status_info["has_changes"]:
            return False, "변경사항 없음"
        
        analysis = self.analyze_changes(status_info)
        
        # 즉시 push 필요한 경우
        if analysis["requires_immediate_push"]:
            return True, f"즉시 push 필요: {analysis['criticality']} 중요도, {len(analysis['critical_files_changed'])}개 중요 파일 변경"
        
        # 시간 기반 판단
        if self.last_push_time:
            time_since_push = (datetime.now() - self.last_push_time).total_seconds()
            if time_since_push >= analysis["recommended_interval"]:
                return True, f"권장 간격 도달: {time_since_push/60:.1f}분 경과 (권장: {analysis['recommended_interval']/60:.1f}분)"
        
        # 변경사항 규모 기반 판단
        if status_info["total_files"] >= self.config["file_count_threshold"]:
            return True, f"변경 파일 수 임계값 초과: {status_info['total_files']}개"
        
        return False, f"Push 불필요 (중요도: {analysis['criticality']}, 파일: {status_info['total_files']}개)"
    
    def execute_safe_push(self, commit_message: str = None) -> Tuple[bool, str]:
        """안전한 push 실행"""
        try:
            status_info = self.get_git_status()
            
            if not status_info["has_changes"]:
                return True, "변경사항이 없어 push하지 않음"
            
            # 스테이징되지 않은 변경사항이 있는 경우
            if status_info["unstaged_files"] or status_info["untracked_files"]:
                self._log("스테이징되지 않은 변경사항 발견, 자동 add 수행", "INFO")
                success, output = self._run_git_command(["git", "add", "."])
                if not success:
                    return False, f"git add 실패: {output}"
            
            # 커밋 메시지 생성
            if not commit_message:
                analysis = self.analyze_changes(status_info)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if analysis["critical_files_changed"]:
                    commit_message = f"작업 진행 업데이트: {len(analysis['critical_files_changed'])}개 핵심 파일 변경 ({timestamp})"
                else:
                    commit_message = f"정기 작업 백업 ({timestamp})"
            
            # 커밋
            success, output = self._run_git_command(["git", "commit", "-m", commit_message])
            if not success:
                if "nothing to commit" in output:
                    return True, "커밋할 내용 없음"
                else:
                    return False, f"커밋 실패: {output}"
            
            # Push
            success, output = self._run_git_command(["git", "push"])
            if success:
                self.last_push_time = datetime.now()
                self._log(f"성공적으로 push 완료: {commit_message}", "SUCCESS")
                return True, f"Push 성공: {commit_message}"
            else:
                return False, f"Push 실패: {output}"
        
        except Exception as e:
            return False, f"Push 중 예외 발생: {e}"
    
    def set_work_session_type(self, session_type: str):
        """작업 세션 타입 설정"""
        valid_types = list(self.config["push_intervals"].keys())
        if session_type in valid_types:
            self.work_session_type = session_type
            self._log(f"작업 세션 타입 변경: {session_type}")
        else:
            self._log(f"유효하지 않은 세션 타입: {session_type}. 유효한 타입: {valid_types}")
    
    def generate_push_recommendation(self) -> str:
        """Push 권장사항 생성"""
        status_info = self.get_git_status()
        analysis = self.analyze_changes(status_info)
        should_push, reason = self.should_push_now(force_check=True)
        
        report = f"# Git Push 최적화 권장사항\n\n"
        report += f"**분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 현재 상태
        report += "## 📊 현재 Git 상태\n\n"
        report += f"- **브랜치**: {status_info['current_branch']}\n"
        report += f"- **변경된 파일**: {status_info['total_files']}개\n"
        report += f"  - 스테이징됨: {len(status_info['staged_files'])}개\n"
        report += f"  - 수정됨: {len(status_info['unstaged_files'])}개\n"
        report += f"  - 추적 안됨: {len(status_info['untracked_files'])}개\n"
        
        if status_info["last_commit_time"]:
            time_since_commit = datetime.now() - status_info["last_commit_time"]
            report += f"- **마지막 커밋**: {time_since_commit.total_seconds()/3600:.1f}시간 전\n"
        
        report += f"- **변경 중요도**: {analysis['criticality'].upper()}\n\n"
        
        # 중요 파일 변경
        if analysis["critical_files_changed"]:
            report += "### ⚠️ 중요 파일 변경 감지\n"
            for file_path in analysis["critical_files_changed"]:
                report += f"- `{file_path}`\n"
            report += "\n"
        
        # Push 권장사항
        report += "## 🚀 Push 권장사항\n\n"
        if should_push:
            report += f"**✅ PUSH 권장**: {reason}\n\n"
            report += "### 권장 조치\n"
            report += "```bash\n"
            report += "# 자동 push 실행\n"
            report += "python scripts/git_push_optimizer.py --push\n\n"
            report += "# 또는 수동 push\n"
            report += "git add .\n"
            report += f"git commit -m \"작업 진행 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n"
            report += "git push\n"
            report += "```\n\n"
        else:
            report += f"**ℹ️ PUSH 불필요**: {reason}\n\n"
        
        # 최적화 제안
        report += "## 💡 최적화 제안\n\n"
        
        if analysis["criticality"] == "high":
            report += "### 🔥 고위험 변경사항\n"
            report += "- 즉시 백업을 위한 push 권장\n"
            report += "- 중요 파일 변경은 5분 간격으로 push\n\n"
        
        report += "### 일반적인 Push 전략\n"
        report += f"- **일반 작업**: {self.config['push_intervals']['normal_work']//60}분 간격\n"
        report += f"- **중요 작업**: {self.config['push_intervals']['critical_work']//60}분 간격\n"
        report += f"- **실험적 작업**: {self.config['push_intervals']['experimental']//60}분 간격\n"
        report += f"- **문서 작업**: {self.config['push_intervals']['documentation']//60}분 간격\n\n"
        
        report += "### 🎛️ 설정 조정\n"
        report += "```bash\n"
        report += "# 작업 세션 타입 변경\n"
        report += "python scripts/git_push_optimizer.py --session critical_work\n\n"
        report += "# 자동 push 활성화/비활성화\n"
        report += "python scripts/git_push_optimizer.py --toggle-auto\n"
        report += "```\n\n"
        
        return report

def main():
    """Git Push 최적화 메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Push 최적화 시스템")
    parser.add_argument("--check", action="store_true", help="Push 필요 여부 확인")
    parser.add_argument("--push", action="store_true", help="안전한 push 실행")
    parser.add_argument("--report", action="store_true", help="Push 권장사항 보고서 생성")
    parser.add_argument("--session", choices=["normal_work", "critical_work", "experimental", "documentation"],
                       help="작업 세션 타입 설정")
    parser.add_argument("--toggle-auto", action="store_true", help="자동 push 토글")
    parser.add_argument("--message", "-m", help="커밋 메시지")
    
    args = parser.parse_args()
    
    optimizer = GitPushOptimizer()
    
    if args.session:
        optimizer.set_work_session_type(args.session)
        print(f"작업 세션 타입이 '{args.session}'으로 설정되었습니다.")
    
    elif args.toggle_auto:
        optimizer.config["auto_push_enabled"] = not optimizer.config["auto_push_enabled"]
        optimizer.save_config(optimizer.config)
        status = "활성화" if optimizer.config["auto_push_enabled"] else "비활성화"
        print(f"자동 push가 {status}되었습니다.")
    
    elif args.push:
        success, message = optimizer.execute_safe_push(args.message)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            sys.exit(1)
    
    elif args.check:
        should_push, reason = optimizer.should_push_now(force_check=True)
        if should_push:
            print(f"🚀 Push 권장: {reason}")
        else:
            print(f"ℹ️ Push 불필요: {reason}")
    
    elif args.report:
        report = optimizer.generate_push_recommendation()
        print(report)
        
        # 파일로도 저장
        report_file = optimizer.workspace_path / "docs" / "git_push_optimization.md"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 보고서 저장됨: {report_file}")
    
    else:
        # 기본: 상태 확인 및 권장사항
        should_push, reason = optimizer.should_push_now(force_check=True)
        print(f"\n📊 Git Push 상태")
        print("="*40)
        
        if should_push:
            print(f"🚀 Push 권장: {reason}")
            print("\n실행 명령:")
            print("python scripts/git_push_optimizer.py --push")
        else:
            print(f"ℹ️ Push 불필요: {reason}")
        
        print("\n더 자세한 분석:")
        print("python scripts/git_push_optimizer.py --report")
        print("="*40)

if __name__ == "__main__":
    main()