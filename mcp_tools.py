from typing import Dict, List, Optional, Any

class MCPtools:
    def __init__(self):
        self.tools = {}
    
    def add(self, tools) -> None:
        for tool in tools:
            self.tools[tool['name']] = tool
      
    
    def get_tool(self, tool_name: str) -> Optional[List[Any]]:
        if self.tools[tool_name] is not None:
            return self.tools[tool_name]
        return None
    
    def get_desc(self, tool_name: str) -> Optional[str]:
        tool = self.get_tool(tool_name)
        return tool['description'] if tool else None
    
    def list_tools(self) -> Dict[str, Any]:
        return self.tools
        
    def remove_tool(self, tool_name: str) -> None:
        self.tools.pop(tool_name)

