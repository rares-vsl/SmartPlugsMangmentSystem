
RULES = [
    "How to reason on the task: Use 'Thought:' to reason first about the current task then on the content of CHAT HISTORY and finally on the given tools. Keep it concise and focused.",
    "How to respond to te user: Use 'Action[Answer]:' the content will be read by the user user. This must be clear and user-friendly.",
    "How to use CRITICAL tools: If a tool is marked with 'CRITICAL: Requires user confirmation.', you MUST STOP and: first explain your intention and expected outcome to the user to receive the permission using 'Action[Permission]:'. Wait for user confirmation in the next Observation formatted as: UserPermissionResponse[<message>]. If the permission response is positive, proceed with the tool call. If the permission response is negative, do NOT call the tool and instead respond using 'Action[Answer]:'.",
    "Create and Delete plug is a CRITICAL tool, use only when you have permission.",
    "How to get permission: if and ONLY if there is not tag UserPermissionResponse in the CHAT HISTORY ask the user permission with Action[Permission]. In this step dont generate any tool call.",
    "Only Critical tools needs permission.",
    "Don't answer with incomplete responses, don't tell the user technical information such as what tool you are using.",
    "Read from the CHAT HISTORY the tool responses before calling a tool, Never call a tool twice if is not necessary.",
    "To create a plug verify you have from the user all necessary data to make the request!",
    "Keep the answer as short as possible (TO SAVE TOKENS)",
    "To calculate the real time consumptions consider only plugs with status ON",
    "To before switching a plug, check it's status. After switching check the response in the CHAT HISTORY"
]

class ProceduralMemory:
    def __init__(self, custom_rules=None):
        self.rules = custom_rules or RULES
    def format(self):
        """Format rules for prompt injection."""
        if not self.rules:
            return "No rules available."

        return "".join(f"{i+1}. {r}\n" for i, r in enumerate(self.rules))