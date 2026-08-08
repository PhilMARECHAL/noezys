"""Reproduction of the reference case (specification, chapter 9).

Acceptance criteria: mass + water closure on every scenario and
reproduction of the documented values. Tolerances reflect the DOCUMENTED
residual deviations of the calibration (see data/reference_feed_curve.json
and the README): CR.5009 / CR.5011 powers carry a known gap, reported to
the specification author.
"""

import json

import pytest

from wankoe_model import REFERENCE_FEED_CURVE_PATH, load_parameters, run_scenario


@pytest.fixture(scope="module")
def results():
    # Chapter 9 was authored with the hypothetical reference rock (8 %
    # moisture, calibrated curve). The default parameters now carry the real
    # 2026-08-08 belt-cut measurement, so this suite PINS the reference curve
    # to keep validating the model mathematics against chapter 9.
    with open(REFERENCE_FEED_CURVE_PATH, encoding="utf-8") as f:
        curve = json.load(f)["cumulative_passing_curve"]
    return run_scenario(
        load_parameters(
            overrides={
                "feed_product": {
                    "cumulative_passing_curve": curve,
                    "properties": {"moisture_pct": {"default": 8}},
                }
            }
        )
    )


def test_balances_closed(results):
    for name, balance in results["balances"].items():
        assert balance["closed"], f"balance {name} not closed: {balance}"


def test_9_1_zone_1_1(results):
    # KFS 59.3 t/h (23.7 %) at 250 t/h — calibrated
    assert results["products"]["KFS"]["tph"] == pytest.approx(59.3, abs=1.0)
    # 0/20: 190.7 t/h wet
    q020 = results["intermediate_flows"]["0/20_dry_tph"] / (1 - 0.08)
    assert q020 == pytest.approx(190.7, abs=1.5)
    # CR.5009 expected ~116 kW; achieved ~106 kW (-9 % documented deviation)
    assert results["machines"]["CR.5009"]["P_installed_kW"] == pytest.approx(116.0, rel=0.15)


def test_9_2_zone_1_2(results):
    # AgLime 55 t/h wet (55 % of the 100 t/h reclaim) — exact split by conservation
    assert results["products"]["AgLime"]["tph"] == pytest.approx(55.0, abs=0.6)


def test_9_3_zone_1_3(results):
    p = results["products"]
    m = results["machines"]
    assert m["DY.03"]["evaporated_water_tph"] == pytest.approx(2.26, abs=0.05)
    assert m["DY.03"]["burner_power_kW"] == pytest.approx(3827.0, rel=0.05)
    assert p["FeedLime grits"]["tph"] == pytest.approx(10.1, abs=0.5)
    assert p["UltraFin"]["tph"] == pytest.approx(1.3, abs=0.3)
    assert m["ML.26"]["P_installed_kW"] == pytest.approx(45.0, rel=0.25)


def test_ultrafin_not_certified_without_measurement(results):
    assert any("NOT CERTIFIED" in a for a in results["alerts"])


def test_product_compliance_reported(results):
    kfs = results["products"]["KFS"]["compliance"]
    assert kfs is not None
    # KFS 30/55/15 envelope (three %-passing thresholds) is wired and evaluated
    assert set(kfs["envelope"]) == {"below_ok", "in_cut_ok", "above_ok"}
    assert kfs["below_cut_pct"] + kfs["in_cut_pct"] + kfs["above_cut_pct"] == pytest.approx(
        100.0, abs=0.1
    )
