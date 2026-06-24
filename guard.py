"""Heuristic injection scanner: screens tool descriptions and tool output
text before they reach the model's context. Same approach as mcp-sentinel's
rules.py (word-boundary regex, not substring) -- deliberately simple, see
the limitations section of report.py for what this misses.
"""
import re

# ponytail: keyword/regex heuristics only, no semantic understanding -- the
# obfuscated scenarios in scenarios.py are designed to slip past this.
# Upgrade path: classify with a small model instead of regex if false
# negatives on paraphrased injections matter more than latency/cost.
RULES: list[tuple[str, re.Pattern]] = [
    (
        "override_instructions",
        re.compile(r"\b(ignore|disregard|forget)\b(?:\s+\w+){0,3}\s+\b(previous|prior|above|earlier)\b(?:\s+\w+){0,3}\s+\b(instructions?|directions?|prompt)\b", re.I),
    ),
    ("new_instructions_marker", re.compile(r"\b(system|new|updated)\s*:\s", re.I)),
    ("cc_bcc_redirect", re.compile(r"\b(cc|bcc|forward|also\s+(?:send|email|notify))\b(?:\s+\w+){0,6}\s+[\w.+-]+@[\w-]+\.[\w.-]+", re.I)),
    ("exfil_keyword", re.compile(r"\bexfiltrat\w*\b", re.I)),
    (
        "compliance_social_engineering",
        re.compile(r"\bfor\s+(compliance|audit(?:ing)?|logging)\s+purposes?\b(?:\s+\w+){0,6}\s+(cc|send|email|forward)", re.I),
    ),
]


def scan(text: str) -> list[str]:
    """Return the names of every rule that matches text."""
    return [name for name, pattern in RULES if pattern.search(text)]


def clean(text: str) -> str:
    """Redact any matched span, leaving the rest of the text intact."""
    out = text
    for _, pattern in RULES:
        out = pattern.sub("[REDACTED: possible injected instruction]", out)
    return out
