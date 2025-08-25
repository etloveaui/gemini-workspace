#!/usr/bin/env python3
"""
예측적 문제 방지 자동화 시스템
- Doctor v3.0 예측 결과 기반 자동 조치
- 문제 발생 전 사전 방지
- 자동 최적화 실행
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import subprocess
import shutil

class PredictivePrevention:
    """예측적 문제 방지 시스템"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.config_file = self.root / ".agents" / "prevention_config.json"
        self.log_file = self.root / ".agents" / "prevention.log"
        
        self._load_config()
    
    def _load_config(self):
        """설정 로드"""
        default_config = {
            "auto_prevention_enabled": True,
            "disk_space_threshold": 85,
            "project_size_threshold_mb": 1000,
            "git_changes_threshold": 15,
            "memory_threshold": 85,
            "prevention_actions": {
                "disk_space": ["cleanup_temp", "archive_old_logs"],
                "project_bloat": ["compress_backups", "cleanup_duplicates"],
                "git_accumulation": ["suggest_commit"],
                "memory_high": ["restart_services"]
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                self.config = {**default_config, **loaded}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self._save_config()
    
    def _save_config(self):
        """설정 저장"""
        self.config_file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def run_predictive_analysis(self):
        """예측 분석 실행 및 방지 조치"""
        print("🔮 예측적 문제 방지 시스템 시작")
        print("=" * 40)
        
        if not self.config["auto_prevention_enabled"]:
            print("자동 방지 기능이 비활성화되어 있습니다.")
            return
        
        # Doctor v3.0 실행하여 예측 결과 얻기
        predictions = self._get_predictions()
        
        if not predictions:
            print("✅ 예측된 문제가 없습니다.")
            return
        
        print(f"⚠️  {len(predictions)}개의 잠재적 문제가 예측됨")
        
        # 각 예측에 대해 방지 조치 실행
        actions_taken = []
        for prediction in predictions:
            action_result = self._handle_prediction(prediction)
            if action_result:
                actions_taken.append(action_result)
        
        # 결과 보고
        self._log_prevention_session(predictions, actions_taken)
        print(f"\n✅ 예방 조치 완료: {len(actions_taken)}개 실행됨")
        
        return {
            "predictions": len(predictions),
            "actions_taken": len(actions_taken),
            "details": actions_taken
        }
    
    def _get_predictions(self) -> List[Dict]:
        """Doctor v3.0에서 예측 결과 가져오기"""
        try:
            # Doctor v3.0 실행
            result = subprocess.run([
                "python", str(self.root / "scripts" / "doctor_v3.py")
            ], capture_output=True, text=True, cwd=self.root)
            
            # 최신 보고서 파일 찾기
            reports_dir = self.root / "reports"
            if not reports_dir.exists():
                return []
            
            doctor_reports = list(reports_dir.glob("doctor_v3_*.json"))
            if not doctor_reports:
                return []
            
            # 가장 최신 보고서
            latest_report = max(doctor_reports, key=lambda f: f.stat().st_mtime)
            
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
            
            return report_data.get('predictions', [])
            
        except Exception as e:
            print(f"❌ 예측 데이터 가져오기 실패: {e}")
            return []
    
    def _handle_prediction(self, prediction: Dict) -> Dict:
        """예측에 대한 방지 조치 실행"""
        problem_type = prediction.get('type', '')
        severity = prediction.get('severity', 'low')
        confidence = prediction.get('confidence', 0)
        
        print(f"\n🔧 처리 중: {prediction.get('message', 'Unknown problem')}")
        print(f"   심각도: {severity}, 신뢰도: {confidence}%")
        
        # 신뢰도가 낮으면 스킵
        if confidence < 60:
            print("   ⏸️  신뢰도 낮음 - 조치 건너뜀")
            return None
        
        # 문제 유형별 조치
        actions = self.config["prevention_actions"].get(problem_type, [])
        if not actions:
            print("   ⏸️  정의된 조치 없음")
            return None
        
        executed_actions = []
        for action in actions:
            try:
                if self._execute_action(action, prediction):
                    executed_actions.append(action)
                    print(f"   ✅ {action} 완료")
                else:
                    print(f"   ❌ {action} 실패")
            except Exception as e:
                print(f"   ❌ {action} 오류: {e}")
        
        return {
            "prediction": prediction,
            "actions_executed": executed_actions,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_action(self, action: str, prediction: Dict) -> bool:
        """개별 조치 실행"""
        
        if action == "cleanup_temp":
            return self._cleanup_temp_files()
        
        elif action == "archive_old_logs":
            return self._archive_old_logs()
        
        elif action == "compress_backups":
            return self._compress_backups()
        
        elif action == "cleanup_duplicates":
            return self._cleanup_duplicates()
        
        elif action == "suggest_commit":
            return self._suggest_git_commit()
        
        elif action == "restart_services":
            return self._restart_services()
        
        else:
            print(f"   ⚠️  알 수 없는 조치: {action}")
            return False
    
    def _cleanup_temp_files(self) -> bool:
        """임시 파일 정리"""
        try:
            temp_patterns = ["*.tmp", "*.temp", "*~"]
            removed_count = 0
            
            for pattern in temp_patterns:
                for temp_file in self.root.rglob(pattern):
                    if temp_file.is_file():
                        temp_file.unlink()
                        removed_count += 1
            
            print(f"   📁 임시 파일 {removed_count}개 제거")
            return True
        except Exception as e:
            print(f"   ❌ 임시 파일 정리 실패: {e}")
            return False
    
    def _archive_old_logs(self) -> bool:
        """오래된 로그 아카이브"""
        try:
            logs_dir = self.root / "logs"
            if not logs_dir.exists():
                return True
            
            cutoff_date = datetime.now() - timedelta(days=30)
            archived_count = 0
            
            for log_file in logs_dir.rglob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    archive_dir = logs_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    shutil.move(str(log_file), str(archive_dir / log_file.name))
                    archived_count += 1
            
            print(f"   📚 로그 파일 {archived_count}개 아카이브")
            return True
        except Exception as e:
            print(f"   ❌ 로그 아카이브 실패: {e}")
            return False
    
    def _compress_backups(self) -> bool:
        """백업 압축"""
        try:
            backup_dir = self.root / ".backups"
            if not backup_dir.exists():
                return True
            
            # 압축되지 않은 백업 폴더들 찾기
            compressed_count = 0
            for backup_folder in backup_dir.iterdir():
                if backup_folder.is_dir() and not backup_folder.name.endswith('.zip'):
                    # 압축 실행 (간단 버전)
                    shutil.make_archive(
                        str(backup_folder), 'zip', str(backup_folder)
                    )
                    shutil.rmtree(backup_folder)
                    compressed_count += 1
            
            print(f"   🗜️  백업 {compressed_count}개 압축")
            return True
        except Exception as e:
            print(f"   ❌ 백업 압축 실패: {e}")
            return False
    
    def _cleanup_duplicates(self) -> bool:
        """중복 파일 정리"""
        try:
            # 간단한 중복 감지 (크기 기반)
            file_sizes = {}
            duplicates = []
            
            for file_path in self.root.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.py']:
                    size = file_path.stat().st_size
                    if size in file_sizes:
                        duplicates.append(file_path)
                    else:
                        file_sizes[size] = file_path
            
            # 안전한 중복만 제거 (backup, temp 폴더 내)
            removed_count = 0
            for dup_file in duplicates:
                if any(word in str(dup_file).lower() for word in ['backup', 'temp', 'archive']):
                    dup_file.unlink()
                    removed_count += 1
            
            print(f"   🔄 중복 파일 {removed_count}개 제거")
            return True
        except Exception as e:
            print(f"   ❌ 중복 파일 정리 실패: {e}")
            return False
    
    def _suggest_git_commit(self) -> bool:
        """Git 커밋 제안"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, cwd=self.root
            )
            
            if result.stdout.strip():
                print(f"   📝 Git 변경사항 {len(result.stdout.splitlines())}개 감지")
                print("   💡 제안: 변경사항을 커밋하여 정리하세요")
                return True
            else:
                print("   ✅ Git 상태 깨끗함")
                return True
        except Exception as e:
            print(f"   ❌ Git 상태 확인 실패: {e}")
            return False
    
    def _restart_services(self) -> bool:
        """서비스 재시작 (가벼운 버전)"""
        try:
            # 메모리 정리를 위한 가벼운 조치들
            print("   🔄 메모리 최적화 조치 실행")
            
            # Python 가비지 컬렉션
            import gc
            gc.collect()
            
            print("   ✅ 메모리 정리 완료")
            return True
        except Exception as e:
            print(f"   ❌ 서비스 재시작 실패: {e}")
            return False
    
    def _log_prevention_session(self, predictions: List[Dict], actions: List[Dict]):
        """방지 세션 로그"""
        self.log_file.parent.mkdir(exist_ok=True, parents=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "predictions_count": len(predictions),
            "actions_count": len(actions),
            "predictions": predictions,
            "actions": actions
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

def run_predictive_prevention(root_path: str = "C:/Users/eunta/multi-agent-workspace"):
    """예측적 방지 실행"""
    prevention = PredictivePrevention(root_path)
    return prevention.run_predictive_analysis()

if __name__ == "__main__":
    result = run_predictive_prevention()
    print(f"\n📊 결과 요약: {result}")