import asyncio

import httpx

from smartplugagent.SmartPlugAgent import SmartPlugAgent
from smartplugagent.memories.utilities import loadJSON


async def fetch_plug_stats():
    url = "http://127.0.0.1:8000/api/smart-plugs/stats"
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

async def get_config(task_type, utility= "electricity", status = "on"):
    dataset = loadJSON("test/query_tasks.json")
    stats = await fetch_plug_stats()

    if "info" in task_type:
        info_stats = stats["plugs_by_utility"][utility.upper()]
        all_values = {
            value
            for plug in info_stats
            for key, value in plug.items()
            if key != "id"
        }

        return dataset["utility_plugs_info"].format(utility=utility), all_values
    if "monitoring" in task_type:
        return dataset["utility_plugs_monitoring"].format(utility=utility), [stats["consumption"][str(utility).upper()]]
    if "status" in task_type:
        status_stats = stats["plugs_by_status"][str(status).upper()]
        all_values = [plug["name"] for plug in status_stats]
        return dataset["utility_plugs_status"].format(status=status), all_values

    return "", ""

def word_count(expected_words, response):
    c = 0
    f_response = re.sub(r'[\u2010-\u2015]', '-', response)
    f_response = " ".join(f_response.split())
    for word in expected_words:
        if str(word).lower() in f_response.lower():
            c += 1
    return c

def word_count_stats(expected_words, responses):
    counts = []

    print(expected_words)

    for resp in responses:
        # Count how many expected words are inside this specific response string
        counts.append({
            "response": resp,
            "matches": word_count(expected_words, resp)
        })

    for i, item in enumerate(counts):
        print(f"response {i} contains {item['matches']}/{len(expected_words)} expected words.")

async def test_task(agent, task, utility= "electricity", status = "on"):
    success = 0
    fail_for_ask = 0
    fail_for_error = 0
    fail_for_match = 0

    responses = []

    task, expected_words = await get_config(task, utility, status)

    print_block("Task: " + task)

    for i in range(0,10):
        r_type, response = await agent.analyse_message(task)
        responses.append(response)

        if "answer" in r_type:
            if word_count(expected_words, response) == len(expected_words):
                success += 1
            else:
                fail_for_match += 1
        elif "ask" in r_type: # We don't need permission for this task
            fail_for_ask += 1
        else:
            fail_for_error +=1

    print_block("".join(f"{i} : {msg}\n" for i, msg in enumerate(responses)))
    word_count_stats(expected_words, responses)
    print_block(f"success: {success}-- fail match: {fail_for_match}  -- fail ask: {fail_for_ask}  --  fail error: {fail_for_error}")

    tools_called = agent.debug_tools()
    steps = agent.debug_max_step()
    print_block(f"tools: {len(tools_called)} | steps: {steps}")

    i_t, o_t = agent.debug_token_usage()
    print_block(f"TOKEN INPUT: {i_t} | OUTPUT: {o_t}")

    agent.debug_reset()

    return [
        task,
        f"success: {success}-- fail match: {fail_for_match}  -- fail ask: {fail_for_ask}  --  fail error: {fail_for_error}",
        f"tools: {len(tools_called)} | steps: {steps}"
        f"TOKEN INPUT: {i_t} | OUTPUT: {o_t}"
    ]

def print_block(text):
    print("\n\n=================")
    print(text)
    print("=================\n\n")

import re
async def main():
    agent = SmartPlugAgent(debug_flag=True)
    results = []
    try:
        await agent.start()

        r = await test_task(agent, "status")
        results.append(r)
        r = await test_task(agent, "info", utility= "electricity")
        results.append(r)
        r = await test_task(agent, "monitoring", utility= "water")
        results.append(r)
    finally:
        await agent.llm.cleanup()

    print("===============Summary================")
    for res in results:
        print(res)
        print("----------------------------------")


if __name__ == "__main__":
    asyncio.run(main())