"""Common calculation models M1-M8 (specification §3.0).

Every function is pure: it receives its inputs and ALL its coefficients as
arguments — no coefficient is hardcoded here. Default values live in
data/default_parameters.json (section "calibration").

Coefficient access is STRICT (``calib["key"]``): a missing or misspelled
key raises immediately instead of silently falling back to a hidden default
(audit finding 1.4).
"""

from __future__ import annotations

import math

from .grid import PSD


# --------------------------------------------------------------------- M1
def m1_crusher_product(feed_psd: PSD, x80: float, n: float, calib: dict) -> PSD:
    """M1 — truncated Rosin-Rammler crusher product.

    xc = x80 / (ln arg)^(1/n) ;  P(x) = 1 − exp(−(x/xc)^n).
    Product truncated above trunc_factor·x80 (mass rescaled); the feed
    fraction already finer than x80 passes through unchanged.
    """
    trunc = float(calib["trunc_factor"])
    ln_arg = float(calib["m1_ln_arg"])
    xc = x80 / (math.log(ln_arg) ** (1.0 / n))
    xt = trunc * x80

    def rr(x: float) -> float:
        return 1.0 - math.exp(-((x / xc) ** n))

    p_xt = rr(xt)
    if p_xt <= 0:
        raise ValueError("M1: degenerate truncation (check x80, n, trunc_factor)")

    phi_fine = feed_psd.passing_at(x80)  # feed fraction finer than x80: unchanged
    meshes = feed_psd.meshes
    feed_passing = feed_psd.passing  # meshes ARE the psd grid: direct indexing is exact
    coarse_share = 1.0 - phi_fine
    passing = []
    for i, x in enumerate(meshes):
        fine_part = feed_passing[i] if feed_passing[i] < phi_fine else phi_fine
        crushed = rr(x) / p_xt
        passing.append(fine_part + coarse_share * (crushed if crushed < 1.0 else 1.0))
    passing[-1] = 1.0
    return PSD._trusted(meshes, passing)


# --------------------------------------------------------------------- M2
def m2_bond_power(q_tph: float, f80_mm: float, p80_mm: float, calib: dict) -> dict:
    """M2 — Bond law. W = coef·Wi·(1/√P80 − 1/√F80), P80/F80 in µm."""
    wi = float(calib["Wi"])
    coef = float(calib["bond_coef"])
    eta_m = float(calib["eta_m"])
    f80_um, p80_um = f80_mm * 1000.0, p80_mm * 1000.0
    w = coef * wi * (1.0 / math.sqrt(p80_um) - 1.0 / math.sqrt(f80_um))
    w = max(0.0, w)  # product coarser than feed: zero energy
    p_net = w * q_tph
    return {
        "W_kWh_t": w,
        "P_net_kW": p_net,
        "P_installed_kW": p_net / eta_m,
        "F80_mm": f80_mm,
        "P80_mm": p80_mm,
    }


# --------------------------------------------------------------------- M3
def m3_karra_partition(
    q_tph: float, psd: PSD, aperture_mm: float, imperfection: float, calib: dict
) -> dict:
    """M3 — screen partition (Karra).

    d50c = a·k_d ; s = ln arg / ln(1/(1−I)) ; ro(x) = 1/(1+(d50c/x)^s).
    Returns oversize and undersize: flow rates + PSD.

    I is a CLASSIC imperfection: higher = worse separation (flatter
    partition). The spec's written form s = ln9/ln(1/I) contradicted its
    own narrative (I degrades up to ~0.9 under rain); client arbitration
    2026-08-08 (option A): the narrative wins, hence the (1−I) substitution.
    """
    k_d = float(calib["k_d"])
    ln_arg = float(calib["m3_ln_arg"])
    d50c = aperture_mm * k_d
    if not 0.0 < imperfection < 1.0:
        raise ValueError("M3: imperfection I must be within ]0;1[")
    s = math.log(ln_arg) / math.log(1.0 / (1.0 - imperfection))

    fractions = psd.interval_fractions()
    reps = psd.representative_sizes(float(calib["bottom_interval_ratio"]))
    f_over, f_under = [], []
    for f, x in zip(fractions, reps):
        # computed in log space so an ideal screen (I -> 0, s -> inf)
        # degrades to a clean step partition instead of overflowing
        t = s * math.log(d50c / x)
        if t > 700.0:
            ro = 0.0
        elif t < -700.0:
            ro = 1.0
        else:
            ro = 1.0 / (1.0 + math.exp(t))
        f_over.append(f * ro)
        f_under.append(f * (1.0 - ro))
    q_over = q_tph * sum(f_over)
    q_under = q_tph * sum(f_under)
    out = {"oversize_tph": q_over, "undersize_tph": q_under}
    out["oversize_psd"] = PSD.from_intervals(psd.meshes, f_over) if q_over > 1e-12 else None
    out["undersize_psd"] = PSD.from_intervals(psd.meshes, f_under) if q_under > 1e-12 else None
    return out


# --------------------------------------------------------------------- M4
def m4_screen_area(
    undersize_tph: float, aperture_mm: float, calib: dict, capacity_factor: float = 1.0
) -> dict:
    """M4 — screen area (VSMA / Fontaine). Qb = qb_coef·a^qb_exp ;
    A = U·f_p / (Qb·f0).

    ``capacity_factor`` derates the basic capacity for wet screening (spec
    M3/SR.5115 notes: "la capacité chute" under rain) — pass
    calib["wet_capacity_factor"] when the weather is rain."""
    qb = float(calib["qb_coef"]) * (aperture_mm ** float(calib["qb_exp"])) * capacity_factor
    area = (undersize_tph * float(calib["f_p"])) / (qb * float(calib["f0"]))
    return {"Qb_tph_m2": qb, "required_area_m2": area}


# --------------------------------------------------------------------- M5
def m5_impact_uniformity(v_ms: float, calib: dict) -> dict:
    """M5 — impact breakage: Ecs = v²/ecs_div ;
    t10 = A_j·(1−exp(−b_j·Ecs)) ; n = max(n_min ; (t10_ref/t10)^n_exp)."""
    ecs = v_ms * v_ms / float(calib["ecs_div"])
    t10 = float(calib["A_j"]) * (1.0 - math.exp(-float(calib["b_j"]) * ecs))
    if t10 <= 0:
        raise ValueError("M5: t10 is zero (check v, A_j, b_j)")
    n = max(
        float(calib["m5_n_min"]),
        (float(calib["m5_t10_ref"]) / t10) ** float(calib["m5_n_exp"]),
    )
    return {"Ecs_kWh_t": ecs, "t10_pct": t10, "n": n}


# --------------------------------------------------------------------- M6
def m6_drying(wet_feed_tph: float, m_in_pct: float, m_out_pct: float, calib: dict) -> dict:
    """M6 — drying: water + heat balance (moistures on a wet basis).

    When the feed is already drier than the target (m_in <= m_out) the
    dryer cannot ADD water: evaporation clamps to zero and the outlet
    keeps the feed moisture (flag ``no_drying`` for the caller's alert).
    """
    no_drying = m_in_pct <= m_out_pct
    if no_drying:
        m_out_pct = m_in_pct
    dry = wet_feed_tph * (1.0 - m_in_pct / 100.0)
    wet_out = dry / (1.0 - m_out_pct / 100.0)
    evaporated = wet_feed_tph - wet_out  # t/h of evaporated water
    kg_s = 1000.0 / 3600.0  # t/h -> kg/s (unit conversion, not a parameter)
    duty_kw = (evaporated * kg_s) * (
        float(calib["L_v"]) + float(calib["c_e"]) * float(calib["dT_e"])
    ) + (dry * kg_s) * float(calib["c_s"]) * float(calib["dT_s"])
    burner_kw = duty_kw / float(calib["eta_th"])
    drum_m3 = (evaporated * 1000.0) / float(calib["I_ev"])  # kg/h ÷ kg/m³·h
    return {
        "dry_solids_tph": dry,
        "wet_output_tph": wet_out,
        "evaporated_water_tph": evaporated,
        "thermal_duty_kW": duty_kw,
        "burner_power_kW": burner_kw,
        "drum_volume_m3": drum_m3,
        "no_drying": no_drying,
        "m_out_effective_pct": m_out_pct,
    }


# --------------------------------------------------------------------- M7
_M7_FINES_CACHE: dict = {}


def _m7_attrition_fines(meshes: list, calib: dict) -> PSD:
    """Attrition fines distribution: pure RR(m7_x80_att, m7_n_att).

    Identical at every fixed-point iteration of the ML.26 loop, so it is
    memoized (13 % of scenario runtime — expert review 2026-08-08). PSDs
    are immutable in practice; sharing the cached instance is safe.
    """
    key = (
        tuple(meshes),
        float(calib["m7_x80_att"]),
        float(calib["m7_n_att"]),
        float(calib["trunc_factor"]),
        float(calib["m1_ln_arg"]),
    )
    cached = _M7_FINES_CACHE.get(key)
    if cached is None:
        if len(_M7_FINES_CACHE) > 64:
            _M7_FINES_CACHE.clear()
        # fictitious all-coarse feed -> product is a pure RR fines distribution
        all_coarse = PSD.from_intervals(meshes, [0.0] * (len(meshes) - 1) + [1.0])
        cached = m1_crusher_product(all_coarse, key[1], key[2], calib)
        _M7_FINES_CACHE[key] = cached
    return cached


def m7_bed_mill_pass(feed_psd: PSD, gap_mm: float, calib: dict) -> PSD:
    """M7 — one pass of the bed roller mill (ML.26).

    Two mechanisms (specification §3.0-M7):
    1. COMPRESSION of the +gap fraction -> Rosin-Rammler product (M1) with
       x80 = gap. [HYPOTHESIS H-M7-1, comp_lam not specified by the spec]:
       comp_lam acts as the maximum reduction ratio per pass:
       x80 = max(gap, coarse_F80/comp_lam). In the normal regime
       (F80/comp_lam < gap) this degenerates to exactly x80 = gap.
    2. Inter-particle bed ATTRITION -> fines: a fraction S_att of the mass is
       converted to fines [HYPOTHESIS H-M7-2: Rosin-Rammler distribution with
       parameters m7_x80_att / m7_n_att].
    All coefficients are parameters to be fitted by plant trials.
    """
    comp_lam = float(calib["comp_lam"])
    s_att = float(calib["S_att"])
    n_comp = float(calib["m7_n_comp"])
    bottom_ratio = float(calib["bottom_interval_ratio"])

    # coarse (+gap) fraction: its F80 bounds the per-pass reduction
    phi_fine = feed_psd.passing_at(gap_mm)
    if phi_fine < 1.0 - 1e-9:
        fr = feed_psd.interval_fractions()
        reps = feed_psd.representative_sizes(bottom_ratio)
        f_coarse = [f if x > gap_mm else 0.0 for f, x in zip(fr, reps)]
        coarse_psd = PSD.from_intervals(feed_psd.meshes, f_coarse)
        coarse_f80 = coarse_psd.p80()
    else:
        coarse_f80 = gap_mm
    effective_x80 = max(gap_mm, coarse_f80 / comp_lam)

    compressed = m1_crusher_product(feed_psd, effective_x80, n_comp, calib)
    fines = _m7_attrition_fines(feed_psd.meshes, calib)
    meshes = feed_psd.meshes
    passing = [
        (1.0 - s_att) * compressed.passing[i] + s_att * fines.passing[i]
        for i in range(len(meshes))
    ]
    return PSD(meshes, passing)


# --------------------------------------------------------------------- M8
def m8_air_classification(
    q_fines_tph: float, fines_psd: PSD, cut_um: float, phi_measured_pct: float | None, calib: dict
) -> dict:
    """M8 — air classifier: fine_product = feed·Φ(<cut)·η_cl ; Q_air = fine/λ.

    If Φ(<cut) has not been measured (phi_measured_pct None), it is estimated
    from the computed curve -> "not certified" flag (specification, SP.36).
    """
    eta_cl = float(calib["eta_cl"])
    lam = float(calib["lambda"])
    cut_mm = cut_um / 1000.0

    fr = fines_psd.interval_fractions()
    reps = fines_psd.representative_sizes(float(calib["bottom_interval_ratio"]))
    below = [x <= cut_mm for x in reps]
    sum_below = sum(f for f, b in zip(fr, below) if b)
    warning = None

    if phi_measured_pct is not None:
        phi = phi_measured_pct / 100.0
        certified = True
        # reconcile the modelled curve with the MEASURED below-cut content:
        # rescale below- and above-cut interval masses so the split stays
        # mass-exact per interval (expert review 2026-08-08 — the previous
        # remainder construction lost mass when phi differed from the curve)
        if 0.0 < sum_below < 1.0 and 0.0 <= phi <= 1.0:
            scale_below = phi / sum_below
            scale_above = (1.0 - phi) / (1.0 - sum_below)
            f_adj = [
                f * (scale_below if b else scale_above) for f, b in zip(fr, below)
            ]
            if max(scale_below, 1.0 / max(scale_below, 1e-12)) > 3.0:
                warning = (
                    "measured Phi differs from the modelled fines curve by more "
                    "than 3x — re-measure the 0-1.5 mm curve"
                )
        else:
            f_adj = fr
            warning = (
                "measured Phi inconsistent with the modelled fines curve "
                "(no below-cut content on the grid) — PSDs unreliable"
            )
    else:
        # phi from the same interval masses used for the PSD split, so the
        # tonnage and the curves stay consistent for off-grid cuts too
        phi = sum_below
        certified = False
        f_adj = fr

    q_fine = q_fines_tph * phi * eta_cl
    q_rest = q_fines_tph - q_fine
    q_air_m3h = (q_fine * 1000.0) / lam if lam > 0 else float("inf")

    # per-interval split: the classifier extracts eta_cl of the below-cut
    # mass; everything else stays in the remainder (mass-exact by interval)
    f_fine = [f * eta_cl if b else 0.0 for f, b in zip(f_adj, below)]
    f_rest = [f - ff for f, ff in zip(f_adj, f_fine)]
    fine_psd = (
        PSD.from_intervals(fines_psd.meshes, f_fine) if sum(f_fine) > 0 else fines_psd
    )
    rest_psd = (
        PSD.from_intervals(fines_psd.meshes, f_rest) if sum(f_rest) > 0 else fines_psd
    )
    return {
        "fine_product_tph": q_fine,
        "remainder_tph": q_rest,
        "fine_product_psd": fine_psd,
        "remainder_psd": rest_psd,
        "Phi_cut": phi,
        "certified": certified,
        "Q_air_m3h": q_air_m3h,
        "warning": warning,
    }


def m8_cyclone_d50(calib: dict) -> float | None:
    """M8 — cyclone d50 (Lapple): √(9·µ·b / (2π·N_e·v_in·(ρ_p−ρ_a))), in µm.
    Returns None when the inlet width b is not provided."""
    b = calib.get("b_cyclone")
    if b is None:
        return None
    num = 9.0 * float(calib["mu_air"]) * float(b)
    den = (
        2.0
        * math.pi
        * float(calib["N_e"])
        * float(calib["v_in_cyclone"])
        * (float(calib["rho_p"]) - float(calib["rho_a"]))
    )
    return math.sqrt(num / den) * 1e6
