"""Auto-calibration CLI: fits [H] coefficients to plant measurements.

Usage:
    python scripts/fit_calibration.py [config.json] [-o results.json]

Defaults: config = data/fit_example.json, output = data/fit_results.json.
The config declares the observations (measured values, by result path),
the free parameters (by parameter path, with bounds), and optional
``base_overrides`` applied before fitting. To ADOPT a fit, copy the fitted
values into data/default_parameters.json (they are printed with their
paths) — the script never modifies the defaults by itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model import load_parameters  # noqa: E402
from wankoe_model.fit import fit_parameters  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Wankoe auto-calibration on measurements")
    parser.add_argument("config", nargs="?", default=str(ROOT / "data" / "fit_example.json"))
    parser.add_argument("-o", "--output", default=str(ROOT / "data" / "fit_results.json"))
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    params = load_parameters(overrides=config.get("base_overrides"))
    report = fit_parameters(
        params,
        config["observations"],
        config["free_parameters"],
        max_rounds=config.get("max_rounds", 80),
    )

    Path(args.output).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Cost: {report['initial_cost']} -> {report['final_cost']}")
    for row in report["observations"]:
        print(f"  {row['target']}: measured {row['measured']} / achieved {row['achieved']}")
    print("Fitted values (copy into data/default_parameters.json to adopt):")
    for row in report["fitted_paths"]:
        print(f"  {row['path']} = {row['value']}")
    print(f"Written: {args.output}")


if __name__ == "__main__":
    main()
