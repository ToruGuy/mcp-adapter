from typing import Dict, List, Optional, Any, Tuple

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
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
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
            self.tools[name] = new_tool
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)
        
    def get_desc(self, tool_name: str) -> Optional[str]:
        tool = self.get_tool(tool_name)
        return tool.description
    
    def list_tools(self) -> List[Tuple[str, Tool]]:
        return list(self.tools.values())
        
    def remove_tool(self, tool_name: str):
        self.tools.pop(tool_name, None) 

