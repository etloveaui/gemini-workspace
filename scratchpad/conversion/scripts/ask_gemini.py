import os
import sys
import google.generativeai as genai

try:
    # 파워쉘 스크립트에서 설정한 환경 변수에서 API 키를 가져옵니다.
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("API 키가 설정되지 않았습니다. GEMINI_API_KEY 환경 변수를 확인하세요.")

    genai.configure(api_key=api_key)

    # 질문을 프로그램 실행 인자로부터 받습니다.
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
    else:
        question = "안녕? 자기소개 해봐."

    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(question)

    print(response.text)

except Exception as e:
    print(f"오류가 발생했습니다: {e}")