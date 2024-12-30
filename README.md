# MCP Adapter

A Python package that provides adapters for various LLMs (Large Language Models) to work with the Model Context Protocol (MCP).

## Features

- Base LLM adapter interface
- Gemini adapter implementation
- OpenAI adapter implementation
- Support for filesystem and memory MCP servers
- Extensible design for adding new LLM adapters

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mcp-adapter
```

2. Install the package:
```bash
pip install -e .
```

## Configuration

Create a `.env` file in the root directory with your API keys:

```bash
# LLM Settings
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Filesystem Settings
DESKTOP_PATH=/path/to/desktop
```

## Usage

### Basic Example

```python
import asyncio
from pathlib import Path
from mcp import StdioServerParameters
from src.llm import GeminiAdapter  # or OpenAIAdapter
from src.core import MCPClient, MCPTools
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    # Setup parameters
    desktop_path = os.getenv('DESKTOP_PATH')
    api_key = os.getenv('GEMINI_API_KEY')  # or OPENAI_API_KEY
    
    # Configure MCP server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", desktop_path],
        env=None
    )

    # Initialize clients
    mcp_client = MCPClient(
        server_params,
        debug=True
    )
    
    llm_client = GeminiAdapter(  # or OpenAIAdapter
        model_name='gemini-1.5-flash',  # or 'gpt-4o-mini' for OpenAI
        debug=True
    )

    try:
        # Setup the pipeline
        raw_tools = await mcp_client.get_tools()
        tools = MCPTools()
        tools.add(raw_tools)
        
        await llm_client.prepare_tools(tools)
        await llm_client.configure(api_key)

        # Example: Create a file
        message = f"Create a file called hello.txt with content 'Hello World' in path: {desktop_path}"
        response = await llm_client.send_message(message)
        tool_name, tool_args = llm_client.extract_tool_call(response)
        result = await mcp_client.execute_tool(tool_name, tool_args)
        print("Result:", result)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

## Examples

Check out the `examples` directory for more detailed examples:
- `filesystem_example.py`: Basic filesystem operations using MCP
- `filesystem_memory_example.py`: Combined filesystem and memory operations

## Development

### Adding a New LLM Adapter

1. Create a new adapter class in `src/llm/` that inherits from `BaseLLMAdapter`
2. Implement the required methods:
   - `configure`: Set up the LLM client
   - `prepare_tools`: Convert MCP tools to LLM-specific format
   - `send_message`: Send a message to the LLM
   - `extract_tool_call`: Extract tool call from LLM response

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.