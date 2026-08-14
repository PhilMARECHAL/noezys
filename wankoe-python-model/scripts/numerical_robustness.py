"""Numerical robustness study (confidence program action 5, 2026-08-14).

Two numerical knobs, physics untouched:
1. GRID REFINEMENT: geometric midpoints inserted between every pair of
   consecutive meshes (x2 = 1 midpoint, x4 = 3 midpoints).
2. LOOP TOLERANCE: fixed-point relative tolerance 1e-6 -> 1e-9.

If the reported figures are physics, they must be stable; if they were
grid artifacts, refinement would move them.
Usage: python scripts/numerical_robustness.py
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from wankoe_model import load_parameters, run_scenario  # noqa: E402


def refine(meshes, factor):
    """Insert factor-1 geometric midpoints in every interval."""
    out = []
    for a, b in zip(meshes, meshes[1:]):
        out.append(a)
        for i in range(1, factor):
            out.append(round(a * (b / a) ** (i / factor), 6))
    out.append(meshes[-1])
    return out


def photo(overrides):
    r = run_scenario(load_parameters(overrides=overrides))
    return {
        "kfs_yield_pct": r["indicators"]["kfs_yield_pct"],
        "kfs_tph_wet": r["products"]["KFS"]["tph"],
        "in_cut_pct": r["products"]["KFS"]["compliance"]["in_cut_pct"],
        "recirc_11": r["intermediate_flows"]["zone_1_1_recirculation_tph"],
        "grits_tph": r["products"]["FeedLime grits"]["tph"],
        "balances_closed": all(b["closed"] for b in r["balances"].values()),
    }


base_meshes = load_parameters()["mesh_series_mm"]
runs = {
    "base grid (29 meshes)": {},
    "grid x2 (57 meshes)": {"mesh_series_mm": refine(base_meshes, 2)},
    "grid x4 (113 meshes)": {"mesh_series_mm": refine(base_meshes, 4)},
    "loop tol 1e-9": {"engine": {"loop_relative_tolerance": 1e-9}},
    "grid x4 + tol 1e-9": {
        "mesh_series_mm": refine(base_meshes, 4),
        "engine": {"loop_relative_tolerance": 1e-9},
    },
}
ref = None
report = {}
for tag, ov in runs.items():
    p = photo(ov)
    if ref is None:
        ref = p
        report[tag] = p
    else:
        report[tag] = {**p, "delta_yield_pts": round(p["kfs_yield_pct"] - ref["kfs_yield_pct"], 4),
                       "delta_grits_tph": round(p["grits_tph"] - ref["grits_tph"], 4)}
print(json.dumps(report, indent=1))
