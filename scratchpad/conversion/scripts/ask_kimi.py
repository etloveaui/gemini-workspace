import os
import sys
from openai import OpenAI

try:
    # 환경변수에서 API 키를 가져옴
    api_key = os.environ.get('KIMI_API_KEY')
    if not api_key:
        raise ValueError("API 키가 설정되지 않았습니다. KIMI_API_KEY 환경 변수를 확인하세요.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/anthropic",  # ✅ 최신 기준 반영
    )

    # 질문 인자 처리
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
    else:
        question = "안녕? 너는 누구야?"

    completion = client.chat.completions.create(
        model="kimi-k2-0711-preview",  # ✅ 수정된 모델명
        messages=[
            {"role": "system", "content": "You are Kimi, an AI assistant from Moonshot AI. You are proficient in Chinese and English conversations."},
            {"role": "user", "content": question}
        ],
        temperature=0.6,  # ✅ K2는 공식 권장값이 0.6
    )
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"오류가 발생했습니다: {e}")
