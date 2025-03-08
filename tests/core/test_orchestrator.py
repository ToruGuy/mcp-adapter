"""
Tests for the orchestrator module in the MCP adapter.
"""

import unittest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.core.orchestrator import ToolOrchestrator
from src.core.tools import Tool, MCPTools
from src.core.client import MCPClient

class TestToolOrchestrator(unittest.TestCase):
    """Test the ToolOrchestrator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock clients
        self.client1 = Mock(spec=MCPClient)
        self.client1.client_name = "client1"
        self.client1.get_tools = AsyncMock()
        self.client1.execute_tool = AsyncMock()
        self.client1.close = AsyncMock()
        
        self.client2 = Mock(spec=MCPClient)
        self.client2.client_name = "client2"
        self.client2.get_tools = AsyncMock()
        self.client2.execute_tool = AsyncMock()
        self.client2.close = AsyncMock()
        
        # Create mock tools for each client
        self.tool1 = Tool(
            name="tool1",
            description="First test tool",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        )
        
        self.tool2 = Tool(
            name="tool2",
            description="Second test tool",
            parameters={
                "type": "object",
                "properties": {
                    "param2": {"type": "integer"}
                },
                "required": ["param2"]
            }
        )
        
        # Set up mock responses
        self.client1.get_tools.return_value = [self.tool1]
        self.client2.get_tools.return_value = [self.tool2]
        
        # Set up orchestrator with mock clients
        self.orchestrator = ToolOrchestrator([self.client1, self.client2])

    async def asyncSetUp(self):
        """Set up async fixtures."""
        await self.orchestrator.initialize()

    def test_initialization(self):
        """Test orchestrator initialization."""
        # Check that clients are stored
        self.assertEqual(len(self.orchestrator.clients), 2)
        self.assertIn(self.client1, self.orchestrator.clients)
        self.assertIn(self.client2, self.orchestrator.clients)
        
        # Tools should be empty before initialization
        self.assertEqual(len(self.orchestrator.tools.tools), 0)

    def test_initialize(self):
        """Test the initialize method."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Call initialize
            loop.run_until_complete(self.orchestrator.initialize())
            
            # Check that get_tools was called on each client
            self.client1.get_tools.assert_called_once()
            self.client2.get_tools.assert_called_once()
            
            # Check that tools were added
            self.assertEqual(len(self.orchestrator.tools.tools), 2)
            self.assertIn("tool1", self.orchestrator.tools.tools)
            self.assertIn("tool2", self.orchestrator.tools.tools)
            
            # Check tool-to-client mapping
            self.assertEqual(self.orchestrator.tool_to_client["tool1"], self.client1)
            self.assertEqual(self.orchestrator.tool_to_client["tool2"], self.client2)
        finally:
            loop.close()

    def test_execute(self):
        """Test the execute method."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Set up expected return value for execute_tool
            expected_result = {"status": "success"}
            self.client1.execute_tool.return_value = expected_result
            
            # Initialize and execute
            loop.run_until_complete(self.orchestrator.initialize())
            result = loop.run_until_complete(
                self.orchestrator.execute("tool1", {"param1": "test"})
            )
            
            # Check that execute_tool was called on the correct client
            self.client1.execute_tool.assert_called_once_with("tool1", {"param1": "test"})
            self.assertEqual(result, expected_result)
        finally:
            loop.close()

    def test_execute_unknown_tool(self):
        """Test executing an unknown tool."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize
            loop.run_until_complete(self.orchestrator.initialize())
            
            # Try to execute unknown tool
            with self.assertRaises(KeyError):
                loop.run_until_complete(
                    self.orchestrator.execute("unknown_tool", {})
                )
        finally:
            loop.close()

    def test_execute_invalid_args(self):
        """Test executing with invalid arguments."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize
            loop.run_until_complete(self.orchestrator.initialize())
            
            # Try to execute with invalid args (missing required param)
            with self.assertRaises(ValueError):
                loop.run_until_complete(
                    self.orchestrator.execute("tool1", {})
                )
        finally:
            loop.close()

    def test_close(self):
        """Test the close method."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Call close
            loop.run_until_complete(self.orchestrator.close())
            
            # Check that close was called on each client
            self.client1.close.assert_called_once()
            self.client2.close.assert_called_once()
        finally:
            loop.close()

    def test_client_mapping(self):
        """Test that get_client_name returns correct names."""
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize
            loop.run_until_complete(self.orchestrator.initialize())
            
            # Check client names
            self.assertEqual(self.orchestrator.get_client_name("tool1"), "client1")
            self.assertEqual(self.orchestrator.get_client_name("tool2"), "client2")
            
            # Check with unknown tool
            with self.assertRaises(KeyError):
                self.orchestrator.get_client_name("unknown_tool")
        finally:
            loop.close()

if __name__ == "__main__":
    unittest.main()