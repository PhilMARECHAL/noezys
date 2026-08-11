"""DT-001 extraction script — replay of every figure in technical dossier DT-001.

Any engineer can re-run this without the assistant:

    python dossiers/DT-001/extract_dt001.py

It executes the SAME engine as the web app (wankoe_model), reconstructs the
converged internal streams of the three zones at the DT-001 operating point
(250 t/h wet line feed, dry weather, modes 1A/2A, measured 2026-08-08 belt-cut
feed curve) and prints every datasheet figure as JSON. Every value it prints
must match DT-001 to the decimal; any divergence invalidates the dossier.
"""

import json
import math
import subprocess
import sys

from wankoe_model.scenario import (
    load_parameters,
    run_scenario,
    _flatten_calibration,
    _build_feed,
)
from wankoe_model.planning import run_required_hours
from wankoe_model import flowsheet as fs
from wankoe_model import models


def stream_row(st, meshes):
    return {
        "dry_tph": round(st["q"], 3),
        "wet_tph": round(st["q"] / (1.0 - st["moisture"] / 100.0), 3),
        "P80_mm": round(st["psd"].p80(), 4),
        "moisture_pct": round(st["moisture"], 3),
        "passing_pct": {str(m): round(100.0 * st["psd"].passing_at(m), 2) for m in meshes},
    }


def main():
    params_raw = load_parameters()
    reference = run_scenario(params_raw)  # engine cross-check target
    plan = run_required_hours(params_raw)
    params = {**params_raw, "calibration": _flatten_calibration(params_raw["calibration"])}
    calib = params["calibration"]
    engine = params["engine"]
    mp = params["machines"]
    alerts: list = []
    feed_psd, moisture = _build_feed(params, alerts)

    out = {"_provenance": {
        "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                 capture_output=True, text=True).stdout.strip(),
        "scenario": "250 t/h wet, dry, modes 1A/2A, measured 2026-08-08 belt-cut feed",
    }}

    # ---------------- Zone 1.1 (final converged pass)
    feed = {"q": 250 * (1 - moisture / 100), "psd": feed_psd, "moisture": moisture}
    p9 = mp["CR.5009"]["parameters"]
    x80_9 = p9["x80"]["default"] if p9["x80"]["default"] is not None else p9["g"]["default"]
    psd9 = models.m1_crusher_product(feed["psd"], x80_9, p9["n"]["default"], calib)
    bond9 = models.m2_bond_power(feed["q"], feed["psd"].p80(), psd9.p80(), calib)
    cr5009_out = fs._stream(feed["q"], psd9, feed["moisture"])
    p7 = mp["SR.5007"]["parameters"]
    p11 = mp["CR.5011"]["parameters"]
    a1, a2, imp = p7["a1"]["default"], p7["a2"]["default"], p7["I"]["default"]
    info11: dict = {}

    def it11(recycle):
        sfeed = fs._blend([cr5009_out, recycle]) if recycle else cr5009_out
        over35, under35 = fs._karra_screen(sfeed, a1, imp, calib)
        mid, under20 = fs._karra_screen(under35, a2, imp, calib)
        out11, info = fs._impactor(
            fs._blend([over35]), p11["v"]["default"], p11["x80"]["default"], calib
        )
        info11.update(info)
        return out11, dict(sfeed=sfeed, over35=over35, mid=mid, under20=under20)

    rec11, o11 = fs._fixed_point_loop(it11, engine, alerts, "z11")
    m_coarse = [2, 5, 10, 15, 20, 25, 31.5, 35, 40, 50, 63, 80, 120, 200, 320]
    out["zone_1_1"] = {
        "pivot_feed": stream_row(feed, m_coarse),
        "CR_5009": {
            "settings": {"x80_mm": x80_9, "n": p9["n"]["default"]},
            "product": stream_row(cr5009_out, m_coarse),
            **{k: round(v, 4) for k, v in bond9.items()},
        },
        "SR_5007": {
            "settings": {"a1_mm": a1, "a2_mm": a2, "I": imp,
                          "s": round(math.log(9) / math.log(1 / (1 - imp)), 3)},
            "screen_feed": stream_row(o11["sfeed"], m_coarse),
            "oversize_35": stream_row(o11["over35"], m_coarse),
            "kfs_20_35": stream_row(o11["mid"], m_coarse),
            "undersize_0_20": stream_row(o11["under20"], m_coarse),
            "areas_m2": reference["machines"]["SR.5007"]["areas_m2"],
        },
        "CR_5011": {
            "settings": {"v_ms": p11["v"]["default"], "x80_mm": p11["x80"]["default"],
                          "A": calib["A_j"], "b": calib["b_j"]},
            "recycle": stream_row(rec11, m_coarse),
            **{k: round(v, 4) for k, v in info11.items() if isinstance(v, (int, float))},
        },
        "kfs_compliance": reference["products"]["KFS"]["compliance"],
    }

    # ---------------- Zone 1.2
    reclaim = {"q": 100 * (1 - moisture / 100), "psd": o11["under20"]["psd"], "moisture": moisture}
    p05 = mp["SR.5105"]["parameters"]
    over15, under15 = fs._karra_screen(reclaim, p05["a1"]["default"], calib["I_dry"], calib)
    mid5, under5 = fs._karra_screen(under15, p05["a2"]["default"], calib["I_dry"], calib)
    loop_feed = fs._blend([over15, under5])
    p15 = mp["SR.5115"]["parameters"]
    p07 = mp["CR.5107"]["parameters"]
    info07: dict = {}

    def it12(recycle):
        sfeed = fs._blend([loop_feed, recycle]) if recycle else loop_feed
        oversize, aglime = fs._karra_screen(sfeed, p15["a"]["default"], p15["I"]["default"], calib)
        o, info = fs._impactor(oversize, p07["v"]["default"], p07["x80"]["default"], calib)
        info07.update(info)
        return o, dict(sfeed=sfeed, oversize=oversize, aglime=aglime)

    rec12, o12 = fs._fixed_point_loop(it12, engine, alerts, "z12")
    m_mid = [0.063, 0.125, 0.25, 0.5, 1.0, 1.5, 1.7, 2, 2.8, 4, 5, 8, 10, 12.5, 15, 20]
    out["zone_1_2"] = {
        "reclaim": stream_row(reclaim, m_mid),
        "SR_5105": {
            "settings": {"a1_mm": p05["a1"]["default"], "a2_mm": p05["a2"]["default"],
                          "I": calib["I_dry"]},
            "oversize_15": stream_row(over15, m_mid),
            "feedlime_5_15": stream_row(mid5, m_mid),
            "undersize_0_5": stream_row(under5, m_mid),
            "areas_m2": reference["machines"]["SR.5105"]["areas_m2"],
        },
        "SR_5115": {
            "settings": {"a_mm": p15["a"]["default"], "I": p15["I"]["default"],
                          "I_rain": calib["I_rain"]},
            "fresh_loop_feed": stream_row(loop_feed, m_mid),
            "screen_feed": stream_row(o12["sfeed"], m_mid),
            "oversize_1_7": stream_row(o12["oversize"], m_mid),
            "aglime": stream_row(o12["aglime"], m_mid),
            "areas_m2": reference["machines"]["SR.5115"]["areas_m2"],
            "circulating_load_ratio": round(rec12["q"] / loop_feed["q"], 4),
        },
        "CR_5107": {
            "settings": {"v_ms": p07["v"]["default"], "x80_mm": p07["x80"]["default"],
                          "A": calib["A_j"], "b": calib["b_j"]},
            **{k: round(v, 4) for k, v in info07.items() if isinstance(v, (int, float))},
        },
    }

    # ---------------- Zone 1.3
    fl = {"q": 30 * (1 - moisture / 100), "psd": mid5["psd"], "moisture": moisture}
    m_out_set = mp["DY.03"]["parameters"]["m_out"]["default"]
    m6 = models.m6_drying(fl["q"] / (1 - fl["moisture"] / 100), fl["moisture"], m_out_set, calib)
    dried = fs._stream(m6["dry_solids_tph"], fl["psd"], m6["m_out_effective_pct"])
    p21 = mp["SN.21"]["parameters"]
    a41, a42, a43 = (p21[k]["default"] for k in ("a1", "a2", "a3"))
    p26 = mp["ML.26"]["parameters"]
    calib26 = {**calib, "comp_lam": p26["comp_lam"]["default"], "S_att": p26["S_att"]["default"]}
    info26: dict = {}

    def it13(recycle):
        sfeed = fs._blend([dried, recycle]) if recycle else dried
        over4, under4 = fs._karra_screen(sfeed, a41, calib["I_dry"], calib)
        grits, under2 = fs._karra_screen(under4, a42, calib["I_dry"], calib)
        sliver, fines = fs._karra_screen(under2, a43, calib["I_dry"], calib)
        mill_feed = fs._blend([over4, sliver])
        mpsd = models.m7_bed_mill_pass(mill_feed["psd"], p26["g"]["default"], calib26)
        bond = models.m2_bond_power(mill_feed["q"], mill_feed["psd"].p80(), mpsd.p80(), calib)
        info26.update({**bond, "throughput_tph": mill_feed["q"]})
        return fs._stream(mill_feed["q"], mpsd, mill_feed["moisture"]), dict(
            sfeed=sfeed, over4=over4, grits=grits, sliver=sliver, fines=fines, mill_feed=mill_feed
        )

    rec13, o13 = fs._fixed_point_loop(it13, engine, alerts, "z13")
    p36 = mp["SP.36"]["parameters"]
    calib_cl = {**calib, "eta_cl": p36["eta_cl"]["default"],
                "v_in_cyclone": mp["CL.38"]["parameters"]["v_in"]["default"]}
    m8 = models.m8_air_classification(
        o13["fines"]["q"], o13["fines"]["psd"], p36["coupe"]["default"], calib["Phi_100"], calib_cl
    )
    m_fine = [0.02, 0.04, 0.063, 0.1, 0.125, 0.25, 0.5, 1.0, 1.5, 2, 2.8, 4, 5, 8, 12.5]
    out["zone_1_3"] = {
        "DY_03": {"settings": {"m_out_pct": m_out_set, "eta_th": calib["eta_th"],
                                "I_ev": calib["I_ev"]},
                   **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in m6.items()}},
        "SN_21": {
            "settings": {"a_mm": [a41, a42, a43], "I": calib["I_dry"]},
            "screen_feed": stream_row(o13["sfeed"], m_fine),
            "oversize_4": stream_row(o13["over4"], m_fine),
            "grits_2_4": stream_row(o13["grits"], m_fine),
            "sliver_1_5_2": stream_row(o13["sliver"], m_fine),
            "fines_0_1_5": stream_row(o13["fines"], m_fine),
            "areas_m2": reference["machines"]["SN.21"]["areas_m2"],
        },
        "ML_26": {
            "settings": {"g_mm": p26["g"]["default"], "comp_lam": p26["comp_lam"]["default"],
                          "S_att": p26["S_att"]["default"]},
            "mill_feed": stream_row(o13["mill_feed"], m_fine),
            "product": stream_row(rec13, m_fine),
            "circulating_load_ratio": round(rec13["q"] / dried["q"], 4),
            **{k: round(v, 4) for k, v in info26.items()},
        },
        "SP_36": {
            "settings": {"cut_um": p36["coupe"]["default"], "eta_cl": p36["eta_cl"]["default"]},
            **{k: (round(v, 4) if isinstance(v, float) else v)
               for k, v in m8.items() if not hasattr(v, "passing")},
        },
        "CL_38": {"d50_um": round(models.m8_cyclone_d50(calib_cl), 4),
                   "b_m": calib["b_cyclone"], "N_e": calib["N_e"],
                   "v_in_ms": mp["CL.38"]["parameters"]["v_in"]["default"]},
        "grits_compliance": reference["products"]["FeedLime grits"]["compliance"],
    }

    # ---------------- Planning (hours follow targets) + engine cross-check
    out["planning"] = {"zones": plan["zones"], "production_t": plan["production_t"],
                        "alerts": plan["alerts"]}
    out["engine_cross_check"] = {
        "products_tph": {k: v["tph"] for k, v in reference["products"].items()},
        "balances_closed": all(b["closed"] for b in reference["balances"].values()),
    }
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
