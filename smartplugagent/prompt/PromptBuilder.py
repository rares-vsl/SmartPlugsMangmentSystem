
BASE_TEMPLATE = """You are a smart home assistant that manages and monitor user smart plugs. Don't answer question out of this domain.
You always follow the Thought, Action format. Never respond with plain text only.

In the CHAT HISTORY you can find previous Thought, Action cycles with Observations of action response to resolve the user question. 
If is empty use tools to make request. Before calling tools check if the data is already there.
"""

MEMORY_SLOT = """==
{MEMORY}=="""

class PromptBuilder:
    def __init__(self):
        self.prompt_task = ""

    @staticmethod
    def build_task_prompt(task: str):
        return {
            "role": "user",
            "content": task
        }

    @staticmethod
    def build_system_prompt(pm = None, em = None, sm = None):
        memory_sections = ""

        if pm:
            memory_sections += MEMORY_SLOT.format(MEMORY=
                                                  f"HOW and WHEN to ACT:\n{pm}")
        if sm:
            memory_sections += MEMORY_SLOT.format(MEMORY=
                                                  f"For any doubt use this information:\n{sm}")
        if em:

            memory_sections += MEMORY_SLOT.format(MEMORY=
                                                 f"Look at the examples to handle the interation with the user:\n{em}")


        return {
            "role": "system",
            "content": BASE_TEMPLATE + memory_sections
        }

    @staticmethod
    def build_working_memory_prompt(working_memory_content):
        return {
            "role": "assistant",
            "content": """CHAT HISTORY - List of interactions:
{wm}""".format(wm=working_memory_content)
        }
