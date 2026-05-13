KNOWLEDGE = [
    "real_time_consumption -> how much does a plug consumes",
    "measurement units -> ELECTRICITY (kWh) | WATER (m^3) | GAS (m^3)",
    "status -> if the plug is consuming in real-time"
]

class SemanticMemory:
    def __init__(self, custom_knowledge=None):
        self.knowledge = custom_knowledge or KNOWLEDGE

    def format(self):
        """Format knowledge for prompt injection."""
        if not self.knowledge:
            return "No knowledge available."

        return "".join(f"{i+1}. {r}\n" for i, r in enumerate(self.knowledge))
