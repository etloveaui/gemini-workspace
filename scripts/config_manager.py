import argparse
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    parser = argparse.ArgumentParser(description="Manage CLI configuration.")
    parser.add_argument("--lang", required=True, help="The language to set (e.g., 'en', 'ko').")
    args = parser.parse_args()

    print(f"Setting CLI language to: {args.lang}")
    # 여기에 실제 언어 설정 로직 추가
    print("Language setting simulated.")

if __name__ == "__main__":
    main()
