"""Purchase-datasheet engine evidence — the fresh engine runs behind the
13 purchase technical datasheets of docs/purchase/ (client order
2026-08-15; dryer DY.03 excluded, already acquired).

Traceability rule (client, 2026-08-11): every datasheet figure must be
replayable without the assistant. This script re-runs the per-mode
scenario photos (1A / forced 1B / 2A / 2C / G / F) on the same engine
used everywhere else and extracts, for each of the 13 machines:

- process duty per relevant mode: feed/throughput (dry + wet where the
  total-flow rule applies), F80/P80, absorbed power P_net/eta_m,
  required screen areas per deck;
- the WORST-mode screen area per deck + the stated purchase sizing
  margin (+25 % design allowance [H], pending vendor bed-depth/V-factor
  verification);
- the data-first capacity ratings the client has already decided
  (RC.1 32 t/h; RC.2 2 x 22 t/h; CR.5011 90 t/h wet vendor basis;
  zone-1.2 loop rating 60 t/h) and the engine load ratios against them;
- a recommended minimum installed motor rating = worst-mode absorbed
  x 1.15 service allowance [H], rounded UP to the next standard IEC
  rating (vendor to confirm from its own drive selection).

Run:  PYTHONPATH=src python scripts/purchase_datasheet_evidence.py
Writes docs/purchase/purchase-engine-evidence.json and prints a summary.
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
from wankoe_model.scenario import load_parameters, run_scenario  # noqa: E402

OUT_DIR = ROOT / "docs" / "purchase"

MODE_PHOTO_OVERRIDES = {
    "1A": {"zone_1_1_mode": "1A"},
    "1B": {"zone_1_1_mode": "1B"},  # forced photo: 1B never runs at defaults
    "2A": {"zone_1_2_mode": "2A"},
    "2C": {"zone_1_2_mode": "2C"},
    "G": {"zone_1_3_mode": "G"},
    "F": {"zone_1_3_mode": "F"},
    # Error-hunt PD-2 (client 2026-08-15): rain is a NORMAL circumstance for
    # zone 1.1 (the line continues through rain weeks) — the SR.5008 sizing
    # must see the rain photos (wet_capacity_factor derating)
    "1A-rain": {"zone_1_1_mode": "1A", "weather": "rain"},
    "1B-rain": {"zone_1_1_mode": "1B", "weather": "rain"},
}

MACHINE_MODES = {
    "CR.5006": ["1A", "1B"],
    "SR.5008": ["1A", "1B", "1A-rain", "1B-rain"],
    "CR.5011": ["1A", "1B"],
    "SR.5105": ["2A"],  # inactive in 2C (full reclaim to the loop)
    "SR.5111": ["2A", "2C"],
    "CR.5113": ["2A", "2C"],
    "SR.5115": ["2A", "2C"],
    "RC.1": ["G", "F"],
    "RC.2": ["G", "F"],
    "SC.A": ["G", "F"],
    "SC.B": ["G", "F"],
    "SP.36": ["G", "F"],
    "CL.38": ["G", "F"],
}

AREA_MARGIN = 1.25  # [H] +25 % purchase sizing allowance on the worst mode
MOTOR_SERVICE = 1.15  # [H] service allowance on the worst-mode absorbed kW
IEC_RATINGS_KW = [
    11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200,
    250, 315, 355, 400, 450, 500,
]


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:  # pragma: no cover — provenance best effort
        return "unknown"


def _iec_up(kw: float) -> float:
    for r in IEC_RATINGS_KW:
        if r >= kw:
            return r
    return round(kw, 0)


def _val(node):
    return node["default"] if isinstance(node, dict) else node


def main() -> dict:
    params = load_parameters()
    eta_m = params["calibration"]["eta_m"]["default"]

    photos = {
        mode: run_scenario(
            deep_merge(params, {"default_scenario": {"weather": "dry", **override}})
        )
        for mode, override in MODE_PHOTO_OVERRIDES.items()
    }

    # total-flow rule wet/dry ratios (moisture at each zone boundary)
    feed_1a_dry = photos["1A"]["machines"]["CR.5006"]["throughput_tph"]
    wet_over_dry_11 = 250.0 / feed_1a_dry  # 250 t/h wet pivot feed
    reclaim_dry = photos["2A"]["machines"]["SR.5105"]["feed_tph"]
    wet_over_dry_12 = 100.0 / reclaim_dry  # 100 t/h wet reclaim

    wet_ratio = {"1A": wet_over_dry_11, "1B": wet_over_dry_11,
                 "1A-rain": wet_over_dry_11, "1B-rain": wet_over_dry_11,
                 "2A": wet_over_dry_12, "2C": wet_over_dry_12,
                 "G": 1.0, "F": 1.0}  # zone 1.3 dry basis (0.5 % out-moisture)

    evidence: dict = {}
    for code, modes in MACHINE_MODES.items():
        per_mode = {}
        for mode in modes:
            sheet = photos[mode]["machines"].get(code, {})
            if not sheet.get("active", False):
                per_mode[mode] = {"active": False}
                continue
            entry: dict = {"active": True}
            if "throughput_tph" in sheet:  # crushers / dryer class
                entry["throughput_tph_dry"] = round(sheet["throughput_tph"], 2)
                entry["throughput_tph_wet"] = round(
                    sheet["throughput_tph"] * wet_ratio[mode], 2)
            if "feed_tph" in sheet:  # screens
                entry["feed_tph_dry"] = round(sheet["feed_tph"], 2)
                entry["feed_tph_wet"] = round(sheet["feed_tph"] * wet_ratio[mode], 2)
            for k in ("F80_mm", "P80_mm"):
                if k in sheet:
                    entry[k] = round(sheet[k], 2)
            if "P_net_kW" in sheet:
                entry["P_net_kW"] = round(sheet["P_net_kW"], 1)
                entry["absorbed_kW"] = round(sheet["P_net_kW"] / eta_m, 1)
            if "areas_m2" in sheet:
                entry["required_areas_m2"] = {
                    deck: round(v["required_area_m2"], 2)
                    for deck, v in sheet["areas_m2"].items()
                }
            for k in ("units_in_service", "Q_air_m3h", "Phi_cut", "certified",
                      "d50_um", "W_kWh_t", "Ecs_kWh_t", "t10_pct",
                      "imperfection_used"):
                if k in sheet:
                    entry[k] = (round(sheet[k], 4)
                                if isinstance(sheet[k], float) else sheet[k])
            per_mode[mode] = entry

        block: dict = {"modes": per_mode}

        # worst-mode screen areas + purchase margin
        decks: dict = {}
        for mode, entry in per_mode.items():
            for deck, a in entry.get("required_areas_m2", {}).items():
                # >= : on equal areas the higher-feed (later) mode governs
                if deck not in decks or a >= decks[deck][1]:
                    decks[deck] = (mode, a)
        if decks:
            block["purchase_area_m2"] = {
                deck: {
                    "worst_mode": mode,
                    "required_m2": a,
                    "with_margin_m2": round(a * AREA_MARGIN, 2),
                }
                for deck, (mode, a) in decks.items()
            }
            block["area_margin"] = f"+{round((AREA_MARGIN - 1) * 100)} % [H]"
            # client-decided purchase minima override (data-first), e.g.
            # SR.5008 PD-2 2026-08-15: minima = the rain duty, no stacked margin
            decided = params["machines"].get(code, {}).get("purchase_min_area_m2")
            if decided:
                block["client_decided_min_area_m2"] = decided
                for deck, floor in decided.items():
                    worst = decks.get(deck)
                    if worst and worst[1] > floor:
                        raise SystemExit(
                            f"{code} {deck}: engine worst {worst[1]} m2 exceeds "
                            f"the client-decided minimum {floor} m2 — re-arbitrate"
                        )

        # recommended minimum installed motor rating (engine-modeled drives)
        absorbed = [e["absorbed_kW"] for e in per_mode.values()
                    if "absorbed_kW" in e]
        if absorbed:
            worst = max(absorbed)
            units = max((e.get("units_in_service", 1)
                         for e in per_mode.values()), default=1)
            block["motor_sizing"] = {
                "worst_mode_absorbed_kW": worst,
                "service_allowance": f"x{MOTOR_SERVICE} [H]",
                "recommended_min_installed_kW": _iec_up(worst * MOTOR_SERVICE),
            }
            if units > 1:  # RC.2: engine power is the TOTAL over both units
                per_unit = worst / units
                block["motor_sizing"]["per_unit_absorbed_kW"] = round(per_unit, 1)
                block["motor_sizing"]["recommended_min_installed_kW_per_unit"] = (
                    _iec_up(per_unit * MOTOR_SERVICE))
        evidence[code] = block

    mach = params["machines"]
    ratings = {
        "CR.5011_max_capacity_tph_wet": _val(mach["CR.5011"]["max_capacity_tph"]),
        "CR.5011_installed_kW_vendor": _val(mach["CR.5011"]["installed_power_kW"]),
        "CR.5011_mode_1B_x80_mm": _val(mach["CR.5011"]["mode_1B_x80_mm"]),
        "RC.1_max_capacity_tph_dry": _val(mach["RC.1"]["max_capacity_tph"]),
        "RC.2_max_capacity_tph_dry_per_unit": _val(mach["RC.2"]["max_capacity_tph"]),
        "RC.2_n_units": _val(mach["RC.2"]["n_units"]),
        "RC.2_mode_F_gap_mm": _val(mach["RC.2"]["mode_F_gap_mm"]),
        "zone_1_2_loop_rating_tph": _val(mach["SR.5111"]["loop_rating_tph"]),
        "CR.5006_max_feed_size_mm": _val(mach["CR.5006"]["max_feed_size_mm"]),
    }
    # Error-hunt fix 2026-08-15: the loop ratio must be WET basis, like the
    # engine's own alert (100 t/h wet vs 60) and the client total-flow rule
    # — the dry basis understated the 2C overload as 155 % instead of 167 %
    ratings["SR.5111_loop_load_ratio_2C"] = round(
        evidence["SR.5111"]["modes"]["2C"]["feed_tph_wet"]
        / ratings["zone_1_2_loop_rating_tph"], 3)
    ratings["CR.5011_load_ratio_1A_wet"] = round(
        evidence["CR.5011"]["modes"]["1A"]["throughput_tph_wet"]
        / ratings["CR.5011_max_capacity_tph_wet"], 3)
    ratings["CR.5011_load_ratio_1B_wet"] = round(
        evidence["CR.5011"]["modes"]["1B"]["throughput_tph_wet"]
        / ratings["CR.5011_max_capacity_tph_wet"], 3)
    ratings["RC.1_load_ratio_G"] = round(
        evidence["RC.1"]["modes"]["G"]["throughput_tph_dry"]
        / ratings["RC.1_max_capacity_tph_dry"], 3)
    ratings["RC.2_load_ratio_F"] = round(
        evidence["RC.2"]["modes"]["F"]["throughput_tph_dry"]
        / (ratings["RC.2_max_capacity_tph_dry_per_unit"]
           * ratings["RC.2_n_units"]), 3)

    out = {
        "_provenance": {
            "engine_commit": _git_commit(),
            "run_date": str(date.today()),
            "functions": [
                "wankoe_model.scenario.run_scenario "
                "(per-mode photos 1A / forced 1B / 2A / 2C / G / F, weather dry)"
            ],
            "data": "data/default_parameters.json",
            "eta_m": eta_m,
            "produced_by": "NOEZYS",
            "replay": "PYTHONPATH=src python scripts/purchase_datasheet_evidence.py",
        },
        "conventions": {
            "total_flow_rule": "wet basis primary (client 2026-08-14): zone-1.1 "
            "wet = dry x " + f"{wet_over_dry_11:.5f}" + " (250 t/h wet pivot feed), "
            "zone-1.2 wet = dry x " + f"{wet_over_dry_12:.5f}" + " (100 t/h wet "
            "reclaim); zone 1.3 quoted dry (post-dryer, 0.5 % moisture)",
            "absorbed_kW": "P_net / eta_m (motor input)",
            "screen_area_margin": f"purchase area = worst-mode required area x "
            f"{AREA_MARGIN} ([H] +25 % design allowance, vendor to verify by "
            "bed-depth / V-factor method)",
            "motor_sizing": f"recommended min installed = worst-mode absorbed x "
            f"{MOTOR_SERVICE} [H], rounded up to standard IEC rating "
            "(vendor to confirm)",
        },
        "client_decided_ratings": ratings,
        "machines": evidence,
        "alerts_1A": photos["1A"]["alerts"],
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "purchase-engine-evidence.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {path.relative_to(ROOT)}")
    for code, block in evidence.items():
        line = code + ":"
        for mode, e in block["modes"].items():
            if not e.get("active"):
                line += f" {mode}=inactive"
                continue
            tph = e.get("throughput_tph_dry", e.get("feed_tph_dry", "-"))
            kw = e.get("absorbed_kW", "-")
            line += f" {mode}={tph} t/h dry, {kw} kW abs;"
        print(line)
    return out


if __name__ == "__main__":
    main()
