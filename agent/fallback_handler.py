import json

def get_fallback():
    with open("agent/static_fallbacks.json") as f:
        fallbacks = json.load(f)
    return fallbacks.get("default", {"answer": "Sorry, something went wrong.", "confidence": 0.0})
