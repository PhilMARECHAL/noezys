"""ELECTRICITY-ONLY OPEX model — annual kWh by machine / zone / mode + kWh/t.

Client arbitration 2026-08-15 (4 choices, decision-log row of the same date):

1. PERIMETER — process machines + materials handling + dryer ELECTRICAL
   auxiliaries. The dryer BURNER (BU.04) is fuel-fired: excluded from the
   electricity total, its thermal MWh reported separately.
2. POWER BASIS — ABSORBED power. Engine-modeled machines (CR.5009, CR.5011,
   CR.5113, RC.1, RC.2 — ML.26 in the as-built variant only, skipped at the
   c1 default) use the per-mode photo's P_net_kW / eta_m. Non-modeled drives
   use TYPICAL installed ratings [H] x the absorption factor [H]. Every
   rating and the factor live in data/default_parameters.json
   ("electrical_loads" section) — nothing hardcoded here.
3. HOURS — run_required_hours (hours follow the targets) for BOTH scenarios:
   (a) defaults (today's measured feed), (b) quarry target curve
   (docs/design/zone13-redesign/quarry-target-curve-20pct-margin.json) with
   the AgLime baseline 108 kt (135 kt market - 20 % flex margin, client
   2026-08-14). Per-mode hour buckets: zone 1.1 = 1A/1B; zone 1.2 = 2A
   (dry-season) / 2B (rain bypass) / 2C (AgLime campaigns); zone 1.3 = G/F.
   A consumer runs only during the buckets listed in its data "modes" key
   (client 2026-08-15: SR.5105 and the loop machines SR.5111 / CR.5113 /
   SR.5115 run in BOTH 2A and 2C hours).
4. OUTPUT — kWh only, no euros.

ALLOCATION RULE for kWh/t per sold product (documented per client choice 4):
  - Each zone's annual electricity is spread over that zone's OUTPUT mass
    (wet, as-stocked): zone 1.1 -> KFS + 0/20 produced; zone 1.2 -> AgLime +
    FeedLime produced; zone 1.3 -> grits + fines + UltraFin.
  - The chain EMBEDS upstream energy pro rata of the mass actually pulled
    downstream: zone 1.2 total = its direct kWh + (zone-1.1 kWh/t x the
    reclaimed 0/20 tonnage); zone 1.3 total = its direct kWh + (zone-1.2
    kWh/t x the FeedLime tonnage it consumes).
  - Consequence: energy embedded in LANDFILLED 0/20 (and any net-to-stock
    material) is NOT charged to sold products — it is part of the landfill
    net loss, consistent with the client's 2026-08-13 landfill ruling.
  - kWh/t(KFS) = zone-1.1 rate; kWh/t(AgLime) = zone-1.2 chained rate;
    kWh/t(grits) = kWh/t(fines) = kWh/t(UltraFin) = zone-1.3 chained rate.
  - The LINE-LEVEL figure = total electricity kWh / total SOLD tonnes
    (sales_t view: KFS + grits + fines sold + AgLime sold + UltraFin).

CASCADED ZONE-EXIT ELECTRICITY COST ("prix de revient" cascade — client
arbitration 2026-08-15, second round of the same day):

  - MASS allocation (client option 1): within each zone, every OUTGOING
    tonne carries the same kWh/t regardless of product — no product is
    favoured inside a zone.
  - Zone 1.1 exit: kWh/t = zone-1.1 kWh / (KFS + 0/20 produced, wet).
    The SAME rate applies to 1 t of KFS and 1 t of 0/20.
  - Zone 1.2 exit: each inlet 0/20 tonne carries the zone-1.1 rate; the
    zone adds its own kWh spread over its throughput. Zone 1.2 conserves
    wet mass (reclaimed = AgLime + FeedLime produced), so the exit rate =
    zone-1.1 rate + zone-1.2 kWh / reclaimed tonnes — identical for
    AgLime and FeedLime 6/20 (numerically equal to the chained rate12).
  - Zone 1.3 exit: inlet = the 6/20 stockpile cumulative kWh/t (rate12).
    MASS-SHRINK CONVENTION (stated per the client's request): zone 1.3
    shrinks the mass (wet FeedLime -> dry products + vapor + dedusting);
    the evaporated water carries NO energy out — the WHOLE energy (the
    inherited inlet energy AND the zone-1.3 direct kWh) is divided by the
    OUTGOING product tonnes (grits + fines + UltraFin), so each product
    tonne carries the same added kWh/t. Exit rate identical for grits,
    fines and UltraFin (numerically equal to the chained rate13).
  - EUR/t = kWh/t x electricity price. Price = electrical_loads.
    electricity_price_eur_per_mwh = 115 EUR/MWh [H] (Western-Europe
    industrial average 2025, ex-recoverable taxes; to be replaced by the
    client's contract). Data-first — nothing hardcoded here.

Run:  PYTHONPATH=src python scripts/opex_electricity.py
Writes docs/design/opex/electricity-opex.json and prints the full table.
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

QUARRY_CURVE_PATH = (
    ROOT / "docs" / "design" / "zone13-redesign" / "quarry-target-curve-20pct-margin.json"
)
OUT_DIR = ROOT / "docs" / "design" / "opex"
# AgLime baseline of the quarry-works specification (client 2026-08-14:
# 135 kt market minus the 20 % flex margin held open as shock absorber)
QUARRY_AGLIME_BASELINE_T = 108_000

# scenario-photo overrides that realize each mode-hour bucket (weather is
# "dry" for every photo: rain hours (2B) carry no engine-modeled machine —
# the loop is bypassed — so no rain photo is needed)
MODE_PHOTO_OVERRIDES = {
    "1A": {"zone_1_1_mode": "1A"},
    "1B": {"zone_1_1_mode": "1B"},
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


def _mode_hours(plan: dict) -> dict:
    """Effective hours per mode bucket, straight from the planning splits."""
    return {
        "1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
        "1B": plan["zone_1_1_split"]["mode_1B_hours_effective"],
        "2A": plan["zone_1_2_split"]["dry_season_hours_effective"],
        "2B": plan["zone_1_2_split"]["rain_season_hours_effective"],
        "2C": plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"],
        "G": plan["zone_1_3_split"]["mode_G_hours_effective"],
        "F": plan["zone_1_3_split"]["mode_F_hours_effective"],
    }


def compute_scenario(name: str, params: dict) -> dict:
    """Full electricity model for one scenario (planning + per-mode photos)."""
    el = params["electrical_loads"]
    absorption = el["absorption_factor"]["default"]
    eta_m = params["calibration"]["eta_m"]["default"]
    variant = params["default_scenario"].get("zone_1_3_variant", "as-built")

    plan = run_required_hours(params)
    hours = _mode_hours(plan)

    # per-mode photos (only the modes that actually run and are needed)
    photos = {}
    for mode, override in MODE_PHOTO_OVERRIDES.items():
        if hours[mode] <= 0:
            continue
        photos[mode] = run_scenario(
            deep_merge(params, {"default_scenario": {"weather": "dry", **override}})
        )

    machines_out = {}
    per_zone: dict[str, float] = {}
    per_mode: dict[str, float] = {}
    for code, spec in el["consumers"].items():
        req_variant = spec.get("variant")
        if req_variant is not None and req_variant != variant:
            machines_out[code] = {
                "zone": spec["zone"], "basis": spec["basis"], "modes": spec["modes"],
                "skipped": f"variant '{req_variant}' inactive (current: '{variant}')",
                "annual_kWh": 0.0,
            }
            continue
        row = {
            "zone": spec["zone"],
            "basis": spec["basis"],
            "modes": spec["modes"],
            "absorbed_kW_by_mode": {},
            "kWh_by_mode": {},
            "annual_kWh": 0.0,
        }
        if spec["basis"] == "typical_rating":
            row["installed_kW"] = spec["installed_kW"]
            row["status"] = spec["status"]
        total = 0.0
        for mode in spec["modes"]:
            h = hours[mode]
            if h <= 0:
                continue
            if spec["basis"] == "engine":
                info = photos[mode]["machines"][code]
                if not info.get("active") or "P_net_kW" not in info:
                    continue  # machine idle in this mode's photo
                kw = info["P_net_kW"] / eta_m
            else:
                kw = spec["installed_kW"] * absorption
            row["absorbed_kW_by_mode"][mode] = round(kw, 2)
            kwh = kw * h
            row["kWh_by_mode"][mode] = round(kwh, 0)
            total += kwh
            per_mode[mode] = per_mode.get(mode, 0.0) + kwh
        row["annual_kWh"] = round(total, 0)
        machines_out[code] = row
        per_zone[spec["zone"]] = per_zone.get(spec["zone"], 0.0) + total

    total_kwh = sum(per_zone.values())

    # ---- excluded burner fuel (client choice 1): thermal MWh, reported apart
    # + conversion to ILLUMINATING PARAFFIN (kerosene) tonnes and litres
    # (client fuel specification 2026-08-15; LHV and density [H] from data)
    burner = el["dryer_burner"]
    lhv_kwh_per_kg = burner["lhv_kwh_per_kg"]["default"]
    density_kg_per_l = burner["density_kg_per_l"]["default"]
    burner_fuel_mwh = 0.0
    burner_duty_mwh = 0.0
    fuel_by_mode = {}
    for mode in ("G", "F"):
        if hours[mode] <= 0 or mode not in photos:
            continue
        dy = photos[mode]["machines"]["DY.03"]
        mode_mwh = dy["burner_power_kW"] * hours[mode] / 1000.0
        burner_fuel_mwh += mode_mwh
        burner_duty_mwh += dy["thermal_duty_kW"] * hours[mode] / 1000.0
        mode_kg = mode_mwh * 1000.0 / lhv_kwh_per_kg
        fuel_by_mode[mode] = {
            "burner_fuel_MWh": round(mode_mwh, 1),
            "paraffin_t": round(mode_kg / 1000.0, 1),
            "paraffin_L": round(mode_kg / density_kg_per_l, 0),
        }
    fuel_total_kg = burner_fuel_mwh * 1000.0 / lhv_kwh_per_kg
    fuel_total_t = fuel_total_kg / 1000.0
    fuel_total_l = fuel_total_kg / density_kg_per_l

    # ---- kWh/t chain allocation (rule in the module docstring)
    prod = plan["production_t"]
    stocks = plan["stockpiles_t"]
    sales = plan["sales_t"]
    e11_kwh = per_zone.get("1.1", 0.0)
    e12_kwh = per_zone.get("1.2", 0.0)
    e13_kwh = per_zone.get("1.3", 0.0)
    z11_mass = prod["KFS"] + stocks["0/20 produced"]
    rate11 = e11_kwh / z11_mass if z11_mass > 0 else 0.0
    e12_total = e12_kwh + rate11 * stocks["0/20 reclaimed"]
    z12_mass = prod["AgLime"] + stocks["FeedLime produced"]
    rate12 = e12_total / z12_mass if z12_mass > 0 else 0.0
    e13_total = e13_kwh + rate12 * stocks["FeedLime consumed"]
    z13_mass = prod["FeedLime grits"] + prod["FeedLime fines"] + prod["UltraFin"]
    rate13 = e13_total / z13_mass if z13_mass > 0 else 0.0

    sold = {
        "KFS": prod["KFS"],
        "FeedLime grits": prod["FeedLime grits"],
        "FeedLime fines": sales["FeedLime fines sold as fines"],
        "AgLime": sales["AgLime total sold (loop + campaigns + redirect)"],
        "UltraFin": sales["UltraFin sold (market to develop)"],
    }
    kwh_per_t = {
        "KFS": round(rate11, 3),
        "AgLime": round(rate12, 3),
        "FeedLime grits": round(rate13, 3),
        "FeedLime fines": round(rate13, 3),
        "UltraFin": round(rate13, 3),
    }
    total_sold_t = sum(sold.values())
    landfill_embedded_kwh = rate11 * stocks["0/20 to LANDFILL (net loss)"]

    # ---- CASCADED ZONE-EXIT ELECTRICITY COST (client arbitration 2026-08-15:
    # MASS allocation + Western-Europe industrial average price, [H] in data)
    price = el["electricity_price_eur_per_mwh"]["default"]

    def _eur_t(rate_kwh_per_t: float) -> float:
        return rate_kwh_per_t * price / 1000.0

    zone_exit_costs = {
        "method": (
            "MASS allocation (client option 1, 2026-08-15): within each zone "
            "every outgoing tonne carries the same kWh/t regardless of "
            "product. Zone 1.3 mass-shrink convention: the evaporated water "
            "carries no energy — inherited + direct kWh are divided by the "
            "OUTGOING product tonnes."
        ),
        "electricity_price_eur_per_mwh_H": price,
        "zone_exits": {
            "1.1": {
                "products": ["KFS", "0/20 (to stockpile)"],
                "direct_zone_kWh": round(e11_kwh, 0),
                "outgoing_t_wet": round(z11_mass, 0),
                "inherited_kWh_per_t": 0.0,
                "direct_kWh_per_t": round(rate11, 3),
                "cumulative_kWh_per_t": round(rate11, 3),
                "cost_eur_per_t": round(_eur_t(rate11), 3),
            },
            "1.2": {
                "products": ["AgLime", "FeedLime 6/20"],
                "direct_zone_kWh": round(e12_kwh, 0),
                "inlet_t_wet_at_rate_1_1": round(stocks["0/20 reclaimed"], 0),
                "outgoing_t_wet": round(z12_mass, 0),
                "inherited_kWh_per_t": round(rate11 * stocks["0/20 reclaimed"] / z12_mass, 3)
                if z12_mass > 0
                else 0.0,
                "direct_kWh_per_t": round(e12_kwh / z12_mass, 3) if z12_mass > 0 else 0.0,
                "cumulative_kWh_per_t": round(rate12, 3),
                "cost_eur_per_t": round(_eur_t(rate12), 3),
            },
            "1.3": {
                "products": ["FeedLime grits", "FeedLime fines", "UltraFin"],
                "direct_zone_kWh": round(e13_kwh, 0),
                "inlet_t_wet_at_rate_1_2": round(stocks["FeedLime consumed"], 0),
                "outgoing_t_product": round(z13_mass, 0),
                "mass_shrink_note": (
                    "wet FeedLime in, dry products out — the whole energy is "
                    "carried by the outgoing product tonnes (convention)"
                ),
                "inherited_kWh_per_t": round(rate12 * stocks["FeedLime consumed"] / z13_mass, 3)
                if z13_mass > 0
                else 0.0,
                "direct_kWh_per_t": round(e13_kwh / z13_mass, 3) if z13_mass > 0 else 0.0,
                "cumulative_kWh_per_t": round(rate13, 3),
                "cost_eur_per_t": round(_eur_t(rate13), 3),
            },
        },
        "cost_eur_per_t_by_product": {
            "KFS": round(_eur_t(rate11), 3),
            "AgLime": round(_eur_t(rate12), 3),
            "FeedLime grits": round(_eur_t(rate13), 3),
            "FeedLime fines": round(_eur_t(rate13), 3),
            "UltraFin": round(_eur_t(rate13), 3),
        },
        "line_level_eur_per_t_total_sold": round(
            _eur_t(total_kwh / total_sold_t) if total_sold_t > 0 else 0.0, 3
        ),
        "total_electricity_cost_eur_per_year": round(total_kwh / 1000.0 * price, 0),
    }

    return {
        "scenario": name,
        "hours_effective_by_mode": hours,
        "machines": machines_out,
        "annual_kWh_by_zone": {z: round(v, 0) for z, v in sorted(per_zone.items())},
        "annual_kWh_by_mode": {m: round(v, 0) for m, v in per_mode.items()},
        "total_annual_kWh": round(total_kwh, 0),
        "total_annual_MWh": round(total_kwh / 1000.0, 1),
        "kWh_per_t_sold_product": kwh_per_t,
        "sold_t": sold,
        "line_level_kWh_per_t_total_sold": round(total_kwh / total_sold_t, 3),
        "allocation": {
            "zone_1_1_rate_kWh_per_t_output": round(rate11, 3),
            "zone_1_2_chained_rate_kWh_per_t_output": round(rate12, 3),
            "zone_1_3_chained_rate_kWh_per_t_output": round(rate13, 3),
            "kWh_embedded_in_landfilled_0_20_not_charged_to_products": round(
                landfill_embedded_kwh, 0
            ),
        },
        "cascaded_zone_exit_costs": zone_exit_costs,
        "excluded_dryer_burner_fuel": {
            "burner_fuel_MWh_per_year": round(burner_fuel_mwh, 1),
            "thermal_duty_MWh_per_year": round(burner_duty_mwh, 1),
            "note": params["electrical_loads"]["dryer_burner"]["note"],
            "fuel_conversion": {
                "fuel": burner["fuel"],
                "lhv_kwh_per_kg_H": lhv_kwh_per_kg,
                "density_kg_per_l_H": density_kg_per_l,
                "by_dryer_mode": fuel_by_mode,
                "paraffin_t_per_year": round(fuel_total_t, 1),
                "paraffin_L_per_year": round(fuel_total_l, 0),
                "status": "Client fuel specification 2026-08-15: illuminating paraffin (kerosene). LHV 11.97 kWh/kg [H] and density 0.80 kg/L [H] pending the supplier datasheet.",
            },
        },
        "planning_context": {
            "production_t": prod,
            "sales_t": sales,
            "stockpiles_t": stocks,
        },
    }


def main() -> dict:
    # scenario (a): today's measured feed, all defaults
    params_a = load_parameters()

    # scenario (b): quarry target curve + AgLime baseline 108 kt
    with open(QUARRY_CURVE_PATH, encoding="utf-8") as f:
        quarry_curve = json.load(f)["cumulative_passing_curve"]
    aglime_key = next(
        k for k, t in params_a["production_targets"].items() if t["product"] == "AgLime"
    )
    params_b = load_parameters(
        overrides={
            "feed_product": {"cumulative_passing_curve": quarry_curve},
            "production_targets": {
                aglime_key: {"market_cap_t_per_year": QUARRY_AGLIME_BASELINE_T}
            },
        }
    )

    results = {
        "_provenance": {
            "engine_commit": _git_commit(),
            "run_date": date.today().isoformat(),
            "functions": [
                "wankoe_model.planning.run_required_hours",
                "wankoe_model.scenario.run_scenario (per-mode photos)",
            ],
            "data": "data/default_parameters.json (electrical_loads section)",
            "produced_by": "NOEZYS",
        },
        "scenarios": {
            "defaults_todays_feed": compute_scenario("defaults (today's feed)", params_a),
            "quarry_target_20pct_margin": compute_scenario(
                "quarry target curve (AgLime baseline 108 kt)", params_b
            ),
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "electricity-opex.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=True)
        f.write("\n")

    _print_report(results)
    print(f"\nWritten: {out_path.relative_to(ROOT)}")
    return results


def _print_report(results: dict) -> None:
    for scn in results["scenarios"].values():
        print("=" * 100)
        print(f"ELECTRICITY OPEX — {scn['scenario']}")
        print("=" * 100)
        h = scn["hours_effective_by_mode"]
        print(
            "Effective hours  1A %.1f | 1B %.1f | 2A %.1f | 2B %.1f | 2C %.1f | G %.1f | F %.1f"
            % (h["1A"], h["1B"], h["2A"], h["2B"], h["2C"], h["G"], h["F"])
        )
        print(f"\n{'Machine':<26}{'Zone':<6}{'Basis':<20}{'Absorbed kW by mode':<36}{'kWh/y':>12}")
        print("-" * 100)
        for code, row in scn["machines"].items():
            if row.get("skipped"):
                print(f"{code:<26}{row['zone']:<6}{'engine':<20}{'SKIPPED: ' + row['skipped']:<36}")
                continue
            kws = ", ".join(f"{m}:{kw:g}" for m, kw in row["absorbed_kW_by_mode"].items())
            basis = row["basis"] + (" [H]" if row["basis"] == "typical_rating" else "")
            print(f"{code:<26}{row['zone']:<6}{basis:<20}{kws:<36}{row['annual_kWh']:>12,.0f}")
        print("-" * 100)
        for z, v in scn["annual_kWh_by_zone"].items():
            print(f"Zone {z:<10} {v:>14,.0f} kWh/y")
        for m, v in sorted(scn["annual_kWh_by_mode"].items()):
            print(f"Mode {m:<10} {v:>14,.0f} kWh/y")
        print(
            f"TOTAL {scn['total_annual_kWh']:>16,.0f} kWh/y  =  "
            f"{scn['total_annual_MWh']:,.1f} MWh/y"
        )
        print("\nkWh per tonne of sold product (chained mass allocation):")
        for p, v in scn["kWh_per_t_sold_product"].items():
            print(f"  {p:<16} {v:>8.3f} kWh/t   (sold {scn['sold_t'][p]:,.0f} t)")
        print(
            f"  {'LINE-LEVEL':<16} {scn['line_level_kWh_per_t_total_sold']:>8.3f} kWh/t "
            f"of total sold product ({sum(scn['sold_t'].values()):,.0f} t)"
        )
        zc = scn["cascaded_zone_exit_costs"]
        print(
            f"\nCASCADED ZONE-EXIT ELECTRICITY COST (mass allocation, "
            f"{zc['electricity_price_eur_per_mwh_H']} EUR/MWh [H]):"
        )
        for zone, row in zc["zone_exits"].items():
            print(
                f"  zone {zone} exit ({' = '.join(row['products'])}): "
                f"inherited {row['inherited_kWh_per_t']:.3f} + direct "
                f"{row['direct_kWh_per_t']:.3f} = {row['cumulative_kWh_per_t']:.3f} kWh/t "
                f"-> {row['cost_eur_per_t']:.3f} EUR/t"
            )
        print(
            f"  LINE-LEVEL {zc['line_level_eur_per_t_total_sold']:.3f} EUR/t of total "
            f"sold product; total electricity cost "
            f"{zc['total_electricity_cost_eur_per_year']:,.0f} EUR/y"
        )
        bf = scn["excluded_dryer_burner_fuel"]
        print(
            f"\nEXCLUDED (fuel, not electricity): dryer burner "
            f"{bf['burner_fuel_MWh_per_year']:,.1f} MWh/y fuel input "
            f"({bf['thermal_duty_MWh_per_year']:,.1f} MWh/y thermal duty)"
        )
        fc = bf["fuel_conversion"]
        print(
            f"Dryer fuel = {fc['fuel'].upper()} (client 2026-08-15): "
            f"{fc['paraffin_t_per_year']:,.1f} t/y = "
            f"{fc['paraffin_L_per_year']:,.0f} L/y "
            f"(LHV {fc['lhv_kwh_per_kg_H']} kWh/kg [H], "
            f"density {fc['density_kg_per_l_H']} kg/L [H])"
        )
        for mode, row in fc["by_dryer_mode"].items():
            print(
                f"  mode {mode}: {row['burner_fuel_MWh']:,.1f} MWh = "
                f"{row['paraffin_t']:,.1f} t/y = {row['paraffin_L']:,.0f} L/y"
            )
        print()


if __name__ == "__main__":
    main()
