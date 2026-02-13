import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("AI_API_KEY")
base_url = os.getenv("AI_BASE_URL" )
model_name = os.getenv("AI_MODEL")

if not api_key:
    print("❌ 错误: 未在 .env 中检测到 AI_API_KEY")
    exit(1)
if not base_url:
    print("❌ 错误: 未在 .env 中检测到AI_BASE_URL ")
    exit(1)
if not model_name:
    print("❌ 错误: 未在 .env 中检测到AI_MODEL_NAME ")
    exit(1)