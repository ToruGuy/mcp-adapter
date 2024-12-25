from typing import Any, Dict, List
import logging

from mcp import StdioServerParameters
from session import MCPSession

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self._session = MCPSession(server_params)

    async def __aenter__(self):
        await self._session.establish_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.cleanup()

    async def get_tools(self) -> List[Any]:
        print(11)
        session = await self._session.ensure_session()
        print(12)
        tools = await session.list_tools()
        print(13)
        return tools.tools

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        session = await self._session.ensure_session()
        return await session.call_tool(tool_name, tool_args)