"""Tests of the auto-calibration module (fit on measurements)."""

import pytest

from wankoe_model import load_parameters, run_scenario
from wankoe_model.fit import fit_parameters


def test_recovers_a_known_parameter():
    # synthetic truth: CR.5009 power computed with Wi = 15.5
    truth = run_scenario(
        load_parameters(overrides={"calibration": {"Wi": {"default": 15.5}}})
    )
    measured_power = truth["machines"]["CR.5009"]["P_installed_kW"]

    report = fit_parameters(
        load_parameters(),  # starts from the default Wi = 12.54
        observations=[
            {
                "result_path": ["machines", "CR.5009", "P_installed_kW"],
                "measured": measured_power,
            }
        ],
        free_parameters=[{"path": ["calibration", "Wi", "default"], "min": 8, "max": 25}],
    )
    assert report["fitted"]["calibration.Wi.default"] == pytest.approx(15.5, rel=0.01)
    assert report["final_cost"] < report["initial_cost"]
    assert report["final_cost"] < 1e-6


def test_bounds_are_respected():
    report = fit_parameters(
        load_parameters(),
        observations=[
            {
                "result_path": ["machines", "CR.5009", "P_installed_kW"],
                "measured": 1e6,  # unreachable: pushes Wi to its upper bound
            }
        ],
        free_parameters=[{"path": ["calibration", "Wi", "default"], "min": 8, "max": 25}],
        max_rounds=30,
    )
    assert report["fitted"]["calibration.Wi.default"] <= 25


def test_multi_parameter_fit_improves_cost():
    # the ML.26 free parameter belongs to the as-built circuit — pinned
    # since the C1 adoption (client 2026-08-14) made "c1" the default
    report = fit_parameters(
        load_parameters(overrides={"default_scenario": {"zone_1_3_variant": "as-built"}}),
        observations=[
            {"result_path": ["products", "FeedLime grits", "tph"], "measured": 9.0},
            {"result_path": ["products", "FeedLime fines", "tph"], "measured": 17.5},
        ],
        free_parameters=[
            {"path": ["calibration", "m7_n_comp", "default"], "min": 0.7, "max": 1.6},
            {"path": ["machines", "ML.26", "parameters", "S_att", "default"], "min": 0.15, "max": 0.25},
        ],
        max_rounds=40,
    )
    assert report["final_cost"] < report["initial_cost"]


def test_requires_observations_and_parameters():
    with pytest.raises(ValueError):
        fit_parameters(load_parameters(), [], [{"path": ["calibration", "Wi", "default"], "min": 1, "max": 2}])
    with pytest.raises(ValueError):
        fit_parameters(load_parameters(), [{"result_path": ["x"], "measured": 1}], [])
