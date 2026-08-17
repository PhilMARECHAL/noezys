"""FMECA engine evidence — load/capacity factors feeding the occurrence
and severity cotations of the maintenance-plan FMECA register.

Client arbitration 2026-08-15 (FMECA maintenance plan, choice 4): the
generic occurrence classes by equipment type [H] are MODULATED by the
ENGINE's load factors — this script extracts them from the same engine
runs used everywhere else (run_required_hours + per-mode run_scenario
photos), so every number cited in docs/design/maintenance/
fmeca-register.{json,md} and preventive-maintenance-plan.md can be
replayed without the assistant.

Evidence extracted (defaults scenario = today's measured feed, plus the
quarry-target planning for the maintenance-window utilizations):

- planning: required hours, ceilings and utilization per zone, effective
  hours per mode bucket (1A/1B/2A/2B/2C/G/F) -> annual running hours of
  each equipment bucket;
- per-mode photos: absorbed power (P_net/eta_m) and throughput of the
  engine-modeled machines, screen feed rates, dryer duty;
- load/capacity ratios against the DATA-FIRST ratings
  (machines.*.max_capacity_tph, zone-1.2 loop_rating_tph, the BC.22 /
  BE.40 handling ratings of electrical_loads): RC.2 in mode F, CR.5011
  in mode 1B (90 t/h WET limit), CR.5113 absorbed kW in 2C vs 2A,
  DY.03 outlet vs its 30 t/h limit, BC.22 / BE.40 vs their ratings,
  SR.5111 / BC.5110 loop feed in 2C vs the 60 t/h loop rating.

Run:  PYTHONPATH=src python scripts/fmeca_engine_evidence.py
Writes docs/design/maintenance/fmeca-engine-evidence.json and prints a
summary table.
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

OUT_DIR = ROOT / "docs" / "design" / "maintenance"
QUARRY_CURVE_PATH = (
    ROOT / "docs" / "design" / "zone13-redesign" / "quarry-target-curve-20pct-margin.json"
)
QUARRY_AGLIME_BASELINE_T = 108_000  # client 2026-08-14 (135 kt - 20 % flex)

MODE_PHOTO_OVERRIDES = {
    "1A": {"zone_1_1_mode": "1A"},
    "1B": {"zone_1_1_mode": "1B"},  # forced photo: 1B never runs at defaults
    "2A": {"zone_1_2_mode": "2A"},
    "2C": {"zone_1_2_mode": "2C"},
    "G": {"zone_1_3_mode": "G"},
    "F": {"zone_1_3_mode": "F"},
}


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover — provenance best effort
        return "unknown"


def main() -> dict:
    params = load_parameters()
    eta_m = params["calibration"]["eta_m"]["default"]

    plan = run_required_hours(params)
    with open(QUARRY_CURVE_PATH, encoding="utf-8") as f:
        quarry_curve = json.load(f)["cumulative_passing_curve"]
    aglime_key = next(
        k for k, t in params["production_targets"].items() if t["product"] == "AgLime"
    )
    params_q = load_parameters(
        overrides={
            "feed_product": {"cumulative_passing_curve": quarry_curve},
            "production_targets": {
                aglime_key: {"market_cap_t_per_year": QUARRY_AGLIME_BASELINE_T}
            },
        }
    )
    plan_q = run_required_hours(params_q)

    photos = {
        mode: run_scenario(
            deep_merge(params, {"default_scenario": {"weather": "dry", **override}})
        )
        for mode, override in MODE_PHOTO_OVERRIDES.items()
    }

    # wet/dry conversion of zone-1.1 internal streams (feed moisture ratio)
    feed_wet_tph = photos["1A"]["machines"]["CR.5006"]["throughput_tph"]
    wet_over_dry_11 = 250.0 / feed_wet_tph  # 250 t/h wet pivot feed (total-flow rule)

    def m(mode: str, code: str) -> dict:
        return photos[mode]["machines"][code]

    def absorbed(mode: str, code: str) -> float:
        return round(m(mode, code)["P_net_kW"] / eta_m, 1)

    def _val(node):
        return node["default"] if isinstance(node, dict) else node

    mach = params["machines"]
    rc1_cap = _val(mach["RC.1"]["max_capacity_tph"])
    rc2_cap = _val(mach["RC.2"]["max_capacity_tph"])
    rc2_units = _val(mach["RC.2"]["n_units"])
    cr5011_cap_wet = _val(mach["CR.5011"]["max_capacity_tph"])
    dy_out_cap = _val(mach["DY.03"]["max_outlet_tph"])
    # loop rating lives in the zone-1.2 planning block (data-first)
    def _find_loop_rating(node):
        if isinstance(node, dict):
            if "loop_rating_tph" in node:
                return node["loop_rating_tph"]
            for v in node.values():
                r = _find_loop_rating(v)
                if r is not None:
                    return r
        return None
    loop_rating_tph = _find_loop_rating(params)

    grits_G = photos["G"]["products"]["FeedLime grits"]["tph"]
    fines_F = photos["F"]["products"]["FeedLime fines"]["tph"]
    fines_G = photos["G"]["products"]["FeedLime fines"]["tph"]
    bc22_rating = 15.0  # electrical_loads.consumers["BC.22"] status: rated 15 t/h [H]
    be40_rating = 20.0  # electrical_loads.consumers["BE.40"] status: rated 20 t/h [H]

    cr5011_1B_dry = m("1B", "CR.5011")["throughput_tph"]
    cr5011_1A_dry = m("1A", "CR.5011")["throughput_tph"]

    evidence = {
        "_provenance": {
            "engine_commit": _git_commit(),
            "run_date": date.today().isoformat(),
            "functions": [
                "wankoe_model.planning.run_required_hours",
                "wankoe_model.scenario.run_scenario (per-mode photos, incl. forced 1B)",
            ],
            "data": "data/default_parameters.json",
            "produced_by": "NOEZYS",
        },
        "planning_defaults": {
            "zones": plan["zones"],
            "mode_hours_effective": {
                "1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
                "1B": plan["zone_1_1_split"]["mode_1B_hours_effective"],
                "2A": plan["zone_1_2_split"]["dry_season_hours_effective"],
                "2B": plan["zone_1_2_split"]["rain_season_hours_effective"],
                "2C": plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"],
                "G": plan["zone_1_3_split"]["mode_G_hours_effective"],
                "F": plan["zone_1_3_split"]["mode_F_hours_effective"],
            },
            "alerts": plan["alerts"],
        },
        "planning_quarry_target": {"zones": plan_q["zones"]},
        "load_factors": {
            "CR.5006": {
                "absorbed_kW_1A": absorbed("1A", "CR.5006"),
                "throughput_tph_dry_1A": round(m("1A", "CR.5006")["throughput_tph"], 1),
                "F80_mm": round(m("1A", "CR.5006")["F80_mm"], 1),
                "note": "feed F80 > 150 mm max nip size — SATURATION alert (planning alerts): the primary runs saturated at the measured feed",
            },
            "CR.5011": {
                "capacity_tph_wet": cr5011_cap_wet,
                "throughput_1A_tph_dry": round(cr5011_1A_dry, 1),
                "throughput_1A_tph_wet": round(cr5011_1A_dry * wet_over_dry_11, 1),
                "load_ratio_1A": round(cr5011_1A_dry * wet_over_dry_11 / cr5011_cap_wet, 3),
                "throughput_1B_tph_dry": round(cr5011_1B_dry, 1),
                "throughput_1B_tph_wet": round(cr5011_1B_dry * wet_over_dry_11, 1),
                "load_ratio_1B": round(cr5011_1B_dry * wet_over_dry_11 / cr5011_cap_wet, 3),
                "absorbed_kW_1A": absorbed("1A", "CR.5011"),
                "absorbed_kW_1B": absorbed("1B", "CR.5011"),
                "installed_kW": _val(mach["CR.5011"]["installed_power_kW"]),
                "note": "mode 1B (auto-rule photo) runs the loop AT its 90 t/h WET limit",
            },
            "CR.5113": {
                "absorbed_kW_2A": absorbed("2A", "CR.5113"),
                "absorbed_kW_2C": absorbed("2C", "CR.5113"),
                "throughput_2A_tph": round(m("2A", "CR.5113")["throughput_tph"], 1),
                "throughput_2C_tph": round(m("2C", "CR.5113")["throughput_tph"], 1),
                "note": "STANDING FINDING (OPEX 2026-08-15): 2C campaign duty ~348 kW absorbed vs ~87 kW in 2A — installed-motor sizing to be checked",
            },
            "RC.1": {
                "capacity_tph_dry": rc1_cap,
                "throughput_G_tph": round(m("G", "RC.1")["throughput_tph"], 1),
                "load_ratio_G": round(m("G", "RC.1")["throughput_tph"] / rc1_cap, 3),
                "throughput_F_tph": round(m("F", "RC.1")["throughput_tph"], 1),
                "load_ratio_F": round(m("F", "RC.1")["throughput_tph"] / rc1_cap, 3),
                "absorbed_kW_G": absorbed("G", "RC.1"),
                "absorbed_kW_F": absorbed("F", "RC.1"),
            },
            "RC.2": {
                "capacity_tph_dry_total": rc2_cap * rc2_units,
                "n_units": rc2_units,
                "throughput_G_tph": round(m("G", "RC.2")["throughput_tph"], 1),
                "load_ratio_G": round(m("G", "RC.2")["throughput_tph"] / (rc2_cap * rc2_units), 3),
                "throughput_F_tph": round(m("F", "RC.2")["throughput_tph"], 1),
                "load_ratio_F": round(m("F", "RC.2")["throughput_tph"] / (rc2_cap * rc2_units), 3),
                "absorbed_kW_G": absorbed("G", "RC.2"),
                "absorbed_kW_F": absorbed("F", "RC.2"),
                "note": "mode F runs BOTH units at 100 % of the 2 x 22 t/h capacity (mode-F gap 1.5 mm)",
            },
            "DY.03": {
                "max_outlet_tph": dy_out_cap,
                "outlet_G_tph": round(m("G", "DY.03")["wet_output_tph"], 1),
                "load_ratio_G": round(m("G", "DY.03")["wet_output_tph"] / dy_out_cap, 3),
                "outlet_F_tph": round(m("F", "DY.03")["wet_output_tph"], 1),
                "load_ratio_F": round(m("F", "DY.03")["wet_output_tph"] / dy_out_cap, 3),
                "burner_power_kW_G": round(m("G", "DY.03")["burner_power_kW"], 0),
                "drum_volume_m3": round(m("G", "DY.03")["drum_volume_m3"], 1),
                "note": "mode G runs the dryer AT its 30 t/h outlet limit — the ONLY drying line (single point)",
            },
            "screens_feed_tph": {
                "SR.5008_1A": round(m("1A", "SR.5008")["feed_tph"], 1),
                "SR.5105_2A": round(m("2A", "SR.5105")["feed_tph"], 1),
                "SR.5111_2A": round(m("2A", "SR.5111")["feed_tph"], 1),
                "SR.5111_2C": round(m("2C", "SR.5111")["feed_tph"], 1),
                "SR.5115_2A": round(m("2A", "SR.5115")["feed_tph"], 1),
                "SR.5115_2C": round(m("2C", "SR.5115")["feed_tph"], 1),
                "SC.A_G": round(m("G", "SC.A")["feed_tph"], 1),
                "SC.B_G": round(m("G", "SC.B")["feed_tph"], 1),
                "SC.B_F": round(m("F", "SC.B")["feed_tph"], 1),
            },
            "zone_1_2_loop_rating": {
                "loop_rating_tph": loop_rating_tph,
                "loop_feed_2C_tph": round(m("2C", "SR.5111")["feed_tph"], 1),
                "load_ratio_2C": round(m("2C", "SR.5111")["feed_tph"] / loop_rating_tph, 3),
                "note": "2C campaigns push the FULL reclaim through the 60 t/h-rated loop (BC.5110/BC.5116 + SR.5111) — 155 % of rating",
            },
            "BC.22": {
                "rating_tph_H": bc22_rating,
                "grits_G_tph": round(grits_G, 2),
                "load_ratio_G": round(grits_G / bc22_rating, 3),
                "note": "mode-G grits flow EXCEEDS the 15 t/h DBR-PFD belt rating [H]",
            },
            "BE.40": {
                "rating_tph_H": be40_rating,
                "fines_F_tph": round(fines_F, 2),
                "load_ratio_F": round(fines_F / be40_rating, 3),
                "fines_G_tph": round(fines_G, 2),
                "load_ratio_G": round(fines_G / be40_rating, 3),
                "note": "mode-F fines flow EXCEEDS the 20 t/h DBR-PFD elevator rating [H]",
            },
        },
        "annual_running_hours_defaults": {
            "zone_1_1_machines_1A_1B": round(
                plan["zone_1_1_split"]["mode_1A_hours_effective"]
                + plan["zone_1_1_split"]["mode_1B_hours_effective"], 1),
            "zone_1_2_loop_machines_2A_2C": round(
                plan["zone_1_2_split"]["dry_season_hours_effective"]
                + plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"], 1),
            "zone_1_2_feedlime_belts_2A_2B": round(
                plan["zone_1_2_split"]["dry_season_hours_effective"]
                + plan["zone_1_2_split"]["rain_season_hours_effective"], 1),
            "zone_1_3_machines_G_F": round(
                plan["zone_1_3_split"]["mode_G_hours_effective"]
                + plan["zone_1_3_split"]["mode_F_hours_effective"], 1),
            "BC.22_G_only": round(plan["zone_1_3_split"]["mode_G_hours_effective"], 1),
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fmeca-engine-evidence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=1, ensure_ascii=True)
        f.write("\n")

    lf = evidence["load_factors"]
    print("FMECA ENGINE EVIDENCE (defaults scenario)")
    print("-" * 78)
    for zone, z in evidence["planning_defaults"]["zones"].items():
        print(f"zone {zone}: {z['required_hours_effective']} h eff, "
              f"utilization {z['utilization_pct']} % of {z['ceiling_hours_clock']} h ceiling")
    zq = evidence["planning_quarry_target"]["zones"]
    print("quarry target utilizations: "
          + " / ".join(f"{zq[z]['utilization_pct']} %" for z in ("1.1", "1.2", "1.3")))
    print("-" * 78)
    print(f"RC.2 mode F: {lf['RC.2']['throughput_F_tph']} t/h of "
          f"{lf['RC.2']['capacity_tph_dry_total']} t/h -> {lf['RC.2']['load_ratio_F']:.0%}")
    print(f"CR.5011 mode 1B: {lf['CR.5011']['throughput_1B_tph_wet']} t/h wet of "
          f"{lf['CR.5011']['capacity_tph_wet']} -> {lf['CR.5011']['load_ratio_1B']:.0%}")
    print(f"CR.5113: {lf['CR.5113']['absorbed_kW_2C']} kW absorbed in 2C vs "
          f"{lf['CR.5113']['absorbed_kW_2A']} kW in 2A (STANDING FINDING)")
    print(f"DY.03 mode G: {lf['DY.03']['outlet_G_tph']} t/h of "
          f"{lf['DY.03']['max_outlet_tph']} -> {lf['DY.03']['load_ratio_G']:.0%} (single point)")
    print(f"Loop 2C: {lf['zone_1_2_loop_rating']['loop_feed_2C_tph']} t/h vs "
          f"{lf['zone_1_2_loop_rating']['loop_rating_tph']} t/h rating -> "
          f"{lf['zone_1_2_loop_rating']['load_ratio_2C']:.0%}")
    print(f"BC.22 mode G: {lf['BC.22']['grits_G_tph']} t/h vs {lf['BC.22']['rating_tph_H']} "
          f"t/h rating [H] -> {lf['BC.22']['load_ratio_G']:.0%}")
    print(f"BE.40 mode F: {lf['BE.40']['fines_F_tph']} t/h vs {lf['BE.40']['rating_tph_H']} "
          f"t/h rating [H] -> {lf['BE.40']['load_ratio_F']:.0%}")
    print(f"\nWritten: {out_path.relative_to(ROOT)}")
    return evidence


if __name__ == "__main__":
    main()
