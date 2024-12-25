import asyncio
import os
from pathlib import Path
from mcp import StdioServerParameters
from gemini_adapter import GeminiAdapter
from mcp_client_wrapper import MCPClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup parameters
    desktop_path = "/Users/tako/Desktop"
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Configure MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/tako/Desktop"],
        env=None
    )

    # Initialize clients with logging enabled
    mcp_client = MCPClient(
        server_params,
        debug=True,  # Enable debug logging
        log_file=log_dir / "mcp_client.log"
    )
    
    llm_client = GeminiAdapter(
        model_name='gemini-1.5-flash',
        debug=True,  # Enable debug logging
        log_file=log_dir / "gemini_adapter.log"
    )

    try:
        # Setup the pipeline
        tools = await mcp_client.get_tools()
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
        # The error will be automatically logged by the respective components
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())