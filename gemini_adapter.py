import google.generativeai as genai
from typing import Any, Dict, List, Optional
from pathlib import Path

import mcp
from logger import MCPLogger

from mcp_tools import MCPtools

class GeminiAdapter:
    def __init__(self, 
                 model_name: str = 'gemini-1.5-flash',
                 debug: bool = False,
                 log_file: Optional[Path] = None):
        self.model_name = model_name
        self.model = None
        self.chat = None
        self.tools = None
        self.logger = MCPLogger("GeminiAdapter", debug_mode=debug, log_file=log_file)

    async def configure(self, api_key: str, **kwargs) -> None:
        self.logger.log_debug(f"Configuring Gemini with model {self.model_name}")
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=self.tools
            )
            self.chat = self.model.start_chat()
            self.logger.log_info("Successfully configured Gemini model")
        except Exception as e:
            self.logger.log_error(f"Failed to configure Gemini: {str(e)}")
            raise

    async def prepare_tools(self, mcp_tools: MCPtools) -> Dict:
        mcp_tools = mcp_tools.list_tools()
        self.logger.log_debug(f"Preparing {len(mcp_tools)} tools for Gemini")
        self.tools = [{"function_declarations": []}]
        try:
            for tool in mcp_tools:
                self.logger.log_debug(f"Converting tool: {tool.name}")

                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": tool.function_type,
                        "properties": tool.properties,
                        "required": tool.required
                    },
                }
                self.tools[0]["function_declarations"].append(tool_dict)
            
            self.logger.log_info(f"Successfully prepared {len(mcp_tools)} tools")
            return self.tools
            
        except Exception as e:
            self.logger.log_error(f"Failed to prepare tools: {str(e)}")
            raise

    async def send_message(self, message: str) -> Any:
        self.logger.log_debug(f"Sending message to Gemini: {message[:100]}...")
        try:
            response = await self.chat.send_message_async(message)
            self.logger.log_info("Successfully received response from Gemini")
            return response
        except Exception as e:
            self.logger.log_error(f"Failed to send message: {str(e)}")
            raise

    def _extract_by_schema(self, value: Any, schema: Dict[str, Any]) -> Any:
        """Extract value according to the schema definition"""
        # Handle primitive types
        if schema.get("type") == "string":
            return str(value)
        elif schema.get("type") == "number":
            return float(value)
        elif schema.get("type") == "integer":
            return int(value)
        elif schema.get("type") == "boolean":
            return bool(value)
            
        # Handle arrays
        elif schema.get("type") == "array":
            items_schema = schema.get("items", {})
            if hasattr(value, '__iter__'):
                return [self._extract_by_schema(item, items_schema) for item in value]
            return []
            
        # Handle objects
        elif schema.get("type") == "object":
            if hasattr(value, 'items'):
                properties = schema.get("properties", {})
                result = {}
                items = dict(value.items())
                
                for prop_name, prop_schema in properties.items():
                    if prop_name in items:
                        result[prop_name] = self._extract_by_schema(items[prop_name], prop_schema)
                        
                return result
            return {}
            
        # Default
        return value

    def extract_tool_call(self, response: Any) -> tuple[str, Dict[str, Any]]:
        """
        Extract tool call using the tool's schema definition.
        """
        try:
            function_call = response.parts[0].function_call
            tool_name = str(function_call.name)
            
            # Get the tool schema
            tool = next((t for t in self.tools[0]["function_declarations"] 
                        if t["name"] == tool_name), None)
            
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            # Extract according to schema
            raw_args = function_call.args
            tool_args = self._extract_by_schema(raw_args, tool["parameters"])
            
            self.logger.log_debug(f"Extracted arguments: {tool_args}")
            return tool_name, tool_args
            
        except Exception as e:
            self.logger.log_error(f"Failed to extract tool call: {str(e)}")
            raise