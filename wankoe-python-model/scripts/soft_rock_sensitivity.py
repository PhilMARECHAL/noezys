"""SOFT-ROCK sensitivity study — engine evidence behind
docs/design/soft-rock/soft-rock-study.md (client arbitrations 2026-08-15,
3 choices: rock class UCS 20 MPa [15-30], soft-rock coefficient scenario,
engine sensitivity run vs the current defaults).

Runs the SAME engine as everywhere else (run_scenario per-mode photos +
run_required_hours) for four coefficient cases:

  defaults  — current mid-hard reference set (Wi 12.54, A 60 x b 0.80,
              CR.5009 n 1.35, RC n_comp 1.8 / S_att 0.06, ML.26 0.171)
  soft20    — docs/design/soft-rock/soft-rock-scenario.json (central,
              UCS 20 MPa: Wi 7.5, A 65 x b 1.5, n 1.15, n_comp 1.6,
              S_att 0.09 / ML.26 0.22) — every value [H]
  soft15 / soft30 — the UCS-envelope endpoint variants

and extracts, per case: KFS yield realized/required + envelope, grits D6
margins, fines <1.7 mm redirect eligibility, zone-1.3 fines/grits ratio,
machine loads vs the client-decided capacities (RC.1 32, RC.2 2x22,
CR.5011 90 wet, zone-1.2 loop 60), CR.5113 2C duty, absorbed powers with
the engine-modeled electricity MWh/y (hours x absorbed kW, priced at the
[H] 115 EUR/MWh of the OPEX study), the two-mode annual plan (hours,
utilizations, feasibility, landfill).

QUARRY-TARGET CHECK: replays the 40.1 % < 20 mm quarry works spec
(homothetic rescale of the measured curve, AgLime baseline 108 kt) under
the soft-rock coefficients, and re-bisects the rescale k for zero
landfill — the soft-rock replacement of the 40.1 % control value.

Run:  PYTHONPATH=src python scripts/soft_rock_sensitivity.py
Writes docs/design/soft-rock/soft-rock-engine-evidence.json.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wankoe_model.paths import deep_merge  # noqa: E402
from wankoe_model.planning import run_required_hours  # noqa: E402
from wankoe_model.scenario import (  # noqa: E402
    interp_curve,
    load_parameters,
    run_scenario,
)

OUT_DIR = ROOT / "docs" / "design" / "soft-rock"
QUARRY_CURVE_PATH = (
    ROOT / "docs" / "design" / "zone13-redesign" / "quarry-target-curve-20pct-margin.json"
)
QUARRY_AGLIME_BASELINE_T = 108_000  # client 2026-08-14: 135 kt - 20 % flex
ELECTRICITY_EUR_PER_MWH = 115.0  # [H] OPEX study 2026-08-15 (data-first there)

MODE_PHOTO_OVERRIDES = {
    "G": {"zone_1_3_mode": "G"},   # also the 1A / 2A photo
    "F": {"zone_1_3_mode": "F"},
    "1B": {"zone_1_1_mode": "1B"},  # forced photo: 1B never runs at defaults
    "2C": {"zone_1_2_mode": "2C"},
}


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover — provenance best effort
        return "unknown"


def _load_overrides(name: str) -> dict:
    with open(OUT_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def compute_case(label: str, overrides: dict | None) -> dict:
    params = load_parameters(overrides=overrides)
    eta_m = params["calibration"]["eta_m"]["default"]
    photos = {
        mode: run_scenario(
            deep_merge(params, {"default_scenario": {"weather": "dry", **ov}})
        )
        for mode, ov in MODE_PHOTO_OVERRIDES.items()
    }
    plan = run_required_hours(params)
    pg, pf = photos["G"], photos["F"]

    # wet/dry conversion at the zone-1.1 boundary (total-flow rule)
    wet_ratio_11 = 250.0 / pg["machines"]["CR.5009"]["throughput_tph"]
    wet_ratio_1b = 186.1 / photos["1B"]["machines"]["CR.5009"]["throughput_tph"]

    kfs = pg["products"]["KFS"]
    grits = pg["products"]["FeedLime grits"]
    fines_g = pg["products"]["FeedLime fines"]
    fines_f = pf["products"]["FeedLime fines"]

    def _abs(photo, code):
        return photo["machines"][code]["P_net_kW"] / eta_m

    # engine-modeled electricity (same method as the OPEX study: absorbed
    # kW per mode photo x the planning's effective mode hours)
    h = {
        "1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
        "1B": plan["zone_1_1_split"]["mode_1B_hours_effective"],
        "2A": plan["zone_1_2_split"]["dry_season_hours_effective"],
        "2C": plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"],
        "G": plan["zone_1_3_split"]["mode_G_hours_effective"],
        "F": plan["zone_1_3_split"]["mode_F_hours_effective"],
    }
    modeled_mwh = {
        "CR.5009": (_abs(pg, "CR.5009") * h["1A"]
                    + _abs(photos["1B"], "CR.5009") * h["1B"]) / 1000.0,
        "CR.5011": (_abs(pg, "CR.5011") * h["1A"]
                    + _abs(photos["1B"], "CR.5011") * h["1B"]) / 1000.0,
        "CR.5113": (_abs(pg, "CR.5113") * h["2A"]
                    + _abs(photos["2C"], "CR.5113") * h["2C"]) / 1000.0,
        "RC.1": (_abs(pg, "RC.1") * h["G"] + _abs(pf, "RC.1") * h["F"]) / 1000.0,
        "RC.2": (_abs(pg, "RC.2") * h["G"] + _abs(pf, "RC.2") * h["F"]) / 1000.0,
    }
    modeled_total_mwh = sum(modeled_mwh.values())

    result = {
        "label": label,
        "kfs": {
            "tph_wet": kfs["tph"],
            "yield_realized_pct": plan["kfs_yield"]["realized_pct"],
            "yield_required_pct": plan["kfs_yield"]["required_for_zero_landfill_pct"],
            "psd_pct": plan["kfs_yield"]["kfs_real_psd_pct"],
            "envelope": kfs["compliance"]["envelope"],
            "envelope_compliant": kfs["compliance"]["compliant"],
        },
        "grits_D6": {
            "tph_dry_mode_G": grits["tph"],
            "below_2mm_pct": grits["compliance"]["below_cut_pct"],
            "above_4mm_pct": grits["compliance"]["above_cut_pct"],
            "margin_below_pt": round(15.0 - grits["compliance"]["below_cut_pct"], 2),
            "margin_above_pt": round(5.0 - grits["compliance"]["above_cut_pct"], 2),
            "compliant": grits["compliance"]["compliant"],
        },
        "fines": {
            "tph_mode_G": fines_g["tph"],
            "tph_mode_F": fines_f["tph"],
            "passing_1p7_mode_G_pct": round(
                100.0 * interp_curve(fines_g["passing_curve_pct"], 1.7), 2),
            "passing_1p7_mode_F_pct": round(
                100.0 * interp_curve(fines_f["passing_curve_pct"], 1.7), 2),
            "redirect_eligible_G": bool(
                100.0 * interp_curve(fines_g["passing_curve_pct"], 1.7) >= 95.0),
            "redirect_eligible_F": bool(
                100.0 * interp_curve(fines_f["passing_curve_pct"], 1.7) >= 95.0),
        },
        "zone_1_3": {
            "fines_over_grits_ratio_mode_G": round(grits["tph"] and fines_g["tph"] / grits["tph"], 3),
            "recirculation_tph_G": pg["intermediate_flows"]["zone_1_3_recirculation_tph"],
            "recirculation_tph_F": pf["intermediate_flows"]["zone_1_3_recirculation_tph"],
        },
        "machine_loads": {
            "RC.1_mode_G_tph_dry": round(pg["machines"]["RC.1"]["throughput_tph"], 2),
            "RC.1_capacity_tph": 32,
            "RC.2_mode_F_tph_dry_total": round(pf["machines"]["RC.2"]["throughput_tph"], 2),
            "RC.2_capacity_tph_total": 44,
            "CR.5011_mode_1A_tph_wet": round(
                pg["machines"]["CR.5011"]["throughput_tph"] * wet_ratio_11, 2),
            "CR.5011_forced_1B_tph_wet": round(
                photos["1B"]["machines"]["CR.5011"]["throughput_tph"] * wet_ratio_1b, 2),
            "CR.5011_capacity_tph_wet": 90,
            "SR.5111_loop_feed_2C_tph_dry": round(
                photos["2C"]["machines"]["SR.5111"]["feed_tph"], 2),
            "zone_1_2_loop_rating_tph": 60,
        },
        "absorbed_kW": {
            "CR.5009_1A": round(_abs(pg, "CR.5009"), 1),
            "CR.5011_1A": round(_abs(pg, "CR.5011"), 1),
            "CR.5011_1B": round(_abs(photos["1B"], "CR.5011"), 1),
            "CR.5113_2A": round(_abs(pg, "CR.5113"), 1),
            "CR.5113_2C": round(_abs(photos["2C"], "CR.5113"), 1),
            "RC.1_G": round(_abs(pg, "RC.1"), 1),
            "RC.2_F_total": round(_abs(pf, "RC.2"), 1),
        },
        "plan": {
            "zones": {
                z: {
                    "required_hours_clock": v["required_hours_clock"],
                    "utilization_pct": v["utilization_pct"],
                    "feasible": v["feasible"],
                }
                for z, v in plan["zones"].items()
            },
            "zone_1_1_split_eff_h": plan["zone_1_1_split"],
            "zone_1_3_split_eff_h": plan["zone_1_3_split"],
            "zone_1_2_split_eff_h": plan["zone_1_2_split"],
            "production_t": plan["production_t"],
            "landfill_t_per_y": plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"],
        },
        "electricity_modeled_drives": {
            "per_machine_MWh_per_y": {k: round(v, 1) for k, v in modeled_mwh.items()},
            "total_MWh_per_y": round(modeled_total_mwh, 1),
            "cost_kEUR_per_y_at_115": round(
                modeled_total_mwh * ELECTRICITY_EUR_PER_MWH / 1000.0, 1),
            "_note": "engine-modeled drives only (CR.5009/CR.5011/CR.5113/"
            "RC.1/RC.2), same absorbed-power x mode-hours method as the "
            "2026-08-15 OPEX study; non-modeled drives keep their typical "
            "ratings and move only through the hour changes",
        },
    }
    return result


# ---------------------------------------------------------------- quarry
def _measured_points(params: dict) -> list:
    curve = params["feed_product"]["cumulative_passing_curve"]
    if not curve:  # defaults keep the curve empty -> calibrated reference
        with open(ROOT / "data" / "reference_feed_curve.json", encoding="utf-8") as f:
            curve = json.load(f)["cumulative_passing_curve"]
    return sorted((float(k), float(v)) for k, v in curve.items())


def _interp_pts(pts: list, x: float) -> float:
    if x <= pts[0][0]:
        return pts[0][1] * x / pts[0][0]
    if x >= pts[-1][0]:
        return 100.0
    for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
        if x <= x1:
            t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return p0 + t * (p1 - p0)
    return 100.0


def _scaled_curve(pts: list, k: float) -> dict:
    curve = {str(x): round(_interp_pts(pts, x / k), 4) for x, _ in pts}
    curve[str(pts[-1][0])] = 100.0
    return curve


def quarry_case(label: str, soft_overrides: dict | None, curve: dict,
                aglime_cap: int = QUARRY_AGLIME_BASELINE_T) -> dict:
    base = load_parameters()
    aglime_key = next(
        k for k, t in base["production_targets"].items() if t["product"] == "AgLime"
    )
    ov: dict = {
        "feed_product": {"cumulative_passing_curve": curve},
        "production_targets": {aglime_key: {"market_cap_t_per_year": aglime_cap}},
    }
    if soft_overrides:
        ov = deep_merge(soft_overrides, ov)
    plan = run_required_hours(load_parameters(overrides=ov))
    return {
        "label": label,
        "p20_inlet_pct": round(float(curve["20.0"]), 2),
        "landfill_t_per_y": plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"],
        "kfs_yield_realized_pct": plan["kfs_yield"]["realized_pct"],
        "kfs_yield_required_pct": plan["kfs_yield"]["required_for_zero_landfill_pct"],
        "utilizations_pct": [v["utilization_pct"] for v in plan["zones"].values()],
        "feasible": all(v["feasible"] for v in plan["zones"].values()),
    }


def bisect_zero_landfill(soft_overrides: dict | None, pts: list,
                         lo: float = 1.0, hi: float = 2.6) -> dict:
    """Smallest homothetic rescale k of the measured curve with ~zero
    landfill at the AgLime 108 kt baseline (the quarry-spec construction)."""
    def landfill(k: float) -> float:
        case = quarry_case(f"k={k:.4f}", soft_overrides, _scaled_curve(pts, k))
        return case["landfill_t_per_y"]

    if landfill(hi) > 1.0:
        raise ValueError("bisection bracket too small (landfill > 0 at hi)")
    for _ in range(30):
        mid = (lo + hi) / 2.0
        if landfill(mid) > 1.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 5e-4:
            break
    k = hi
    curve = _scaled_curve(pts, k)
    case = quarry_case(f"zero-landfill k={k:.4f}", soft_overrides, curve)
    case["rescale_k"] = round(k, 4)
    return case


def main() -> dict:
    cases = {
        "defaults": compute_case("defaults (mid-hard reference set)", None),
        "soft20": compute_case(
            "soft-rock central UCS 20", _load_overrides("soft-rock-scenario.json")),
        "soft15": compute_case(
            "soft-rock envelope UCS 15", _load_overrides("soft-rock-scenario-soft15.json")),
        "soft30": compute_case(
            "soft-rock envelope UCS 30", _load_overrides("soft-rock-scenario-soft30.json")),
    }

    with open(QUARRY_CURVE_PATH, encoding="utf-8") as f:
        quarry_curve = json.load(f)["cumulative_passing_curve"]
    pts = _measured_points(load_parameters())
    soft20 = _load_overrides("soft-rock-scenario.json")
    quarry = {
        "defaults_quarry_401": quarry_case(
            "defaults + quarry 40.1 % curve + AgLime 108 kt", None, quarry_curve),
        "soft20_quarry_401": quarry_case(
            "soft20 + quarry 40.1 % curve + AgLime 108 kt", soft20, quarry_curve),
        "soft20_zero_landfill_rebisect": bisect_zero_landfill(soft20, pts),
    }

    out = {
        "_provenance": {
            "engine_commit": _git_commit(),
            "run_date": date.today().isoformat(),
            "functions": [
                "wankoe_model.scenario.run_scenario (per-mode photos G/F/forced 1B/2C, weather dry)",
                "wankoe_model.planning.run_required_hours",
            ],
            "data": "data/default_parameters.json + docs/design/soft-rock/soft-rock-scenario*.json",
            "produced_by": "NOEZYS",
            "replay": "PYTHONPATH=src python scripts/soft_rock_sensitivity.py",
        },
        "cases": cases,
        "quarry_target_check": quarry,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "soft-rock-engine-evidence.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path.relative_to(ROOT)}")

    for name, c in cases.items():
        print(f"--- {name}: yield {c['kfs']['yield_realized_pct']}/"
              f"{c['kfs']['yield_required_pct']} | landfill {c['plan']['landfill_t_per_y']:.0f} "
              f"| D6 below {c['grits_D6']['below_2mm_pct']} | RC.1 {c['machine_loads']['RC.1_mode_G_tph_dry']} "
              f"| RC.2F {c['machine_loads']['RC.2_mode_F_tph_dry_total']} "
              f"| CR.5113 2C {c['absorbed_kW']['CR.5113_2C']} kW "
              f"| elec {c['electricity_modeled_drives']['total_MWh_per_y']} MWh")
    for name, q in quarry.items():
        print(f"--- {name}: <20mm {q['p20_inlet_pct']} % | landfill {q['landfill_t_per_y']:.0f} "
              f"| yield {q['kfs_yield_realized_pct']}/{q['kfs_yield_required_pct']} "
              f"| feasible {q['feasible']}")
    return out


if __name__ == "__main__":
    main()
