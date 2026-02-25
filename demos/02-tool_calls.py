from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("AI_API_KEY")

def get_weather(location :str):
    return "24℃"

functions = {
    "get_weather": get_weather
}

def send_messages(messages):
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "tools": tools,
    }
    # print("POST data to LLM:\n", payload)
    print("POST data:\n", json.dumps(payload, ensure_ascii=False, indent=2))
    response_in_function = client.chat.completions.create(
       **payload
    )

    print("Response from LLM:\n",json.dumps(response_in_function.model_dump(), ensure_ascii=False, indent=2))
    return response_in_function

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]

if __name__ == '__main__':

    print(f"User>\t {messages[0]['content']}")
    response = send_messages(messages)
    message = response.choices[0].message


    messages.append(response.model_dump()["choices"][0]["message"])
    tool_calls = message.tool_calls
    if tool_calls:
        for tool in tool_calls:
            f = functions[tool.function.name]
            args = json.loads(tool.function.arguments)
            data = f(**args)
            print(f"AI 应用> 执行tool call {tool.function.name} ...获取信息{data}")
            messages.append({"role": "tool", "tool_call_id": tool.id, "content": f"{data}"})

    response = send_messages(messages)
    message = response.choices[0].message

    print(f"Model>\t {message.content}")