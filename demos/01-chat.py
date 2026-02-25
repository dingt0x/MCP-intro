from openai import OpenAI
from dotenv import load_dotenv
import os
import json
# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
load_dotenv()
api_key = os.getenv("AI_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
if __name__ == '__main__':
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        max_tokens=1024,
        temperature=0.7,
        stream=False
    )

    print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
