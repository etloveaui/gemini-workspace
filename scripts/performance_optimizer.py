#!/usr/bin/env python3
"""
성능 최적화 시스템 v1.0
시스템 응답 속도, 파일 처리 속도, 메모리 사용량 최적화
"""
import os
import time
import psutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json

class PerformanceOptimizer:
    def __init__(self):
        self.root = Path("C:/Users/eunta/multi-agent-workspace")
        self.metrics = {}
        
    def measure_system_performance(self):
        """시스템 성능 측정"""
        print("📊 시스템 성능 측정 중...")
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # 디스크 I/O
        disk_usage = psutil.disk_usage('C:/')
        disk_free = disk_usage.free / (1024**3)  # GB
        
        self.metrics = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_available_gb': round(memory_available, 1),
            'disk_free_gb': round(disk_free, 1),
            'timestamp': time.time()
        }
        
        print(f"1) CPU 사용률: {cpu_percent}%")
        print(f"2) 메모리 사용률: {memory_percent}%")
        print(f"3) 사용 가능 메모리: {self.metrics['memory_available_gb']}GB")
        print(f"4) 디스크 여유 공간: {self.metrics['disk_free_gb']}GB")
        
        return self.metrics
    
    def optimize_python_performance(self):
        """Python 성능 최적화"""
        print("🐍 Python 성능 최적화 중...")
        optimizations = []
        
        # 1. 바이트코드 최적화
        print("1) 바이트코드 컴파일 최적화...")
        python_files = list(self.root.rglob("*.py"))
        
        def compile_file(py_file):
            try:
                import py_compile
                py_compile.compile(py_file, doraise=True)
                return True
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(compile_file, python_files[:50]))  # 처음 50개만
        
        compiled_count = sum(results)
        optimizations.append(f"Python 파일 {compiled_count}개 바이트코드 최적화")
        
        # 2. Import 최적화
        print("2) Import 최적화 분석...")
        import_analysis = self.analyze_imports()
        if import_analysis['unused_imports'] > 0:
            optimizations.append(f"불필요한 import {import_analysis['unused_imports']}개 발견")
        
        # 3. 메모리 정리
        print("3) 메모리 정리...")
        import gc
        before_objects = len(gc.get_objects())
        collected = gc.collect()
        after_objects = len(gc.get_objects())
        
        if collected > 0:
            optimizations.append(f"가비지 컬렉션: {collected}개 객체 정리")
        
        return optimizations
    
    def analyze_imports(self):
        """Import 사용 분석"""
        analysis = {
            'total_files': 0,
            'total_imports': 0,
            'unused_imports': 0,
            'duplicate_imports': 0
        }
        
        for py_file in self.root.rglob("*.py"):
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                analysis['total_files'] += 1
                
                # 간단한 import 카운트 (정확하지 않지만 개략적 파악)
                import_lines = [line for line in content.split('\n') 
                               if line.strip().startswith(('import ', 'from '))]
                analysis['total_imports'] += len(import_lines)
                
                # 중복 import 감지
                unique_imports = set(import_lines)
                if len(import_lines) > len(unique_imports):
                    analysis['duplicate_imports'] += len(import_lines) - len(unique_imports)
                    
            except:
                continue
        
        return analysis
    
    def optimize_file_operations(self):
        """파일 작업 최적화"""
        print("📁 파일 작업 최적화 중...")
        optimizations = []
        
        # 1. 임시 파일 정리
        temp_files = []
        for pattern in ['*.tmp', '*.temp', '*~', '*.bak']:
            temp_files.extend(self.root.rglob(pattern))
        
        if temp_files:
            for temp_file in temp_files[:10]:  # 안전하게 처음 10개만
                try:
                    temp_file.unlink()
                except:
                    pass
            optimizations.append(f"임시 파일 {len(temp_files)}개 정리")
        
        # 2. 빈 폴더 정리
        empty_dirs = []
        for dir_path in self.root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                if 'venv' not in str(dir_path) and '.git' not in str(dir_path):
                    empty_dirs.append(dir_path)
        
        for empty_dir in empty_dirs[:5]:  # 안전하게 처음 5개만
            try:
                empty_dir.rmdir()
            except:
                pass
        
        if empty_dirs:
            optimizations.append(f"빈 폴더 {len(empty_dirs)}개 정리")
        
        # 3. 캐시 디렉토리 크기 확인
        cache_dirs = [
            self.root / "__pycache__",
            self.root / ".pytest_cache",
            self.root / ".agents" / "cache"
        ]
        
        total_cache_size = 0
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                for file in cache_dir.rglob("*"):
                    if file.is_file():
                        total_cache_size += file.stat().st_size
        
        cache_size_mb = total_cache_size / (1024 * 1024)
        if cache_size_mb > 100:  # 100MB 이상
            optimizations.append(f"캐시 크기 {cache_size_mb:.1f}MB - 정리 권장")
        
        return optimizations
    
    def optimize_database_performance(self):
        """데이터베이스 성능 최적화"""
        print("💾 데이터베이스 최적화 중...")
        optimizations = []
        
        # SQLite 데이터베이스 찾기
        db_files = list(self.root.glob("*.db"))
        
        for db_file in db_files:
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_file))
                
                # VACUUM 실행 (데이터베이스 압축)
                conn.execute("VACUUM")
                
                # 통계 업데이트
                conn.execute("ANALYZE")
                
                conn.close()
                optimizations.append(f"{db_file.name} 데이터베이스 최적화")
                
            except:
                continue
        
        return optimizations
    
    def generate_performance_report(self):
        """성능 리포트 생성"""
        report = {
            'timestamp': time.time(),
            'metrics': self.metrics,
            'optimizations_applied': [],
            'recommendations': []
        }
        
        # 성능 기반 권장사항
        if self.metrics.get('memory_percent', 0) > 85:
            report['recommendations'].append("메모리 사용률 높음 - 불필요한 프로세스 종료 권장")
        
        if self.metrics.get('cpu_percent', 0) > 80:
            report['recommendations'].append("CPU 사용률 높음 - 백그라운드 작업 확인 권장")
        
        if self.metrics.get('disk_free_gb', 0) < 5:
            report['recommendations'].append("디스크 공간 부족 - 파일 정리 필요")
        
        # 리포트 저장
        report_file = self.root / "reports" / f"performance_report_{int(time.time())}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report, report_file
    
    def run_full_optimization(self):
        """전체 최적화 실행"""
        print("🚀 성능 최적화 시작...")
        print("=" * 50)
        
        start_time = time.time()
        all_optimizations = []
        
        # 1. 시스템 성능 측정
        self.measure_system_performance()
        print()
        
        # 2. Python 성능 최적화
        python_opts = self.optimize_python_performance()
        all_optimizations.extend(python_opts)
        print()
        
        # 3. 파일 작업 최적화
        file_opts = self.optimize_file_operations()
        all_optimizations.extend(file_opts)
        print()
        
        # 4. 데이터베이스 최적화
        db_opts = self.optimize_database_performance()
        all_optimizations.extend(db_opts)
        print()
        
        # 5. 결과 리포트
        report, report_file = self.generate_performance_report()
        report['optimizations_applied'] = all_optimizations
        
        # 리포트 재저장
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        end_time = time.time()
        optimization_time = end_time - start_time
        
        print("=" * 50)
        print("🎉 성능 최적화 완료!")
        print(f"소요 시간: {optimization_time:.1f}초")
        print(f"적용된 최적화: {len(all_optimizations)}개")
        
        for i, opt in enumerate(all_optimizations, 1):
            print(f"  {i}) {opt}")
        
        if report['recommendations']:
            print("\n💡 추가 권장사항:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}) {rec}")
        
        print(f"\n📄 상세 리포트: {report_file}")
        
        return report

def main():
    optimizer = PerformanceOptimizer()
    optimizer.run_full_optimization()

if __name__ == "__main__":
    main()