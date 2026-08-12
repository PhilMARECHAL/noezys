"""Tests of the required-hours planning (hours follow the targets)."""

import pytest

from wankoe_model import load_parameters, run_required_hours


@pytest.fixture(scope="module")
def plan():
    return run_required_hours(load_parameters())


def test_production_lands_exactly_on_targets(plan):
    assert plan["production_t"]["KFS"] == pytest.approx(85000, abs=1)
    # Client rule c2 (2026-08-12) on the PFD REV18 topology: FeedLime
    # demand binds FIRST (the 6 mm cut co-produces more FeedLime per
    # AgLime tonne), so AgLime lands BELOW its 135 kt market cap —
    # ~113 kt at defaults. The cap must never be exceeded.
    assert plan["production_t"]["AgLime"] <= 135000 + 1
    assert plan["production_t"]["AgLime"] == pytest.approx(112822, rel=0.02)
    assert plan["production_t"]["FeedLime grits"] == pytest.approx(40000, abs=1)


def test_zone_feasibility_at_defaults(plan):
    # client arbitration 2026-08-10 (Q1/12): dry imperfection I = 0.15 (literature): the sharper cut yields less KFS per hour, so zone 1.1
    # needs ~2069 h > its 2000 h ceiling — a DOCUMENTED design risk (the
    # securing levers are the client's question 7/12). Zones 1.2/1.3 hold.
    assert plan["zones"]["1.1"]["feasible"] is False
    for name in ("1.2", "1.3"):
        zone = plan["zones"][name]
        assert zone["feasible"] is True, f"zone {name} infeasible: {zone}"
        assert zone["required_hours_clock"] <= zone["ceiling_hours_clock"]
    assert any("Zone 1.1" in a and "NOT reachable" in a for a in plan["alerts"])


def test_zone_1_1_driven_by_kfs(plan):
    z11 = plan["zones"]["1.1"]
    assert z11["driven_by"] == "KFS target"
    # client arbitration 2026-08-10 (Q1/12): dry imperfection I = 0.15 (literature): ~103.5 % utilization — the 85 kt firm KFS commitment
    # exceeds the 2000 h regime at 250 t/h (securing lever pending, Q7/12)
    assert 100 < z11["utilization_pct"] < 110


def test_feedlime_stock_balanced(plan):
    assert plan["stockpiles_t"]["FeedLime net to stock"] == pytest.approx(0, abs=1)


def test_020_surplus_accumulates(plan):
    # the spec's "mechanical surplus": more 0/20 produced than reclaimed
    assert plan["stockpiles_t"]["0/20 net to stock"] > 0


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