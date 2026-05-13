import asyncio

from smartplugagent.SmartPlugAgent import SmartPlugAgent

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

        for i in range(0, 10):
            r_type, response = await agent.analyse_message("I want to monitor my new lamp, it's Living‑Room Lamp with 2.4kwh consumption.")

            if "answer" in r_type:
                f_answer += 1
                rs.append(response)
            elif "ask" in r_type:
                r_type, response = await agent.analyse_message("No, I change my mind")

                if "answer" in r_type:
                    if agent.debug_tools_calls() == 0:
                        s += 1
                    else:
                        f_tool += 1

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
            print(f"[xx] success: {s} -- fail answer {f_answer}  -- fail ask: {f_ask}  --  fail error: {f_error} -- fail tool: {f_tool}")

        print("\n\n=================")
        print(f"success: {s} -- fail answer {f_answer}  -- fail ask: {f_ask}  --  fail error: {f_error} -- fail tool: {f_tool}")
        print("=================\n\n")

        print("\n\n=================")
        for i, msg in enumerate(rs):
            print(f"{i} : {msg}")
        print("=================\n\n")

        tools_called = agent.debug_tools()
        steps = agent.debug_max_step()
        print_block(f"tools: {len(tools_called)} | steps: {steps}")

        print(agent.debug_tools())

        if len(agent.debug_tools()) > 0:
            print("fail")

        i_t, o_t = agent.debug_token_usage()
        print_block(f"TOKEN INPUT: {i_t} | OUTPUT: {o_t}")


    finally:
        await agent.llm.cleanup()


if __name__ == "__main__":
    asyncio.run(main())