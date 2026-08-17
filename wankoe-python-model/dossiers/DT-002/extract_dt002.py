"""DT-002 extraction script — replay of every figure in technical dossier DT-002.

Any engineer can re-run this without the assistant:

    PYTHONPATH=src python dossiers/DT-002/extract_dt002.py

DT-002 = complete zone-1.1 sizing note for the model exchange with the
client's in-house colleague running Metso's Bruno model. It executes the
SAME engine as the plan and web app (wankoe_model), reconstructs the
converged zone-1.1 internal streams for BOTH operating modes (1A KFS
production at 250 t/h wet; 1B 0/20 campaigns at 172.0 t/h wet, CSS 18)
on the measured 2026-08-08 belt-cut feed curve, dry weather, reference
settings g 60 / CSS 30 / v 30, and prints every dossier figure as JSON:
full-chain stream PSD tables (% passing), machine duties, screen areas,
annual planning translation and the PFD REV15 adequacy confrontation.
Every value must match DT-002 to the decimal; any divergence invalidates
the dossier. Tags are the NACO 11-01-PFD REV15 tags (zone-1.1 retag,
client decision 2026-08-17).
"""

import json
import pathlib
import subprocess

from wankoe_model.scenario import (
    load_parameters,
    run_scenario,
    _flatten_calibration,
    _build_feed,
)
from wankoe_model.planning import run_required_hours
from wankoe_model import flowsheet as fs
from wankoe_model import models

# Spec presentation sieve series (client rule 2026-08-14: the spec sieves
# stay the presentation format; the engine computes on the x2 grid).
MESHES = [0.5, 1, 2, 5, 10, 15, 20, 25, 31.5, 35, 40, 50, 63, 80, 120, 200, 320]

# PFD 11-01-PFD REV15 design figures (the sheet's own numbers, for the
# adequacy confrontation — design-curve based, see dossier section 9).
PFD_DESIGN = {
    "scenario_A": {"kfs_tph": 80.0, "crude_0_20_tph": 170.0},
    "scenario_B": {"kfs_tph": None, "crude_0_20_tph": 150.0},
    "screen_feed_BC5007_tph": 350.0,
    "recycle_BC5010_tph": 125.0,
    "fresh_feed_tph": 250.0,
}


def stream_row(st, label):
    """One dossier PSD table row: rates + % passing on the spec sieves."""
    if st is None:
        return {"label": label, "present": False}
    wet = st["q"] / (1.0 - st["moisture"] / 100.0)
    return {
        "label": label,
        "present": True,
        "dry_tph": round(st["q"], 2),
        "wet_tph": round(wet, 2),
        "moisture_pct": round(st["moisture"], 2),
        "P80_mm": round(st["psd"].p80(), 2),
        "passing_pct": {str(m): round(100.0 * st["psd"].passing_at(m), 2) for m in MESHES},
    }


def run_mode(mode, params, calib, engine, mp, feed_psd, moisture, alerts):
    """Replay the zone-1.1 converged loop for one mode, exposing EVERY stream."""
    sc = params["default_scenario"]
    feed_wet = (
        sc["flow_rates_tph"]["zone_1_1_feed"]
        if mode == "1A"
        else sc["flow_rates_tph"]["zone_1_1_feed_mode_1B"]
    )
    feed = fs._stream(feed_wet * (1.0 - moisture / 100.0), feed_psd, moisture)

    p9 = mp["CR.5006"]["parameters"]
    gap9 = p9["g"]["default"]
    x80_9 = p9["x80"]["default"] if p9["x80"]["default"] is not None else gap9
    psd9 = models.m1_crusher_product(feed["psd"], x80_9, p9["n"]["default"], calib)
    bond9 = models.m2_bond_power(feed["q"], feed["psd"].p80(), psd9.p80(), calib)
    cr5006_out = fs._stream(feed["q"], psd9, feed["moisture"])

    p7 = mp["SR.5008"]["parameters"]
    p11 = mp["CR.5011"]["parameters"]
    a1, a2, imp = p7["a1"]["default"], p7["a2"]["default"], p7["I"]["default"]
    x80_11 = p11["x80"]["default"]
    if mode == "1B":
        x80_11 = mp["CR.5011"].get("mode_1B_x80_mm", x80_11)
    info11: dict = {}
    snap: dict = {}

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
            feed11, out11, new_recycle = None, None, None
        snap.update(
            screen_feed=screen_feed, over35=over35, under35=under35, mid=mid,
            under20=under20, feed11=feed11, out11=out11,
        )
        outputs = {
            "kfs": mid if mode == "1A" else None,
            "undersize_0_20": under20,
            "u_top": under35["q"] if under35 else 0.0,
            "u_bottom": under20["q"] if under20 else 0.0,
        }
        return new_recycle, outputs

    recycle, outputs = fs._fixed_point_loop(iterate, engine, alerts, f"DT-002 z11 {mode}")

    areas = {
        "top_deck_35mm": models.m4_screen_area(outputs["u_top"], a1, calib, 1.0),
        "bottom_deck_20mm": models.m4_screen_area(outputs["u_bottom"], a2, calib, 1.0),
    }
    cap11 = mp["CR.5011"].get("max_capacity_tph")
    load11_wet = (
        recycle["q"] / (1.0 - recycle["moisture"] / 100.0) if recycle else 0.0
    )

    kfs = outputs["kfs"]
    envelope = None
    if kfs is not None:
        below = 100.0 * kfs["psd"].passing_at(a2)
        above = 100.0 * (1.0 - kfs["psd"].passing_at(a1))
        envelope = {
            "below_20mm_pct": round(below, 2),
            "in_cut_20_35_pct": round(100.0 - below - above, 2),
            "above_35mm_pct": round(above, 2),
            "spec": "max 30 below / min 55 in cut / max 15 above",
            "compliant": below <= 30.0 and (100.0 - below - above) >= 55.0 and above <= 15.0,
        }

    return {
        "mode": mode,
        "settings": {
            "CR.5006_gap_mm": gap9, "CR.5006_x80_mm": x80_9, "CR.5006_n": p9["n"]["default"],
            "SR.5008_a1_mm": a1, "SR.5008_a2_mm": a2, "SR.5008_I": imp,
            "CR.5011_v_ms": p11["v"]["default"], "CR.5011_x80_css_mm": x80_11,
        },
        "streams": [
            stream_row(feed, "Pivot feed (BC.5005, measured belt-cut curve)"),
            stream_row(cr5006_out, "CR.5006 product (to BC.5007)"),
            stream_row(snap["screen_feed"], "SR.5008 screen feed (BC.5007 = fresh + recycle, converged)"),
            stream_row(snap["over35"], "SR.5008 deck-1 oversize +35 (via DV.5009 to CR.5011)"),
            stream_row(snap["under35"], "SR.5008 deck-1 undersize 0/35 (internal, to deck 2)"),
            stream_row(snap["mid"], "SR.5008 20/35 cut" + (" -> KFS product (BC.5013 to SP.5015)" if mode == "1A" else " -> recycled to CR.5011 (mode 1B: no KFS)")),
            stream_row(snap["under20"], "SR.5008 undersize 0/20 -> crude product (BC.5012 to SP.5014)"),
            stream_row(snap["feed11"], "CR.5011 feed (converged)"),
            stream_row(snap["out11"], "CR.5011 product (BC.5010 recycle to BC.5007)"),
        ],
        "machines": {
            "CR.5006": {
                **{k: round(v, 3) for k, v in bond9.items()},
                "throughput_dry_tph": round(feed["q"], 2),
                "throughput_wet_tph": round(feed["q"] / (1 - moisture / 100), 2),
                "utilization_pct_of_250_wet": round(100 * (feed["q"] / (1 - moisture / 100)) / 250.0, 1),
            },
            "SR.5008": {
                "feed_dry_tph": round(snap["screen_feed"]["q"], 2),
                "feed_wet_tph": round(snap["screen_feed"]["q"] / (1 - moisture / 100), 2),
                "required_areas_m2": {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in areas.items()},
                "purchase_min_area_m2": mp["SR.5008"].get("purchase_min_area_m2"),
                **{k: round(v, 2) for k, v in models.m4_feed_composition(snap["screen_feed"]["psd"], a1).items()},
            },
            "CR.5011": {
                **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in info11.items()},
                "loop_load_wet_tph": round(load11_wet, 2),
                "vendor_capacity_wet_tph": cap11,
                "utilization_pct": round(100 * load11_wet / cap11, 1) if cap11 else None,
            },
        },
        "recirculation_dry_tph": round(recycle["q"], 2) if recycle else 0.0,
        "kfs_envelope_check": envelope,
        "mass_balance_check_dry_tph": {
            "in": round(feed["q"], 3),
            "out": round(sum(s["q"] for s in [snap["mid"] if mode == "1A" else None, snap["under20"]] if s), 3)
            if mode == "1A"
            else round(snap["under20"]["q"], 3),
            "note": "mode 1B: the 20/35 cut recirculates; sole zone output = 0/20",
        },
    }


def main():
    params_raw = load_parameters()
    params = {**params_raw, "calibration": _flatten_calibration(params_raw["calibration"])}
    calib, engine, mp = params["calibration"], params["engine"], params["machines"]
    alerts: list = []
    feed_psd, moisture = _build_feed(params, alerts)

    out = {
        "_provenance": {
            "commit": subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
            ).stdout.strip(),
            "engine": "wankoe_model (run_scenario / run_required_hours / flowsheet.zone_1_1 replay)",
            "scenario": "modes 1A (250 t/h wet) + 1B (172.0 t/h wet, CSS 18), measured 2026-08-08 belt-cut feed, dry weather, reference settings g60/CSS30/v30",
            "tags": "NACO 11-01-PFD REV15 (zone-1.1 retag 2026-08-17; CR.5006 ex-CR.5009, SR.5008 ex-SR.5007)",
        },
        "replay_kit_inputs": {
            "feed_curve_passing_pct": {str(m): round(100.0 * feed_psd.passing_at(m), 2) for m in MESHES},
            "feed_F80_mm": round(feed_psd.p80(), 2),
            "feed_moisture_pct_wet_basis": moisture,
            "total_flow_rule": "every line feed rate is TOTAL flow, WET basis (dry solids + water) as belt-weighed — client rule 2026-08-14",
            "flow_rates_wet_tph": {
                "mode_1A_feed": params["default_scenario"]["flow_rates_tph"]["zone_1_1_feed"],
                "mode_1B_feed": params["default_scenario"]["flow_rates_tph"]["zone_1_1_feed_mode_1B"],
            },
            "calibration": {
                "Wi_kWh_t": calib["Wi"], "bond_coef": calib["bond_coef"], "eta_m": calib["eta_m"],
                "m1_trunc_factor": calib["trunc_factor"], "m1_ln_arg": calib["m1_ln_arg"],
                "m3_k_d": calib["k_d"], "m3_ln_arg": calib["m3_ln_arg"],
                "m4_qb_coef": calib["qb_coef"], "m4_qb_exp": calib["qb_exp"],
                "m4_f_p": calib["f_p"], "m4_f0": calib["f0"],
                "m5_A_j": calib["A_j"], "m5_b_j": calib["b_j"], "m5_ecs_div": calib["ecs_div"],
                "m5_t10_ref": calib["m5_t10_ref"], "m5_n_exp": calib["m5_n_exp"], "m5_n_min": calib["m5_n_min"],
                "computation_grid_refinement": engine["computation_grid_refinement"],
            },
            "declared_hypotheses_H": {
                "I_imperfection_0.15": "literature value, client arbitration 2026-08-10 — convention question open (Q3, expert note pending)",
                "A_j_60_b_j_0.80": "impact breakage parameters pending drop-weight tests (none launched, client decision 2026-08-16)",
                "n_1.35_CR.5006": "RR uniformity pending vendor gradation table",
                "feed_curve_H-FEED-1/2": "measured belt-cut completed by tail hypotheses",
            },
            "references": {"Wi_12.54": "[ref.] Fontaine, Belgian limestone (client arbitration Q2, 2026-08-11)"},
        },
        "modes": {},
        "cross_check_run_scenario": {},
        "annual_planning": {},
        "pfd_rev15_adequacy": {},
    }

    for mode in ("1A", "1B"):
        out["modes"][mode] = run_mode(mode, params, calib, engine, mp, feed_psd, moisture, alerts)

    # Cross-check: the aggregate engine photos must agree with the replay
    for mode in ("1A", "1B"):
        r = run_scenario(load_parameters(overrides={"default_scenario": {"zone_1_1_mode": mode}}))
        out["cross_check_run_scenario"][mode] = {
            "CR.5006_throughput_tph": round(r["machines"]["CR.5006"]["throughput_tph"], 2),
            "SR.5008_feed_tph": round(r["machines"]["SR.5008"]["feed_tph"], 2),
            "KFS_present": r["products"]["KFS 20/35"]["present"] if "KFS 20/35" in r["products"] else r["products"].get("KFS", {}).get("present"),
            "zone_1_1_recirculation_tph": round(r["intermediate_flows"]["zone_1_1_recirculation_tph"], 2),
        }

    plan = run_required_hours(params_raw)
    out["annual_planning"] = {
        "principle": plan["principle"],
        "zone_1_1_hours": {k: round(v, 1) for k, v in plan["zone_1_1_split"].items()},
        "zone_1_1_ceiling_h": 2400,
        "production_t": {k: round(v, 0) for k, v in plan["production_t"].items()},
        "kfs_yield": plan["kfs_yield"],
        "stockpiles_t": {k: round(v, 0) for k, v in plan["stockpiles_t"].items() if isinstance(v, (int, float))},
    }

    m1a = out["modes"]["1A"]
    kfs_tph_wet = next(s for s in m1a["streams"] if s["label"].startswith("SR.5008 20/35"))["wet_tph"]
    crude_tph_wet = next(s for s in m1a["streams"] if "0/20" in s["label"] and "crude" in s["label"])["wet_tph"]
    sfeed_wet = next(s for s in m1a["streams"] if "screen feed" in s["label"])["wet_tph"]
    rec_wet = next(s for s in m1a["streams"] if "recycle" in s["label"])["wet_tph"]
    out["pfd_rev15_adequacy"] = {
        "pfd_design_figures": PFD_DESIGN,
        "engine_measured_curve_mode_1A_wet_tph": {
            "kfs_20_35": kfs_tph_wet, "crude_0_20": crude_tph_wet,
            "screen_feed": sfeed_wet, "recycle": rec_wet,
        },
        "confrontations": [
            "PFD scenario A: KFS 80 t/h vs engine ~{:.0f} t/h; crude 170 vs ~{:.0f} — the PFD figures assume the NACO DESIGN feed curve; the engine runs the MEASURED belt-cut curve (45.5 % already < 20 mm at the pivot). Same flowsheet, different feed curve: the gap is a FEED-CURVE question, not a flowsheet disagreement (same family as the KFS 80-vs-51 spec question).".format(kfs_tph_wet, crude_tph_wet),
            "PFD screen feed 350 t/h vs engine {:.0f} t/h and PFD recycle 125 vs {:.0f} — consistent with the finer measured feed (less +35 oversize, less recycle).".format(sfeed_wet, rec_wet),
            "PFD scenario B (crude only, 150 t/h product) vs engine mode 1B (feed 172.0 t/h wet re-bisected 2026-08-15 so the CR.5011 90 t/h wet guarantee holds on both feed curves): same operating intent (no KFS), different sizing basis — the PFD states a PRODUCT rate, the engine sets the FEED so the loop machine survives.",
        ],
    }

    out["_alerts_during_replay"] = alerts
    dest = pathlib.Path(__file__).parent / "dt002_data.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out["cross_check_run_scenario"], indent=1))
    print("KFS envelope 1A:", out["modes"]["1A"]["kfs_envelope_check"])
    print("written:", dest)


if __name__ == "__main__":
    main()
