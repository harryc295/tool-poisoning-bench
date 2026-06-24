"""Minimal client for Ollama's /api/chat, stdlib only."""
import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"


def chat(model: str, messages: list[dict], tools: list[dict]) -> dict:
    """One non-streaming call. Returns the response 'message' dict."""
    body = json.dumps({"model": model, "messages": messages, "tools": tools, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["message"]
