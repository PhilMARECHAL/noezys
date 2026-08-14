"""Tests of the required-hours planning (hours follow the targets)."""

import pytest

from wankoe_model import load_parameters, run_required_hours


@pytest.fixture(scope="module")
def plan():
    return run_required_hours(load_parameters())


def test_production_lands_exactly_on_targets(plan):
    assert plan["production_t"]["KFS"] == pytest.approx(85000, abs=1)
    # ZERO-WASTE rule (client 2026-08-13): the fines surplus beyond its
    # 60 kt market is redirected into the AgLime channel; the loop only
    # produces the complement, so TOTAL AgLime sales land exactly on the
    # 135 kt market cap and nothing is unsellable.
    # Reference configuration 2026-08-13 (0/20-closure campaign): optimal
    # zone-1 settings + grits planning target 44 400 t/y at the dryer limit
    assert plan["production_t"]["AgLime"] == pytest.approx(75241, rel=0.02)
    assert plan["sales_t"]["AgLime total sold (loop + redirect)"] == pytest.approx(135000, abs=1)
    assert plan["sales_t"]["FeedLime fines sold as fines"] == pytest.approx(60000, abs=1)
    assert not any("unsellable" in a for a in plan["alerts"])
    assert plan["production_t"]["FeedLime grits"] == pytest.approx(44400, abs=1)


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
    # Zero-residual rule (client 2026-08-13): the mechanical 0/20 surplus
    # is SOLD as crude product — the stock balance closes at zero in every
    # configuration, and the crude tonnage is the swing variable
    assert plan["stockpiles_t"]["0/20 net to stock"] == pytest.approx(0, abs=1)
    assert plan["stockpiles_t"]["0/20 sold as crude"] > 0
    assert plan["sales_t"]["Crude 0/20 sold (balancing)"] == pytest.approx(
        plan["stockpiles_t"]["0/20 sold as crude"], abs=1
    )


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