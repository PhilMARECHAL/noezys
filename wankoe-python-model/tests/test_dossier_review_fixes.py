"""Regression tests for the full-dossier review fixes (night of 2026-08-08)."""

import pytest

from wankoe_model import load_parameters, run_scenario, run_design_check
from wankoe_model.feed import build_curve_from_measurement
from wankoe_model.optimize import _kpis, _score


def test_wet_screening_derates_capacity():
    dry = run_scenario(load_parameters())
    rain = run_scenario(load_parameters(overrides={"default_scenario": {"weather": "rain"}}))
    a_dry = dry["machines"]["SR.5007"]["areas_m2"]["top_deck"]["required_area_m2"]
    a_rain = rain["machines"]["SR.5007"]["areas_m2"]["top_deck"]["required_area_m2"]
    # spec: capacity drops when wet -> required area grows by 1/wet_capacity_factor
    assert a_rain > a_dry * 1.2


def test_sp36_block_toggle():
    off = run_scenario(load_parameters(overrides={"machines": {"SP.36": {"enabled": False}}}))
    assert off["products"]["UltraFin"]["present"] is False
    assert any("disabled by parameter" in a for a in off["alerts"])
    assert off["balances"]["zone_1_3"]["closed"]


def test_ml26_vendor_curve_table_replaces_hypothesis():
    # ML.26 lives in the AS-BUILT circuit only — pinned since the C1
    # adoption made "c1" the default variant (client, 2026-08-14)
    as_built = {"default_scenario": {"zone_1_3_variant": "as-built"}}
    table = {
        "curve_pct": {"0.5": 20, "1.5": 45, "2.0": 55, "4.0": 82, "6.3": 100},
        "interpolation": "linear",
    }
    results = run_scenario(
        load_parameters(
            overrides={**as_built, "machines": {"ML.26": {"product_curve_table": table}}}
        )
    )
    assert any("vendor product curve" in a for a in results["alerts"])
    assert results["balances"]["zone_1_3"]["closed"]
    base = run_scenario(load_parameters(overrides=as_built))
    assert (
        results["products"]["FeedLime grits"]["tph"] != base["products"]["FeedLime grits"]["tph"]
    )


def test_fines_surplus_weighted_higher():
    kpis = {
        "firm_shortfall_t": 0.0,
        "unsellable_surplus_t": 100.0,
        "fines_surplus_t": 100.0,
        "stockpile_deficit_t": 0.0,
        "total_installed_power_kW": 0.0,
        "n_alerts": 0,
    }
    default = _score(kpis, {})
    neutral = _score(kpis, {"fines_surplus_weight": 1.0})
    # spec priority: a fines surplus costs more than a generic one by default
    assert default == pytest.approx(200.0)
    assert neutral == pytest.approx(100.0)


def test_design_check_has_three_verdicts_and_not_checkable():
    report = run_design_check(load_parameters())
    v = report["verdicts"]
    assert set(v) == {"machines_hold", "quality_holds", "targets_reachable"}
    # Re-baselined 2026-08-16 (CR.5009 panel Q2+Q3: sizer class + quarry
    # <= 250 mm lump guarantee closed the 2026-08-11 nip exceedance) —
    # machines_hold now True at the measured curve
    assert v["machines_hold"] is True
    # KFS envelope HOLDS (Q1) and targets FIT since the Saturday regime
    # extension (Q7 closed 2026-08-13: zone 1.1 ceiling 2400 h).
    # 2026-08-14 (same day, two re-baselines): the D6 grits envelope made
    # the AS-BUILT default fail quality (15.4 % < 2 mm > 15 %); then the
    # client ADOPTED the C1 redesign as the default configuration — its
    # grits PASS D6 (13.6 % < 2 mm), so quality_holds is True again
    assert v["quality_holds"] is True
    assert v["targets_reachable"] is True
    assert report["not_checkable"][0]["machine"] == "CR.5003"


def test_measurement_without_average_key_averages_tests():
    meas = {
        "_meta": {"moisture_pct_wet_basis": 7},
        "cumulative_passing_pct": {"19": {"test_2": 44.0, "test_3": 46.0}, "200": {"test_2": 80.0, "test_3": 82.0}, "320": 100},
    }
    curve = build_curve_from_measurement(meas, load_parameters())
    assert curve["320"] == 100.0


def test_non_monotone_measurement_rejected():
    meas = {
        "_meta": {},
        "cumulative_passing_pct": {"19": 60.0, "80": 45.0, "200": 90.0},
    }
    with pytest.raises(ValueError, match="not monotone"):
        build_curve_from_measurement(meas, load_parameters())


def test_m8_off_grid_cut_tonnage_matches_psd():
    # 65 um is NOT a grid mesh: tonnage and curves must still agree
    results = run_scenario(
        load_parameters(
            overrides={"machines": {"SP.36": {"parameters": {"coupe": {"default": 65}}}}}
        )
    )
    assert results["balances"]["zone_1_3"]["closed"]
    uf = results["products"]["UltraFin"]
    assert uf["present"] and uf["tph"] > 0
