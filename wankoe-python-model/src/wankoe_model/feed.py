"""Feed-measurement ingestion (the ONLY plant data this project will get).

Client framing (2026-08-08): the line is a NEW process — no downstream
measurement will ever exist. The only recurring data are belt-cut PSD
analyses at the primary (jaw) crusher outlet, in the same format as the
first one. This module industrializes their ingestion:

- measurements live in ``data/feed_measurements/*.json`` (one file per
  campaign, same schema as ``2026-08-08-belt-cut.json``; sieve values may
  be either ``{"average": x, "test_2": ...}`` records or plain numbers);
- ``build_curve_from_measurement`` completes a measurement into a
  full-grid curve with the two documented hypotheses:
  H-FEED-1 (fine tail below the smallest sieve: reference-curve shape
  renormalized to the measured passing) and H-FEED-2 (top size: log-linear
  to 100 % at the engine's top mesh);
- ``apply_measurement`` returns a parameter set carrying that curve and
  the measurement's moisture — ready for run_scenario / design checks.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .paths import deep_merge
from .scenario import REFERENCE_FEED_CURVE_PATH, interp_curve

MEASUREMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "feed_measurements"


def list_measurements() -> dict:
    """{name: path} of the stored feed measurements, newest name last."""
    if not MEASUREMENTS_DIR.exists():
        return {}
    return {p.stem: p for p in sorted(MEASUREMENTS_DIR.glob("*.json"))}


def load_measurement(name_or_path) -> dict:
    path = Path(name_or_path)
    if not path.exists():
        candidates = list_measurements()
        if str(name_or_path) not in candidates:
            known = ", ".join(candidates) or "(none)"
            raise ValueError(
                f"unknown feed measurement '{name_or_path}' (known: {known})"
            )
        path = candidates[str(name_or_path)]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _points(measurement: dict) -> list:
    """Sorted (mesh_mm, % passing) points; accepts record or plain values."""
    points = []
    for mesh, value in measurement["cumulative_passing_pct"].items():
        pct = value["average"] if isinstance(value, dict) else float(value)
        points.append((float(mesh), float(pct)))
    points.sort()
    if len(points) < 2:
        raise ValueError("a feed measurement needs at least 2 sieve points")
    return points


def _loglin(x, x0, p0, x1, p1):
    t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
    return p0 + t * (p1 - p0)


def build_curve_from_measurement(measurement: dict, params: dict) -> dict:
    """Full-grid curve dict from a measurement (H-FEED-1 / H-FEED-2 applied)."""
    with open(REFERENCE_FEED_CURVE_PATH, encoding="utf-8") as f:
        reference = json.load(f)["cumulative_passing_curve"]
    points = _points(measurement)
    grid = sorted(set(params["mesh_series_mm"]) | set(params["engine"]["extension_meshes_mm"]))
    top_mesh = grid[-1]
    (x_min, p_min), (x_max, p_max) = points[0], points[-1]
    ref_at_min = 100.0 * interp_curve(reference, x_min)

    curve = {}
    for x in grid:
        if x <= x_min:
            # H-FEED-1: reference shape renormalized to the measured passing
            p = p_min * (100.0 * interp_curve(reference, x)) / ref_at_min
        elif x >= top_mesh:
            p = 100.0
        elif x > x_max:
            # H-FEED-2: log-linear tail up to 100 % at the engine top mesh
            p = _loglin(x, x_max, p_max, top_mesh, 100.0)
        else:
            for (x0, p0), (x1, p1) in zip(points, points[1:]):
                if x <= x1:
                    p = _loglin(x, x0, p0, x1, p1)
                    break
        curve[str(x)] = round(p, 3)
    return curve


def apply_measurement(params: dict, name_or_path) -> dict:
    """Parameter set carrying the measurement's curve and moisture."""
    measurement = load_measurement(name_or_path)
    overrides = {
        "feed_product": {
            "cumulative_passing_curve": build_curve_from_measurement(measurement, params)
        }
    }
    moisture = measurement.get("_meta", {}).get("moisture_pct_wet_basis")
    if moisture is not None:
        overrides["feed_product"]["properties"] = {"moisture_pct": {"default": moisture}}
    return deep_merge(params, overrides)
