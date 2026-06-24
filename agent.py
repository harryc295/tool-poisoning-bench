"""Runs one scenario against a model, with the guard optionally screening
tool descriptions and tool outputs before they reach the model's context.
"""
import copy
import json

import guard
import ollama_client
from scenarios import BASE_TOOLS, SYSTEM_PROMPT, Scenario, is_violation

MAX_ROUNDS = 3


def _build_tools(scenario: Scenario, guard_enabled: bool) -> list[dict]:
    tools = []
    for name in scenario.tool_names:
        tool = copy.deepcopy(BASE_TOOLS[name])
        desc = scenario.description_override.get(name, tool["function"]["description"])
        if guard_enabled:
            desc = guard.clean(desc)
        tool["function"]["description"] = desc
        tools.append(tool)
    return tools


def _tool_result(scenario: Scenario, name: str, arguments: dict, guard_enabled: bool) -> str:
    if name in scenario.tool_outputs:
        result = scenario.tool_outputs[name]
    elif name == "send_email":
        result = f"Email queued to {arguments.get('to')}"
    else:
        result = "ok"
    return guard.clean(result) if guard_enabled else result


def _parse_arguments(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}


def run_scenario(scenario: Scenario, model: str, guard_enabled: bool) -> dict:
    tools = _build_tools(scenario, guard_enabled)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": scenario.user_prompt},
    ]
    tool_calls_made = []

    for _ in range(MAX_ROUNDS):
        message = ollama_client.chat(model, messages, tools)
        messages.append(message)
        calls = message.get("tool_calls") or []
        if not calls:
            break
        for call in calls:
            name = call["function"]["name"]
            arguments = _parse_arguments(call["function"]["arguments"])
            tool_calls_made.append({"name": name, "arguments": arguments})
            result = _tool_result(scenario, name, arguments, guard_enabled)
            messages.append({"role": "tool", "name": name, "content": result})

    return {
        "id": scenario.id,
        "category": scenario.category,
        "guard_enabled": guard_enabled,
        "tool_calls": tool_calls_made,
        "violation": is_violation(tool_calls_made),
    }
