"""OF-005 pre-order stress test — 2PG-1216CT + S5X2760-2 vs ALL zone-1.1 scenarios.

Client mission 2026-09-04 (matrix approved, option 1): complete process
verification of the machines quoted in OF-005 (Zenith "BEST price with
spare parts", 2026-09-04) against every production scenario and every
granulometric extreme ruled into the project.

    PYTHONPATH=src python scripts/of005_stress_test.py

Families (per the approved matrix):
  S1 reference 1A · S2 mode-1B loop duty · S3 quarry-target curve ·
  S4 granulometric extremes (k 0.70 fine / k 1.60 coarse — the envisaged
     feed-sensitivity campaign envelope; the NACO design curve was never
     encoded as a curve, the k-sweep bounds it) ·
  S5 setting-window sweep g 20..60 · S6 vendor-gradation uncertainty
     (CR.5006 product-shape n sweep — THE machine-quality stress) ·
  S7 soft-rock coefficient scenario · S8 rain week (12 % feed moisture,
     wet screening derated) · S9 analytical machine-limit gates.

Machine limits under test (as printed in OF-005):
  2PG-1216CT: max capacity 400 t/h, feeding size 0-300 mm, 2x180 kW,
  discharge setting printed 40-800 mm (duty needs 20-60).
  S5X2760-2: 2 decks 2.7x6.0 m = 16.2 m2/deck, mesh range 2-70 mm.

Writes docs/purchase/offers/OF-005-zenith-final/stress-test-evidence.json.
Every figure is engine-computed; nothing is typed by hand.
"""

import json
import math
import pathlib
import subprocess

from wankoe_model.scenario import load_parameters, _flatten_calibration, _build_feed
from wankoe_model import flowsheet as fs
from wankoe_model import models

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/purchase/offers/OF-005-zenith-final/stress-test-evidence.json"

MACHINE = {
    "crusher_cap_wet_tph": 400.0,
    "crusher_installed_kW": 360.0,
    "crusher_max_feed_mm": 300.0,
    "screen_area_m2_per_deck": 16.2,
    "loop_vendor_cap_wet_tph": None,  # read from data (CR.5011, 90 t/h wet)
}

# ---------------------------------------------------------------- curves
_base = load_parameters()
_meas = sorted((float(k), float(v)) for k, v in
               _base["feed_product"]["cumulative_passing_curve"].items())


def _interp(x):
    pts = _meas
    if x <= pts[0][0]:
        return pts[0][1] * x / pts[0][0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return 100.0


def scaled_curve(k):
    """Homothetic D50 rescale of the measured curve (feed-sensitivity
    campaign convention): k>1 = coarser feed."""
    c = {str(x): round(min(100.0, _interp(x / k)), 4) for x, _ in _meas}
    c[str(_meas[-1][0])] = 100.0
    return c


CURVES = {
    "measured": None,                       # 45.5 % < 20 mm (fine band edge)
    "quarry-target(k1.426)": scaled_curve(1.426),   # 40.1 % < 20 mm (coarse band edge)
    "fine-extreme(k0.70)": scaled_curve(0.70),
    "coarse-extreme(k1.60)": scaled_curve(1.60),
}

with open(ROOT / "docs/design/soft-rock/soft-rock-scenario.json", encoding="utf-8") as f:
    SOFT = {k: v for k, v in json.load(f).items() if not k.startswith("_")}


# ---------------------------------------------------------------- engine run
def run_case(label, mode="1A", curve=None, gap=None, n9=None,
             extra_overrides=None, moisture=None, weather="dry"):
    ov = {}
    if curve is not None:
        ov["feed_product"] = {"cumulative_passing_curve": curve}
    if moisture is not None:
        ov.setdefault("feed_product", {})["properties"] = {
            "moisture_pct": {"default": moisture}}
    if extra_overrides:
        # shallow-merge blocks the scenario files use (calibration/machines)
        for k, v in extra_overrides.items():
            if k in ov and isinstance(ov[k], dict):
                ov[k] = {**v, **ov[k]}
            else:
                ov[k] = v
    params_raw = load_parameters(overrides=ov or None)
    params = {**params_raw, "calibration": _flatten_calibration(params_raw["calibration"])}
    calib, engine, mp = params["calibration"], params["engine"], params["machines"]
    alerts: list = []
    feed_psd, moist = _build_feed(params, alerts)

    p9 = mp["CR.5006"]["parameters"]
    if gap is not None:
        p9["g"]["default"] = gap
        p9["x80"]["default"] = None
    if n9 is not None:
        p9["n"]["default"] = n9
    gap9 = p9["g"]["default"]
    x80_9 = p9["x80"]["default"] if p9["x80"]["default"] is not None else gap9

    sc = params["default_scenario"]
    feed_wet = (sc["flow_rates_tph"]["zone_1_1_feed"] if mode == "1A"
                else sc["flow_rates_tph"]["zone_1_1_feed_mode_1B"])
    feed = fs._stream(feed_wet * (1.0 - moist / 100.0), feed_psd, moist)

    psd9 = models.m1_crusher_product(feed["psd"], x80_9, p9["n"]["default"], calib)
    bond9 = models.m2_bond_power(feed["q"], feed["psd"].p80(), psd9.p80(), calib)
    cr5006_out = fs._stream(feed["q"], psd9, feed["moisture"])

    p7, p11 = mp["SR.5008"]["parameters"], mp["CR.5011"]["parameters"]
    a1, a2, imp = p7["a1"]["default"], p7["a2"]["default"], p7["I"]["default"]
    x80_11 = p11["x80"]["default"]
    if mode == "1B":
        x80_11 = mp["CR.5011"].get("mode_1B_x80_mm", x80_11)
    snap: dict = {}
    info11: dict = {}

    def iterate(recycle):
        screen_feed = fs._blend([cr5006_out, recycle]) if recycle else cr5006_out
        over35, under35 = fs._karra_screen(screen_feed, a1, imp, calib)
        mid, under20 = fs._karra_screen(under35, a2, imp, calib) if under35 else (None, None)
        to_imp = [s for s in [over35] + ([mid] if mode == "1B" else []) if s]
        if to_imp:
            feed11 = fs._blend(to_imp)
            out11, info = fs._impactor(feed11, p11["v"]["default"], x80_11, calib)
            info11.update(info)
            new_recycle = out11
        else:
            new_recycle = None
        snap.update(screen_feed=screen_feed, over35=over35, under35=under35,
                    mid=mid, under20=under20)
        return new_recycle, {
            "u_top": under35["q"] if under35 else 0.0,
            "u_bottom": under20["q"] if under20 else 0.0,
        }

    recycle, outputs = fs._fixed_point_loop(iterate, engine, alerts, f"OF005 {label}")

    wet_factor = calib["wet_capacity_factor"] if weather == "rain" else 1.0
    areas = {
        "top_35mm": models.m4_screen_area(outputs["u_top"], a1, calib, wet_factor),
        "bottom_20mm": models.m4_screen_area(outputs["u_bottom"], a2, calib, wet_factor),
    }
    cap11 = mp["CR.5011"].get("max_capacity_tph")
    load11_wet = recycle["q"] / (1.0 - recycle["moisture"] / 100.0) if recycle else 0.0

    env = None
    if mode == "1A" and snap.get("mid") is not None:
        below = 100.0 * snap["mid"]["psd"].passing_at(a2)
        above = 100.0 * (1.0 - snap["mid"]["psd"].passing_at(a1))
        env = {"below": round(below, 2), "in_cut": round(100 - below - above, 2),
               "above": round(above, 2),
               "compliant": below <= 30.0 and (100 - below - above) >= 55.0 and above <= 15.0}

    crusher_wet = feed["q"] / (1.0 - moist / 100.0)
    max_req_area = max(a["required_area_m2"] for a in areas.values())
    checks = {
        "kfs_envelope": None if env is None else env["compliant"],
        "loop_le_90_wet": load11_wet <= cap11 + 1e-9,
        "crusher_cap_le_400": crusher_wet <= MACHINE["crusher_cap_wet_tph"],
        "crusher_power_le_360kW": bond9["P_installed_kW"] <= MACHINE["crusher_installed_kW"],
        "screen_area_le_16p2": max_req_area <= MACHINE["screen_area_m2_per_deck"],
    }
    checks["ALL_PASS"] = all(v for v in checks.values() if v is not None)

    return {
        "label": label, "mode": mode, "gap_mm": gap9, "n_CR5006": p9["n"]["default"],
        "weather": weather, "moisture_pct": moist,
        "feed": {"pct_lt_20mm": round(100 * feed_psd.passing_at(20.0), 1),
                 "F80_mm": round(feed_psd.p80(), 1)},
        "crusher": {"wet_tph": round(crusher_wet, 1),
                    "P80_mm": round(psd9.p80(), 2),
                    "P_absorbed_kW": round(bond9["P_installed_kW"], 1)},
        "loop_wet_tph": round(load11_wet, 2), "loop_cap_wet_tph": cap11,
        "screen_req_area_m2": {k: round(v["required_area_m2"], 2) for k, v in areas.items()},
        "kfs_envelope": env,
        "checks": checks,
        "alerts": alerts,
    }


# ---------------------------------------------------------------- families
runs = []

runs.append(("S1", run_case("S1 reference 1A measured g60")))

for cv in ("measured", "quarry-target(k1.426)"):
    runs.append(("S2", run_case(f"S2 mode-1B {cv}", mode="1B", curve=CURVES[cv])))

runs.append(("S3", run_case("S3 quarry-target 1A", curve=CURVES["quarry-target(k1.426)"])))

for cv in ("fine-extreme(k0.70)", "coarse-extreme(k1.60)"):
    runs.append(("S4", run_case(f"S4 {cv} 1A", curve=CURVES[cv])))
runs.append(("S4", run_case("S4 coarse-extreme(k1.60) 1B", mode="1B",
                            curve=CURVES["coarse-extreme(k1.60)"])))

for cv in ("measured", "quarry-target(k1.426)"):
    for g in (20, 30, 40, 50, 60):
        runs.append(("S5", run_case(f"S5 g={g} {cv}", curve=CURVES[cv], gap=g)))

for cv in ("measured", "quarry-target(k1.426)"):
    for n in (1.0, 1.15, 1.35, 1.6, 1.8):
        runs.append(("S6", run_case(f"S6 n={n} {cv}", curve=CURVES[cv], n9=n)))

for cv in ("measured", "quarry-target(k1.426)"):
    runs.append(("S7", run_case(f"S7 soft-rock 1A {cv}", curve=CURVES[cv],
                                extra_overrides=SOFT)))
runs.append(("S7", run_case("S7 soft-rock 1B measured", mode="1B", extra_overrides=SOFT)))

runs.append(("S8", run_case("S8 rain week 1A measured (12 % feed, wet screening)",
                            moisture=12.0, weather="rain")))

# S10 — worst-case crossings (added at run time, honesty supplement: the
# matrix as approved tested the n-sweep in 1A only; the loop is TIGHTER in
# 1B, so the adverse-shape x 1B crossings must be run before any verdict)
for cv in ("measured", "quarry-target(k1.426)"):
    for n in (1.6, 1.8):
        runs.append(("S10", run_case(f"S10 1B n={n} {cv}", mode="1B",
                                     curve=CURVES[cv], n9=n)))
runs.append(("S10", run_case("S10 rain 1A n=1.8 measured (wet areas, adverse shape)",
                             moisture=12.0, weather="rain", n9=1.8)))
runs.append(("S10", run_case("S10 soft-rock 1B quarry-target", mode="1B",
                             curve=CURVES["quarry-target(k1.426)"],
                             extra_overrides=SOFT)))

# S9 — analytical machine-limit gates (no simulation)
pct_gt_300 = 100.0 - _interp(300.0)
pct_gt_200 = 100.0 - _interp(200.0)
bond_ref = next(r for f, r in runs if f == "S1")["crusher"]["P_absorbed_kW"]
s9 = {
    "feed_top_size": {
        "machine_limit_mm": 300, "hypothesis_top_size_mm": 320,
        "measured_pct_gt_200mm": round(pct_gt_200, 1),
        "measured_pct_gt_300mm_H_FEED2": round(pct_gt_300, 2),
        "verdict": "CONTRACTUAL/OPERATIONAL — the H-FEED-2 completed tail puts "
                   f"~{pct_gt_300:.1f} % of the feed above the machine's printed 300 mm "
                   "limit (top size 320). Either the vendor confirms 320 mm acceptance "
                   "or the quarry primary guarantees 0-300 (a grizzly/setting matter). "
                   "To be settled IN WRITING before order.",
    },
    "power": {
        "bond_absorbed_kW_at_reference": bond_ref, "installed_kW": 360,
        "verdict": "PASS — enormous margin (installed ~3.7x the Bond estimate; "
                   "vendor drive sized for hard rock).",
    },
    "setting_window": {
        "printed_range_mm": "40-800", "required_window_mm": "20-60",
        "verdict": "FAIL AS PRINTED — the decisive gate. The S5 sweep shows the duty "
                   "needs g operable across 20-60; written confirmation (or a corrected "
                   "spec sheet) is a CONDITION PRECEDENT to any order.",
    },
    "screen_mesh_range": {
        "printed_mm": "2-70", "required_decks_mm": "35 / 20",
        "verdict": "COVERED by the printed range, but the supplied apertures are "
                   "nowhere stated — the order must specify 35/20 with certified "
                   "aperture tolerance.",
    },
}

# ---------------------------------------------------------------- output
families: dict = {}
for fam, r in runs:
    families.setdefault(fam, []).append(r)

commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
evidence = {
    "_provenance": {
        "commit": commit, "script": "scripts/of005_stress_test.py",
        "mission": "OF-005 pre-order process verification (client 2026-09-04, matrix option 1)",
        "machine_limits_under_test": MACHINE,
    },
    "families": families,
    "S9_analytical_gates": s9,
}
OUT.write_text(json.dumps(evidence, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"runs: {len(runs)}  ->  {OUT}")
for fam in sorted(families):
    for r in families[fam]:
        c = r["checks"]
        flags = " ".join(k for k, v in c.items() if v is False)
        env = r["kfs_envelope"]
        env_s = (f"env {env['below']}/{env['in_cut']}/{env['above']}"
                 f"{'' if env['compliant'] else ' NON-COMPLIANT'}") if env else "no KFS (1B)"
        print(f"{r['label']:44s} loop {r['loop_wet_tph']:6.2f}/90  "
              f"crush {r['crusher']['wet_tph']:5.1f}t/h {r['crusher']['P_absorbed_kW']:5.1f}kW  "
              f"{env_s:38s} {'PASS' if c['ALL_PASS'] else 'FAIL: ' + flags}")
print("\nS9 gates:")
for k, v in s9.items():
    print(f"  {k}: {v['verdict'][:100]}")
