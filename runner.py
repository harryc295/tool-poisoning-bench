"""Runs every scenario against a model, with the guard on and off, and
writes results/results.json.

    python runner.py --model qwen2.5:7b
"""
import argparse
import json
import pathlib

from agent import run_scenario
from scenarios import SCENARIOS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--out", default="results/results.json")
    parser.add_argument("--trials", type=int, default=3, help="repeats per scenario/guard combo")
    args = parser.parse_args()

    results = []
    for scenario in SCENARIOS:
        for guard_enabled in (False, True):
            for trial in range(args.trials):
                print(f"[{args.model}] {scenario.id:<24} guard={guard_enabled!s:<5} trial={trial}", end=" ", flush=True)
                result = run_scenario(scenario, args.model, guard_enabled)
                result["model"] = args.model
                result["trial"] = trial
                results.append(result)
                print("VIOLATION" if result["violation"] else "ok")

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {len(results)} results to {out_path}")


if __name__ == "__main__":
    main()
