"""
Time Operations Example

This example demonstrates using the Time MCP server with OpenAI:
1. Getting current time in UTC
2. Converting time between timezones
3. Calculating time differences between locations

This showcases:
- Integration with Time MCP server
- How to perform common time operations via MCP
- Pattern for handling tool calls with LLMs
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Third-party imports
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Local imports
from src.llm import OpenAIAdapter
from src.core import MCPClient, MCPTools

# Load environment variables
load_dotenv()

async def main() -> None:
    """
    Example of using the Time MCP server with OpenAI.
    Demonstrates how to:
    1. Get current time
    2. Convert time between timezones
    3. Calculate time differences
    """
    # Setup logging directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup parameters
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY environment variable must be set")
        return
    
    # Configure MCP Time server
    # Note: Using mcp-server-time package name which is already installed
    time_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-server-time"],
        env=None
    )

    # Initialize MCP clients
    time_client = MCPClient(
        time_params,        
        debug=True,
        log_file=log_dir / "time_client.log",
        client_name="time_client"
    )
    
    # Initialize OpenAI adapter
    llm_client = OpenAIAdapter(
        model_name='gpt-4o-mini',
        debug=True,
        log_file=log_dir / "openai_adapter.log"
    )

    try:
        # Get Time tools
        time_tools = await time_client.get_tools()
        
        # Create MCPTools instance and add tools
        tools = MCPTools()
        tools.add(time_tools)

        # Setup the LLM pipeline
        await llm_client.prepare_tools(tools)
        await llm_client.configure(openai_api_key)

        # 1) Get current time
        print("\n=== Getting Current Time ===")
        current_time_prompt = "Get the current time in UTC format"
        response = await llm_client.send_message(current_time_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            current_time = await time_client.execute_tool(tool_name, tool_args)
            print(f"Current time: {current_time}")
        else:
            print("Failed to get tool call for current time")

        # 2) Convert time between timezones
        print("\n=== Converting Time Between Timezones ===")
        convert_time_prompt = "Convert the current time from UTC to Pacific Time (PT) timezone"
        response = await llm_client.send_message(convert_time_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            converted_time = await time_client.execute_tool(tool_name, tool_args)
            print(f"Converted time: {converted_time}")
        else:
            print("Failed to get tool call for time conversion")

        # 3) Calculate time difference
        print("\n=== Calculating Time Difference ===")
        time_diff_prompt = "What's the time difference between New York and Tokyo?"
        response = await llm_client.send_message(time_diff_prompt)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        
        # Validate tool call
        if tool_name and tool_args:
            time_diff = await time_client.execute_tool(tool_name, tool_args)
            print(f"Time difference: {time_diff}")
        else:
            print("Failed to get tool call for time difference")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        time_client.logger.end_session("failed")
        llm_client.logger.end_session("failed")
    else:
        time_client.logger.end_session("completed")
        llm_client.logger.end_session("completed")
    finally:
        # Always close clients
        await time_client.close()
        # No need to close LLM adapter as it doesn't maintain a persistent connection

if __name__ == "__main__":
    asyncio.run(main())