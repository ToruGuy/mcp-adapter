import asyncio
import os
import sys
from pathlib import Path
from mcp.client.stdio import StdioServerParameters, get_default_environment

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp import StdioServerParameters
from src.llm import GeminiAdapter
from src.core.orchestrator import ToolOrchestrator
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Configure MCP servers
    server_params = [
        # # Brave Search server
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={**get_default_environment(), "BRAVE_API_KEY": os.getenv('BRAVE_API_KEY')}
        ),
        # Filesystem server
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
            env=None
        ),
        # Memory server
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env=None
        )
    ]

    # Initialize orchestrator with all servers
    orchestrator = ToolOrchestrator(
        server_params,
        debug=True,
        log_dir=log_dir
    )
    await orchestrator.initialize()

    # Initialize Gemini adapter
    llm_client = GeminiAdapter(
        model_name='gemini-1.5-flash',
        debug=True,
        log_file=log_dir / "gemini_adapter.log"
    )

    # Setup the LLM pipeline
    await llm_client.prepare_tools(orchestrator.tools)
    await llm_client.configure(api_key)

    try:
        # 1) Create a file
        print("\n=== Creating File ===")
        create_file_prompt = (
            f"Create a file called test-orchestrator-example.txt "
            f"with text 'Testing the MCP Tool Orchestrator!' "
            f"in path: {desktop_path}"
        )
        response = await llm_client.send_message(create_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Execute through orchestrator
        result = await orchestrator.execute(tool_name, tool_args)
        print(f"Create file result (using {result.client_name}):", result.data)

        # 2) Read the file
        print("\n=== Reading File ===")
        read_file_prompt = f"Read the file test-orchestrator-example.txt from path: {desktop_path}"
        response = await llm_client.send_message(read_file_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        result = await orchestrator.execute(tool_name, tool_args)
        print(f"File content (using {result.client_name}):", result.data)

        # 3) Store in memory
        print("\n=== Storing in Memory ===")
        memory_prompt = (
            "Create a memory node named 'test-orchestrator' with information "
            "about the file we just created and its contents"
        )
        response = await llm_client.send_message(memory_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        result = await orchestrator.execute(tool_name, tool_args)
        print(f"Memory store result (using {result.client_name}):", result.data)

        # 4) Search for best Opel model
        print("\n=== Searching for Best Opel Model ===")
        search_prompt = """Use the brave_web_search tool to search for "best Opel model 2023 2024 review". 
        The search should focus on finding reliable reviews and comparisons of recent Opel models.
        The tool requires a 'query' parameter with the search text."""
        response = await llm_client.send_message(search_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Execute search
        search_result = await orchestrator.execute(tool_name, tool_args)
        print(f"Search result (using {search_result.client_name}):", search_result.data)

        # Write results to file
        write_prompt = f"""Use the write_file tool to save the search results to a file. The tool requires:
        - path: The full path '/Users/tako/Desktop/best-opel.txt'
        - content: A formatted summary of the search results with title and links

        Here are the search results to format:
        {search_result.data}

        Format the content with a clear title, key findings about the best Opel models, and relevant links from the search results."""
        response = await llm_client.send_message(write_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        write_result = await orchestrator.execute(tool_name, tool_args)
        print(f"Write result (using {write_result.client_name}):", write_result.data)

    finally:
        # Clean up
        await orchestrator.close()

if __name__ == "__main__":
    asyncio.run(main())
