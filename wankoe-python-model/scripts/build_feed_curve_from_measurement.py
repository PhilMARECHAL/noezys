"""Builds the full-grid feed curve from a stored belt-cut measurement.

Measurements live in data/feed_measurements/*.json (the only plant data
this project will get — client, 2026-08-08). This script is a thin CLI
over ``wankoe_model.feed``; hypotheses H-FEED-1 (fine tail) and H-FEED-2
(top size) are documented there.

Usage:
    python scripts/build_feed_curve_from_measurement.py [measurement-name]

Default: the most recent measurement. Output: data/measured_feed_curve.json
(paste its curve into default_parameters.json to adopt it as the default,
or use wankoe_model.feed.apply_measurement at run time).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model import load_parameters  # noqa: E402
from wankoe_model.feed import build_curve_from_measurement, list_measurements, load_measurement  # noqa: E402


def main() -> None:
    measurements = list_measurements()
    if not measurements:
        raise SystemExit("no measurement in data/feed_measurements/")
    name = sys.argv[1] if len(sys.argv) > 1 else list(measurements)[-1]
    measurement = load_measurement(name)
    params = load_parameters()
    curve = build_curve_from_measurement(measurement, params)
    report = {
        "_status": (
            f"MEASURED feed curve ({name}) completed with hypotheses "
            "H-FEED-1 (fine tail) and H-FEED-2 (top size)"
        ),
        "source_measurement": f"data/feed_measurements/{name}.json",
        "moisture_pct": measurement.get("_meta", {}).get("moisture_pct_wet_basis"),
        "cumulative_passing_curve": curve,
    }
    out = ROOT / "data" / "measured_feed_curve.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(curve, indent=2))
    print(f"Written: {out}")


if __name__ == "__main__":
    main()
