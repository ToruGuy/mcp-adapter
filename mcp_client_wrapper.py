from typing import Any, Dict, List
import logging

from mcp import StdioServerParameters
from session import MCPSession

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self._session = MCPSession(server_params)

    async def get_tools(self) -> List[Any]:
        session = await self._session.ensure_session()
        try:
            tools = await session.list_tools()
            return tools.tools
        except Exception as e:
            logger.error(f"Error getting tools: {e}")
            await self._session.cleanup()
            raise

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        session = await self._session.ensure_session()
        try:
            return await session.call_tool(tool_name, tool_args)
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            await self._session.cleanup()
            raise