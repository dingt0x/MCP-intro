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
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    # print(response.choices[0])
    print(response.choices[0].message.content)