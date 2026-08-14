#!/usr/bin/env python3
"""Independent recomputation of the WANKOE zone-1.1 flowsheet (mode 1A, dry).

BLIND-PROTOCOL VERIFICATION SCRIPT.
Written WITHOUT reading the engine source (src/) or its tests: every formula
is taken from the allowed documentation only --
  - data/default_parameters.json                       (all setting VALUES)
  - docs/model-science-review.md                       (formula provenance M1-M5)
  - docs/calc-notes/zone1/WANKOE-Zone1-Machine-Calculation-Sheets.html
    (full derivations; its numeric examples used OLDER settings g=40/CSS=20/
    v=45 -- formulas only were taken from it, values come from the JSON).

Topology (zone 1.1, mode 1A):
  pivot feed 250 t/h wet (7 % moisture) -> CR.5009 (toothed roll crusher, M1)
  -> blend with CR.5011 recycle -> SR.5007 double-deck screen 35/20 (M3):
       +35 oversize  -> CR.5011 impact crusher (M5 slope + M1 product)
                        -> recycled to the SR.5007 feed (closed loop,
                           fixed-point iteration on the recycle stream)
       20-35 mid cut -> KFS product (sold WET)
       0/20 undersize -> stockpile
  Powers: Bond (M2).  Screen areas: VSMA (M4).

Only the Python standard library is used (json, math, os).
Run:  python3 scripts/verify_zone11_independent.py
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PARAMS_PATH = os.path.join(HERE, "..", "data", "default_parameters.json")

# --------------------------------------------------------------------------
# Documented assumptions I had to decide myself (blind protocol: recorded,
# never checked against the source code).
# --------------------------------------------------------------------------
ASSUMPTIONS = [
    "M1 bypass convention taken in cumulative form: P_prod(x) = min(F(x), F(x80)) + (1-F(x80)) * P_trunc(x), where F is the feed cumulative-passing fraction; F(x80) obtained by linear interpolation in ln(size). Validated against the calc document's CR.5009 numeric table (old settings g=40: reproduces 68.8 % @ 20 mm, 91.9 % @ 40 mm exactly).",
    "M1 truncation implemented as renormalization: P_trunc(x) = P_RR(x)/P_RR(trunc_factor*x80) for x below the truncation size, 1 above (mass rescaled over kept classes, per the calc document).",
    "x80 values (60 and 30 mm) fall between mesh points; all cumulative-curve evaluations at off-mesh sizes use linear interpolation in ln(size), consistent with the log-size grid interpolation the engine documents for the feed curve.",
    "F80/P80 of any stream extracted from its cumulative curve on the mesh grid by linear interpolation in ln(size) (validated: reproduces the document's feed F80 = 180.6 mm and old-settings CR.5009 P80 = 27.96 mm).",
    "Screen partition applied class-by-class on the mesh intervals at a representative size = geometric mean sqrt(lo*hi) of the interval bounds; the bottom interval [0, 0.063] uses rep = 0.063/sqrt(bottom_interval_ratio) per calibration.bottom_interval_ratio = 2.",
    "Double-deck screen modelled sequentially: top-deck (35 mm) partition on the full screen feed; its undersize is the bottom-deck (20 mm) feed; mid cut = bottom-deck oversize.",
    "Closed loop initialized with zero recycle; fixed point iterated until BOTH the relative change of the recycle dry flow AND the max absolute change of its cumulative-passing fractions are < engine.loop_relative_tolerance (1e-6), capped at engine.loop_max_iterations (200). Exact convergence metric wording was my choice; at 1e-6 the fixed point is metric-insensitive.",
    "CR.5009 x80 = g (gap) because its x80 parameter is null in the JSON ('x80 = g validated 2026-08-08').",
    "Bond W uses the F80 of each machine's own feed (fresh feed for CR.5009; converged +35 oversize for CR.5011) and the P80 of its computed product curve, in micrometres (mm*1000).",
    "Installed power = P_net / eta_m with eta_m = 0.75 (the document's only net->installed factor); no extra design margin applied.",
    "VSMA deck loads: U(top deck) = screen feed minus +35 oversize (flow THROUGH the top deck), U(bottom deck) = 0/20 undersize; dry weather, so no wet_capacity_factor derating.",
    "KFS envelope figures read directly at the exact 20 and 35 mm mesh points of the KFS cumulative curve (in-cut = P(35)-P(20)).",
    "Moisture is conserved through zone 1.1 (no drying): wet flow = dry flow / (1 - 0.07) for every stream; KFS sold wet; yield = wet KFS / 250 wet feed.",
    "CR.5011 t10->n floor (m5_n_min = 0.65) checked but not binding at v = 30 m/s.",
    "engine.max_circulating_ratio = 10 treated as a divergence guard only; the loop converges far below it so no action needed.",
    "kfs_passing_curve_pct reported on the base mesh_series_mm (29 meshes), without the 250/320 extension meshes used internally.",
]


# --------------------------------------------------------------------------
# Curve helpers (cumulative % passing, on the extended mesh grid)
# --------------------------------------------------------------------------

def interp_log(xs, ys, x):
    """Linear interpolation of y in ln(x). xs strictly increasing."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (math.log(x) - math.log(xs[i - 1])) / (
                math.log(xs[i]) - math.log(xs[i - 1]))
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def percentile_size(meshes, cum_frac, p):
    """Size at cumulative passing fraction p (log-size interpolation)."""
    if cum_frac[0] >= p:
        return meshes[0]
    for i in range(1, len(meshes)):
        if cum_frac[i] >= p:
            lo, hi = meshes[i - 1], meshes[i]
            clo, chi = cum_frac[i - 1], cum_frac[i]
            if chi == clo:
                return hi
            t = (p - clo) / (chi - clo)
            return math.exp(math.log(lo) + t * (math.log(hi) - math.log(lo)))
    return meshes[-1]


def classes_from_cum(cum_frac):
    """Per-interval mass fractions from cumulative passing at the meshes.
    Interval i: (mesh[i-1], mesh[i]]; interval 0 is (0, mesh[0]]."""
    out = [cum_frac[0]]
    for i in range(1, len(cum_frac)):
        out.append(max(0.0, cum_frac[i] - cum_frac[i - 1]))
    return out


def cum_from_classes(classes):
    tot = sum(classes)
    out, run = [], 0.0
    for m in classes:
        run += m
        out.append(run / tot if tot > 0 else 0.0)
    return out


def rep_sizes(meshes, bottom_ratio):
    """Representative size per interval: geometric mean of the bounds;
    bottom interval lower bound = mesh/bottom_ratio (rep = mesh/sqrt(ratio))."""
    reps = [meshes[0] / math.sqrt(bottom_ratio)]
    for i in range(1, len(meshes)):
        reps.append(math.sqrt(meshes[i - 1] * meshes[i]))
    return reps


# --------------------------------------------------------------------------
# M1 -- truncated Rosin-Rammler crusher product with sub-x80 bypass
# --------------------------------------------------------------------------

def m1_product_cum(meshes, feed_cum_frac, x80, n, trunc_factor, ln_arg):
    """Product cumulative passing (fractions) on the meshes."""
    xc = x80 / (math.log(ln_arg) ** (1.0 / n))
    x_tr = trunc_factor * x80
    p_tr_norm = 1.0 - math.exp(-((x_tr / xc) ** n))

    def p_trunc(x):
        if x >= x_tr:
            return 1.0
        return (1.0 - math.exp(-((x / xc) ** n))) / p_tr_norm

    f_x80 = interp_log(meshes, feed_cum_frac, x80)  # bypass fraction
    broken = 1.0 - f_x80
    prod = []
    for i, x in enumerate(meshes):
        bypass_part = min(feed_cum_frac[i], f_x80)
        prod.append(min(1.0, bypass_part + broken * p_trunc(x)))
    return prod


# --------------------------------------------------------------------------
# M3 -- imperfection-based partition (single deck)
# --------------------------------------------------------------------------

def screen_deck(class_flows, reps, aperture, k_d, s):
    """Split class flows (t/h per interval) into (oversize, undersize)."""
    d50c = k_d * aperture
    over, under = [], []
    for m, x in zip(class_flows, reps):
        rho = 1.0 / (1.0 + (d50c / x) ** s)
        over.append(m * rho)
        under.append(m * (1.0 - rho))
    return over, under


# --------------------------------------------------------------------------
# M2 -- Bond power
# --------------------------------------------------------------------------

def bond_w(wi, bond_coef, p80_mm, f80_mm):
    return bond_coef * wi * (1.0 / math.sqrt(p80_mm * 1000.0)
                             - 1.0 / math.sqrt(f80_mm * 1000.0))


# --------------------------------------------------------------------------
# Main flowsheet
# --------------------------------------------------------------------------

def main():
    with open(PARAMS_PATH) as fh:
        P = json.load(fh)

    base_meshes = list(P["mesh_series_mm"])
    meshes = base_meshes + list(P["engine"]["extension_meshes_mm"])
    reps = rep_sizes(meshes, P["calibration"]["bottom_interval_ratio"]["default"])

    cal = {k: v["default"] for k, v in P["calibration"].items()}

    # ---- feed --------------------------------------------------------------
    moisture = P["feed_product"]["properties"]["moisture_pct"]["default"] / 100.0
    q_wet_feed = 250.0
    q_dry_feed = q_wet_feed * (1.0 - moisture)          # 232.5 t/h dry

    raw = P["feed_product"]["cumulative_passing_curve"]
    pts = sorted(((float(k), v / 100.0) for k, v in raw.items()))
    feed_cum = [interp_log([p[0] for p in pts], [p[1] for p in pts], x)
                for x in meshes]
    feed_f80 = percentile_size(meshes, feed_cum, 0.80)

    # ---- CR.5009 toothed roll crusher (M1) --------------------------------
    g = P["machines"]["CR.5009"]["parameters"]["g"]["default"]
    x80_5009 = P["machines"]["CR.5009"]["parameters"]["x80"]["default"]
    if x80_5009 is None:
        x80_5009 = g                                     # x80 follows the gap
    n_5009 = P["machines"]["CR.5009"]["parameters"]["n"]["default"]

    cr09_cum = m1_product_cum(meshes, feed_cum, x80_5009, n_5009,
                              cal["trunc_factor"], cal["m1_ln_arg"])
    cr09_classes = [q_dry_feed * m for m in classes_from_cum(cr09_cum)]
    cr09_p80 = percentile_size(meshes, cr09_cum, 0.80)

    wi = cal["Wi"]
    if P["feed_product"]["properties"]["Wi_kWht"]["default"] is not None:
        wi = P["feed_product"]["properties"]["Wi_kWht"]["default"]
    w_5009 = bond_w(wi, cal["bond_coef"], cr09_p80, feed_f80)
    pnet_5009 = w_5009 * q_dry_feed
    pinst_5009 = pnet_5009 / cal["eta_m"]

    # ---- SR.5007 screen settings (M3) -------------------------------------
    a1 = P["machines"]["SR.5007"]["parameters"]["a1"]["default"]   # 35 mm
    a2 = P["machines"]["SR.5007"]["parameters"]["a2"]["default"]   # 20 mm
    imperfection = P["machines"]["SR.5007"]["parameters"]["I"]["default"]
    s_sharp = math.log(cal["m3_ln_arg"]) / math.log(1.0 / (1.0 - imperfection))
    k_d = cal["k_d"]

    # ---- CR.5011 impact crusher settings (M5 -> M1) -----------------------
    v_rot = P["machines"]["CR.5011"]["parameters"]["v"]["default"]  # 30 m/s
    css = P["machines"]["CR.5011"]["parameters"]["x80"]["default"]  # 30 mm
    ecs = v_rot ** 2 / cal["ecs_div"]
    t10 = cal["A_j"] * (1.0 - math.exp(-cal["b_j"] * ecs))
    n_5011 = max(cal["m5_n_min"], (cal["m5_t10_ref"] / t10) ** cal["m5_n_exp"])

    # ---- closed loop: fixed-point iteration on the recycle stream ---------
    tol = P["engine"]["loop_relative_tolerance"]
    max_it = P["engine"]["loop_max_iterations"]

    nclass = len(meshes)
    recycle = [0.0] * nclass          # CR.5011 product, t/h per class
    prev_q, prev_cum = 0.0, [0.0] * nclass
    converged = False
    for _ in range(max_it):
        # blend fresh crusher product with recycle -> screen feed
        sf = [a + b for a, b in zip(cr09_classes, recycle)]
        # top deck 35 mm
        over35, thru35 = screen_deck(sf, reps, a1, k_d, s_sharp)
        # bottom deck 20 mm
        kfs_cls, under20 = screen_deck(thru35, reps, a2, k_d, s_sharp)
        # CR.5011 on the +35 oversize
        q_over = sum(over35)
        if q_over > 0.0:
            over_cum = cum_from_classes(over35)
            cr11_cum = m1_product_cum(meshes, over_cum, css, n_5011,
                                      cal["trunc_factor"], cal["m1_ln_arg"])
            recycle = [q_over * m for m in classes_from_cum(cr11_cum)]
        else:
            recycle = [0.0] * nclass
        # convergence on both flow and curve
        new_cum = cum_from_classes(recycle) if q_over > 0 else [0.0] * nclass
        dq = abs(q_over - prev_q) / q_over if q_over > 0 else 0.0
        dc = max(abs(x - y) for x, y in zip(new_cum, prev_cum))
        prev_q, prev_cum = q_over, new_cum
        if dq < tol and dc < tol:
            converged = True
            break
    if not converged:
        raise RuntimeError("closed loop did not converge")

    # ---- converged streams -------------------------------------------------
    q_sf = sum(sf)
    q_over35 = sum(over35)
    q_kfs = sum(kfs_cls)
    q_020 = sum(under20)

    sf_cum = cum_from_classes(sf)
    over_cum = cum_from_classes(over35)
    kfs_cum = cum_from_classes(kfs_cls)
    cr11_prod_cum = cum_from_classes(recycle)

    over_f80 = percentile_size(meshes, over_cum, 0.80)
    cr11_p80 = percentile_size(meshes, cr11_prod_cum, 0.80)

    # ---- CR.5011 Bond power ------------------------------------------------
    w_5011 = bond_w(wi, cal["bond_coef"], cr11_p80, over_f80)
    pnet_5011 = w_5011 * q_over35

    # ---- SR.5007 VSMA areas (M4), dry weather ------------------------------
    qb_top = cal["qb_coef"] * a1 ** cal["qb_exp"]
    qb_bot = cal["qb_coef"] * a2 ** cal["qb_exp"]
    u_top = q_sf - q_over35            # flow through the top deck
    u_bot = q_020                      # flow through the bottom deck
    area_top = u_top * cal["f_p"] / (qb_top * cal["f0"])
    area_bot = u_bot * cal["f_p"] / (qb_bot * cal["f0"])

    # ---- KFS product (sold wet) -------------------------------------------
    kfs_wet = q_kfs / (1.0 - moisture)
    kfs_yield = kfs_wet / q_wet_feed * 100.0
    i20 = meshes.index(20.0)
    i35 = meshes.index(35.0)
    kfs_below20 = kfs_cum[i20] * 100.0
    kfs_above35 = (1.0 - kfs_cum[i35]) * 100.0
    kfs_incut = (kfs_cum[i35] - kfs_cum[i20]) * 100.0

    result = {
        "kfs_yield_pct": round(kfs_yield, 2),
        "kfs_tph_wet": round(kfs_wet, 3),
        "kfs_psd": {
            "in_cut_20_35": round(kfs_incut, 2),
            "below_20": round(kfs_below20, 2),
            "above_35": round(kfs_above35, 2),
        },
        "stream_0_20_dry_tph": round(q_020, 3),
        "recirculation_tph": round(q_over35, 3),
        "CR5009": {
            "W_kWh_t": round(w_5009, 4),
            "P_net_kW": round(pnet_5009, 2),
            "P_installed_kW": round(pinst_5009, 2),
            "F80_mm": round(feed_f80, 2),
            "P80_mm": round(cr09_p80, 2),
            "throughput_tph": round(q_dry_feed, 3),
            "x80_mm": x80_5009,
        },
        "CR5011": {
            "Ecs_kWh_t": round(ecs, 4),
            "t10_pct": round(t10, 3),
            "n": round(n_5011, 4),
            "W_kWh_t": round(w_5011, 4),
            "P_net_kW": round(pnet_5011, 2),
            "F80_mm": round(over_f80, 2),
            "P80_mm": round(cr11_p80, 2),
            "throughput_tph": round(q_over35, 3),
        },
        "SR5007": {
            "feed_tph": round(q_sf, 3),
            "areas": {
                "top_deck": round(area_top, 3),
                "bottom_deck": round(area_bot, 3),
            },
        },
        "kfs_passing_curve_pct": {
            str(m): round(kfs_cum[i] * 100.0, 3)
            for i, m in enumerate(meshes) if m in base_meshes
        },
        "assumptions": ASSUMPTIONS,
    }

    print(json.dumps(result, indent=2))

    # mass-balance sanity check (dry)
    gap = abs(q_dry_feed - (q_kfs + q_020)) / q_dry_feed
    print("\n# dry mass balance: feed {:.3f} = KFS {:.3f} + 0/20 {:.3f} "
          "(relative gap {:.2e})".format(q_dry_feed, q_kfs, q_020, gap))
    return result


if __name__ == "__main__":
    main()
