import google.generativeai as genai
from typing import Any, Dict, List

class GeminiAdapter():
    def __init__(self, model_name: str = 'gemini-1.5-flash'):
        self.model_name = model_name
        self.model = None
        self.chat = None
        self.tools = None

    async def configure(self, api_key: str, **kwargs) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools
        )
        self.chat = self.model.start_chat()

    async def prepare_tools(self, mcp_tools: List[Any]) -> Dict:
        self.tools = [{"function_declarations": []}]
        
        for tool in mcp_tools:
            name, description, inputSchema = tool
            function_type = inputSchema[1]["type"]
            properties = inputSchema[1]["properties"]
            
            if properties == {}:
                tool_dict = {
                    "name": name[1],
                    "description": description[1],
                    "parameters": {
                        "type": 'Object',
                        "properties": {
                            "_dummy": {
                                "type": "string",
                                "description": "Unused parameter"
                            }
                        },
                        "required": []
                    },
                }
            else:
                tool_dict = {
                    "name": name[1],
                    "description": description[1],
                    "parameters": {
                        "type": function_type,
                        "properties": properties,
                        "required": inputSchema[1]["required"]
                    },
                }
            self.tools[0]["function_declarations"].append(tool_dict)
        
        return self.tools

    async def send_message(self, message: str) -> Any:
        return await self.chat.send_message_async(message)

    def extract_tool_call(self, response: Any) -> tuple[str, Dict[str, Any]]:
        tool = response.parts[0].function_call
        tool_name = tool.name
        tool_args = {k: v for k, v in tool.args.items() if k != "_dummy"}
        return tool_name, tool_args