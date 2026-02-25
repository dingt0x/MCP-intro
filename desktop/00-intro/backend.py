from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys

from openai import OpenAI

app = FastAPI()

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

def resource_path(rel: str) -> Path:
    """
    兼容 PyInstaller：
    - 开发环境：当前文件所在目录
    - 打包环境：sys._MEIPASS 目录
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / rel
    return Path(__file__).resolve().parent / rel

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")

    if not user_input:
        raise HTTPException(status_code=400, detail="消息不能为空")

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": user_input}
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=1.3
    )
    answer = response.choices[0].message.content
    return {"answer": answer}

@app.get("/", response_class=HTMLResponse)
async def index():
    p = resource_path("index.html")
    if not p.exists():
        return "<h3>index.html 未找到，请检查打包资源</h3>"
    return p.read_text(encoding="utf-8")