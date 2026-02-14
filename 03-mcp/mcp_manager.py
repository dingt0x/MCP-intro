import json
import asyncio
from contextlib import AsyncExitStack  # 关键：用来保持连接不中断
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPManager:
    def __init__(self, config_path="mcp_config.json"):
        self.config_path = config_path
        # 存储已连接的会话，格式：{ "工具名": session_object }
        self.sessions = {}
        # 存储提供给 OpenAI 格式的工具描述
        self.formatted_tools = []
        # 核心：这个“栈”负责管理所有子进程的生命周期，确保它们一直运行
        self.exit_stack = AsyncExitStack()

    async def start(self):
        # 1. 读取你写好的 mcp_config.json
        with open(self.config_path, "r") as f:
            config = json.load(f)

        # 2. 遍历配置里的每一个 Server
        for name, srv_config in config.get("mcpServers", {}).items():
            # 准备启动参数（就是你 JSON 里的那些字段）
            params = StdioServerParameters(
                command=srv_config["command"],
                args=srv_config["args"],
                env=srv_config.get("env"),
                cwd=srv_config.get("cwd")
            )

            # 3. 【核心环节】启动子进程并建立 stdio 隧道
            # 我们把连接交给 exit_stack 管理，这样函数结束了，连接也不会断
            read, write = await self.exit_stack.enter_async_context(stdio_client(params))

            # 4. 创建 MCP 会话并初始化
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            # 5. 获取这个 Server 能干什么（工具列表）
            tools_res = await session.list_tools()

            for tool in tools_res.tools:
                # 记录：这个工具归哪个 session 管
                self.sessions[tool.name] = session

                # 转换为 OpenAI 兼容的格式
                self.formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
        return self.formatted_tools
    async def stop(self):
        """关闭所有连接，清理子进程"""
        await self.exit_stack.aclose()

    async def call_tool(self, tool_name, arguments):
        """根据工具名，把请求转发给对应的 MCP Server"""
        session = self.sessions.get(tool_name)
        if not session:
            return {"error": f"找不到工具 {tool_name} 对应的 MCP 会话"}

        # 调用 MCP 协议的 call_tool 方法
        result = await session.call_tool(tool_name, arguments)

        # MCP 返回的结果通常在 result.content 里
        # 我们假设返回的是文本（最常见的情况）
        return result.content[0].text if result.content else "无返回内容"
