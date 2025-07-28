import sys

sys.stdout.reconfigure(encoding='utf-8')

print("""
환영합니다! Gemini CLI를 빠르게 시작하는 방법입니다:

1. 가상 환경(venv) 생성 및 활성화:
   `python -m venv venv`
   `.\venv\Scripts\activate` (Windows)
   `source venv/bin/activate` (Linux/macOS)

2. 필요한 패키지 설치:
   `pip install -r requirements.txt`

3. 세션 시작 및 초기화:
   `invoke start`

4. 시스템 검증:
   `invoke test`

5. 더 많은 도움말 보기:
   `invoke help`

""")
sys.exit(0)
