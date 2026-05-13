import logging

import ollama
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import json

OLLAMA_MODEL = "gpt-oss:120b-cloud"

def mcp_tool_to_ollama(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }
class OllamaClient:
    def __init__(self):
        self.write = None
        self.stdio = None
        self.tools = []
        self.model = OLLAMA_MODEL
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def call_tool(self, tool_name: str, tool_args: dict) -> str:
        print(f"[Tool] {tool_name}({json.dumps(tool_args)})")
        logging.getLogger("httpx").setLevel(logging.WARNING)

        logging.getLogger("mcp").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        try:
            result = await self.session.call_tool(tool_name, tool_args)

            output = " ".join(
                item.text if hasattr(item, "text") else str(item)
                for item in result.content
            )
            return output
        except Exception as e:
            return f"Error calling {tool_name}: {e}"

    async def connect_to_server(self, mpc_servers):
        server_params = StdioServerParameters(
            command="python",
            args=mpc_servers,
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.tools =  [mcp_tool_to_ollama(t) for t in response.tools]
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    def prompt(self, messages, full_response = False, stats_required = True):
        for i in range (0, 2):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    stream=False,
                    think=False,
                    options={
                        "stop": ["\nObservation"]
                    }
                )
                break
            except Exception as last_exception:
                if i == 1:
                    raise last_exception


        stats = {
            "input_tokens": response.get("prompt_eval_count", 0),
            "output_tokens": response.get("eval_count", 0),
            "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
        }

        if stats_required:
           return response if full_response else response["message"], stats
        return response if full_response else response["message"]

    async def cleanup(self):
        await self.exit_stack.aclose()