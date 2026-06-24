# tool-poisoning-bench

[![test](https://github.com/harryc295/tool-poisoning-bench/actions/workflows/test.yml/badge.svg)](https://github.com/harryc295/tool-poisoning-bench/actions/workflows/test.yml)

Measures how often a tool-using LLM agent falls for an attacker
instruction hidden in a tool's *description* versus hidden in a tool's
*output* (indirect prompt injection), and how much a lightweight regex
guard reduces it. Runs against a local open-source model through
Ollama, so it needs no API key and costs nothing to run.

## Why

Most write-ups on tool poisoning show one cherry-picked attack that
works once. This benchmark scores eight scenarios automatically
instead: control, description-injection, and output-injection, each
with an explicit, a social-engineering, and an obfuscated variant, run
three trials at a time with the guard on and off. It turns "the guard
works" into a number you can rerun and check.

## Results

Latest run against `qwen2.5:7b`, 3 trials per cell:

| Category | Guard | Violations | N | Rate |
|---|---|---|---|---|
| control | off | 0 | 9 | 0% |
| control | on | 0 | 9 | 0% |
| tool_description_injection | off | 3 | 9 | 33% |
| tool_description_injection | on | 0 | 9 | 0% |
| tool_output_injection | off | 0 | 9 | 0% |
| tool_output_injection | on | 0 | 9 | 0% |

Only the explicit "ignore previous instructions" override in a tool
*description* succeeded, and only with the guard off. The same phrase
in a tool's *output*, and every social-engineering or obfuscated
variant, failed against this model regardless of the guard. Full
writeup with methodology and limitations: [`results/report.md`](results/report.md).

## See it happen

Two standalone, narrated scripts in [`demo/`](demo/) show the same
mechanic with no statistics attached: a code-execution tool and a
webpage-fetch tool, both clean, both handing back a poisoned result.

```sh
python demo/run_code_demo.py
python demo/fetch_webpage_demo.py
```

## How it works

- `scenarios.py` -- the eight scenarios: toolset, user task, where the
  injected instruction lives (if anywhere), and what counts as a
  violation.
- `guard.py` -- word-boundary regex rules that screen tool descriptions
  and tool outputs before they reach the model. Deliberately simple;
  the obfuscated scenarios are built to slip past it.
- `agent.py` -- runs one scenario: builds the (possibly guarded)
  toolset, loops the model against Ollama's tool-calling API, executes
  tool calls against canned responses, and checks for a violation.
- `ollama_client.py` -- a ~10-line stdlib HTTP client for Ollama's
  `/api/chat`.
- `runner.py` / `report.py` -- run every scenario N times and turn the
  results into a markdown table plus findings and limitations.

## Quickstart

```sh
ollama pull qwen2.5:7b
python runner.py --model qwen2.5:7b --trials 3
python report.py
```

No dependencies beyond the standard library and a running Ollama
server (`ollama serve`).

## Tests

```sh
python -m unittest test_bench.py
```

Covers the guard's regex rules (including the word-boundary false
positive class mcp-sentinel hit on substring matching) and the
violation check. Doesn't call a live model, so it runs in CI without
Ollama installed.

## Limitations

Small N, synthetic hand-written scenarios, one model family, and a
guard that's regex-based by design. Full list in
[`results/report.md`](results/report.md).
