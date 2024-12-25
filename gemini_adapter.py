import google.generativeai as genai
from typing import Any, Dict, List, Optional
from pathlib import Path
from logger import MCPLogger

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

    async def prepare_tools(self, mcp_tools: List[Any]) -> Dict:
        self.logger.log_debug(f"Preparing {len(mcp_tools)} tools for Gemini")
        self.tools = [{"function_declarations": []}]
        
        try:
            for tool in mcp_tools:
                name, description, inputSchema = tool
                self.logger.log_debug(f"Converting tool: {name[1]}")
                
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

    def extract_tool_call(self, response: Any) -> tuple[str, Dict[str, Any]]:
        self.logger.log_debug("Extracting tool call from response")
        try:
            tool = response.parts[0].function_call
            tool_name = tool.name
            tool_args = {k: v for k, v in tool.args.items() if k != "_dummy"}
            self.logger.log_info(f"Extracted tool call: {tool_name}")
            return tool_name, tool_args
        except Exception as e:
            self.logger.log_error(f"Failed to extract tool call: {str(e)}")
            raise