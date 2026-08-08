"""Tests of the automatic sweep / optimum search module."""

import pytest

from wankoe_model import load_parameters
from wankoe_model.optimize import run_sweep

HOURS = {"available_hours": 4000, "availability_pct": 80}


def params_with_hours():
    return load_parameters(
        overrides={
            "default_scenario": {"zones": {"1.1": HOURS, "1.2": HOURS, "1.3": HOURS}}
        }
    )


def test_grid_sweep_counts_and_ranks():
    config = {
        "method": "grid",
        "seasonal": False,
        "variables": [
            {"path": ["default_scenario", "flow_rates_tph", "zone_1_1_feed"], "values": [200, 250]},
            {"path": ["machines", "SR.5007", "parameters", "a1", "default"], "values": [33, 35, 37]},
        ],
        "objective": {"firm_shortfall_weight": 100.0, "surplus_weight": 1.0},
    }
    report = run_sweep(params_with_hours(), config)
    assert report["evaluated"] == 6
    scores = report["all_scores"]
    assert scores == sorted(scores)
    assert report["best"]["score"] == scores[0]


def test_higher_feed_beats_firm_shortfall():
    # with few hours the KFS firm target is binding: more feed -> better score
    few_hours = {"available_hours": 400, "availability_pct": 80}
    params = load_parameters(
        overrides={
            "default_scenario": {"zones": {"1.1": few_hours, "1.2": few_hours, "1.3": few_hours}}
        }
    )
    config = {
        "method": "grid",
        "seasonal": False,
        "variables": [
            {"path": ["default_scenario", "flow_rates_tph", "zone_1_1_feed"], "values": [150, 250]},
        ],
        "objective": {"firm_shortfall_weight": 100.0, "surplus_weight": 0.0},
    }
    report = run_sweep(params, config)
    assert report["best"]["values"]["default_scenario.flow_rates_tph.zone_1_1_feed"] == 250


def test_random_sweep_reproducible():
    config = {
        "method": "random",
        "seasonal": False,
        "random_samples": 5,
        "random_seed": 42,
        "variables": [
            {"path": ["machines", "SR.5007", "parameters", "a1", "default"], "min": 30, "max": 40, "step": 1},
        ],
    }
    a = run_sweep(params_with_hours(), config)
    b = run_sweep(params_with_hours(), config)
    assert a["all_scores"] == b["all_scores"]
    assert a["evaluated"] == 5


def test_grid_overflow_rejected():
    config = {
        "method": "grid",
        "max_scenarios": 3,
        "variables": [
            {"path": ["machines", "SR.5007", "parameters", "a1", "default"], "values": [33, 34, 35, 36]},
        ],
    }
    with pytest.raises(ValueError):
        run_sweep(params_with_hours(), config)


def test_hourly_proxy_flagged_without_hours():
    no_hours = {"available_hours": None, "availability_pct": 80}
    params = load_parameters(
        overrides={
            "default_scenario": {"zones": {"1.1": no_hours, "1.2": no_hours, "1.3": no_hours}}
        }
    )
    config = {
        "method": "grid",
        "seasonal": False,
        "variables": [
            {"path": ["default_scenario", "flow_rates_tph", "zone_1_1_feed"], "values": [250]},
        ],
    }
    report = run_sweep(params, config)
    assert "PER HOUR PROXY" in report["tonnage_basis"]


def test_seasonal_sweep_uses_combined_tonnages():
    config = {
        "method": "grid",
        "seasonal": True,
        "variables": [
            {"path": ["default_scenario", "flow_rates_tph", "zone_1_2_reclaim"], "values": [100]},
        ],
    }
    base = params_with_hours()
    report = run_sweep(base, config)
    # AgLime only runs 75 % of the time (dry season) in the seasonal mix
    aglime = report["best"]["kpis"]["tonnages"]["AgLime"]
    assert aglime > 0
    from wankoe_model import run_scenario

    hourly_tph = run_scenario(base)["products"]["AgLime"]["tph"]
    full_year = hourly_tph * 4000 * 0.8
    assert aglime == pytest.approx(full_year * 0.75, rel=0.05)
