import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from openai import OpenAI
from conf import model_name,base_url,api_key
client = OpenAI(
    base_url = base_url,
    api_key = api_key
)

if __name__ == '__main__':
    # Round 1
    messages = [{"role": "user", "content": "What's the highest mountain in the world?"}]
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    messages.append(response.choices[0].message)
    print(f"Messages Round 1: {messages}")

    # Round 2
    messages.append({"role": "user", "content": "What is the second?"})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

    messages.append(response.choices[0].message)
    print(f"Messages Round 2: {messages}")