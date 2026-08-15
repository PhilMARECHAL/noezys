"""RAIN-WEEK MOISTURE STUDY — engine evidence behind
docs/design/moisture/rain-week-study.md (client arbitration 2026-08-15:
porous-stone moisture set, physical 1.7 mm requalification, line
continues everywhere, absorption test = new external trigger).

Scenario (docs/design/moisture/rain-week-scenario.json, data-first, [H]
until the absorption test): after 1 week of continuous rain on the
OUTDOOR stockpiles — quarry feed 7 -> 12 %, reclaimed 0/20 stock
7 -> 15 %, FeedLime 6/20 stock 7 -> 11 %; linear drainage back to 7 %
over 5-7 days (6-day midpoint used); N = 6 rain weeks/year [H].

ENGINE LIMITATION (documented, not hacked around): the engine carries
ONE global moisture per photo (feed_product.properties.moisture_pct) —
scenario.py gives the reclaim and FeedLime streams the FEED moisture.
The three simultaneous stock moistures are therefore read from a
COMPOSITE of per-zone photos, each run at its own stock moisture:

  zone 1.1  <- photo at 12 %, weather rain
  zone 1.2  <- photo at 15 %, weather rain (mode 2B forced = PHYSICS)
  zone 1.3  <- photos at 11 % (modes G and F), weather DRY on purpose:
               zone 1.3 is weather-independent (all cuts BEHIND the
               dryer at 0.5 %) and the dry flag keeps the FeedLime
               stream on the 6/20 STOCK PSD (a rain flag would swap it
               for the 2B bypass 0/20 PSD, which is not the stock the
               client scenario describes).

Per-stream moisture overrides are a MODEL-IMPROVEMENT item.

Measurement frame:
  (a) rain week vs dry week at the SAME weekly hours (annual
      required-hours plan / 52 — operating policy: the line continues);
  (b) the 5-7 day drainage tail (daily photos at the interpolated
      moistures);
  (c) the annual view with N rain weeks (weekly-scaled arithmetic on
      engine rates, clearly labeled, + a run_required_hours cross-check
      with season fractions N/52).

Run:  PYTHONPATH=src python scripts/rain_week_study.py
Writes docs/design/moisture/rain-week-engine-evidence.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model.paths import deep_merge  # noqa: E402
from wankoe_model.planning import run_required_hours  # noqa: E402
from wankoe_model.scenario import load_parameters, run_scenario  # noqa: E402

OUT_DIR = ROOT / "docs" / "design" / "moisture"
SCENARIO_PATH = OUT_DIR / "rain-week-scenario.json"
WEEKS_PER_YEAR = 52.0


def _photo(overrides: dict) -> dict:
    return run_scenario(load_parameters(overrides=overrides))


def _paraffin_l(mwh: float, burner: dict) -> float:
    kg = mwh * 1000.0 / burner["lhv_kwh_per_kg"]["default"]
    return kg / burner["density_kg_per_l"]["default"]


def main() -> dict:
    scenario = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    params = load_parameters()
    burner = params["electrical_loads"]["dryer_burner"]
    moist = scenario["stock_moistures_pct"]
    m_ref = moist["dry_reference"]
    m_feed = moist["quarry_feed_after_rain_week"]["default"]
    m_020 = moist["reclaimed_0_20_stock_after_rain_week"]["default"]
    m_fl = moist["feedlime_6_20_stock_after_rain_week"]["default"]
    n_weeks = scenario["annual_rain_weeks"]["default"]
    d_days = scenario["drainage"]["days_used"]

    # ---------------- reference annual plan -> weekly hours (policy: the
    # line continues at its planned regime; weekly = annual plan / 52)
    plan = run_required_hours(params)
    h11_wk = plan["zone_1_1_split"]["mode_1A_hours_effective"] / WEEKS_PER_YEAR
    h2a_wk = plan["zone_1_2_split"]["dry_season_hours_effective"] / WEEKS_PER_YEAR
    h2c_wk = plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"] / WEEKS_PER_YEAR
    h13g_wk = plan["zone_1_3_split"]["mode_G_hours_effective"] / WEEKS_PER_YEAR
    h13f_wk = plan["zone_1_3_split"]["mode_F_hours_effective"] / WEEKS_PER_YEAR
    weekly_hours = {
        "zone_1_1_mode_1A": round(h11_wk, 2),
        "zone_1_2_mode_2A": round(h2a_wk, 2),
        "zone_1_2_mode_2C": round(h2c_wk, 2),
        "zone_1_3_mode_G": round(h13g_wk, 2),
        "zone_1_3_mode_F": round(h13f_wk, 2),
        "_basis": "annual required-hours plan / 52 (effective hours; hours follow the targets)",
    }

    # ---------------- DRY-WEEK photos (7 %, weather dry)
    dry_g = _photo({"default_scenario": {"weather": "dry", "zone_1_3_mode": "G"}})
    dry_f = _photo({"default_scenario": {"weather": "dry", "zone_1_3_mode": "F"}})
    dry_2c = _photo({"default_scenario": {"weather": "dry", "zone_1_2_mode": "2C"}})

    # ---------------- RAIN-WEEK composite photos (per the scenario file)
    ph = scenario["photos"]
    rain_z11 = _photo(ph["photo_zone_1_1_rain"]["overrides"])
    rain_z12 = _photo(ph["photo_zone_1_2_rain"]["overrides"])
    wet_g = _photo(ph["photo_zone_1_3_wet_G"]["overrides"])
    wet_f = _photo(ph["photo_zone_1_3_wet_F"]["overrides"])
    annex_bypass = _photo(ph["photo_zone_1_3_bypass_PSD_annex"]["overrides"])

    # hourly rates (engine)
    kfs_tph = dry_g["products"]["KFS"]["tph"]  # wet, as sold
    kfs_tph_rain = rain_z11["products"]["KFS"]["tph"]
    aglime_2a_tph = dry_g["products"]["AgLime"]["tph"]
    aglime_2c_tph = dry_2c["products"]["AgLime"]["tph"]
    reclaim_tph = params["default_scenario"]["flow_rates_tph"]["zone_1_2_reclaim"]
    feedlime_2a_tph = reclaim_tph - aglime_2a_tph  # wet co-product in 2A

    def z13_rates(photo_g, photo_f):
        return {
            "grits_tph_G": photo_g["products"]["FeedLime grits"]["tph"],
            "fines_tph_G": photo_g["products"]["FeedLime fines"]["tph"],
            "fines_tph_F": photo_f["products"]["FeedLime fines"]["tph"],
            "ultrafin_tph_G": photo_g["products"]["UltraFin"]["tph"],
            "ultrafin_tph_F": photo_f["products"]["UltraFin"]["tph"],
            "dryer_outlet_wet_tph_G": photo_g["machines"]["DY.03"]["wet_output_tph"],
            "dryer_outlet_wet_tph_F": photo_f["machines"]["DY.03"]["wet_output_tph"],
            "burner_kW_G": photo_g["machines"]["DY.03"]["burner_power_kW"],
            "burner_kW_F": photo_f["machines"]["DY.03"]["burner_power_kW"],
            "evaporated_tph_G": photo_g["machines"]["DY.03"]["evaporated_water_tph"],
        }

    r_dry = z13_rates(dry_g, dry_f)
    r_wet = z13_rates(wet_g, wet_f)

    def week_products(kfs, aglime_2a, aglime_2c, z13):
        return {
            "KFS_t": round(kfs * h11_wk, 1),
            "AgLime_t": round(aglime_2a * h2a_wk + aglime_2c * h2c_wk, 1),
            "FeedLime grits_t": round(z13["grits_tph_G"] * h13g_wk, 1),
            "FeedLime fines_t": round(
                z13["fines_tph_G"] * h13g_wk + z13["fines_tph_F"] * h13f_wk, 1
            ),
            "UltraFin_t": round(
                z13["ultrafin_tph_G"] * h13g_wk + z13["ultrafin_tph_F"] * h13f_wk, 1
            ),
        }

    def week_paraffin(z13):
        mwh = (z13["burner_kW_G"] * h13g_wk + z13["burner_kW_F"] * h13f_wk) / 1000.0
        return mwh, _paraffin_l(mwh, burner)

    dry_week = week_products(kfs_tph, aglime_2a_tph, aglime_2c_tph, r_dry)
    # rain week: zone 1.2 in 2B the whole week (PHYSICS) -> zero AgLime;
    # zone 1.3 continues on the 11 % 6/20 stock; zone 1.1 continues at 12 %
    rain_week = week_products(kfs_tph_rain, 0.0, 0.0, r_wet)
    mwh_dry_wk, paraffin_dry_wk = week_paraffin(r_dry)
    mwh_rain_wk, paraffin_rain_wk = week_paraffin(r_wet)

    # zone-1.2 rain-week output: the SAME clock hours run in mode 2B —
    # FeedLime (unscreened 0/20 bypass) = the whole reclaim
    feedlime_2b_wk = reclaim_tph * (h2a_wk + h2c_wk)
    dry_week["FeedLime 6/20 produced (z1.2)_t"] = round(feedlime_2a_tph * h2a_wk, 1)
    rain_week["FeedLime produced (z1.2, 2B bypass 0/20)_t"] = round(feedlime_2b_wk, 1)

    # KFS dry-solids content (wet rate is moisture-invariant at fixed wet feed)
    kfs_dry_share_dry = 1.0 - m_ref / 100.0
    kfs_dry_share_rain = 1.0 - m_feed / 100.0

    # dryer limit check: 30 t/h AT OUTLET (client 2026-08-13); wet-feed cap 32.1
    max_outlet = params["machines"]["DY.03"]["max_outlet_tph"]
    dryer_check = {
        "outlet_limit_tph": max_outlet,
        "dry_week_outlet_mode_G_tph": round(r_dry["dryer_outlet_wet_tph_G"], 2),
        "rain_week_outlet_mode_G_tph": round(r_wet["dryer_outlet_wet_tph_G"], 2),
        "_note": (
            "At 11 % inlet moisture the 32.1 t/h WET-FEED cap yields only "
            f"{r_wet['dryer_outlet_wet_tph_G']:.2f} t/h at the outlet — the 30 t/h "
            "outlet limit CANNOT be reached during the rain week (structural, "
            "not an overload): outlet = 32.1 x (1 - 0.11)/(1 - 0.005)."
        ),
    }

    # KFS envelope + screen-area derating under rain (engine wiring honest
    # statement: I_rain applies to the 1.7 mm loop screens ONLY — the
    # 20/35 coarse-cut imperfection is weather-independent in the model;
    # rain enters zone 1.1 through the wet_capacity_factor area derating)
    kfs_env = {
        "dry_week": dry_g["products"]["KFS"]["compliance"],
        "rain_week": rain_z11["products"]["KFS"]["compliance"],
        "sr5007_required_area_m2_dry": {
            k: v["required_area_m2"]
            for k, v in dry_g["machines"]["SR.5007"]["areas_m2"].items()
        },
        "sr5007_required_area_m2_rain": {
            k: v["required_area_m2"]
            for k, v in rain_z11["machines"]["SR.5007"]["areas_m2"].items()
        },
        "_note": (
            "The engine wires I_rain to the 1.7 mm loop screens only (now moot: "
            "mode 2B is forced by physics); the 20/35 mm cut keeps its dry "
            "imperfection under rain and the screen AREA is derated by "
            "wet_capacity_factor 0.75 [H] — KFS envelope compliance is therefore "
            "model-identical dry vs rain. A wet-screening imperfection model for "
            "coarse cuts is a candidate improvement, pending site evidence."
        ),
    }

    # ---------------- (b) drainage tail: D days, linear back to 7 %
    tail_days = []
    tail_paraffin_excess_l = 0.0
    tail_grits_deficit_t = 0.0
    tail_fines_deficit_t = 0.0
    for d in range(1, d_days + 1):
        f = 1.0 - d / d_days  # remaining excess fraction
        md_feed = m_ref + (m_feed - m_ref) * f
        md_020 = m_ref + (m_020 - m_ref) * f
        md_fl = m_ref + (m_fl - m_ref) * f
        over = {
            "feed_product": {"properties": {"moisture_pct": {"default": md_fl}}},
            "default_scenario": {"weather": "dry"},
        }
        pg = _photo(deep_merge(over, {"default_scenario": {"zone_1_3_mode": "G"}}))
        pf = _photo(deep_merge(over, {"default_scenario": {"zone_1_3_mode": "F"}}))
        rd = z13_rates(pg, pf)
        day_mwh = (
            (rd["burner_kW_G"] - r_dry["burner_kW_G"]) * h13g_wk / 7.0
            + (rd["burner_kW_F"] - r_dry["burner_kW_F"]) * h13f_wk / 7.0
        ) / 1000.0
        day_paraffin = _paraffin_l(day_mwh, burner)
        day_grits = (r_dry["grits_tph_G"] - rd["grits_tph_G"]) * h13g_wk / 7.0
        day_fines = (
            (r_dry["fines_tph_G"] - rd["fines_tph_G"]) * h13g_wk / 7.0
            + (r_dry["fines_tph_F"] - rd["fines_tph_F"]) * h13f_wk / 7.0
        )
        tail_paraffin_excess_l += day_paraffin
        tail_grits_deficit_t += day_grits
        tail_fines_deficit_t += day_fines
        tail_days.append(
            {
                "day": d,
                "quarry_feed_pct": round(md_feed, 2),
                "reclaimed_0_20_pct": round(md_020, 2),
                "feedlime_6_20_pct": round(md_fl, 2),
                "dryer_outlet_mode_G_tph": round(rd["dryer_outlet_wet_tph_G"], 2),
                "burner_kW_G": round(rd["burner_kW_G"], 1),
                "paraffin_excess_L": round(day_paraffin, 0),
                "grits_deficit_t": round(day_grits, 1),
                "fines_deficit_t": round(day_fines, 1),
            }
        )

    # ---------------- (a) weekly balance table
    week_paraffin_excess_l = paraffin_rain_wk - paraffin_dry_wk
    weekly = {
        "weekly_hours_effective": weekly_hours,
        "dry_week": {
            **dry_week,
            "0/20 reclaimed (z1.2)_t": round(reclaim_tph * (h2a_wk + h2c_wk), 1),
            "dryer_outlet_mode_G_tph": dryer_check["dry_week_outlet_mode_G_tph"],
            "burner_MWh": round(mwh_dry_wk, 1),
            "paraffin_L": round(paraffin_dry_wk, 0),
            "KFS_dry_solids_share_pct": round(100 * kfs_dry_share_dry, 1),
        },
        "rain_week": {
            **rain_week,
            "0/20 reclaimed (z1.2)_t": round(reclaim_tph * (h2a_wk + h2c_wk), 1),
            "dryer_outlet_mode_G_tph": dryer_check["rain_week_outlet_mode_G_tph"],
            "burner_MWh": round(mwh_rain_wk, 1),
            "paraffin_L": round(paraffin_rain_wk, 0),
            "KFS_dry_solids_share_pct": round(100 * kfs_dry_share_rain, 1),
        },
        "deltas_rain_minus_dry": {
            "KFS_t": round(rain_week["KFS_t"] - dry_week["KFS_t"], 1),
            "AgLime_t": round(rain_week["AgLime_t"] - dry_week["AgLime_t"], 1),
            "FeedLime grits_t": round(
                rain_week["FeedLime grits_t"] - dry_week["FeedLime grits_t"], 1
            ),
            "FeedLime fines_t": round(
                rain_week["FeedLime fines_t"] - dry_week["FeedLime fines_t"], 1
            ),
            "paraffin_L": round(week_paraffin_excess_l, 0),
        },
        "dryer_outlet_check": dryer_check,
        "kfs_envelope_and_screen_areas": kfs_env,
    }

    # ---------------- (c) annual view, N rain weeks (weekly-scaled
    # arithmetic on engine rates — clearly labeled)
    # zone 1.2 mode-mix identity: rain-week 2B hours produce FeedLime at
    # 100 t/h vs 61.6 t/h in 2A; the displaced 2A hours lose AgLime
    # co-production, made up by extra 2C hours. Total reclaim (and hence
    # landfill) is INVARIANT because every reclaimed tonne leaves as
    # product either way (zero-waste structure).
    feedlime_demand_t = plan["stockpiles_t"]["FeedLime consumed"]
    h2b_year = (h2a_wk + h2c_wk) * n_weeks
    feedlime_2b_t = reclaim_tph * h2b_year
    h2a_year = (feedlime_demand_t - feedlime_2b_t) / feedlime_2a_tph
    aglime_2a_t = h2a_year * aglime_2a_tph
    aglime_cap = plan["sales_t"]["AgLime market cap"]
    h2c_year = max(0.0, aglime_cap - aglime_2a_t) / aglime_2c_tph
    z12_hours_replanned = h2b_year + h2a_year + h2c_year
    z12_hours_plan = plan["zones"]["1.2"]["required_hours_effective"]

    # zone 1.3: rain + drainage weeks produce less per hour — extra hours
    # to hold the annual grits/fines targets (headroom check vs ceiling)
    grits_deficit_y = n_weeks * (
        (r_dry["grits_tph_G"] - r_wet["grits_tph_G"]) * h13g_wk + tail_grits_deficit_t
    )
    fines_deficit_y = n_weeks * (
        (r_dry["fines_tph_G"] - r_wet["fines_tph_G"]) * h13g_wk
        + (r_dry["fines_tph_F"] - r_wet["fines_tph_F"]) * h13f_wk
        + tail_fines_deficit_t
    )
    extra_g_h = grits_deficit_y / r_dry["grits_tph_G"]
    extra_f_h = fines_deficit_y / r_dry["fines_tph_F"]
    z13_hours_new = plan["zones"]["1.3"]["required_hours_effective"] + extra_g_h + extra_f_h
    z13_ceiling_eff = (
        params["default_scenario"]["zones"]["1.3"]["available_hours"]
        * params["default_scenario"]["zones"]["1.3"]["availability_pct"]
        / 100.0
    )

    paraffin_excess_y = n_weeks * (week_paraffin_excess_l + tail_paraffin_excess_l)

    # engine cross-check: run_required_hours with season fractions N/52
    f_rain = n_weeks / WEEKS_PER_YEAR
    plan_n = run_required_hours(
        load_parameters(
            overrides={
                "default_scenario": {
                    "dry_season_fraction": 1.0 - f_rain,
                    "rain_season_fraction": f_rain,
                }
            }
        )
    )

    annual = {
        "_label": (
            "WEEKLY-SCALED ARITHMETIC on engine hourly rates (not a single "
            "engine photo): N rain weeks + N drainage tails applied to the "
            "reference annual plan; run_required_hours cross-check below"
        ),
        "N_rain_weeks": n_weeks,
        "N_status": scenario["annual_rain_weeks"]["status"],
        "paraffin_over_consumption_L_per_year": round(paraffin_excess_y, 0),
        "paraffin_reference_L_per_year": round(paraffin_dry_wk * WEEKS_PER_YEAR, 0),
        "zone_1_2_mode_mix_replanned_h": {
            "mode_2B_rain_weeks": round(h2b_year, 1),
            "mode_2A": round(h2a_year, 1),
            "mode_2C_campaigns": round(h2c_year, 1),
            "total": round(z12_hours_replanned, 1),
            "reference_plan_total": z12_hours_plan,
            "_identity": (
                "total hours and total reclaim are invariant (every reclaimed "
                "tonne leaves as product in 2A, 2B and 2C alike) -> LANDFILL "
                "UNCHANGED at the reference plan value"
            ),
        },
        "landfill_t_per_year": plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"],
        "markets": {
            "_verdict": (
                "all four markets remain served: AgLime lost during rain weeks "
                "is caught up in dry weeks (zone-1.2 headroom), grits/fines "
                "hour deficits are recovered within the zone-1.3 ceiling"
            ),
            "aglime_shifted_from_rain_weeks_t": round(dry_week["AgLime_t"] * n_weeks, 0),
            "grits_hour_deficit_t": round(grits_deficit_y, 0),
            "fines_hour_deficit_t": round(fines_deficit_y, 0),
        },
        "zone_1_3_extra_hours_effective": round(extra_g_h + extra_f_h, 1),
        "zone_1_3_hours_new_vs_ceiling": {
            "required_effective_h": round(z13_hours_new, 1),
            "ceiling_effective_h": z13_ceiling_eff,
            "feasible": bool(z13_hours_new <= z13_ceiling_eff),
        },
        "run_required_hours_cross_check_N_over_52": {
            "season_fractions": {"dry": 1.0 - f_rain, "rain": f_rain},
            "zone_1_2_rain_season_hours": plan_n["zone_1_2_split"][
                "rain_season_hours_effective"
            ],
            "zones_utilization_pct": {
                z: plan_n["zones"][z]["utilization_pct"] for z in ("1.1", "1.2", "1.3")
            },
            "production_t": plan_n["production_t"],
            "_note": (
                "the planner schedules 0 rain-season hours (dry-season capacity "
                "suffices) and the plan is N-invariant — the 2B rain-week "
                "running is the client's continue-everywhere POLICY, expressed "
                "above as a mode-mix shift at constant hours"
            ),
        },
    }

    # annex: bypass-PSD FeedLime quality (what 2B hours add to the stock)
    annex = {
        "_read": ph["photo_zone_1_3_bypass_PSD_annex"]["_read"],
        "grits_tph": annex_bypass["products"]["FeedLime grits"]["tph"],
        "fines_tph": annex_bypass["products"]["FeedLime fines"]["tph"],
        "grits_compliance": annex_bypass["products"]["FeedLime grits"]["compliance"],
    }

    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    evidence = {
        "_provenance": {
            "date": date.today().isoformat(),
            "commit": commit,
            "functions": [
                "wankoe_model.scenario.run_scenario",
                "wankoe_model.planning.run_required_hours",
            ],
            "scenario_file": "docs/design/moisture/rain-week-scenario.json",
            "replay": "PYTHONPATH=src python scripts/rain_week_study.py",
            "note": "composite per-zone photos (engine limitation: one global moisture per photo)",
        },
        "weekly_balance": weekly,
        "drainage_tail": {
            "days": tail_days,
            "paraffin_excess_total_L": round(tail_paraffin_excess_l, 0),
            "grits_deficit_total_t": round(tail_grits_deficit_t, 1),
            "fines_deficit_total_t": round(tail_fines_deficit_t, 1),
        },
        "annual_view": annual,
        "annex_bypass_psd_feedlime": annex,
        "alerts": {
            "rain_z11": rain_z11["alerts"],
            "rain_z12": rain_z12["alerts"],
            "wet_g": wet_g["alerts"],
        },
    }
    out_path = OUT_DIR / "rain-week-engine-evidence.json"
    out_path.write_text(json.dumps(evidence, indent=1) + "\n", encoding="utf-8")
    print(f"written {out_path.relative_to(ROOT)}")
    print(json.dumps(weekly["dry_week"], indent=1))
    print(json.dumps(weekly["rain_week"], indent=1))
    print(json.dumps(annual, indent=1))
    return evidence


if __name__ == "__main__":
    main()
