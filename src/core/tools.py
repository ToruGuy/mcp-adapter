from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from src.core.logger import MCPLogger

class Tool:
    def __init__(self, name: str, 
                 description: str, 
                 function_type: str, 
                 properties: Dict[str, Any],
                 required: List[str]):
        self.name = name
        self.description = description
        self.function_type = function_type
        self.properties = properties
        self.required = required


class MCPTools:
    def __init__(self, tools: Optional[List[Tool]] = None):
        self.tools = tools or []
    
    def __len__(self) -> int:
        return len(self.tools)
    
    def add(self, tools: List[Tuple[str, str, List[Dict[str, Any]]]]) -> None:
        for tool in tools:
            name, description, input_schema = tool
            
            function_type = input_schema[1]["type"]
            properties = input_schema[1]["properties"]
            required = input_schema[1].get("required", [])

            if not properties:
                properties = {
                    "_dummy": {
                        "type": "string",
                        "description": "Unused parameter"
                    }
                }
            
            new_tool = Tool(
                name=name[1],
                description=description[1],
                function_type=function_type,
                properties=properties,
                required=required
            )
            self.tools.append(new_tool)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
        
    def list_tools(self) -> List[Tool]:
        return self.tools
        
    def remove_tool(self, tool_name: str):
        self.tools = [t for t in self.tools if t.name != tool_name]
