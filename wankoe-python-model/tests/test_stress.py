"""Stress regression tests (derived from the 2026-08-08 stress campaign:
554 scenarios, 0 crashes; 2 findings hardened into policy below)."""

import random

import pytest

from wankoe_model import load_parameters, run_scenario, run_sweep


def _invariants(results):
    for name, balance in results["balances"].items():
        declared = any("did not converge" in a for a in results["alerts"])
        assert balance["closed"] or declared, f"balance {name} silently open"
    for name, product in results["products"].items():
        assert product["tph"] >= -1e-9
        curve = product.get("passing_curve_pct")
        if curve:
            values = list(curve.values())
            assert all(-1e-6 <= v <= 100.000001 for v in values)
            assert all(b - a >= -1e-6 for a, b in zip(values, values[1:]))


def test_random_mini_campaign_holds_invariants():
    rng = random.Random(42)
    params = load_parameters()
    settings = [
        (code, symbol, spec)
        for code, machine in params["machines"].items()
        for symbol, spec in machine.get("parameters", {}).items()
        if isinstance(spec, dict) and spec.get("min") is not None and spec.get("max") is not None
    ]
    for _ in range(25):
        overrides = {
            "machines": {},
            "default_scenario": {
                "zone_1_1_mode": rng.choice(["1A", "1B"]),
                "zone_1_2_mode": rng.choice(["2A", "2B", "2C"]),
                "weather": rng.choice(["dry", "rain"]),
                "flow_rates_tph": {
                    "zone_1_1_feed": rng.uniform(50, 400),
                    "zone_1_2_reclaim": rng.uniform(10, 150),
                    "zone_1_3_feedlime": rng.uniform(2, 60),
                },
            },
        }
        for code, symbol, spec in settings:
            if rng.random() < 0.5:
                continue
            overrides["machines"].setdefault(code, {"parameters": {}})["parameters"][symbol] = {
                "default": round(rng.uniform(spec["min"], spec["max"]), 4)
            }
        _invariants(run_scenario(load_parameters(overrides=overrides)))


def test_divergent_loop_is_self_declared():
    # CR.5113 CSS above the 1.7 mm closing cut: no steady state can exist —
    # the model must say so, never publish silently wrong tonnages
    results = run_scenario(
        load_parameters(
            overrides={
                "machines": {
                    "CR.5113": {"parameters": {"x80": {"default": 2.9}}},
                    "SR.5115": {"parameters": {"a": {"default": 1.5}, "I": {"default": 0.11}}},
                }
            }
        )
    )
    assert any("did not converge" in a for a in results["alerts"])


def test_sweep_rejects_no_steady_state_scenarios():
    report = run_sweep(
        load_parameters(),
        {
            "method": "grid",
            "seasonal": False,
            "variables": [
                {"path": ["machines", "CR.5113", "parameters", "x80", "default"],
                 "values": [1.0, 2.9]},
                {"path": ["machines", "SR.5115", "parameters", "I", "default"],
                 "values": [0.11]},
            ],
        },
    )
    assert report["evaluated"] == 1  # the sane CSS
    assert len(report["failed"]) == 1
    assert "no steady state" in report["failed"][0]["error"]


def test_degenerate_feeds_run_clean():
    curves = {
        "ultra-fine": {"0.063": 20, "0.5": 60, "1.0": 90, "2.0": 99, "320": 100},
        "ultra-coarse": {"10.0": 0.5, "35.0": 2, "80.0": 20, "160.0": 60, "320": 100},
        "two-point": {"1.0": 50, "320": 100},
        "step-at-20": {"19.9": 0.1, "20.0": 99.9, "320": 100},
    }
    for name, curve in curves.items():
        results = run_scenario(
            load_parameters(overrides={"feed_product": {"cumulative_passing_curve": curve}})
        )
        _invariants(results)


def test_moisture_extremes():
    for moisture in (0.0, 30.0):
        results = run_scenario(
            load_parameters(
                overrides={"feed_product": {"properties": {"moisture_pct": {"default": moisture}}}}
            )
        )
        _invariants(results)
    dry = run_scenario(
        load_parameters(
            overrides={"feed_product": {"properties": {"moisture_pct": {"default": 0.0}}}}
        )
    )
    assert any("already drier" in a for a in dry["alerts"])


def test_brutal_flow_rates_scale_linearly():
    tiny = run_scenario(
        load_parameters(
            overrides={"default_scenario": {"flow_rates_tph": {
                "zone_1_1_feed": 0.1, "zone_1_2_reclaim": 0.1, "zone_1_3_feedlime": 0.1}}}
        )
    )
    huge = run_scenario(
        load_parameters(
            overrides={"default_scenario": {"flow_rates_tph": {
                "zone_1_1_feed": 10000, "zone_1_2_reclaim": 5000, "zone_1_3_feedlime": 2000}}}
        )
    )
    _invariants(tiny)
    _invariants(huge)
    # reported tonnages are rounded to 3 decimals, hence the loose tolerance
    assert huge["products"]["KFS"]["tph"] == pytest.approx(
        tiny["products"]["KFS"]["tph"] * 1e5, rel=0.05
    )
