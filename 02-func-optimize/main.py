import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
import uvicorn
from conf import base_url, api_key, model_name, port
from ops import ops_tools ,get_server_info
from weather import get_weather,weather_tools
import asyncio
from fastapi.responses import StreamingResponse


app = FastAPI()
client = OpenAI(base_url=base_url, api_key=api_key)

chat_memory = {}
MAX_HISTORY = 20

tools = ops_tools + weather_tools

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")
    session_id = data.get("session_id", "default_user")

    if session_id not in chat_memory:
        chat_memory[session_id] = []

    chat_memory[session_id].append({"role": "user", "content": user_input})

    async def event_generator():
        try:
            # 1. 第一次调用：判断意图
            response = client.chat.completions.create(
                model=model_name,
                messages=chat_memory[session_id],
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            if response_message.tool_calls:
                # 将模型的“调用意图”加入历史
                chat_memory[session_id].append(response_message)

                # 遍历所有工具调用（支持 AI 一次性调用多个工具）
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # 动态推送状态给前端，告知正在调用哪个工具
                    yield f"data: {json.dumps({'type': 'status', 'content': f'🛠️ 正在执行: {function_name}...'})}\n\n"

                    # 执行逻辑分支
                    if function_name == "get_weather":
                        city = function_args.get("city")
                        result = get_weather(city)
                    elif function_name == "get_server_info":
                        platform = function_args.get("platform")
                        result = get_server_info(platform)
                    else:
                        result = {"error": "未定义的工具"}

                    # 将执行结果回传给历史记录
                    chat_memory[session_id].append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

                # 第二次调用：获取流式总结
                yield f"data: {json.dumps({'type': 'status', 'content': '🚀 正在汇总数据并生成报告...'})}\n\n"

                second_res = client.chat.completions.create(
                    model=model_name,
                    messages=chat_memory[session_id],
                    stream=True
                )

                full_answer = ""
                for chunk in second_res:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_answer += content
                        yield f"data: {json.dumps({'type': 'text', 'content': content})}\n\n"

                chat_memory[session_id].append({"role": "assistant", "content": full_answer})

            else:
                # 如果没有工具调用，直接流式返回内容
                # 为了让前端统一处理，我们也分片“假流式”或者直接发送
                full_answer = response_message.content
                yield f"data: {json.dumps({'type': 'text', 'content': full_answer})}\n\n"
                chat_memory[session_id].append({"role": "assistant", "content": full_answer})

            # 保持滑动窗口
            if len(chat_memory[session_id]) > MAX_HISTORY:
                chat_memory[session_id] = chat_memory[session_id][-MAX_HISTORY:]

        except Exception as e:
            error_msg = f"❌ 系统错误: {str(e)}"
            print(f"🔥 {error_msg}")
            yield f"data: {json.dumps({'type': 'text', 'content': error_msg})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    port = int(port) + 2
    print(f"🚀 Level 2 (Function Call) 运行在: http://127.0.0.1:{port}")
    uvicorn.run(app, host="0.0.0.0", port=int(port))