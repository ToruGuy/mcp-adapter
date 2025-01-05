import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp import StdioServerParameters
from src.llm import GeminiAdapter
from src.core import MCPClient, MCPTools
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

async def main():
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Configure the Filesystem MCP server
    fs_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )

    # Configure the Memory MCP server
    mem_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        env=None
    )

    # Initialize MCP clients for filesystem and memory
    fs_client = MCPClient(
        fs_params,        
        debug=True,  # Enable debug logging
        log_file=log_dir / "mcp_client.log",
        client_name="fs_client")
    mem_client = MCPClient(
        mem_params,
        debug=True,  # Enable debug logging
        log_file=log_dir / "mcp_client.log",
        client_name="mem_client"
        )

    # Initialize our Gemini adapter (LLM client)
    llm_client = GeminiAdapter(
        model_name='gemini-1.5-flash',
        debug=True,  # Enable debug logging
        log_file=log_dir / "gemini_adapter.log"
    )

    try:
        # Get tools from both servers
        fs_tools = await fs_client.get_tools()
        mem_tools = await mem_client.get_tools()
        
        # Create MCPTools instance and add tools
        tools = MCPTools()
        tools.add(fs_tools)
        tools.add(mem_tools)

        # Setup the pipeline
        await llm_client.prepare_tools(tools)
        await llm_client.configure(api_key)

        # 1) Create a file in /Users/tako/Desktop
        print("\n=== Creating File ===")
        create_file_prompt = (
            f"Create a file called test-mcp-adapter-example.txt "
            f"with text 'This is a test for the MCP adapter example!' "
            f"in path: {desktop_path}"
        )
        response = await llm_client.send_message(create_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        create_file_result = await fs_client.execute_tool(tool_name, tool_args)
        print("Create file result:", create_file_result)

        # 2) Read the file content and print it
        print("\n=== Reading File Content ===")
        read_file_prompt = f"Read the file test-mcp-adapter-example.txt from path: {desktop_path}"
        response = await llm_client.send_message(read_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        file_content = await fs_client.execute_tool(tool_name, tool_args)
        print("File content:", file_content)

        # 3) Create a new "test-mcp-adapter-example" node in memory with text & path
        print("\n=== Creating Memory Node ===")
        create_node_prompt = (
            "Create a new memory node named 'test-mcp-adapter-example' and would remeber where the file is and what is about."
        )
        response = await llm_client.send_message(create_node_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        node_creation_result = await mem_client.execute_tool(tool_name, tool_args)
        print("Memory node creation result:", node_creation_result)

        # 4) Search for 'mcp-adapter-example' node and print the found result
        print("\n=== Searching for 'mcp-adapter-example' Node ===")
        search_node_prompt = "Search for memory nodes that match the name 'mcp-adapter-example'"
        response = await llm_client.send_message(search_node_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        search_result = await mem_client.execute_tool(tool_name, tool_args)
        print("Search result:", search_result)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        fs_client.logger.end_session("failed")
        mem_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
        raise
    else:
        fs_client.logger.end_session("completed")
        mem_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")

if __name__ == "__main__":
    asyncio.run(main())