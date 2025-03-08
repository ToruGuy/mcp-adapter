#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run tests for each module
echo "Running tests for core/tools.py..."
python tests/core/test_tools.py -v

echo "Running tests for core/logger.py..."
python tests/core/test_logger.py -v

# Add more test modules as they are fixed
# python tests/core/test_orchestrator.py -v
# python tests/llm/test_openai.py -v

echo "All tests completed!"