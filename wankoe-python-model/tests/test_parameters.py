"""Golden rule #3: every parameter is adjustable WITHOUT touching the code.

Each test overrides a parameter through ``load_parameters(overrides=...)``
and checks that the result changes accordingly — proof that the value is
not hardcoded. Includes regression tests for the dead-parameter findings
of the 2026-08-08 parameterization audit.
"""

import pytest

from wankoe_model import load_parameters, run_scenario, run_seasonal_balance


def test_screen_aperture_is_adjustable():
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(
            overrides={
                "machines": {"SR.5007": {"parameters": {"a1": {"default": 30}, "a2": {"default": 25}}}}
            }
        )
    )
    assert changed["products"]["KFS"]["tph"] != base["products"]["KFS"]["tph"]


def test_bond_index_is_adjustable():
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(overrides={"calibration": {"Wi": {"default": 25.08}}})
    )
    # doubled Wi -> doubled specific energy (Bond law is linear in Wi)
    assert changed["machines"]["CR.5009"]["P_installed_kW"] == pytest.approx(
        2 * base["machines"]["CR.5009"]["P_installed_kW"], rel=1e-6
    )


def test_feed_bond_index_overrides_calibration():
    # audit finding: feed_product Wi was dead — it must now take precedence
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(
            overrides={"feed_product": {"properties": {"Wi_kWht": {"default": 25.08}}}}
        )
    )
    assert changed["machines"]["CR.5009"]["P_installed_kW"] == pytest.approx(
        2 * base["machines"]["CR.5009"]["P_installed_kW"], rel=1e-6
    )


def test_cr5009_gap_is_live():
    # audit finding 1.1: x80 default null -> follows the gap, so sweeping g works
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(
            overrides={"machines": {"CR.5009": {"parameters": {"g": {"default": 40}}}}}
        )
    )
    assert (
        changed["machines"]["CR.5009"]["x80_mm"] != base["machines"]["CR.5009"]["x80_mm"]
    )


def test_cr5009_explicit_x80_overrides_gap():
    changed = run_scenario(
        load_parameters(
            overrides={"machines": {"CR.5009": {"parameters": {"x80": {"default": 55}}}}}
        )
    )
    assert changed["machines"]["CR.5009"]["x80_mm"] == 55


def test_ml26_machine_sheet_coefficients_are_live():
    # audit finding: calibration.comp_lam/S_att were shadowed — the machine
    # sheet is now the single source and sweeping it must change the result.
    # ML.26 lives in the as-built circuit — pinned since the C1 adoption
    # (client 2026-08-14) made "c1" the shipped default variant
    as_built = {"default_scenario": {"zone_1_3_variant": "as-built"}}
    base = run_scenario(load_parameters(overrides=as_built))
    changed = run_scenario(
        load_parameters(
            overrides={**as_built, "machines": {"ML.26": {"parameters": {"S_att": {"default": 0.18}}}}}
        )
    )
    assert (
        changed["products"]["FeedLime grits"]["tph"] != base["products"]["FeedLime grits"]["tph"]
    )


def test_rc2_machine_sheet_coefficients_are_live():
    # same single-source guarantee for the adopted C1 machines
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(
            overrides={"machines": {"RC.2": {"parameters": {"S_att": {"default": 0.09}}}}}
        )
    )
    assert (
        changed["products"]["FeedLime grits"]["tph"] != base["products"]["FeedLime grits"]["tph"]
    )


def test_product_state_comes_from_data():
    # audit finding 1.2: wet/dry state was hardcoded — it must come from data
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(overrides={"output_products": {"KFS": {"state": "dry"}}})
    )
    assert changed["products"]["KFS"]["state"] == "dry"
    assert changed["products"]["KFS"]["tph"] < base["products"]["KFS"]["tph"]


def test_scenario_flow_rate_is_adjustable():
    changed = run_scenario(
        load_parameters(
            overrides={"default_scenario": {"flow_rates_tph": {"zone_1_1_feed": 125}}}
        )
    )
    base = run_scenario(load_parameters())
    # reported tonnages are rounded to 3 decimals, hence the loose tolerance
    assert changed["products"]["KFS"]["tph"] == pytest.approx(
        base["products"]["KFS"]["tph"] / 2, rel=1e-4
    )


def test_mode_1b_removes_kfs():
    changed = run_scenario(
        load_parameters(overrides={"default_scenario": {"zone_1_1_mode": "1B"}})
    )
    assert changed["products"]["KFS"]["tph"] == 0.0


def test_rain_forces_mode_2b():
    changed = run_scenario(
        load_parameters(overrides={"default_scenario": {"weather": "rain"}})
    )
    assert changed["products"]["AgLime"]["tph"] == 0.0
    assert changed["scenario"]["zone_1_2_mode"] == "2B"
    assert any("2B" in a for a in changed["alerts"])


def test_rain_forcing_can_be_disabled_and_uses_i_rain():
    # audit finding: I_rain was unreachable — the forcing is now a parameter
    changed = run_scenario(
        load_parameters(
            overrides={
                "default_scenario": {"weather": "rain", "rain_forces_mode_2B": False}
            }
        )
    )
    assert changed["products"]["AgLime"]["tph"] > 0.0
    assert changed["machines"]["SR.5115"]["imperfection_used"] == pytest.approx(0.9)
    assert any("DIRECTIONAL" in a for a in changed["alerts"])


def test_out_of_range_setting_raises_alert():
    changed = run_scenario(
        load_parameters(
            overrides={"machines": {"SR.5007": {"parameters": {"a1": {"default": 55}}}}}
        )
    )
    assert any("SR.5007.a1" in a for a in changed["alerts"])


def test_installed_area_alert_when_provided():
    changed = run_scenario(
        load_parameters(overrides={"machines": {"SR.5007": {"installed_area_m2": 0.5}}})
    )
    assert any("SR.5007" in a and "installed" in a for a in changed["alerts"])


def test_feed_moisture_is_adjustable():
    base = run_scenario(load_parameters())
    changed = run_scenario(
        load_parameters(
            overrides={
                "feed_product": {"properties": {"moisture_pct": {"default": 12, "status": "test"}}}
            }
        )
    )
    assert (
        changed["machines"]["DY.03"]["evaporated_water_tph"]
        > base["machines"]["DY.03"]["evaporated_water_tph"]
    )


def test_measured_phi_100_clears_the_flag():
    changed = run_scenario(
        load_parameters(overrides={"calibration": {"Phi_100": {"default": 9.0}}})
    )
    assert not any("NOT CERTIFIED" in a for a in changed["alerts"])


def test_period_balance_with_hours():
    hours = {"available_hours": 5000, "availability_pct": 80}
    changed = run_scenario(
        load_parameters(
            overrides={
                "default_scenario": {"zones": {"1.1": hours, "1.2": hours, "1.3": hours}}
            }
        )
    )
    balance = changed["period_balance"]
    assert balance is not None
    assert balance["per_product"]["KFS"]["tonnage_t"] == pytest.approx(
        changed["products"]["KFS"]["tph"] * 4000, rel=1e-6
    )


def test_seasonal_balance_mixes_weathers():
    # audit finding: season fractions were dead — run_seasonal_balance wires them
    hours = {"available_hours": 5000, "availability_pct": 80}
    params = load_parameters(
        overrides={
            "default_scenario": {"zones": {"1.1": hours, "1.2": hours, "1.3": hours}}
        }
    )
    seasonal = run_seasonal_balance(params)
    assert seasonal["combined"] is not None
    assert seasonal["season_fractions"] == {"dry": 0.75, "rain": 0.25}
    # AgLime is only produced in the dry season (rain forces mode 2B)
    dry_aglime = seasonal["photos"]["dry"]["period_balance"]["per_product"]["AgLime"]["tonnage_t"]
    rain_aglime = seasonal["photos"]["rain"]["period_balance"]["per_product"]["AgLime"]["tonnage_t"]
    assert rain_aglime == 0.0
    assert seasonal["combined"]["AgLime"]["tonnage_t"] == pytest.approx(dry_aglime)
