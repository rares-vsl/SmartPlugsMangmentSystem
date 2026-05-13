from pathlib import Path
import json


def loadJSON(filepath: str, memory = "Memory"):
    base_dir = Path(__file__).resolve().parent
    filepath = base_dir.parent / filepath

    if not filepath.exists():
        print(f"[{memory}] File not found: {filepath}")
        return []

    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        return data

    except Exception as e:
        print(f"[{memory}] Failed to load JSON: {e}")
        return []