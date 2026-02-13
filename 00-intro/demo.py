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
            {"role": "user", "content": "Say Hi to me and tell me, which kind of AI model you are."},
        ],
        stream=False
    )

    print(response.choices[0])
    print(response.choices[0].message.content)