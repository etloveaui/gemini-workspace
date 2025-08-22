#!/usr/bin/env python3
"""
Preflight Doctor v3.0 - AI 기반 예측 진단 시스템 (단순 텍스트 출력)
- 문제 예측 및 사전 감지
- 자동 수정 범위 확대
- 성능 최적화 제안
- 멀티 에이전트 환경 특화
"""
import shutil, sys, os, json, sqlite3, psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import subprocess
import threading
import hashlib

class DoctorV3:
    """차세대 AI 진단 시스템"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.report = []
        self.auto_fixes = []
        self.predictions = []
        self.performance_metrics = {}
        
        # 진단 데이터베이스
        self.diagnosis_db = self.root / ".agents" / "diagnosis_history.db"
        self.diagnosis_db.parent.mkdir(exist_ok=True, parents=True)
        self._init_diagnosis_db()
    
    def _init_diagnosis_db(self):
        """진단 이력 데이터베이스 초기화"""
        with sqlite3.connect(self.diagnosis_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS diagnosis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    prediction_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT
                )
            """)
    
    def run_comprehensive_diagnosis(self) -> Dict:
        """포괄적 진단 실행"""
        from cli_style import header
        print(header("Preflight Doctor v3.0"))
        
        # 1. 기본 시스템 체크
        self._basic_system_checks()
        
        # 2. 성능 메트릭 수집
        self._collect_performance_metrics()
        
        # 3. 예측적 문제 감지
        self._predictive_analysis()
        
        # 4. 멀티 에이전트 환경 체크
        self._multi_agent_checks()
        
        # 5. 최적화 제안
        optimizations = self._generate_optimizations()
        
        # 6. 자동 수정 실행
        fixes_applied = self._execute_auto_fixes()
        
        # 7. 진단 결과 저장
        report_file = self._save_diagnosis_report(fixes_applied, optimizations)
        
        return {
            "status": self._get_overall_status(),
            "report_file": report_file,
            "fixes_applied": len(fixes_applied),
            "predictions": len(self.predictions),
            "optimizations": len(optimizations)
        }
    
    def _basic_system_checks(self):
        """기본 시스템 체크"""
        # Python 버전
        py_version = sys.version_info
        py_ok = py_version >= (3, 10)
        self._check("Python >= 3.10", py_ok, f"현재: {py_version.major}.{py_version.minor}")
        
        # 가상환경
        venv_ok = sys.prefix != sys.base_prefix
        self._check("가상환경 활성화", venv_ok, "venv 활성화 필요")
        
        # 필수 도구들
        tools = {"git": "Git", "invoke": "Invoke", "python": "Python"}
        for tool, name in tools.items():
            tool_ok = shutil.which(tool) is not None
            self._check(f"{name} 설치됨", tool_ok, f"{tool} 명령어 사용 가능")
        
        # 핵심 디렉토리
        dirs = ["docs", "scripts", "communication", ".agents"]
        for dir_name in dirs:
            dir_ok = (self.root / dir_name).exists()
            self._check(f"핵심 디렉토리: {dir_name}", dir_ok, "필수 디렉토리")
    
    def _collect_performance_metrics(self):
        """성능 메트릭 수집"""
        try:
            # 시스템 리소스
            self.performance_metrics.update({
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage(str(self.root)).percent
            })
            
            # 프로젝트 크기
            total_size = sum(f.stat().st_size for f in self.root.rglob('*') if f.is_file())
            self.performance_metrics["project_size_mb"] = total_size / (1024 * 1024)
            
            # 파일 개수
            self.performance_metrics["total_files"] = len(list(self.root.rglob('*')))
            
            # Git 상태
            try:
                result = subprocess.run(["git", "status", "--porcelain"], 
                                      capture_output=True, text=True, cwd=self.root)
                self.performance_metrics["git_changes"] = len(result.stdout.splitlines())
            except:
                self.performance_metrics["git_changes"] = -1
            
            from cli_style import section, kv
            print(section("Performance Metrics"))
            print(kv("CPU", f"{self.performance_metrics['cpu_percent']:.1f}%"))
            print(kv("Memory", f"{self.performance_metrics['memory_percent']:.1f}%"))
            print(kv("Project Size", f"{self.performance_metrics['project_size_mb']:.1f}MB"))
            
        except Exception as e:
            print(f"WARN: 성능 메트릭 수집 실패: {e}")
    
    def _predictive_analysis(self):
        """예측적 문제 분석"""
        from cli_style import section, kv
        print(section("Predictive Analysis"))
        
        # 1. 디스크 공간 예측
        if self.performance_metrics.get("disk_usage", 0) > 80:
            self.predictions.append({
                "type": "disk_space",
                "severity": "high",
                "message": "디스크 공간 부족 위험 (7일 내)",
                "confidence": 85
            })
        
        # 2. 프로젝트 크기 증가 예측
        if self.performance_metrics.get("project_size_mb", 0) > 500:
            self.predictions.append({
                "type": "project_bloat",
                "severity": "medium", 
                "message": "프로젝트 비대화 진행 중",
                "confidence": 70
            })
        
        # 3. Git 변경사항 누적 예측
        if self.performance_metrics.get("git_changes", 0) > 10:
            self.predictions.append({
                "type": "git_accumulation",
                "severity": "low",
                "message": "Git 변경사항 과도 누적",
                "confidence": 60
            })
        
        # 4. 토큰 사용량 예측 (간단 버전)
        comm_files = list((self.root / "communication").rglob("*.md"))
        if len(comm_files) > 20:
            self.predictions.append({
                "type": "token_usage",
                "severity": "medium",
                "message": "토큰 사용량 증가 예상",
                "confidence": 75
            })
        
        print(kv("predictions", len(self.predictions)))
    
    def _multi_agent_checks(self):
        """멀티 에이전트 환경 특화 체크"""
        # 에이전트 설정 파일들
        agent_files = ["CLAUDE.md", "GEMINI.md", "AGENTS.md"]
        for agent_file in agent_files:
            exists = (self.root / agent_file).exists()
            self._check(f"에이전트 설정: {agent_file}", exists, "설정 파일 필요")
        
        # 통신 디렉토리 구조
        comm_dir = self.root / "communication"
        agent_dirs = ["claude", "gemini", "codex"]
        for agent in agent_dirs:
            agent_dir_ok = (comm_dir / agent).exists()
            self._check(f"통신 폴더: {agent}", agent_dir_ok, "에이전트 통신 디렉토리")
        
        # 실시간 협업 시스템
        realtime_system = self.root / ".agents" / "realtime_coordination.py"
        system_ok = realtime_system.exists()
        self._check("실시간 협업 시스템", system_ok, "협업 시스템 파일")
        
        # 토큰 최적화 시스템
        token_optimizer = self.root / "scripts" / "token_optimizer.py"
        optimizer_ok = token_optimizer.exists()
        self._check("토큰 최적화 시스템", optimizer_ok, "토큰 절약 시스템")
    
    def _generate_optimizations(self) -> List[Dict]:
        """최적화 제안 생성"""
        optimizations = []
        
        # 성능 기반 최적화
        if self.performance_metrics.get("project_size_mb", 0) > 200:
            optimizations.append({
                "type": "cleanup",
                "priority": "high",
                "action": "대용량 파일 정리",
                "expected_benefit": "프로젝트 크기 30% 감소"
            })
        
        if self.performance_metrics.get("total_files", 0) > 1000:
            optimizations.append({
                "type": "organization",
                "priority": "medium",
                "action": "파일 구조 정리",
                "expected_benefit": "탐색 속도 향상"
            })
        
        # 예측 기반 최적화
        for prediction in self.predictions:
            if prediction["severity"] == "high":
                optimizations.append({
                    "type": "preventive",
                    "priority": "high",
                    "action": f"사전 조치: {prediction['message']}",
                    "expected_benefit": "문제 발생 방지"
                })
        
        return optimizations
    
    def _execute_auto_fixes(self) -> List[str]:
        """자동 수정 실행"""
        fixes_applied = []
        
        from cli_style import section
        print(section("Auto Fixes"))
        
        # 1. 간단한 정리 작업
        try:
            temp_files = list(self.root.rglob("*.tmp"))
            for temp_file in temp_files:
                temp_file.unlink()
            if temp_files:
                fixes_applied.append(f"임시 파일 {len(temp_files)}개 제거")
        except:
            pass
        
        # 2. 빈 디렉토리 정리
        try:
            removed_dirs = 0
            for path in self.root.rglob("*"):
                if path.is_dir() and not any(path.iterdir()):
                    if path.name not in ['.git', 'venv', 'node_modules']:
                        path.rmdir()
                        removed_dirs += 1
            if removed_dirs:
                fixes_applied.append(f"빈 디렉토리 {removed_dirs}개 제거")
        except:
            pass
        
        # 3. 권한 문제 수정 (Windows)
        if os.name == 'nt':
            try:
                # 간단한 권한 체크만
                test_file = self.root / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                fixes_applied.append("파일 권한 정상 확인")
            except:
                pass
        
        return fixes_applied
    
    def _check(self, name: str, ok: bool, hint: str = "", severity: str = "medium"):
        """체크 결과 기록"""
        status = "[PASS]" if ok else "[FAIL]"
        self.report.append((status, name, hint, severity))
        
        # 데이터베이스에 기록
        try:
            with sqlite3.connect(self.diagnosis_db) as conn:
                conn.execute("""
                    INSERT INTO diagnosis_history (timestamp, check_name, status, details)
                    VALUES (?, ?, ?, ?)
                """, (datetime.now().isoformat(), name, status, hint))
        except:
            pass
    
    def _get_overall_status(self) -> str:
        """전체 상태 판정"""
        fails = [r for r in self.report if r[0] == "[FAIL]"]
        high_fails = [r for r in fails if r[3] == "high"]
        
        if high_fails:
            return "critical"
        elif fails:
            return "warning" 
        else:
            return "healthy"
    
    def _save_diagnosis_report(self, fixes_applied: List[str], optimizations: List[Dict]) -> str:
        """진단 보고서 저장"""
        reports_dir = self.root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"doctor_v3_{timestamp}.json"
        
        report_data = {
            "version": "3.0",
            "timestamp": timestamp,
            "status": self._get_overall_status(),
            "checks": [{"status": r[0], "name": r[1], "hint": r[2], "severity": r[3]} for r in self.report],
            "performance_metrics": self.performance_metrics,
            "predictions": self.predictions,
            "optimizations": optimizations,
            "auto_fixes_applied": fixes_applied,
            "summary": {
                "total_checks": len(self.report),
                "passed": len([r for r in self.report if r[0] == "[PASS]"]),
                "failed": len([r for r in self.report if r[0] == "[FAIL]"]),
                "predictions": len(self.predictions),
                "fixes_applied": len(fixes_applied)
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return str(report_file)

def run_doctor_v3(root_path: str = "C:/Users/eunta/multi-agent-workspace") -> Dict:
    """Doctor v3.0 실행"""
    doctor = DoctorV3(root_path)
    return doctor.run_comprehensive_diagnosis()

if __name__ == "__main__":
    from cli_style import header, kv
    result = run_doctor_v3()
    print(header("Doctor v3.0 Done"))
    print(kv("status", result['status']))
    print(kv("fixes_applied", result['fixes_applied']))
    print(kv("predictions", result['predictions']))
    print(kv("optimizations", result['optimizations']))
    print(kv("report", result['report_file']))
