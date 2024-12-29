# MCP Adapter

A Python package that provides adapters for various LLMs (Large Language Models) to work with the Model Context Protocol (MCP).

## Features

- Base LLM adapter interface
- Gemini adapter implementation
- Support for filesystem and memory MCP servers
- Extensible design for adding new LLM adapters

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mcp-adapter
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

1. Create a `.env` file in the project root (you can copy from `.env.example`):
```bash
cp .env.example .env
```

2. Set your environment variables in `.env`:
```bash
GEMINI_API_KEY=your_api_key_here
DESKTOP_PATH=/path/to/your/desktop
```

## Usage

The package includes two example scripts demonstrating how to use the adapters:

### Basic Filesystem Example

```python
from mcp import StdioServerParameters
from src.llm import GeminiAdapter
from src.core import MCPClient, MCPTools

# Initialize clients
mcp_client = MCPClient(server_params)
llm_client = GeminiAdapter()

# Setup tools
tools = MCPTools()
tools.add(await mcp_client.get_tools())

# Configure LLM
await llm_client.prepare_tools(tools)
await llm_client.configure(api_key)

# Use the LLM
response = await llm_client.send_message("Create a file called test.txt")
```

Run the example:
```bash
python examples/filesystem_example.py
```

### Filesystem and Memory Example

Demonstrates using both filesystem and memory MCP servers together:

```bash
python examples/filesystem_memory_example.py
```

## Project Structure

```
mcp-adapter/
├── src/
│   ├── core/           # Core functionality
│   │   ├── client.py   # MCP client wrapper
│   │   ├── tools.py    # Tools management
│   │   └── logger.py   # Logging utilities
│   └── llm/            # LLM adapters
│       ├── base.py     # Base adapter interface
│       └── gemini.py   # Gemini implementation
├── examples/           # Usage examples
└── logs/              # Log files directory
```

## Adding New LLM Adapters

To add support for a new LLM:

1. Create a new file in `src/llm/` for your adapter
2. Inherit from `BaseLLMAdapter`
3. Implement the required abstract methods:
   - `configure()`
   - `prepare_tools()`
   - `send_message()`
   - `extract_tool_call()`

## Requirements

- Python 3.8+
- google-generativeai
- python-dotenv
- mcp
