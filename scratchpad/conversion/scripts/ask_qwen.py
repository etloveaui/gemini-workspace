import os
import sys
from openai import OpenAI

try:
    # 파워쉘 스크립트에서 설정한 환경 변수에서 API 키를 가져옵니다.
    api_key = os.environ.get('QWEN_API_KEY')
    if not api_key:
        raise ValueError("API 키가 설정되지 않았습니다. QWEN_API_KEY 환경 변수를 확인하세요.")

    client = OpenAI(
        api_key=api_key, # 이 키는 실제로 사용되지 않을 수 있으나 형식상 유지
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    # 질문을 프로그램 실행 인자로부터 받습니다.
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
    else:
        question = "안녕? 너는 누구야?"

    completion = client.chat.completions.create(
        model="qwen3-coder-plus",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        # Qwen(Dashscope)은 별도의 헤더로 키를 전달해야 합니다.
        extra_headers={"Authorization": f"Bearer {api_key}"}
    )
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"오류가 발생했습니다: {e}")