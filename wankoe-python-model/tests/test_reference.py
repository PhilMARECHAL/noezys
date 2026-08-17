"""Reproduction of the reference case (specification, chapter 9).

Acceptance criteria: mass + water closure on every scenario and
reproduction of the documented values. Tolerances reflect the DOCUMENTED
residual deviations of the calibration (see data/reference_feed_curve.json
and the README): CR.5006 / CR.5011 powers carry a known gap, reported to
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
    # Chapter 9 also embeds the spec-era fuzzy imperfection (I = 0.4). The
    # client arbitration 2026-08-10 (Q1/12): dry imperfection I = 0.15 (literature)
    # supersedes it as the shipped default, so this suite pins the SPEC-ERA
    # value: the model must keep reproducing ch.9 under ch.9's calibration.
    return run_scenario(
        load_parameters(
            overrides={
                "feed_product": {
                    "cumulative_passing_curve": curve,
                    "properties": {"moisture_pct": {"default": 8}},
                },
                # ch.9 was authored with 30 t/h at the dryer INLET; the
                # 2026-08-13 client ruling redefined the default as 32.1
                # (= 30 t/h at the OUTLET, the dryer's capacity limit) —
                # pin the spec-era inlet basis here. 2026-08-14: the C1
                # redesign became the shipped default (zone_1_3_variant
                # "c1", feed 22.27) — ch.9 describes the AS-BUILT circuit,
                # so this suite pins the as-built variant too
                "default_scenario": {
                    "flow_rates_tph": {"zone_1_3_feedlime": 30},
                    "zone_1_3_variant": "as-built",
                },
                # ch.9 numerics were the unrefined spec sieve grid — the x2
                # computation grid (client arbitration 2026-08-14) is pinned
                # back to 1 here for exact spec-era reproduction
                "engine": {"computation_grid_refinement": 1},
                "calibration": {"I_dry": {"default": 0.4}},
                "machines": {
                    # 2026-08-13 optimization changed the shipped defaults
                    # (g 60, CSS 30, v 35) — pin ch.9's spec-era settings
                    "CR.5006": {"parameters": {"g": {"default": 40}}},
                    "CR.5011": {"parameters": {"x80": {"default": 20}, "v": {"default": 45}}},
                    "SR.5008": {"parameters": {"I": {"default": 0.4}}},
                    "SR.5115": {"parameters": {"I": {"default": 0.4}}},
                    # ch.9 fines were authored with the spec-era 100 um cut;
                    # Q6 (2026-08-11, expert book ch.11) moved the shipped
                    # default to 65 um — pin the spec-era value here
                    "SP.36": {"parameters": {"coupe": {"default": 100}}},
                },
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
    q020 = results["intermediate_flows"]["stream_0_20_dry_tph"] / (1 - 0.08)
    assert q020 == pytest.approx(190.7, abs=1.5)
    # CR.5006 expected ~116 kW; achieved ~106 kW (-9 % documented deviation)
    assert results["machines"]["CR.5006"]["P_installed_kW"] == pytest.approx(116.0, rel=0.15)


def test_9_2_zone_1_2(results):
    # Ch.9's 55 t/h AgLime was authored on the SPEC zone-1.2 topology
    # (15/5 double deck + single closing loop). The client ruling of
    # 2026-08-12 makes PFD REV18 authoritative (6 mm single-deck split;
    # open SR.5111 + CR.5113/SR.5115 loop), so the ch.9 figure is
    # superseded: re-baselined to the engine value on the PFD topology.
    # Q12 re-baseline 2026-08-17: A_j 60->65, b_j 0.8->1.5 (client option 2, expert-book calcite centrals)
    assert results["products"]["AgLime"]["tph"] == pytest.approx(43.52, abs=0.6)
    # topology-invariant conservation: FeedLime + AgLime = reclaim (dry)
    moisture = 8.0
    fl = results["products"]  # AgLime wet; FeedLime is internal, check via balance
    assert results["balances"]["zone_1_2"]["closed"]


def test_9_3_zone_1_3(results):
    p = results["products"]
    m = results["machines"]
    assert m["DY.03"]["evaporated_water_tph"] == pytest.approx(2.26, abs=0.05)
    assert m["DY.03"]["burner_power_kW"] == pytest.approx(3827.0, rel=0.05)
    # Ch.9's 10.1 t/h grits was authored with the spec's 5-15 FeedLime;
    # PFD REV18 (client ruling 2026-08-12) makes FeedLime the 6/20 cut —
    # coarser dryer feed, grits re-baselined to the engine value 9.34.
    assert p["FeedLime grits"]["tph"] == pytest.approx(9.34, abs=0.2)
    assert p["UltraFin"]["tph"] == pytest.approx(1.3, abs=0.3)
    # ch.9's ~45 kW was authored with the finer 5-15 FeedLime; the PFD's
    # 6/20 FeedLime is coarser (more +4 to mill) — re-baselined 2026-08-12
    assert m["ML.26"]["P_installed_kW"] == pytest.approx(61.2, rel=0.1)


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
