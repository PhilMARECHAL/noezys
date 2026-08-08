"""Runs a parameter sweep from a JSON config and writes the ranked results.

Usage:
    python scripts/run_sweep.py [config.json] [-o results.json]

Defaults: config = data/sweep_example.json, output = data/sweep_results.json.
The config's optional ``base_overrides`` are applied to the default
parameters before sweeping (e.g. to set available hours).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model import load_parameters  # noqa: E402
from wankoe_model.optimize import run_sweep  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Wankoe parameter sweep")
    parser.add_argument("config", nargs="?", default=str(ROOT / "data" / "sweep_example.json"))
    parser.add_argument("-o", "--output", default=str(ROOT / "data" / "sweep_results.json"))
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    params = load_parameters(overrides=config.get("base_overrides"))
    report = run_sweep(params, config)

    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Evaluated {report['evaluated']} scenarios ({len(report['failed'])} failed)")
    print(f"Tonnage basis: {report['tonnage_basis']}")
    if report["best"]:
        print("Best configuration:")
        for label, value in report["best"]["values"].items():
            print(f"  {label} = {value}")
        print(f"  score = {report['best']['score']}")
        for key, value in report["best"]["kpis"].items():
            print(f"  {key} = {value}")
    print(f"Written: {args.output}")


if __name__ == "__main__":
    main()
