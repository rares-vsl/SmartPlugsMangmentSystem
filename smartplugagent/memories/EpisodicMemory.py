from smartplugagent.memories.utilities import loadJSON

EXAMPLE_TEMPLATE = """EXAMPLE {i} - {ex_type}
Task: {task}
{trace}
"""

class EpisodicMemory:
    def __init__(self, filepath: str):
        self.examples = loadJSON(filepath, "Episodic Memory")
    """Loads few-shot examples from a JSON file."""

    def format(self):
        """Format examples for prompt injection."""
        if not self.examples:
            return "No examples available."

        formatted_examples = []

        for i, ex in enumerate(self.examples, start=1):

            formatted_examples.append(
                EXAMPLE_TEMPLATE.format(
                    i=i,
                    ex_type=ex['type'],
                    task=ex['task'],
                    trace=ex['trace'])
            )

        return "\n".join(formatted_examples)
