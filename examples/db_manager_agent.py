import asyncio
import os
import json
from typing import Dict, Any
from pathlib import Path
from mcp import StdioServerParameters
from src.core.orchestrator import ToolOrchestrator
from src.llm import GeminiAdapter
from dotenv import load_dotenv

load_dotenv()

# Setup logging directory
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

class DBAgent:
    def __init__(self, db_path: str = ':memory:'):
        self.db_path = db_path
        
        # Configure MCP servers
        self.server_params = [
            StdioServerParameters(
                command="docker",
                args=[
                    "run",
                    "--rm",
                    "-i",
                    "-v",
                    f"{Path(self.db_path).parent.absolute()}:/mcp",
                    "mcp/sqlite",
                    "--db-path",
                    f"/mcp/{Path(self.db_path).name}"
                ],
                env=None
            )
        ]
        
        self.orchestrator = ToolOrchestrator(self.server_params)
        self.llm_client = GeminiAdapter(
            model_name='gemini-1.5-flash',
            debug=True,
            log_file=log_dir / "gemini_adapter.log"
        )

    async def initialize(self):
        """Initialize async components"""
        # First initialize orchestrator to get tools
        await self.orchestrator.initialize()
        
        # Then configure Gemini with API key and tools
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        await self.llm_client.configure(api_key)
        await self.llm_client.prepare_tools(self.orchestrator.tools)

    async def _decompose_command(self, prompt: str) -> list[str]:
        """Break complex prompts into atomic steps using LLM"""
        decomposition_prompt = (
            "Break this database operation into atomic steps: "
            f"{prompt}. Return ONLY a JSON list of steps."
        )
        response = await self.llm_client.send_message(decomposition_prompt)
        # Convert Gemini response to string
        response_text = response.text if hasattr(response, 'text') else str(response)
        return self._validate_step_format(response_text)

    def _validate_step_format(self, response: str) -> list[str]:
        """Validate and parse LLM response into list of steps"""
        try:
            if isinstance(response, (dict, list)):
                return response if isinstance(response, list) else [response]
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {response}")
            raise ValueError(f"Invalid step format: {e}")

    def _validate_single_action(self, step: str) -> bool:
        """Ensure a step contains only one executable action"""
        return len(self.llm_client.extract_tool_call(step)) == 1

    async def _execute_step(self, step: str) -> dict:
        """Execute and validate a single step"""
        for attempt in range(3):
            tool_name, tool_args = self.llm_client.extract_tool_call(step)
            result = await self.orchestrator.execute(tool_name, tool_args)
            
            if result.success:
                return result
            
            # Analyze failure and refine step
            analysis_prompt = (
                f"Step failed: {step}\nError: {result.error}\n"
                "Suggest a corrected step. Return ONLY the corrected command."
            )
            step = await self.llm_client.send_message(analysis_prompt)
        
        raise RuntimeError(f"Failed to execute step after 3 attempts: {step}")

    async def _verify_results(self, results: list[dict]) -> bool:
        """Final consistency check"""
        verification_prompt = (
            "Verify if these results indicate successful completion: "
            f"{json.dumps(results)}. Return ONLY 'YES' or 'NO'."
        )
        response = await self.llm_client.send_message(verification_prompt)
        return "YES" in response.upper()

    async def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        try:
            # Initialize components
            await self.initialize()
            
            # Agentic workflow
            steps = await self._decompose_command(user_prompt)
            print(f"Decomposed steps: {steps}")  # Debug output
            execution_results = []

            for step in steps:
                if not self._validate_single_action(step):
                    raise ValueError(f"Multi-action step detected: {step}")
                
                result = await self._execute_step(step)
                print(result)
                execution_results.append(result.data)

            # Post-execution verification
            if not await self._verify_results(execution_results):
                raise RuntimeError("Final verification failed")

            return {
                "steps_executed": len(steps),
                "results": execution_results,
                "verified": True
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            await self.orchestrator.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='MCP DB Manager Agent')
    parser.add_argument('prompt', type=str, help='Natural language command')
    parser.add_argument('--db', type=str, default=':memory:', help='Database path')
    args = parser.parse_args()
    
    async def main():
        agent = DBAgent(args.db)
        await agent.initialize()
        result = await agent.process_prompt(args.prompt)
        print(json.dumps(result, indent=2))

    asyncio.run(main())
