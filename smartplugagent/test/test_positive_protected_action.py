import asyncio

from smartplugagent.SmartPlugAgent import SmartPlugAgent
import httpx

async def delete_plug(plug:str):
    url = f"http://127.0.0.1:8000/api/smart-plugs/{plug}"
    async with httpx.AsyncClient() as client:
        try:
            await client.delete(url)

        except httpx.HTTPStatusError as e:
            print(f"Server error: {e}")
        except Exception as e:
            print(f"Connection error: {e}")

def print_block(text):
    print("\n\n=================")
    print(text)
    print("=================\n\n")

async def main():
    agent = SmartPlugAgent()

    s = 0

    f_answer = 0
    f_tool = 0
    f_ask = 0
    f_error = 0

    rs = []

    try:
        await agent.start()

        for i in range(0, 3):
            await  delete_plug("smart-lamp")
            r_type, response = await agent.analyse_message("I want to monitor my new lamp, it's Smart-Lamp with 0.4kwh consumption. (its an ELECTRICITY plug)")
            if "answer" in r_type:
                f_answer += 1
                rs.append(response)
            elif "ask" in r_type:
                print("==================User=================")
                print("yes, do it!")
                print("========================================")
                r_type, response = await agent.analyse_message("yes, do it")

                if "answer" in r_type:
                    if agent.debug_tools_calls() == 0:
                        f_tool += 1
                    else:
                        s += 1

                    rs.append(response)
                elif "ask" in r_type:
                    f_ask += 1

                    rs.append(response)
                    agent.reset_context()
                else:
                    f_error +=1
                    rs.append(response)
                    agent.reset_context()
            else:
                f_error +=1
                rs.append(response)
                agent.reset_context()

            agent.reset_debug_tools_calls()

        print("\n\n=================")
        print(f"success: {s} -- fail answer {f_answer}  -- fail ask: {f_ask}  --  fail error: {f_error} -- fail tool: {f_tool}")
        print("=================\n\n")

        print("\n\n=================")
        for i, msg in enumerate(rs):
            print(f"{i} : {msg}")
        print("=================\n\n")

        print(agent.debug_tools())

        if len(agent.debug_tools()) > 0:
            print("fail")

        tools_called = agent.debug_tools()
        steps = agent.debug_max_step()
        print_block(f"tools: {len(tools_called)} | steps: {steps}")

        i_t, o_t = agent.debug_token_usage()
        print_block(f"TOKEN INPUT: {i_t} | OUTPUT: {o_t}")


    finally:
        await agent.llm.cleanup()


if __name__ == "__main__":
    asyncio.run(main())