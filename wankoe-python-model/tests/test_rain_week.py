"""Rain-week moisture study (client arbitrations 2026-08-15).

Pins the data-first scenario file, the composite-photo physics and the
requalified 1.7 mm rule so the study stays replayable.
"""

import json
from pathlib import Path

import pytest

from wankoe_model.scenario import load_parameters, run_scenario

SCENARIO_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "design"
    / "moisture"
    / "rain-week-scenario.json"
)


def _scenario():
    return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))


def test_scenario_file_moisture_set():
    sc = _scenario()
    m = sc["stock_moistures_pct"]
    assert m["dry_reference"] == 7
    assert m["quarry_feed_after_rain_week"]["default"] == 12
    assert m["reclaimed_0_20_stock_after_rain_week"]["default"] == 15
    assert m["feedlime_6_20_stock_after_rain_week"]["default"] == 11
    # every moisture is [H] until the absorption test (new external trigger)
    for key in (
        "quarry_feed_after_rain_week",
        "reclaimed_0_20_stock_after_rain_week",
        "feedlime_6_20_stock_after_rain_week",
    ):
        assert "[H]" in m[key]["status"]
    assert sc["annual_rain_weeks"]["default"] == 6
    assert "[H]" in sc["annual_rain_weeks"]["status"]
    assert "ABSORPTION TEST" in sc["external_trigger"]


def test_all_photo_overrides_load_and_run():
    # every override block must pass the validated deep-merge and run
    for name, photo in _scenario()["photos"].items():
        result = run_scenario(load_parameters(overrides=photo["overrides"]))
        assert result["balances"]["zone_1_1"]["closed"], name


def test_rain_week_zone_1_2_is_2b_physics():
    # 1.7 mm wet screening impossible -> zero AgLime at the 15 % photo
    photo = _scenario()["photos"]["photo_zone_1_2_rain"]
    result = run_scenario(load_parameters(overrides=photo["overrides"]))
    assert result["scenario"]["zone_1_2_mode"] == "2B"
    assert result["products"]["AgLime"]["tph"] == 0.0


def test_dryer_outlet_limit_unreachable_at_11_pct():
    # at 11 % inlet the 32.1 t/h wet-feed cap yields < 30 t/h at the outlet
    photo = _scenario()["photos"]["photo_zone_1_3_wet_G"]
    result = run_scenario(load_parameters(overrides=photo["overrides"]))
    outlet = result["machines"]["DY.03"]["wet_output_tph"]
    assert outlet == pytest.approx(32.1 * (1 - 0.11) / (1 - 0.005), rel=1e-6)
    assert outlet < 30.0
    # and the burner duty rises vs the 7 % reference
    ref = run_scenario(load_parameters())
    assert (
        result["machines"]["DY.03"]["burner_power_kW"]
        > ref["machines"]["DY.03"]["burner_power_kW"]
    )


def test_physical_requalification_noted_in_data():
    params = load_parameters()
    assert "PHYSICS" in params["default_scenario"]["_rain_forces_mode_2B_note"]
    # raw calibration records (before flattening) carry the requalified notes
    assert "IMPOSSIBLE" in params["calibration"]["I_rain"]["status"]
    assert "BEHIND the dryer" in params["calibration"]["wet_capacity_factor"]["status"]
