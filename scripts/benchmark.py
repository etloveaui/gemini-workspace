import time
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# scripts.runner 모듈을 직접 임포트
from scripts.runner import run_command

def run_benchmark():
    print("Running benchmarks...")

    # 벤치마크 1: invoke start 시간 측정
    start_time = time.time()
    run_command("benchmark.start", [sys.executable, "-m", "invoke", "start"], check=False)
    end_time = time.time()
    print(f"invoke start took: {end_time - start_time:.2f} seconds")

    # 벤치마크 2: context build 시간 측정
    start_time = time.time()
    run_command("benchmark.context_build", [sys.executable, "-m", "invoke", "context.build"], check=False)
    end_time = time.time()
    print(f"invoke context.build took: {end_time - start_time:.2f} seconds")

    print("Benchmarks completed.")

if __name__ == "__main__":
    run_benchmark()
