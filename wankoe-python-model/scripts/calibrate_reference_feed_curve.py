"""Calibration of the reference feed size curve.

No real measurement exists to date (spec §5.1). This script builds a
PLAUSIBLE pivot curve and FITS it to reproduce the chapter 9 reference case
(validated by the client on 2026-08-08):

  - zone 1.1, mode 1A, 250 t/h: KFS = 23.7 % of the feed
  - CR.5009 power ≈ 116 kW
  - zone 1.2, mode 2A: FeedLime (5-15) = 45 % of the reclaim
  - CR.5011 power ≈ 37 kW (secondary target — known structural deviation)

Curve model (3 degrees of freedom) — a physical blend consistent with spec
§5.1 ("grizzly <80 passing, uncrushed + jaw crusher product"):
  pivot = w · RR(x80=150, n=1.15, truncated) + (1−w) · RR_truncated_at_80(x80_g, n_g)

Output: data/reference_feed_curve.json (curve + fitting report).
The curve is a WORKING HYPOTHESIS, to be replaced by the first measurement.

Usage: python scripts/calibrate_reference_feed_curve.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model.scenario import load_parameters, run_scenario  # noqa: E402

TARGETS = {"kfs_pct": 23.7, "p_cr5009_kw": 116.0, "feedlime_pct": 45.0, "p_cr5011_kw": 37.0}
WEIGHTS = {"kfs_pct": 4.0, "p_cr5009_kw": 0.02, "feedlime_pct": 2.0, "p_cr5011_kw": 0.05}


def pivot_curve(params: dict, w: float, x80_g: float, n_g: float) -> dict:
    """Builds the pivot curve (mesh -> % passing dict) on the extended series."""
    trunc = params["calibration"]["trunc_factor"]["default"]
    ln_arg = params["calibration"]["m1_ln_arg"]["default"]
    p_jaw = params["machines"]["CR.5003"]["parameters"]
    x80_j, n_j = p_jaw["x80"]["default"], p_jaw["n"]["default"]

    def truncated_rr(x: float, x80: float, n: float, x_max: float) -> float:
        xc = x80 / (math.log(ln_arg) ** (1.0 / n))
        p = 1.0 - math.exp(-((x / xc) ** n))
        p_max = 1.0 - math.exp(-((x_max / xc) ** n))
        return min(1.0, p / p_max)

    # extended grid: the jaw product carries a tail up to trunc·x80 (> 200 mm)
    series = sorted(set(params["mesh_series_mm"]) | set(params["engine"]["extension_meshes_mm"]))
    curve = {}
    for x in series:
        p_jaw_product = truncated_rr(x, x80_j, n_j, trunc * x80_j)  # CR.5003 product
        p_grizzly = truncated_rr(x, x80_g, n_g, 80.0)  # natural grizzly <80 passing
        curve[str(x)] = round(100.0 * (w * p_jaw_product + (1.0 - w) * p_grizzly), 4)
    return curve


def evaluate(base_params: dict, w: float, x80_g: float, n_g: float) -> tuple[float, dict]:
    curve = pivot_curve(base_params, w, x80_g, n_g)
    params = load_parameters(overrides={"feed_product": {"cumulative_passing_curve": curve}})
    try:
        res = run_scenario(params)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        return 1e9, {"error": str(exc)}
    q_feed = res["scenario"]["flow_rates_tph"]["zone_1_1_feed"]
    kfs_pct = 100.0 * res["products"]["KFS"]["tph"] / q_feed
    p9 = res["machines"]["CR.5009"]["P_installed_kW"]
    p11 = res["machines"]["CR.5011"].get("P_installed_kW", 0.0)
    # FeedLime share = reclaim − AgLime (closed circuit), consistent wet basis
    q_reclaim = res["scenario"]["flow_rates_tph"]["zone_1_2_reclaim"]
    aglime_tph = res["products"]["AgLime"]["tph"]
    feedlime_pct = 100.0 * (q_reclaim - aglime_tph) / q_reclaim
    achieved = {
        "kfs_pct": kfs_pct,
        "p_cr5009_kw": p9,
        "feedlime_pct": feedlime_pct,
        "p_cr5011_kw": p11,
    }
    cost = sum(WEIGHTS[k] * (achieved[k] - TARGETS[k]) ** 2 for k in TARGETS)
    return cost, achieved


def calibrate() -> dict:
    base_params = load_parameters()

    # 1) coarse sweep
    best = None
    for w in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        for x80_g in [15, 25, 35, 45, 60]:
            for n_g in [0.7, 0.9, 1.1, 1.3]:
                cost, achieved = evaluate(base_params, w, x80_g, n_g)
                if best is None or cost < best[0]:
                    best = (cost, (w, x80_g, n_g), achieved)
    print(f"Coarse sweep: cost {best[0]:.2f} at {best[1]} -> {best[2]}")

    # 2) local pattern-search refinement
    (cost, (w, x80_g, n_g), achieved) = best
    steps = [0.05, 5.0, 0.1]
    for _ in range(60):
        improved = False
        for i, (delta, lo, hi) in enumerate(zip(steps, [0.05, 5.0, 0.5], [0.95, 79.0, 2.0])):
            for sign in (+1, -1):
                candidate = [w, x80_g, n_g]
                candidate[i] = min(hi, max(lo, candidate[i] + sign * delta))
                c, a = evaluate(base_params, *candidate)
                if c < cost:
                    cost, (w, x80_g, n_g), achieved = c, tuple(candidate), a
                    improved = True
        if not improved:
            if max(steps) < 1e-3:
                break
            steps = [s / 2 for s in steps]
    print(f"Refinement: cost {cost:.3f} at w={w:.3f}, x80_g={x80_g:.2f}, n_g={n_g:.3f}")
    print(f"Achieved: {achieved}  |  Targets: {TARGETS}")

    curve = pivot_curve(base_params, w, x80_g, n_g)
    return {
        "_status": "CALIBRATED CURVE — working hypothesis, to be replaced by the first real measurement",
        "calibration_date": "2026-08-08",
        "model": "pivot = w*RR(150; 1.15) + (1-w)*RR_truncated_80(x80_g; n_g)",
        "fitted_parameters": {"w": round(w, 4), "x80_g_mm": round(x80_g, 3), "n_g": round(n_g, 4)},
        "chapter_9_targets": TARGETS,
        "achieved_values": {k: round(v, 2) for k, v in achieved.items()},
        "cumulative_passing_curve": curve,
    }


if __name__ == "__main__":
    report = calibrate()
    out = ROOT / "data" / "reference_feed_curve.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {out}")
