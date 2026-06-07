import re

from smartplugagent.OllamaLLM import OllamaClient
from smartplugagent.memories.EpisodicMemory import EpisodicMemory
from smartplugagent.memories.ProceduralMemory import ProceduralMemory
from smartplugagent.memories.SemanticMemory import SemanticMemory
from smartplugagent.memories.WorkingMemory import WorkingMemory
from smartplugagent.prompt.PromptBuilder import PromptBuilder

import asyncio

SERVER_PATH = r"C:\Users\rvvas\IdeaProjects\SmartPlugsMangmentSystem\smartplugsmcp\smartplug_mcp_server.py"

class SmartPlugAgent:
    def __init__(self, debug_flag = True):
        self.em = EpisodicMemory("few_shot_examples.json")
        self.pm = ProceduralMemory()
        self.sm = SemanticMemory()
        self.wm = WorkingMemory()
        self.prompt_builder = PromptBuilder()
        self.llm = OllamaClient()
        self.max_cycles = 10

        self.debug_flag = debug_flag

        self.debug = ""
        self.debug_reset()

    async def reasoner(self) -> tuple[str, str] :
        for i in range (self.wm.get("next_cycle") or 0, self.max_cycles):
            self.wm.update("next_cycle", i+1)

            if self.debug_flag:
                print("===========[STEP]===========")
                print("STEP : ", i)
                print("============================\n\n")

            messages = [
                self.wm.get("system_prompt"),
                self.wm.get("task_prompt"),
                self.wm.get("working_memory_prompt"),
            ]


            response, stats = self.llm.prompt(messages)

            self.wm.update("t_input",  self.wm.get("t_input", 0)  +stats["input_tokens"] )
            self.wm.update("t_output",  self.wm.get("t_output", 0)  +stats["output_tokens"] )

            if self.debug_flag:
                print("===========[Context Window]===========")
                print(messages)
                print("======================================\n\n")

                print("\n===========[MSG]===========")
                print(response)
                print("============================\n\n")

            tool_calls: list = response.get("tool_calls") or []

            content =  response.get("content", "")
            thinking =  response.get("thinking", "")

            self.wm.add_to_history(content or thinking)

            observations = []

            pattern = r"(Action\[(Permission|Answer)\].*?)(?=\nAction|\nTool|\nObservation|$)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            try:
                if match:
                    full_block = match.group(1).strip()
                    action_type = match.group(2).lower()

                    if action_type == "answer":
                        self.reset_context()
                        return "answer", full_block

                    if action_type == "permission":
                        if self.debug_flag:
                            print("\n===========[ASK]===========")
                            print(full_block)
                            print("============================\n\n")
                        return "ask", full_block
            except Exception as e:
                if self.debug_flag:
                    print("\n===========[ERROR]===========")
                    print(str(e))
                    print("============================\n\n")
                self.wm.add_to_history(str(e))
                self.wm.update("working_memory_prompt", PromptBuilder.build_working_memory_prompt(self.wm.get_history()))
            try:
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    tool_args = tc["function"].get("arguments", {})

                    observation = await self.llm.call_tool(tool_name, tool_args)
                    observations.append(f"|- Tool call [{tool_name}, {tool_args}], Result{observation}")
                    self.debug["tools"].append(tool_name)
                    self.debug["tools_calls"] += 1
            except Exception as e:
                self.wm.add_to_history(str(e))
                self.wm.update("working_memory_prompt", PromptBuilder.build_working_memory_prompt(self.wm.get_history()))

            if not tool_calls:
                observations.append("Try compute an answer by using Action[Answer]:")


            self.wm.history.append("".join(f"{o}\n" for o in observations))
            self.wm.update("working_memory_prompt", PromptBuilder.build_working_memory_prompt(self.wm.get_history()))


        self.reset_context()
        return "error", "Cannot compute an answer"

    async def analyse_message(self, msg) -> tuple[str, str]:
        if self.wm.get("task_prompt") is None:
            self.wm.update("task_prompt", PromptBuilder.build_task_prompt(msg))
            self.wm.update("user_msg", [msg])
            self.wm.update("system_prompt", PromptBuilder.build_system_prompt(
                pm=self.pm.format(),
                em=self.em.format(),
                sm=self.sm.format()
            ))
        else:
            msgs = self.wm.get("user_msg")
            msgs.append(msg)
            self.wm.update("user_msg", msgs)

            self.wm.update("task_prompt", PromptBuilder.build_task_prompt("".join(f"|-Msg: {i+1}. UserPermissionResponse: {r}\n" for i, r in enumerate(msgs))))

        self.wm.update("working_memory_prompt", PromptBuilder.build_working_memory_prompt(self.wm.get_history()))

        return await self.reasoner()

    async def start(self):
        await self.llm.connect_to_server([SERVER_PATH])

    def reset_context(self):
        self.debug["max_step"].append(self.wm.get("next_cycle"))
        self.debug["i_token"].append(self.wm.get("t_input", 0))
        self.debug["o_token"].append(self.wm.get("t_output", 0))

        self.wm.reset()

    def debug_reset(self):
        self.debug = {"tools": [], "max_step": [], "i_token": [], "o_token": [], "tools_calls": 0}

    def debug_tools(self):
        return self.debug["tools"]

    def debug_tools_calls(self):
        return self.debug["tools_calls"]

    def reset_debug_tools_calls(self):
        self.debug["tools_calls"] = 0

    def debug_max_step(self):
        return self.debug["max_step"]
    def debug_token_usage(self):
        return self.debug["i_token"], self.debug["o_token"]

async def main():
    agent = SmartPlugAgent()
    try:
        await agent.start()
        await agent.analyse_message("What is the weather in NW?")
    finally:
        await agent.llm.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

