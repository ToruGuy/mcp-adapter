# MCP Adapter

A Python package that provides adapters for various LLMs (Large Language Models) to work with the Model Context Protocol (MCP).

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