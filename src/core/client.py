from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, Dict, List, Optional
from pathlib import Path
from src.core.logger import MCPLogger

class MCPClient:
    def __init__(self, 
                 server_params: StdioServerParameters, 
                 debug: bool = False,
                 log_file: Optional[Path] = None,
                 client_name: Optional[str] = "MCPClient"):
        self.server_params = server_params
        self.logger = MCPLogger(client_name, debug_mode=debug, log_file=log_file)

    async def get_tools(self) -> List[Any]:
        self.logger.log_debug("Retrieving tools from MCP server")
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.logger.log_debug("Initializing session")
                    await session.initialize()
                    tools = await session.list_tools()
                    self.logger.log_info(f"Retrieved {len(tools.tools)} tools")
                    return tools.tools
        except Exception as e:
            self.logger.log_error(f"Failed to get tools: {str(e)}")
            raise

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        self.logger.log_debug(f"Executing tool {tool_name} with args: {tool_args}")
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.logger.log_debug("Initializing session")
                    await session.initialize()
                    result = await session.call_tool(tool_name, tool_args)
                    self.logger.log_info(f"Successfully executed tool {tool_name}")
                    return result
        except Exception as e:
            self.logger.log_error(f"Failed to execute tool {tool_name}: {str(e)}")
            raise