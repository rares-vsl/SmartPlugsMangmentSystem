import asyncio
from smartplugagent.SmartPlugAgent import SmartPlugAgent
import re

def parse_response(response):
    return re.sub(r"^Action\[[^]]+]:\s*", "", response)

async def main():
    agent = SmartPlugAgent(debug_flag=False)

    await agent.start()

    print("SmartPlugAgent ready. Type 'exit' to quit.\n")

    try:
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                break
            if not user_input:
                continue

            result_type, content = await agent.analyse_message(user_input)
            print(f"Agent [{result_type}]: {parse_response(content)}\n")
    finally:
        await agent.llm.cleanup()

if __name__ == "__main__":
    asyncio.run(main())