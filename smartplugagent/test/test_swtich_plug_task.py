import asyncio

import httpx

from smartplugagent.SmartPlugAgent import SmartPlugAgent

async def set_plug_status(plug:str, status:str):
    url = f"http://127.0.0.1:8000/api/smart-plugs/{plug}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, json={'status': status.lower()})
            response.raise_for_status()
            data = response.json()

            return data

        except httpx.HTTPStatusError as e:
            print(f"Server error: {e}")
        except Exception as e:
            print(f"Connection error: {e}")

async def check_plug_status(plug:str):
    url = f"http://127.0.0.1:8000/api/smart-plugs/{plug}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            return data

        except httpx.HTTPStatusError as e:
            print(f"Server error: {e}")
        except Exception as e:
            print(f"Connection error: {e}")

def print_block(text):
    print("\n\n=================")
    print(text)
    print("=================\n\n")

async def main():
    agent = SmartPlugAgent(debug_flag=True)

    success = 0

    fail_for_switch = 0
    fail_for_ask = 0
    fail_for_error = 0

    responses = []

    try:
        await agent.start()
        plug = "refrigerator"
        for i in range(0, 10):
            await set_plug_status(plug, "off")
            r_type, response = await agent.analyse_message("Can you turn on the fridge?")

            if "answer" in r_type:

                plug_info = await check_plug_status(plug)
                print("[xx] ", plug_info["status"], "-", response,)
                if "off" in plug_info["status"]:
                    fail_for_switch += 1
                else : success += 1
            elif "ask" in r_type:
                fail_for_ask += 1
                agent.reset_context()
            else:
                fail_for_error +=1

            responses.append(response)



        print_block("".join(f"{i} : {msg}\n" for i, msg in enumerate(responses)))

        print_block(f"success: {success} -- fail switch: {fail_for_switch}  -- fail ask: {fail_for_ask}  --  fail error: {fail_for_error}")

        tools_called = agent.debug_tools()
        steps = agent.debug_max_step()
        print_block(f"tools: {len(tools_called)} | steps: {steps}")

        i_t, o_t = agent.debug_token_usage()
        print_block(f"TOKEN INPUT: {i_t} | OUTPUT: {o_t}")

    finally:
        await agent.llm.cleanup()


if __name__ == "__main__":
    asyncio.run(main())