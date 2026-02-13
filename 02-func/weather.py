import requests

def get_weather(city: str):
    """通过 wttr.in 获取真实天气数据"""
    try:

        url = f"https://wttr.in/{city}?format=j1&lang=zh-cn"
        response = requests.get(url, timeout=10)
        data = response.json()

        forecast = []
        for day in data['weather'][:3]: # 只取前三天
            forecast.append({
                "日期": day['date'],
                "最高温": f"{day['maxtempC']}°C",
                "最低温": f"{day['mintempC']}°C",
                "天气": day['hourly'][4]['lang_zh-cn'][0]['value'] # 取中午左右的天气描述
            })

        current = data['current_condition'][0]
        return {
            "城市": city,
            "当前温度": f"{current['temp_C']}°C",
            "当前天气": current['lang_zh-cn'][0]['value'],
            "未来三日预报": forecast
        }
    except Exception as e:
        return {"error": f"无法获取 {city} 的天气: {str(e)}"}

weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取中国及全球城市的实时天气和未来三天预报",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、Shenzhen"
                    }
                },
                "required": ["city"]
            }
        }
    }
]