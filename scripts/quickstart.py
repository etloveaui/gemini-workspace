import sys
from cli_style import header, item

sys.stdout.reconfigure(encoding='utf-8')


def main() -> None:
    print(header("Quickstart"))
    print("환영합니다! Gemini CLI 빠른 시작")
    print(item(1, "가상 환경(venv) 생성 및 활성화"))
    print("   - python -m venv venv")
    print("   - .\\venv\\Scripts\\activate (Windows)")
    print("   - source venv/bin/activate (Linux/macOS)")
    print(item(2, "필요한 패키지 설치"))
    print("   - pip install -r requirements.txt")
    print(item(3, "세션 시작"))
    print("   - invoke start")
    print(item(4, "시스템 검증"))
    print("   - invoke test")
    print(item(5, "더 많은 도움말"))
    print("   - invoke help")
    sys.exit(0)


if __name__ == "__main__":
    main()
