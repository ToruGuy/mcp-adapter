import asyncio
import os
from mcp import StdioServerParameters
from gemini_adapter import GeminiAdapter
from mcp_client_wrapper import MCPClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Setup parameters
    desktop_path = "/Users/tako/Desktop"
    api_key = os.getenv('GEMINI_API_KEY')
    client_id = "filesystem-client"  # Unique identifier for this client
    
    # Configure MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/tako/Desktop"],
        env=None
    )

    # Initialize clients
    mcp_client = MCPClient(server_params)
    llm_client = GeminiAdapter()

    try:
        # Setup the pipeline
        tools = await mcp_client.get_tools()
        await llm_client.configure(api_key)
        await llm_client.prepare_tools(client_id, tools)

        # Example 1: Create a file
        response = await llm_client.send_message(
            client_id, 
            f"Create a file called hello.txt 'Hello from MCP!' in path: {desktop_path}"
        )
        tool_name, tool_args = llm_client.extract_tool_call(response)
        result = await mcp_client.execute_tool(tool_name, tool_args)
        print("Create file result:", result)

        # Example 2: List directory
        response = await llm_client.send_message(
            client_id,
            f"List the contents of {desktop_path}"
        )
        tool_name, tool_args = llm_client.extract_tool_call(response)
        result = await mcp_client.execute_tool(tool_name, tool_args)
        print("Directory contents:", result)

    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        # Cleanup
        await mcp_client._session.cleanup()

if __name__ == "__main__":
    asyncio.run(main())