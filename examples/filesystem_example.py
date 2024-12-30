import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp import StdioServerParameters
from src.llm import OpenAIAdapter
from src.core import MCPClient, MCPTools
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Configure MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )

    # Initialize clients with logging enabled
    mcp_client = MCPClient(
        server_params,
        debug=True,  # Enable debug logging
        log_file=log_dir / "mcp_client.log",
        client_name="fs_client"
    )
    
    llm_client = OpenAIAdapter(
        model_name='gpt-4o-mini',
        debug=True,  # Enable debug logging
        log_file=log_dir / "openai_adapter.log"
    )

    try:
        # Setup the pipeline
        raw_tools = await mcp_client.get_tools()
        tools = MCPTools()
        tools.add(raw_tools)
        
        await llm_client.prepare_tools(tools)
        await llm_client.configure(api_key)

        # Example 1: Create a file
        message = f"Create a file called hello.txt 'Hello from MCP!' in path: {desktop_path}"
        response = await llm_client.send_message(message)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        result = await mcp_client.execute_tool(tool_name, tool_args)
        print("Create file result:", result)

        # Example 2: List directory
        message = f"List the contents of {desktop_path}"
        response = await llm_client.send_message(message)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        result = await mcp_client.execute_tool(tool_name, tool_args)
        print("Directory contents:", result)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        mcp_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
        raise
    else:
        mcp_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")

if __name__ == "__main__":
    asyncio.run(main())