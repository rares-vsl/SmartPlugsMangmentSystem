class WorkingMemory:
    def __init__(self):
        self.store = {}
        self.history = []

    def reset(self):
        self.store = {}
        self.history = []

    def add_to_history(self, element):
        self.history.append(element)
    def get_history(self):
        if not self.history:
            return "Empty. Reason on the current task to add new elements."

        return "".join(f"{h}\n" for h in self.history)
    def update(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)

