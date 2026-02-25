from openai import OpenAI
from dotenv import load_dotenv
import os
# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
load_dotenv()
api_key = os.getenv("AI_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
if __name__ == '__main__':
    while 1:
        user_text = input("User> ")
        if user_text == "/exit": print("Bye");break

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content":  user_text},
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=False
        )

        print(response.choices[0].message.content)