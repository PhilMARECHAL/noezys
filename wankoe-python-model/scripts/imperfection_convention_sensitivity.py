"""Q3 sensitivity — screen imperfection CONVENTION (client option 1, 2026-08-17).

The implemented M3 sharpness is s = ln9 / ln(1/(1-I)): at I = 0.15 the
partition realizes a CLASSIC imperfection (d75-d25)/(2 d50) of only
~0.081 — screens ~2x sharper than the classic-0.15 literature value that
justified the default (client Q1, 2026-08-10). The CLASSIC convention
would be s = ln3 / asinh(I) = 7.35 at I = 0.15.

This script replays the ruled reference points with the classic-0.15
sharpness and reports what HOLDS and what BREAKS, so the client can
ratify Q3 with the consequences on the table. Implementation: the
engine is untouched — the classic sharpness is reproduced through the
existing formula by the EQUIVALENT parameter
    I_eq = 1 - exp(-ln9 / s_classic) = 0.2584
applied to every dry screen imperfection (calibration I_dry + the
per-screen I parameters of SR.5008 / SR.5111 / SR.5115). Rain values
(I_rain physics) are untouched; weather is dry at the reference photos.

Replay:
    PYTHONPATH=src python scripts/imperfection_convention_sensitivity.py
writes docs/design/error-hunt/imperfection-convention-sensitivity.json
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from wankoe_model import load_parameters, run_scenario, run_design_check
from wankoe_model.planning import run_required_hours

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "design" / "error-hunt" / "imperfection-convention-sensitivity.json"

I_NOMINAL = 0.15
S_IMPLEMENTED = math.log(9) / math.log(1 / (1 - I_NOMINAL))          # 13.52
S_CLASSIC = math.log(3) / math.asinh(I_NOMINAL)                      # 7.35
I_EQ = 1 - math.exp(-math.log(9) / S_CLASSIC)                        # 0.2584
CLASSIC_REALIZED_TODAY = math.sinh(math.log(1 / (1 - I_NOMINAL)) / 2)  # ~0.081


def classic_overrides() -> dict:
    i = round(I_EQ, 4)
    return {
        "calibration": {"I_dry": {"default": i}},
        "machines": {
            code: {"parameters": {"I": {"default": i}}}
            for code in ("SR.5008", "SR.5111", "SR.5115")
        },
    }


def psd_pct(product: dict, mesh: float) -> float | None:
    curve = product.get("cumulative_passing_pct") or {}
    key = str(mesh)
    if key in curve:
        return curve[key]
    try:
        return 100.0 * product["psd"].passing_at(mesh)
    except Exception:
        return None


def gates(scenario_overrides: dict | None, label: str) -> dict:
    """Run the reference photos and extract every quality gate."""
    ov = scenario_overrides or {}
    r = run_scenario(load_parameters(overrides=ov))
    plan = run_required_hours(load_parameters(overrides=ov))
    design = run_design_check(load_parameters(overrides=ov))

    products = r["products"]

    def compliance(name):
        c = (products.get(name) or {}).get("compliance") or {}
        return {k: c.get(k) for k in ("below_cut_pct", "in_cut_pct", "above_cut_pct", "compliant")}

    quality_by_product = {q["product"]: q for q in design.get("quality", [])}

    ky = plan["kfs_yield"]
    out = {
        "label": label,
        "kfs_envelope": {
            "below_20_pct": ky["kfs_real_psd_pct"]["below_20"],
            "in_cut_pct": ky["kfs_real_psd_pct"]["in_cut_20_35"],
            "above_35_pct": ky["kfs_real_psd_pct"]["above_35"],
            "spec": "max 30 / min 55 / max 15",
            "compliant": (
                ky["kfs_real_psd_pct"]["below_20"] <= 30
                and ky["kfs_real_psd_pct"]["in_cut_20_35"] >= 55
                and ky["kfs_real_psd_pct"]["above_35"] <= 15
            ),
        },
        "grits_d6": {**compliance("FeedLime grits"), "spec": "<2 mm <= 15 % ; >4 mm <= 5 %"},
        "fines_0_1_5": compliance("FeedLime fines"),
        "aglime": compliance("AgLime"),
        "design_quality_noncompliant": sorted(
            p for p, q in quality_by_product.items() if not q.get("compliant", True)
        ),
        "kfs_yield": {
            "realized_pct": ky["realized_pct"],
            "required_pct": ky["required_for_zero_landfill_pct"],
        },
        "landfill_t": plan["stockpiles_t"].get("0/20 to LANDFILL (net loss)", 0.0),
        "production_t": {k: round(v) for k, v in plan["production_t"].items()},
        "zone_hours": {
            "z11_1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
            "z13_G": plan["zone_1_3_split"]["mode_G_hours_effective"],
            "z13_F": plan["zone_1_3_split"]["mode_F_hours_effective"],
        },
        "design_verdicts": design["verdicts"],
        "sr5008_required_areas_m2": {
            k: round(v["required_area_m2"], 2)
            for k, v in r["machines"]["SR.5008"]["areas_m2"].items()
        },
        "alerts_count": len(r["alerts"]),
        "alerts_new_or_notable": r["alerts"][:12],
    }
    return out


def main() -> None:
    print(
        f"Derivation: s_implemented = ln9/ln(1/(1-0.15)) = {S_IMPLEMENTED:.2f} ; "
        f"classic realized today = sinh(ln(1/0.85)/2) = {CLASSIC_REALIZED_TODAY:.3f} ; "
        f"s_classic = ln3/asinh(0.15) = {S_CLASSIC:.2f} ; equivalent I_eq = {I_EQ:.4f}"
    )
    base = gates(None, "baseline (implemented convention, I=0.15, s=13.52)")
    classic = gates(
        classic_overrides(), "classic convention (realized classic I=0.15, s=7.35, via I_eq=0.2584)"
    )

    comparison = []
    for gate, fmt in (
        ("kfs_envelope", None),
        ("grits_d6", None),
        ("fines_0_1_5", None),
        ("aglime", None),
        ("design_quality_noncompliant", None),
        ("kfs_yield", None),
        ("landfill_t", None),
        ("design_verdicts", None),
        ("sr5008_required_areas_m2", None),
    ):
        comparison.append({"gate": gate, "baseline": base[gate], "classic": classic[gate]})
        print(f"\n== {gate}\n  baseline: {base[gate]}\n  classic : {classic[gate]}")

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    OUT.write_text(
        json.dumps(
            {
                "_provenance": {
                    "engine_commit": commit,
                    "script": "scripts/imperfection_convention_sensitivity.py",
                    "client_order": "Q3 option 1 (2026-08-17): sensitivity before ratification",
                    "derivation": {
                        "s_implemented": round(S_IMPLEMENTED, 3),
                        "classic_realized_at_I_0_15_today": round(CLASSIC_REALIZED_TODAY, 4),
                        "s_classic": round(S_CLASSIC, 3),
                        "equivalent_I_eq": round(I_EQ, 4),
                    },
                    "note": (
                        "Engine untouched: classic sharpness reproduced through the "
                        "existing M3 formula by the equivalent parameter I_eq on "
                        "every DRY screen imperfection (I_dry + SR.5008/SR.5111/"
                        "SR.5115 per-screen I). Defaults unchanged pending the "
                        "client's Q3 ratification."
                    ),
                },
                "baseline": base,
                "classic": classic,
                "comparison": comparison,
            },
            indent=1,
        )
    )
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
