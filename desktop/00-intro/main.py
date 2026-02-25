import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
import uvicorn

from conf import base_url,api_key,model_name,port

app = FastAPI()
client = OpenAI(
    base_url=base_url,
    api_key=api_key

)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message")

        if not user_input:
            raise HTTPException(status_code=400, detail="消息不能为空")

        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": user_input}
        ]
        print(f"messages: ${messages}")
        # 调用模型 (Level 0: 无记忆)
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=1.3
        )

        answer = response.choices[0].message.content
        return {"answer": answer}

    except Exception as e:
        print(f"🔥 系统错误: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 服务暂时不可用")

@app.get("/", response_class=HTMLResponse)
async def index():
    # 确保 index.html 在同一目录下
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h3>index.html 未找到，请检查文件路径</h3>"

if __name__ == "__main__":
    port = int(port)
    print(f"🚀 服务已启动: http://127.0.0.1:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)