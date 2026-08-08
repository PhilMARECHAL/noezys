"""Stress test: hammer the model and check its invariants never break.

For every scenario the model runs, these INVARIANTS must hold:
- no crash other than a clean, actionable ValueError;
- every numeric result is finite (no NaN/inf);
- every mass and water balance closes;
- every product curve is monotone within [0; 100] %;
- tonnages and powers are non-negative.

Campaigns:
1. RANDOM  — N seeded random draws of every machine setting within its
   [min; max] bounds, plus flow rates, moisture, modes, weather, hours.
2. EXTREMES — every bounded machine setting pushed to min then max,
   one at a time (all else default).
3. DEGENERATE FEEDS — ultra-fine, ultra-coarse, 2-point, step curves,
   moisture 0 % and 30 %.
4. BRUTAL RATES — near-zero and huge flow rates.

Usage: python scripts/stress_test.py [N_random]   (default 500)
Exit code 1 if any invariant is violated; failures are printed with the
exact overrides to reproduce.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model import load_parameters, run_scenario  # noqa: E402

FAILURES: list = []
CLEAN_REJECTS = 0
RUNS = 0


def walk_numbers(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk_numbers(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk_numbers(value, f"{path}[{i}]")
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        yield path, node


def check_invariants(results) -> list:
    problems = []
    for path, value in walk_numbers(results):
        if not math.isfinite(value):
            problems.append(f"non-finite value at {path}: {value}")
    # an open balance is acceptable ONLY when the model itself declared the
    # scenario has no steady state (loop-not-converged alert) — silent
    # non-closure is a failure
    self_declared = any("did not converge" in a for a in results["alerts"])
    for name, balance in results["balances"].items():
        if not balance["closed"] and not self_declared:
            problems.append(f"balance {name} not closed WITHOUT declaration: "
                            f"gap {balance['relative_gap']:.2e}")
    for name, product in results["products"].items():
        if product["tph"] < -1e-9:
            problems.append(f"negative tonnage for {name}: {product['tph']}")
        curve = product.get("passing_curve_pct")
        if curve:
            values = [curve[k] for k in curve]
            if any(v < -1e-6 or v > 100.000001 for v in values):
                problems.append(f"{name} curve outside [0;100]")
            meshes = sorted(float(k) for k in curve)
            ordered = [curve[str(m) if str(m) in curve else f"{m}"] for m in meshes]
            if any(b - a < -1e-6 for a, b in zip(ordered, ordered[1:])):
                problems.append(f"{name} curve not monotone")
    for code, machine in results["machines"].items():
        for key in ("P_installed_kW", "P_net_kW", "throughput_tph"):
            if machine.get(key) is not None and machine.get(key, 0) < -1e-9:
                problems.append(f"{code}.{key} negative: {machine[key]}")
    return problems


def try_scenario(overrides, label):
    global CLEAN_REJECTS, RUNS
    RUNS += 1
    try:
        results = run_scenario(load_parameters(overrides=overrides))
    except ValueError:
        CLEAN_REJECTS += 1  # clean, actionable rejection is a valid outcome
        return
    except Exception as exc:  # anything else is a stress failure
        FAILURES.append({"label": label, "overrides": overrides,
                         "problem": f"{type(exc).__name__}: {exc}"})
        return
    for problem in check_invariants(results):
        FAILURES.append({"label": label, "overrides": overrides, "problem": problem})


def machine_setting_paths(params):
    for code, machine in params["machines"].items():
        for symbol, spec in machine.get("parameters", {}).items():
            if isinstance(spec, dict) and spec.get("min") is not None and spec.get("max") is not None:
                yield code, symbol, spec


def campaign_random(n):
    params = load_parameters()
    rng = random.Random(20260808)
    settings = list(machine_setting_paths(params))
    for i in range(n):
        overrides = {"machines": {}, "default_scenario": {
            "zone_1_1_mode": rng.choice(["1A", "1B"]),
            "zone_1_2_mode": rng.choice(["2A", "2B", "2C"]),
            "weather": rng.choice(["dry", "rain"]),
            "rain_forces_mode_2B": rng.choice([True, False]),
            "flow_rates_tph": {
                "zone_1_1_feed": rng.uniform(50, 400),
                "zone_1_2_reclaim": rng.uniform(10, 150),
                "zone_1_3_feedlime": rng.uniform(2, 60),
            },
        }, "feed_product": {"properties": {"moisture_pct": {"default": rng.uniform(0.5, 15)}}}}
        for code, symbol, spec in settings:
            if rng.random() < 0.5:
                continue
            overrides["machines"].setdefault(code, {"parameters": {}})["parameters"][symbol] = {
                "default": round(rng.uniform(spec["min"], spec["max"]), 4)
            }
        try_scenario(overrides, f"random#{i}")


def campaign_extremes():
    params = load_parameters()
    for code, symbol, spec in machine_setting_paths(params):
        for bound in ("min", "max"):
            try_scenario(
                {"machines": {code: {"parameters": {symbol: {"default": spec[bound]}}}}},
                f"extreme {code}.{symbol}={bound}",
            )


def campaign_degenerate_feeds():
    fine = {"0.063": 20, "0.5": 60, "1.0": 90, "2.0": 99, "320": 100}
    coarse = {"10.0": 0.5, "35.0": 2, "80.0": 20, "160.0": 60, "320": 100}
    two_points = {"1.0": 50, "320": 100}
    step = {"19.9": 0.1, "20.0": 99.9, "320": 100}
    for name, curve in [("ultra-fine", fine), ("ultra-coarse", coarse),
                        ("two-point", two_points), ("step", step)]:
        try_scenario({"feed_product": {"cumulative_passing_curve": curve}}, f"feed {name}")
    for moisture in (0.0, 30.0):
        try_scenario(
            {"feed_product": {"properties": {"moisture_pct": {"default": moisture}}}},
            f"moisture {moisture}%",
        )


def campaign_brutal_rates():
    for rates, label in [
        ({"zone_1_1_feed": 0.001, "zone_1_2_reclaim": 0.001, "zone_1_3_feedlime": 0.001}, "near-zero"),
        ({"zone_1_1_feed": 10000, "zone_1_2_reclaim": 5000, "zone_1_3_feedlime": 2000}, "huge"),
    ]:
        try_scenario({"default_scenario": {"flow_rates_tph": rates}}, f"rates {label}")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    campaign_random(n)
    campaign_extremes()
    campaign_degenerate_feeds()
    campaign_brutal_rates()
    print(f"runs: {RUNS} | clean rejections (ValueError): {CLEAN_REJECTS} | failures: {len(FAILURES)}")
    for f in FAILURES[:20]:
        print(f"\nFAIL [{f['label']}] {f['problem']}")
        print("  reproduce:", json.dumps(f["overrides"])[:400])
    if len(FAILURES) > 20:
        print(f"... and {len(FAILURES) - 20} more")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
