# weather_mcp_server.py
import requests
import json
from mcp.server.fastmcp import FastMCP

# 1. 初始化 FastMCP，名字会出现在调试日志中
mcp = FastMCP("Weather-Service")

# 2. 将之前的天气查询逻辑包装成 MCP 工具
@mcp.tool()
def fetch_weather(city: str) -> str:
    """
    获取指定城市的实时天气和未来三天预报。
    参数 city: 城市名称，如 '北京' 或 'Shanghai'。
    """
    try:
        # 使用 wttr.in 的 JSON 接口
        url = f"https://wttr.in/{city}?format=j1&lang=zh-cn"
        response = requests.get(url, timeout=10)
        data = response.json()

        # 提取当前天气
        current = data['current_condition'][0]
        temp = current['temp_C']
        desc = current['lang_zh-cn'][0]['value']

        # 提取未来 3 天预报
        forecast_list = []
        for day in data['weather'][:3]:
            forecast_list.append(
                f"{day['date']}: {day['maxtempC']}°C/{day['mintempC']}°C, {day['hourly'][4]['lang_zh-cn'][0]['value']}"
            )

        # 组装成一个清晰的字符串返回给 AI
        result = (
                f"城市: {city}\n"
                f"当前状态: {temp}°C, {desc}\n"
                f"预报:\n" + "\n".join(forecast_list)
        )
        return result

    except Exception as e:
        return f"获取天气失败: {str(e)}"



if __name__ == "__main__":
    # 3. 运行服务器 (默认使用 stdio 模式)
    mcp.run()