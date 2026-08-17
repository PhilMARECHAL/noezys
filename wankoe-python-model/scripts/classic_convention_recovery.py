"""Q3 recovery study — can SETTINGS recover compliance under the CLASSIC
imperfection convention? (client ratification 2026-08-17, option 1:
implemented convention stays the default; this study maps the plan B.)

Under the classic-0.15 sharpness (equivalent I_eq = 0.2584, see
scripts/imperfection_convention_sensitivity.py) the reference settings
fail two gates: KFS envelope (above-35 = 15.12 % > 15) and grits D6
(< 2 mm = 15.95 % > 15 AND > 4 mm = 9.04 % > 5 — BOTH sides). The zones
are independent levers:
  zone 1.1 -> KFS envelope: CR.5006 gap g x CR.5011 CSS (v held at 30)
  zone 1.3 -> grits D6:     SC.B a1 (grits bottom cut) x SC.A a2 (3.75
                            recycle cut, drives the > 4 mm side)
Sweeps run at mode-photo level plus planning (landfill / production
consequences). Purely informational: NO default changes.

Replay:
    PYTHONPATH=src python scripts/classic_convention_recovery.py
writes docs/design/error-hunt/classic-convention-recovery.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from wankoe_model import load_parameters, run_scenario
from wankoe_model.planning import run_required_hours

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "design" / "error-hunt" / "classic-convention-recovery.json"

I_EQ = 0.2584  # classic-0.15 through the implemented formula


def classic(ov: dict) -> dict:
    base = {
        "calibration": {"I_dry": {"default": I_EQ}},
        "machines": {
            code: {"parameters": {"I": {"default": I_EQ}}}
            for code in ("SR.5008", "SR.5111", "SR.5115")
        },
    }
    # deep-merge the sweep overrides into the classic base
    merged = json.loads(json.dumps(base))
    for section, content in ov.items():
        merged.setdefault(section, {})
        for k, v in content.items():
            if k in merged[section] and isinstance(v, dict):
                # machines entry: merge parameters
                merged[section][k].setdefault("parameters", {}).update(v.get("parameters", {}))
            else:
                merged[section][k] = v
    return merged


def z11_case(g: float, css: float) -> dict:
    ov = classic({"machines": {
        "CR.5006": {"parameters": {"g": {"default": g}}},
        "CR.5011": {"parameters": {"x80": {"default": css}}},
    }})
    plan = run_required_hours(load_parameters(overrides=ov))
    r = run_scenario(load_parameters(overrides=ov))
    ky = plan["kfs_yield"]["kfs_real_psd_pct"]
    compliant = ky["below_20"] <= 30 and ky["in_cut_20_35"] >= 55 and ky["above_35"] <= 15
    return {
        "g_mm": g, "css_mm": css,
        "kfs_below_in_above": [ky["below_20"], ky["in_cut_20_35"], ky["above_35"]],
        "kfs_compliant": compliant,
        "kfs_yield_realized_pct": plan["kfs_yield"]["realized_pct"],
        "landfill_t": plan["stockpiles_t"].get("0/20 to LANDFILL (net loss)", 0.0),
        "z11_hours_1A": plan["zone_1_1_split"]["mode_1A_hours_effective"],
        "cr5011_bottleneck_alert": any("CR.5011: bottleneck" in a for a in r["alerts"]),
    }


def z13_case(scb_a1: float, sca_a2: float) -> dict:
    ov = classic({"machines": {
        "SC.B": {"parameters": {"a1": {"default": scb_a1}}},
        "SC.A": {"parameters": {"a2": {"default": sca_a2}}},
    }})
    r = run_scenario(load_parameters(overrides=ov))
    plan = run_required_hours(load_parameters(overrides=ov))
    c = r["products"]["FeedLime grits"]["compliance"]
    fines = r["products"]["FeedLime fines"]["compliance"]
    return {
        "scb_a1_mm": scb_a1, "sca_a2_mm": sca_a2,
        "d6_below2_above4": [c["below_cut_pct"], c["above_cut_pct"]],
        "d6_compliant": bool(c["compliant"]),
        "fines_in_cut_pct": fines["in_cut_pct"],
        "grits_tph": r["products"]["FeedLime grits"]["tph"],
        "production_t": {k: round(v) for k, v in plan["production_t"].items()},
        "z13_hours_G_F": [
            plan["zone_1_3_split"]["mode_G_hours_effective"],
            plan["zone_1_3_split"]["mode_F_hours_effective"],
        ],
    }


def main() -> None:
    z11 = [z11_case(g, css) for g in (40, 45, 50, 55, 60) for css in (20, 25, 30)]
    z13 = [z13_case(a1, a2) for a1 in (2.0, 2.1, 2.2, 2.3, 2.4) for a2 in (3.5, 3.6, 3.75)]

    z11_ok = [c for c in z11 if c["kfs_compliant"] and not c["cr5011_bottleneck_alert"]]
    z11_best = min(z11_ok, key=lambda c: c["landfill_t"]) if z11_ok else None
    z13_ok = [c for c in z13 if c["d6_compliant"]]
    z13_best = max(z13_ok, key=lambda c: c["grits_tph"]) if z13_ok else None

    print("== zone 1.1 sweep (classic convention): g x CSS, v 30")
    for c in z11:
        print(
            f"  g {c['g_mm']:>2} css {c['css_mm']:>2}: KFS {c['kfs_below_in_above']} "
            f"{'OK ' if c['kfs_compliant'] else 'FAIL'} landfill {c['landfill_t']:.0f} t "
            f"{'(CR.5011 BOTTLENECK)' if c['cr5011_bottleneck_alert'] else ''}"
        )
    print("== zone 1.3 sweep (classic convention): SC.B a1 x SC.A a2")
    for c in z13:
        print(
            f"  a1 {c['scb_a1_mm']} a2 {c['sca_a2_mm']}: D6 [{c['d6_below2_above4'][0]:.2f} "
            f"<2mm ; {c['d6_below2_above4'][1]:.2f} >4mm] "
            f"{'OK ' if c['d6_compliant'] else 'FAIL'} grits {c['grits_tph']:.1f} t/h"
        )
    print("\nBEST z11:", z11_best)
    print("BEST z13:", z13_best)

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    OUT.write_text(json.dumps({
        "_provenance": {
            "engine_commit": commit,
            "script": "scripts/classic_convention_recovery.py",
            "client_order": "Q3 ratification option 1 (2026-08-17): implemented convention stays; this maps the recovery plan under the classic downside scenario",
            "convention": f"classic-0.15 via I_eq {I_EQ} on all dry screens",
        },
        "zone_1_1_sweep": z11,
        "zone_1_3_sweep": z13,
        "best_recovery": {"zone_1_1": z11_best, "zone_1_3": z13_best},
    }, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
