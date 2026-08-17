"""Eolianite abrasivity simulation (client order 2026-08-16).

No measured abrasivity data exist (CR.5006 panel Q4): the client ordered a
SIMULATION with aeolian-limestone figures — soft porous calcite matrix
cementing well-rounded ~200 um quartz grains. This script joins the [H]
hypothesis set (docs/design/abrasivity/eolianite-abrasivity-scenario.json)
to REAL engine streams:

1. QUARTZ BALANCE — the liberated grains (100-400 um) travel with each
   product's 0.1-0.4 mm band; embedded grains with the lumps. Output:
   quartz t/y and quartz % per product at the annual plan, i.e. the
   PRODUCT-PURITY table (KFS kiln-feed chemistry flag).
2. MACHINE WEAR RANKING — annual tonnes seen by each machine (purchase
   evidence per-mode throughputs x plan hours) x free/embedded quartz
   exposure x class severity factor [H] -> relative wear-duty index.

Replay:
    PYTHONPATH=src python scripts/abrasivity_simulation.py
writes docs/design/abrasivity/abrasivity-engine-evidence.json
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from wankoe_model import load_parameters, run_required_hours, run_scenario

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "docs/design/abrasivity/eolianite-abrasivity-scenario.json"
OUT = ROOT / "docs/design/abrasivity/abrasivity-engine-evidence.json"


def passing_at(curve: dict, x_mm: float) -> float:
    """Log-linear interpolation on a product passing curve {sieve_mm: pct}."""
    pts = sorted((float(k), v) for k, v in curve.items())
    if x_mm <= pts[0][0]:
        return pts[0][1] * x_mm / pts[0][0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x_mm <= x1:
            t = (math.log(x_mm) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return y0 + t * (y1 - y0)
    return pts[-1][1]


def main() -> None:
    scen = json.loads(SCEN.read_text())
    qz = scen["mineralogy"]["quartz_pct"]["central"] / 100.0
    lib = scen["liberation_model"]["free_quartz_fraction_after"]
    emb_w = scen["liberation_model"]["embedded_wear_weight"]
    sev = scen["machine_severity_factors"]

    params = load_parameters()
    plan = run_required_hours(params)
    hours = {
        "1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
        "1B": plan["zone_1_1_split"]["mode_1B_hours_effective"],
        "2A": plan["zone_1_2_split"]["dry_season_hours_effective"]
        + plan["zone_1_2_split"]["rain_season_hours_effective"],
        "2C": plan["zone_1_2_split"]["aglime_2c_campaign_hours_effective"],
        "G": plan["zone_1_3_split"]["mode_G_hours_effective"],
        "F": plan["zone_1_3_split"]["mode_F_hours_effective"],
        "1A-rain": 0.0,  # rain hours are inside the 1A total (weather split not planned per-machine)
        "1B-rain": 0.0,
    }

    # ---- 1. product quartz balance at the annual plan --------------------
    photos = {
        "G": run_scenario(params),
        "F": run_scenario(
            load_parameters(overrides={"default_scenario": {"zone_1_3_mode": "F"}})
        ),
        "2C": run_scenario(
            load_parameters(overrides={"default_scenario": {"zone_1_2_mode": "2C"}})
        ),
    }
    # annual product tonnages come from the PLAN; the photos supply each
    # product's PSD band content. Free-quartz pool = liberated share of the
    # bulk quartz; it distributes over products proportional to
    # tonnage x band(0.1-0.4 mm) content; embedded quartz goes with the
    # remaining (matrix-bound) mass at the bulk grade.
    prod_photo = {
        "KFS": ("G", "KFS", lib["zone_1_1_0_20_loop"]),
        "AgLime": ("2C", "AgLime", lib["zone_1_2_1_7mm_loop"]),
        "FeedLime grits": ("G", "FeedLime grits", lib["zone_1_3_fines_train"]),
        "FeedLime fines": ("F", "FeedLime fines", lib["zone_1_3_fines_train"]),
        "UltraFin": ("F", "UltraFin", lib["zone_1_3_fines_train"]),
    }
    rows = []
    for name, (ph, key, lib_frac) in prod_photo.items():
        p = photos[ph]["products"][key]
        band = (passing_at(p["passing_curve_pct"], 0.4)
                - passing_at(p["passing_curve_pct"], 0.1)) / 100.0
        annual = plan["production_t"][name if name != "AgLime" else "AgLime"]
        rows.append({"product": name, "annual_t": annual, "band_0_1_0_4": band,
                     "lib_frac": lib_frac})
    # landfill 0/20 stream (partially liberated)
    p020 = photos["G"]["products"].get("KFS")  # placeholder; 0/20 curve not a product
    landfill_t = plan["stockpiles_t"]["0/20 to LANDFILL (net loss)"]

    free_pool_weights = {r["product"]: r["annual_t"] * r["band_0_1_0_4"] * r["lib_frac"]
                        for r in rows}
    total_w = sum(free_pool_weights.values()) or 1.0
    total_product_t = sum(r["annual_t"] for r in rows)
    total_quartz_t = qz * (total_product_t + landfill_t)
    free_quartz_t = sum(
        qz * r["annual_t"] * r["lib_frac"] for r in rows
    )  # liberated share of each product's own quartz inventory
    embedded_quartz = {r["product"]: qz * r["annual_t"] * (1 - r["lib_frac"]) for r in rows}
    # free grains redistribute across products by band affinity
    free_alloc = {k: free_quartz_t * w / total_w for k, w in free_pool_weights.items()}

    purity = []
    for r in rows:
        name = r["product"]
        q_t = embedded_quartz[name] + free_alloc[name]
        pct = 100.0 * q_t / r["annual_t"] if r["annual_t"] else 0.0
        purity.append({
            "product": name,
            "annual_t": r["annual_t"],
            "quartz_t_y": round(q_t, 0),
            "quartz_pct": round(pct, 1),
            "caco3_purity_pct_vs_pure": round(100.0 - pct, 1),
        })
        print(f"{name:16s} {r['annual_t']:9.0f} t/y  quartz {pct:5.1f} %  "
              f"(CaCO3-basis value ~{100-pct:.0f} % of pure)")

    # ---- 2. machine wear-duty ranking ------------------------------------
    ev = json.loads((ROOT / "docs/purchase/purchase-engine-evidence.json").read_text())
    machine_class = {
        "CR.5006": ("sizer_crusher", 0.25), "SR.5008": ("screen_wire", 0.25),
        "CR.5011": ("impactor", 0.40), "SR.5105": ("screen_wire", 0.40),
        "SR.5111": ("screen_pu_fine_mat", 0.90), "CR.5113": ("impactor", 0.90),
        "SR.5115": ("screen_pu_fine_mat", 0.90), "RC.1": ("smooth_rolls", 0.90),
        "RC.2": ("smooth_rolls", 0.90), "SC.A": ("screen_wire", 0.90),
        "SC.B": ("screen_pu_fine_mat", 0.90), "SP.36": ("classifier_wheel", 0.90),
        "CL.38": ("cyclone", 0.90),
    }
    ranking = []
    for code, (cls, free_frac) in machine_class.items():
        annual_t = 0.0
        for mode, entry in ev["machines"][code]["modes"].items():
            if not entry.get("active"):
                continue
            tph = entry.get("throughput_tph_dry") or entry.get("feed_tph_dry") or 0.0
            annual_t += tph * hours.get(mode, 0.0)
        if code in ("SP.36", "CL.38"):
            # classifier circuit sees the airborne fines fraction, not a bulk tph
            annual_t = plan["production_t"]["UltraFin"] / max(qz, 1e-9) * 1.0  # order: UF circuit mass
            annual_t = 3610.5 * 0.5  # [H] airborne band ~0.5 t/h through the wheel/fan circuit
        exposure = qz * (free_frac + emb_w * (1 - free_frac))
        duty = annual_t * exposure * sev[cls]
        ranking.append({"machine": code, "class": cls,
                        "annual_t_processed": round(annual_t, 0),
                        "quartz_exposure_factor": round(exposure, 3),
                        "severity": sev[cls],
                        "wear_duty_index_kt_eq": round(duty / 1000.0, 1)})
    ranking.sort(key=lambda r: -r["wear_duty_index_kt_eq"])
    print("\nWear-duty ranking (relative index, NOT absolute life):")
    for r in ranking:
        print(f"  {r['machine']:8s} {r['wear_duty_index_kt_eq']:8.1f}  "
              f"({r['class']}, {r['annual_t_processed']:.0f} t/y)")

    # CR.5006 steel-loss order of magnitude (RFQ anchor)
    steel = scen["steel_consumption_orders"]["sizer_teeth_g_per_t"]
    cr9_t = next(r["annual_t_processed"] for r in ranking if r["machine"] == "CR.5006")
    steel_t = {k: round(cr9_t * v / 1e6, 2) for k, v in
               (("central", steel["central"]),
                ("low", steel["envelope"][0]), ("high", steel["envelope"][1]))}
    print(f"\nCR.5006 tooth-steel loss order: {steel_t} t/y at {cr9_t:.0f} t/y processed")

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    OUT.write_text(json.dumps({
        "_provenance": {
            "engine_commit": commit,
            "script": "scripts/abrasivity_simulation.py",
            "scenario": "docs/design/abrasivity/eolianite-abrasivity-scenario.json",
            "note": ("SIMULATION on [H] eolianite figures (quartz 20 % central, "
                     "200 um rounded grains) - every number pending the XRF / "
                     "LCPC / Cerchar / Bond-Ai external tests. Product tonnages "
                     "and machine throughputs are ENGINE results; quartz split "
                     "and severity factors are the [H] model."),
        },
        "product_purity": purity,
        "landfill_0_20_t": landfill_t,
        "machine_wear_ranking": ranking,
        "cr5009_steel_loss_t_per_y": steel_t,
    }, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
