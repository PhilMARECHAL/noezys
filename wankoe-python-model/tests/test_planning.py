"""Tests of the required-hours planning (hours follow the targets)."""

import pytest

from wankoe_model import load_parameters, run_required_hours, run_scenario


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
    # re-baselined 2026-08-14 (fines OBJECTIVE 60 kt + two-mode zone 1.3):
    # more FeedLime demand -> more 2A co-production -> smaller 2C complement
    assert plan["sales_t"]["AgLime from dedicated 2C campaigns"] == pytest.approx(67856, rel=0.02)
    assert plan["sales_t"]["AgLime total sold (loop + campaigns + redirect)"] == pytest.approx(135000, abs=1)
    assert plan["sales_t"]["Fines surplus redirected to the AgLime sales channel"] == pytest.approx(0, abs=1)
    # the fines OBJECTIVE is served exactly (client 2026-08-14): mode-G
    # co-production 33.5 kt + mode-F campaign hours close it to 60 kt
    assert plan["sales_t"]["FeedLime fines sold as fines"] == pytest.approx(60000, abs=1)
    assert plan["production_t"]["FeedLime fines"] == pytest.approx(60000, abs=1)
    assert plan["zone_1_3_split"]["mode_F_hours_effective"] > 0
    assert not any("unsellable" in a for a in plan["alerts"])
    assert plan["production_t"]["FeedLime grits"] == pytest.approx(40000, abs=1)


def test_2c_campaigns_are_toggleable(plan):
    # rule off -> the strict-c2 world returns (AgLime loop-only, market gap)
    off = run_required_hours(
        load_parameters(overrides={"commercial_rules": {"aglime_2c_campaigns": False}})
    )
    # re-baselined 2026-08-14 (fines objective raises the FeedLime demand,
    # so 2A co-production rises): 2A-only AgLime 67 144
    assert off["production_t"]["AgLime"] == pytest.approx(67144, rel=0.02)
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


def test_zone_1_1_auto_mode_1B_serves_020_deficit():
    # Rewritten 2026-08-14 (client rule zone_1_1_auto_mode_1B): KFS is
    # NEVER over-produced — when the 0/20 demand exceeds the KFS-driven
    # hours, KFS lands EXACTLY on its target and the 0/20 deficit is
    # produced by dedicated mode-1B hours (was: max() with co-produced KFS)
    plan = run_required_hours(
        load_parameters(
            overrides={
                "production_targets": {"KFS 20/35": {"target_t_per_year": 10000}}
            }
        )
    )
    assert plan["zones"]["1.1"]["driven_by"] == "KFS target + auto mode-1B for the 0/20 deficit"
    assert plan["production_t"]["KFS"] == pytest.approx(10000, abs=1)
    assert plan["zone_1_1_split"]["mode_1B_hours_effective"] > 0
    # the 0/20 balance still closes: produced = reclaimed + landfill
    assert plan["stockpiles_t"]["0/20 net to stock"] == pytest.approx(0, abs=1)
    assert not any(a.startswith("KFS over-produced") for a in plan["alerts"])


def test_zone_1_1_auto_mode_1B_toggle_off_keeps_legacy_max():
    # Toggle-off audit path (2026-08-14): the legacy max() behavior is
    # preserved — 0/20-driven hours co-produce KFS beyond its target,
    # now surfaced by an overproduction alert
    plan = run_required_hours(
        load_parameters(
            overrides={
                "production_targets": {"KFS 20/35": {"target_t_per_year": 10000}},
                "commercial_rules": {"zone_1_1_auto_mode_1B": False},
            }
        )
    )
    assert plan["zones"]["1.1"]["driven_by"] == "0/20 demand of zone 1.2"
    assert plan["production_t"]["KFS"] > 10000  # co-produced beyond its target
    assert plan["zone_1_1_split"]["mode_1B_hours_effective"] == 0
    assert any(a.startswith("KFS over-produced") for a in plan["alerts"])

def test_rain_capped_branch_is_mass_consistent():
    # Error-hunt fix M-3 (2026-08-15): before the fix a capped plan divided
    # the achievable FeedLime by the mode-G rate only — it reported 100 284 t
    # of product from 84 780 t of dry feed (mass-impossible) with a split
    # that contradicted the zone hours
    plan = run_required_hours(
        load_parameters(
            overrides={
                "default_scenario": {"zones": {"1.2": {"available_hours": 1600}}}
            }
        )
    )
    split = plan["zone_1_3_split"]
    dry_products = (
        plan["production_t"]["FeedLime grits"]
        + plan["production_t"]["FeedLime fines"]
        + plan["production_t"]["UltraFin"]
    )
    dry_feed = 0.93 * plan["stockpiles_t"]["FeedLime consumed"]
    assert dry_products == pytest.approx(dry_feed, rel=0.001)
    # grits keep their priority; the fines miss is alerted honestly
    assert plan["production_t"]["FeedLime grits"] == pytest.approx(40000, abs=1)
    assert plan["production_t"]["FeedLime fines"] < 60000
    assert any("fines objective NOT reachable" in a for a in plan["alerts"])
    assert split["mode_G_hours_effective"] + split["mode_F_hours_effective"] > 0


def test_2c_campaign_hours_fit_the_dry_season():
    # Error-hunt fix M-4 (2026-08-15): 2C (1.7 mm loop) is physically
    # impossible in rain — before the fix a dry-season-saturated plan still
    # scheduled 2C hours and reported the AgLime market served
    plan = run_required_hours(
        load_parameters(
            overrides={
                "default_scenario": {"zones": {"1.2": {"available_hours": 3600}}},
                "production_targets": {
                    "FeedLime grits 2-4": {"target_t_per_year": 80000}
                },
            }
        )
    )
    assert plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"] == 0
    assert plan["production_t"]["AgLime"] < 135000
    assert any("DRY-SEASON capacity" in a for a in plan["alerts"])


def test_scheduled_mode_photo_alerts_reach_the_plan(plan):
    # Error-hunt fix M-5 (2026-08-15): the 2C conveyor overload (standing
    # finding) must be visible in the plan that schedules 679 h/y of 2C
    assert any(
        a.startswith("[zone 1.2 mode 2C]") and "conveyor rating" in a
        for a in plan["alerts"]
    )


def test_mode_F_photo_consumes_feedlime_at_the_mode_F_rate():
    # Error-hunt fix C-5 (2026-08-15): the single-photo stockpile table
    # booked mode-F consumption at the mode-G rate (+28 % phantom draw)
    r = run_scenario(
        load_parameters(overrides={"default_scenario": {"zone_1_3_mode": "F"}})
    )
    consumed = r["period_balance"]["stockpiles_t"]["FeedLime consumed_t"]
    params = load_parameters()
    z13 = params["default_scenario"]["zones"]["1.3"]
    hours_13 = z13["available_hours"] * z13["availability_pct"] / 100.0
    # booked at the mode-F feed 25.05 (data zone_1_3_feedlime_mode_F),
    # not the mode-G 32.1 (+28 % phantom draw before the fix)
    assert consumed == pytest.approx(25.05 * hours_13, abs=1)


def test_kfs_yield_indicator(plan):
    # Client indicator (definition arbitrated in 4 questions, 2026-08-14):
    # whole KFS product stream / wet pivot feed, with the real PSD attached
    # and a DYNAMIC zero-landfill target
    ky = plan["kfs_yield"]
    # 24.88 % on the x2 converged grid (was 24.59 on the spec grid; the
    # action-5 study quantified the +0.3 pt discretization bias)
    assert ky["realized_pct"] == pytest.approx(24.88, abs=0.2)
    # required drops to 25.9 % — the fines objective consumes most of the
    # 0/20 excess (landfill 42.5 -> 13.8 kt/y); gap to realized: 1.05 pt
    assert ky["required_for_zero_landfill_pct"] == pytest.approx(25.9, abs=0.3)
    assert ky["kfs_real_psd_pct"]["in_cut_20_35"] > 80
    assert any(a.startswith("KFS Yield") for a in plan["alerts"])
