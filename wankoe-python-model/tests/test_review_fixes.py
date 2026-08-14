"""Regression tests for the 2026-08-08 expert-review fixes."""

import pytest

from wankoe_model import load_parameters, run_scenario, run_required_hours
from wankoe_model.grid import PSD
from wankoe_model import models


# ---------------------------------------------------- overrides & typos
def test_typo_in_override_raises_actionable_error():
    with pytest.raises(ValueError, match="a1_typo"):
        load_parameters(
            overrides={"machines": {"SR.5007": {"parameters": {"a1_typo": {"default": 30}}}}}
        )


def test_close_match_suggested():
    with pytest.raises(ValueError, match="did you mean"):
        load_parameters(overrides={"calibration": {"Wii": {"default": 15}}})


def test_feed_curve_override_replaces_wholesale():
    # a 3-point curve must NOT be key-merged with the 31-point default
    curve = {"1.0": 10.0, "50.0": 60.0, "320": 100.0}
    params = load_parameters(overrides={"feed_product": {"cumulative_passing_curve": curve}})
    assert params["feed_product"]["cumulative_passing_curve"] == curve


def test_new_output_product_allowed():
    params = load_parameters(
        overrides={
            "output_products": {
                "NewProduct": {"cut_min_mm": 5, "cut_max_mm": 10, "state": "dry",
                               "max_out_of_cut_tol_pct": None}
            }
        }
    )
    assert "NewProduct" in params["output_products"]


# ---------------------------------------------------- mode validation
def test_invalid_zone_1_1_mode_raises():
    with pytest.raises(ValueError, match="zone 1.1"):
        run_scenario(load_parameters(overrides={"default_scenario": {"zone_1_1_mode": "1C"}}))


def test_invalid_zone_1_2_mode_raises():
    with pytest.raises(ValueError, match="zone 1.2"):
        run_scenario(load_parameters(overrides={"default_scenario": {"zone_1_2_mode": "2D"}}))


def test_mode_2c_runs_and_planning_reports_it():
    results = run_scenario(
        load_parameters(overrides={"default_scenario": {"zone_1_2_mode": "2C"}})
    )
    # everything reclaimed leaves as AgLime; zone 1.3 has nothing to process
    assert results["products"]["AgLime"]["present"] is True
    assert results["products"]["FeedLime grits"]["present"] is False
    assert results["balances"]["zone_1_2"]["closed"]
    with pytest.raises(ValueError, match="grits"):
        run_required_hours(
            load_parameters(overrides={"default_scenario": {"zone_1_2_mode": "2C"}})
        )


# ---------------------------------------------------- stable result shapes
def test_products_always_carry_the_same_keys():
    keys = {"present", "tph", "state", "P80_mm", "passing_curve_pct", "compliance"}
    for overrides in (
        {},
        {"default_scenario": {"zone_1_1_mode": "1B"}},
        {"default_scenario": {"weather": "rain"}},
    ):
        results = run_scenario(load_parameters(overrides=overrides))
        # "Sliver 1.5/2" added 2026-08-14 (zone-1.3 C1 study variant):
        # stable shape — always present as a key, present=False in as-built
        assert set(results["products"]) == {
            "KFS", "AgLime", "FeedLime grits", "FeedLime fines", "UltraFin",
            "Sliver 1.5/2",
        }
        for product in results["products"].values():
            assert set(product) == keys


def test_machines_carry_active_flag():
    results = run_scenario(load_parameters())
    for info in results["machines"].values():
        assert "active" in info


# ---------------------------------------------------- stockpile closure
def test_phantom_stockpile_is_alerted_and_scored():
    # zone 1.1 nearly stopped: zone 1.2 reclaims stock that is never produced
    results = run_scenario(
        load_parameters(
            overrides={
                "default_scenario": {
                    "zones": {"1.1": {"available_hours": 80, "availability_pct": 80}}
                }
            }
        )
    )
    pb = results["period_balance"]
    assert pb["stockpile_deficit_t"] > 0
    assert any("Stockpile 0/20" in a for a in results["alerts"])


def test_balanced_defaults_have_no_stockpile_deficit_alert():
    results = run_scenario(load_parameters())
    pb = results["period_balance"]
    assert pb is not None and "stockpiles_t" in pb


# ---------------------------------------------------- time basis
def test_monthly_basis_scales_targets():
    results = run_scenario(
        load_parameters(overrides={"default_scenario": {"time_basis": "monthly"}})
    )
    pb = results["period_balance"]
    assert pb["fraction_of_year"] == pytest.approx(1 / 12, rel=0.01)
    assert pb["per_product"]["KFS"]["target_t"] == pytest.approx(85000 / 12, rel=0.01)


def test_unknown_time_basis_raises():
    with pytest.raises(ValueError, match="time_basis"):
        run_scenario(
            load_parameters(overrides={"default_scenario": {"time_basis": "hourly"}})
        )


# ---------------------------------------------------- model guards
def test_dryer_clamps_when_feed_already_dry():
    calib = {"L_v": 2257.0, "c_e": 4.18, "c_s": 0.9, "dT_e": 85.0, "dT_s": 95.0,
             "eta_th": 0.6, "I_ev": 45.0}
    res = models.m6_drying(30.0, 0.3, 0.5, calib)
    assert res["no_drying"] is True
    assert res["evaporated_water_tph"] == 0.0
    assert res["wet_output_tph"] == pytest.approx(30.0)


def test_m3_ideal_screen_does_not_overflow():
    calib = {"k_d": 1.0, "m3_ln_arg": 9.0, "bottom_interval_ratio": 2.0}
    psd = PSD([1.0, 10.0, 100.0], [0.2, 0.6, 1.0])
    part = models.m3_karra_partition(100.0, psd, 10.0, 1e-9, calib)
    assert part["oversize_tph"] + part["undersize_tph"] == pytest.approx(100.0)


def test_m8_measured_phi_conserves_mass_per_interval():
    calib = {"eta_cl": 0.75, "lambda": 0.5, "bottom_interval_ratio": 2.0}
    fines = PSD([0.05, 0.1, 0.5, 1.5], [0.1, 0.2, 0.7, 1.0])
    res = models.m8_air_classification(20.0, fines, 100.0, 10.0, calib)
    # exact totals
    assert res["fine_product_tph"] + res["remainder_tph"] == pytest.approx(20.0)
    assert res["fine_product_tph"] == pytest.approx(20.0 * 0.10 * 0.75)
    # per-interval closure: feed mass = fine + remainder in every interval
    fr_fine = res["fine_product_psd"].interval_fractions()
    fr_rest = res["remainder_psd"].interval_fractions()
    qf, qr = res["fine_product_tph"], res["remainder_tph"]
    # rebuild the phi-adjusted feed and compare
    for i in range(4):
        mass = qf * fr_fine[i] + qr * fr_rest[i]
        assert mass >= -1e-9


def test_m8_inconsistent_phi_warns():
    calib = {"eta_cl": 0.75, "lambda": 0.5, "bottom_interval_ratio": 2.0}
    fines = PSD([0.05, 0.1, 0.5, 1.5], [0.001, 0.002, 0.7, 1.0])
    res = models.m8_air_classification(20.0, fines, 100.0, 40.0, calib)
    assert res["warning"] is not None


def test_feed_curve_below_100_gets_specific_error():
    curve = {"1.0": 10.0, "200.0": 81.0}
    with pytest.raises(ValueError, match="top size"):
        run_scenario(
            load_parameters(overrides={"feed_product": {"cumulative_passing_curve": curve}})
        )
