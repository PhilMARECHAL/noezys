"""Tests of the required-hours planning (hours follow the targets)."""

import pytest

from wankoe_model import load_parameters, run_required_hours


@pytest.fixture(scope="module")
def plan():
    return run_required_hours(load_parameters())


def test_production_lands_exactly_on_targets(plan):
    assert plan["production_t"]["KFS"] == pytest.approx(85000, abs=1)
    # C1 ADOPTION re-baseline (client 2026-08-14): the redesigned zone 1.3
    # makes 2.8x fewer fines per grits tonne, so at the 40 kt grits target
    # the fines flood DISAPPEARS: fines production falls to ~31.5 kt
    # (below the 60 kt market — nothing left to redirect). The AgLime
    # market is served by the 2A co-production (~49 kt) PLUS dedicated 2C
    # campaigns (~86 kt) — client lever wired 2026-08-14, and the 0/20
    # landfill drops 144 -> 58.4 kt/y (further reduction = grits sales
    # and/or the quarry target curve, client arbitration pending).
    assert plan["production_t"]["AgLime"] == pytest.approx(135000, abs=1)
    assert plan["sales_t"]["AgLime from dedicated 2C campaigns"] == pytest.approx(85811, rel=0.02)
    assert plan["sales_t"]["AgLime total sold (loop + campaigns + redirect)"] == pytest.approx(135000, abs=1)
    assert plan["sales_t"]["Fines surplus redirected to the AgLime sales channel"] == pytest.approx(0, abs=1)
    assert plan["sales_t"]["FeedLime fines sold as fines"] == pytest.approx(31531, rel=0.02)
    assert not any("unsellable" in a for a in plan["alerts"])
    assert plan["production_t"]["FeedLime grits"] == pytest.approx(40000, abs=1)


def test_2c_campaigns_are_toggleable(plan):
    # rule off -> the strict-c2 world returns (AgLime loop-only, market gap)
    off = run_required_hours(
        load_parameters(overrides={"commercial_rules": {"aglime_2c_campaigns": False}})
    )
    assert off["production_t"]["AgLime"] == pytest.approx(49189, rel=0.02)
    assert off["sales_t"]["AgLime from dedicated 2C campaigns"] == 0
    # and the landfill worsens accordingly
    assert (
        off["stockpiles_t"]["0/20 to LANDFILL (net loss)"]
        > plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"]
    )


def test_zone_feasibility_at_defaults(plan):
    # Q7 CLOSED 2026-08-13: the client extended zone 1.1 to 6 days/week
    # (ceiling 2000 -> 2400 h). The 85 kt firm KFS commitment now fits:
    # 2069 h required = 86.2 % utilization. ALL zones feasible.
    for name in ("1.1", "1.2", "1.3"):
        zone = plan["zones"][name]
        assert zone["feasible"] is True, f"zone {name} infeasible: {zone}"
        assert zone["required_hours_clock"] <= zone["ceiling_hours_clock"]
    assert not any("NOT reachable" in a for a in plan["alerts"])


def test_zone_1_1_driven_by_kfs(plan):
    z11 = plan["zones"]["1.1"]
    assert z11["driven_by"] == "KFS target"
    # Saturday regime + optimized KFS yield (23.9 %): 1777 h / 2400 h
    assert 65 < z11["utilization_pct"] < 85


def test_feedlime_stock_balanced(plan):
    assert plan["stockpiles_t"]["FeedLime net to stock"] == pytest.approx(0, abs=1)


def test_020_surplus_accumulates(plan):
    # Client ruling 2026-08-13 (final): NO crude-0/20 market exists — the
    # excess goes to LANDFILL as a net financial loss, alerted so it is
    # minimized, and it never appears as a sale
    assert plan["stockpiles_t"]["0/20 net to stock"] == pytest.approx(0, abs=1)
    assert plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"] > 0
    assert "Crude 0/20 sold (balancing)" not in plan["sales_t"]
    assert any("LANDFILL" in a for a in plan["alerts"])


def test_infeasible_ceiling_is_flagged():
    plan = run_required_hours(
        load_parameters(
            overrides={
                "default_scenario": {
                    "zones": {"1.1": {"available_hours": 1500, "availability_pct": 80}}
                }
            }
        )
    )
    assert plan["zones"]["1.1"]["feasible"] is False
    assert any("Zone 1.1" in a and "NOT reachable" in a for a in plan["alerts"])


def test_zone_1_1_can_be_driven_by_020_demand():
    plan = run_required_hours(
        load_parameters(
            overrides={
                "production_targets": {"KFS 20/35": {"target_t_per_year": 10000}}
            }
        )
    )
    assert plan["zones"]["1.1"]["driven_by"] == "0/20 demand of zone 1.2"
    assert plan["production_t"]["KFS"] > 10000  # co-produced beyond its target