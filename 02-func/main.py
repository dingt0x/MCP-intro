import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
import uvicorn
from conf import base_url, api_key, model_name, port
from ops import ops_tools ,get_server_info
# from weather import get_weather,weather_tools


app = FastAPI()
client = OpenAI(base_url=base_url, api_key=api_key)

chat_memory = {}
MAX_HISTORY = 20

# tools = ops_tools + weather_tools
tools = ops_tools

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message")
        session_id = data.get("session_id", "default_user")

        if session_id not in chat_memory:
            chat_memory[session_id] = []

        chat_memory[session_id].append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=model_name,
            messages=chat_memory[session_id],
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        print("response_message: ", response_message)

        if response_message.tool_calls:
            print(f"🛠️  AI 申请调用工具: {response_message.tool_calls[0].function.name}")

            chat_memory[session_id].append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "get_server_info":
                    function_response = get_server_info(
                        platform=function_args.get("platform")
                    )

                    chat_memory[session_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    })
                if function_name == "get_weather":
                    function_response = get_weather(
                        city=function_args.get("city")
                    )

                    chat_memory[session_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    })


            second_response = client.chat.completions.create(
                model=model_name,
                messages=chat_memory[session_id]
            )
            final_answer = second_response.choices[0].message.content
        else:
            final_answer = response_message.content

        chat_memory[session_id].append({"role": "assistant", "content": final_answer})

        if len(chat_memory[session_id]) > MAX_HISTORY:
            chat_memory[session_id] = chat_memory[session_id][-MAX_HISTORY:]
        return {"answer": final_answer}

    except Exception as e:
        print(f"🔥 系统错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    port = int(port) + 20
    print(f"🚀 Level 2 (Function Call) 运行在: http://127.0.0.1:{port}")
    uvicorn.run(app, host="0.0.0.0", port=int(port))