import argparse
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    parser = argparse.ArgumentParser(description="Analyze an image file.")
    parser.add_argument("--image", required=True, help="The path to the image file.")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)

    # 실제 image_to_text 도구가 없으므로 더미 설명을 생성합니다.
    # 이 부분은 향후 실제 이미지 분석 로직으로 대체될 것입니다.
    from scripts.utils.ko_rationale import is_enabled as _ko_on, build_rationale as _ko_reason
    dummy_description = (
        f"Description: This is a simulated analysis of the image at {image_path.name}. "
        f"It appears to be a placeholder for a real image analysis tool."
    )
    if _ko_on():
        reason = _ko_reason(hint="image")
        print(dummy_description + f"\n\n근거(요약):\n{reason}")
    else:
        print(dummy_description)

if __name__ == "__main__":
    main()
