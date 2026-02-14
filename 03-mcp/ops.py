def get_server_info(platform: str):
    """模拟获取服务器信息的逻辑"""
    if platform.lower() == "prod":
        return {"cpu": "92%", "disk": "10% free", "status": "Warning"}
    else:
        return {"cpu": "15%", "disk": "80% free", "status": "Healthy"}

ops_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_server_info",
            "description": "获取指定环境服务器的实时负载和磁盘状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {
                        "type": "string",
                        "enum": ["prod", "test"],
                        "description": "环境名称"
                    }
                },
                "required": ["platform"]
            }
        }
    }
]