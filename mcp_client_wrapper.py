from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, Dict, List

class MCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params

    async def get_tools(self) -> List[Any]:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return tools.tools

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, tool_args)