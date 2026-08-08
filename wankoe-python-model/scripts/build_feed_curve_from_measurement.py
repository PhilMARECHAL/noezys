"""Builds the full-grid feed curve from the belt-cut measurement.

Measured points (data/feed_measurement_2026-08-08.json) cover 19-200 mm.
The full engine grid (0.063-320 mm) is completed with two documented
hypotheses, both replaceable by data without touching the code:

- H-FEED-1 (fine tail, < 19 mm): shape of the CALIBRATED reference curve,
  renormalized to hit the measured 45 % passing at 19 mm. To be replaced by
  a sieve analysis of the fine fraction.
- H-FEED-2 (top size, > 200 mm): log-linear from the measured 81 % at
  200 mm up to 100 % at the engine's top mesh (320 mm).

In between, measured averages are interpolated log-linearly.

Output: data/measured_feed_curve.json. Paste its curve into
data/default_parameters.json (feed_product.cumulative_passing_curve) or
load it via overrides.

Usage: python scripts/build_feed_curve_from_measurement.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model.scenario import interp_curve, load_parameters  # noqa: E402


def loglin(x, x0, p0, x1, p1):
    t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
    return p0 + t * (p1 - p0)


def build() -> dict:
    with open(ROOT / "data" / "feed_measurement_2026-08-08.json", encoding="utf-8") as f:
        meas = json.load(f)
    with open(ROOT / "data" / "reference_feed_curve.json", encoding="utf-8") as f:
        ref_curve = json.load(f)["cumulative_passing_curve"]

    points = sorted(
        (float(mesh), row["average"]) for mesh, row in meas["cumulative_passing_pct"].items()
    )
    params = load_parameters()
    grid = sorted(set(params["mesh_series_mm"]) | set(params["engine"]["extension_meshes_mm"]))
    top_mesh = grid[-1]
    x_min, p_min = points[0]  # (19 mm, 45 %)
    x_max, p_max = points[-1]  # (200 mm, 81 %)
    ref_at_min = 100.0 * interp_curve(ref_curve, x_min)

    curve = {}
    for x in grid:
        if x <= x_min:
            # H-FEED-1: reference-curve shape renormalized to the measured 45 % at 19 mm
            p = p_min * (100.0 * interp_curve(ref_curve, x)) / ref_at_min
        elif x >= top_mesh:
            p = 100.0
        elif x > x_max:
            # H-FEED-2: log-linear tail from (200 mm, 81 %) to (top mesh, 100 %)
            p = loglin(x, x_max, p_max, top_mesh, 100.0)
        else:
            for (x0, p0), (x1, p1) in zip(points, points[1:]):
                if x <= x1:
                    p = loglin(x, x0, p0, x1, p1)
                    break
        curve[str(x)] = round(p, 3)

    return {
        "_status": "MEASURED feed curve (belt cut 2026-08-08) completed with hypotheses H-FEED-1 (fine tail < 19 mm) and H-FEED-2 (top size)",
        "source_measurement": "data/feed_measurement_2026-08-08.json",
        "moisture_pct": meas["_meta"]["moisture_pct_wet_basis"],
        "checks": {
            "d50_mm_measured": meas["_meta"]["d50_mm"],
            "d80_mm_measured": meas["_meta"]["d80_mm"],
        },
        "cumulative_passing_curve": curve,
    }


if __name__ == "__main__":
    report = build()
    out = ROOT / "data" / "measured_feed_curve.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    curve = report["cumulative_passing_curve"]
    print(json.dumps(curve, indent=2))
    print(f"Written: {out}")
