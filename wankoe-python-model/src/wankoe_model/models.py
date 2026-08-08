"""Modèles de calcul communs M1–M8 (cahier des charges §3.0).

Chaque fonction est pure : elle reçoit ses entrées et TOUS ses coefficients
en arguments — aucun coefficient n'est codé en dur ici. Les valeurs par
défaut vivent dans data/parametres_defaut.json (section "calibration").

Les identités mathématiques structurelles (ln 5 de Rosin-Rammler, ln 9 de
Karra, facteur 10 de Bond) font partie des lois elles-mêmes (§ "frontière
paramètres / codé en dur" du cahier des charges) mais restent néanmoins
surchargables via le dictionnaire ``calib`` pour les besoins de calage.
"""

from __future__ import annotations

import math

from .grid import PSD


# --------------------------------------------------------------------- M1
def m1_produit_concassage(psd_alim: PSD, x80: float, n: float, calib: dict) -> PSD:
    """M1 — produit Rosin-Rammler tronqué.

    xc = x80 / (ln 5)^(1/n) ;  P(x) = 1 − exp(−(x/xc)^n).
    Produit tronqué au-dessus de trunc_factor·x80 (masse réétalée) ;
    la fraction du flux plus fine que x80 passe inchangée.
    """
    trunc = float(calib["trunc_factor"])
    ln5 = float(calib.get("m1_ln_arg", 5.0))
    xc = x80 / (math.log(ln5) ** (1.0 / n))
    xt = trunc * x80

    def rr(x: float) -> float:
        return 1.0 - math.exp(-((x / xc) ** n))

    p_xt = rr(xt)
    if p_xt <= 0:
        raise ValueError("M1 : troncature dégénérée (vérifier x80, n, trunc_factor)")

    phi_fin = psd_alim.passant_a(x80)  # fraction du flux plus fine que x80 : inchangée
    mailles = psd_alim.mailles
    passant = []
    for x in mailles:
        part_fine = min(psd_alim.passant_a(x), phi_fin)
        part_concassee = (1.0 - phi_fin) * min(1.0, rr(x) / p_xt)
        passant.append(part_fine + part_concassee)
    return PSD(mailles, passant)


# --------------------------------------------------------------------- M2
def m2_puissance_bond(q_th: float, f80_mm: float, p80_mm: float, calib: dict) -> dict:
    """M2 — loi de Bond. W = coef·Wi·(1/√P80 − 1/√F80), P80/F80 en µm."""
    wi = float(calib["Wi"])
    coef = float(calib.get("bond_coef", 10.0))
    eta_m = float(calib["eta_m"])
    f80_um, p80_um = f80_mm * 1000.0, p80_mm * 1000.0
    w = coef * wi * (1.0 / math.sqrt(p80_um) - 1.0 / math.sqrt(f80_um))
    w = max(0.0, w)  # produit plus grossier que l'alimentation : énergie nulle
    p_net = w * q_th
    return {
        "W_kWh_t": w,
        "P_net_kW": p_net,
        "P_inst_kW": p_net / eta_m,
        "F80_mm": f80_mm,
        "P80_mm": p80_mm,
    }


# --------------------------------------------------------------------- M3
def m3_partition_karra(
    q_th: float, psd: PSD, a_mm: float, imperfection: float, calib: dict
) -> dict:
    """M3 — partition de crible (Karra).

    d50c = a·k_d ; s = ln 9 / ln(1/I) ; ro(x) = 1/(1+(d50c/x)^s).
    Retourne refus et passant : débits + PSD.
    """
    k_d = float(calib["k_d"])
    ln9 = float(calib.get("m3_ln_arg", 9.0))
    d50c = a_mm * k_d
    if not 0.0 < imperfection < 1.0:
        raise ValueError("M3 : imperfection I doit être dans ]0;1[")
    s = math.log(ln9) / math.log(1.0 / imperfection)

    fractions = psd.fractions_tranches()
    reps = psd.tailles_representatives()
    f_refus, f_passant = [], []
    for f, x in zip(fractions, reps):
        ro = 1.0 / (1.0 + (d50c / x) ** s)
        f_refus.append(f * ro)
        f_passant.append(f * (1.0 - ro))
    q_refus = q_th * sum(f_refus)
    q_passant = q_th * sum(f_passant)
    out = {"q_refus_th": q_refus, "q_passant_th": q_passant}
    out["psd_refus"] = PSD.depuis_tranches(psd.mailles, f_refus) if q_refus > 1e-12 else None
    out["psd_passant"] = PSD.depuis_tranches(psd.mailles, f_passant) if q_passant > 1e-12 else None
    return out


# --------------------------------------------------------------------- M4
def m4_surface_crible(u_passant_th: float, a_mm: float, calib: dict) -> dict:
    """M4 — surface de crible (VSMA / Fontaine). Qb = qb_coef·a^qb_exp ;
    A = U·f_p / (Qb·f0)."""
    qb = float(calib.get("qb_coef", 14.0)) * (a_mm ** float(calib.get("qb_exp", 0.6)))
    surface = (u_passant_th * float(calib["f_p"])) / (qb * float(calib["f0"]))
    return {"Qb_th_m2": qb, "A_requise_m2": surface}


# --------------------------------------------------------------------- M5
def m5_uniformite_impact(v_ms: float, calib: dict) -> dict:
    """M5 — fragmentation par impact : Ecs = v²/ecs_div ;
    t10 = A_j·(1−exp(−b_j·Ecs)) ; n = max(n_min ; (t10_ref/t10)^n_exp)."""
    ecs = v_ms * v_ms / float(calib.get("ecs_div", 7200.0))
    t10 = float(calib["A_j"]) * (1.0 - math.exp(-float(calib["b_j"]) * ecs))
    if t10 <= 0:
        raise ValueError("M5 : t10 nul (vérifier v, A_j, b_j)")
    n = max(
        float(calib.get("m5_n_min", 0.65)),
        (float(calib.get("m5_t10_ref", 30.0)) / t10) ** float(calib.get("m5_n_exp", 0.30)),
    )
    return {"Ecs_kWh_t": ecs, "t10_pct": t10, "n": n}


# --------------------------------------------------------------------- M6
def m6_sechage(w_humide_th: float, m_in_pct: float, m_out_pct: float, calib: dict) -> dict:
    """M6 — séchage : bilan hydrique + thermique (humidités en base humide)."""
    sec = w_humide_th * (1.0 - m_in_pct / 100.0)
    w_out = sec / (1.0 - m_out_pct / 100.0)
    e_vap = w_humide_th - w_out  # t/h d'eau évaporée
    kg_s = 1000.0 / 3600.0  # t/h → kg/s (conversion d'unités, pas un paramètre)
    q_kw = (e_vap * kg_s) * (float(calib["L_v"]) + float(calib["c_e"]) * float(calib["dT_e"])) + (
        sec * kg_s
    ) * float(calib["c_s"]) * float(calib["dT_s"])
    p_bruleur = q_kw / float(calib["eta_th"])
    v_tambour = (e_vap * 1000.0) / float(calib["I_ev"])  # kg/h ÷ kg/m³·h
    return {
        "q_sec_th": sec,
        "q_sortie_humide_th": w_out,
        "eau_evaporee_th": e_vap,
        "Q_thermique_kW": q_kw,
        "P_bruleur_kW": p_bruleur,
        "V_tambour_m3": v_tambour,
    }


# --------------------------------------------------------------------- M7
def m7_passe_broyeur_lit(psd_alim: PSD, gap_mm: float, calib: dict) -> PSD:
    """M7 — une passe du broyeur à cylindres en lit (ML.26).

    Deux mécanismes (cahier des charges §3.0-M7) :
    1. COMPRESSION du +gap → produit Rosin-Rammler (M1) avec x80 = gap.
       [HYPOTHÈSE H-M7-1, comp_lam non spécifié par le CdC] : comp_lam agit
       comme taux de réduction maximal par passe : x80 = max(gap, F80_gros/comp_lam).
       En régime normal (F80/comp_lam < gap) on retombe exactement sur x80 = gap.
    2. ATTRITION inter-particulaire du lit → fines : une fraction S_att de la
       masse est convertie en fines [HYPOTHÈSE H-M7-2 : distribution
       Rosin-Rammler de paramètres m7_x80_att / m7_n_att].
    Tous les coefficients sont des paramètres à caler par essai.
    """
    comp_lam = float(calib["comp_lam"])
    s_att = float(calib["S_att"])
    n_comp = float(calib["m7_n_comp"])

    # fraction grossière (+gap) : son F80 borne la réduction par passe
    phi_fin = psd_alim.passant_a(gap_mm)
    if phi_fin < 1.0 - 1e-9:
        f_gros = []
        fr = psd_alim.fractions_tranches()
        reps = psd_alim.tailles_representatives()
        f_gros = [f if x > gap_mm else 0.0 for f, x in zip(fr, reps)]
        psd_gros = PSD.depuis_tranches(psd_alim.mailles, f_gros)
        f80_gros = psd_gros.p80()
    else:
        f80_gros = gap_mm
    x80_eff = max(gap_mm, f80_gros / comp_lam)

    produit_comp = m1_produit_concassage(psd_alim, x80_eff, n_comp, calib)

    # attrition : S_att de la masse convertie en fines RR(m7_x80_att, m7_n_att)
    fines = m1_produit_concassage(
        # alimentation fictive intégralement grossière → produit = pure RR fines
        PSD.depuis_tranches(psd_alim.mailles, [0.0] * (len(psd_alim.mailles) - 1) + [1.0]),
        float(calib["m7_x80_att"]),
        float(calib["m7_n_att"]),
        calib,
    )
    mailles = psd_alim.mailles
    passant = [
        (1.0 - s_att) * produit_comp.passant[i] + s_att * fines.passant[i]
        for i in range(len(mailles))
    ]
    return PSD(mailles, passant)


# --------------------------------------------------------------------- M8
def m8_classification_air(
    q_fines_th: float, psd_fines: PSD, coupe_um: float, phi_mesure_pct: float | None, calib: dict
) -> dict:
    """M8 — séparateur à air : produit_fin = feed·Φ(<coupe)·η_cl ; Q_air = fin/λ.

    Si Φ(<coupe) n'est pas mesuré (phi_mesure_pct None), il est estimé sur la
    courbe calculée → drapeau « non certifié » (cahier des charges, SP.36).
    """
    eta_cl = float(calib["eta_cl"])
    lam = float(calib["lambda"])
    coupe_mm = coupe_um / 1000.0
    if phi_mesure_pct is not None:
        phi = phi_mesure_pct / 100.0
        certifie = True
    else:
        phi = psd_fines.passant_a(coupe_mm)
        certifie = False
    q_fin = q_fines_th * phi * eta_cl
    q_air_m3h = (q_fin * 1000.0) / lam if lam > 0 else float("inf")

    # PSD du produit fin = tranche < coupe du feed ; reste = complément
    fr = psd_fines.fractions_tranches()
    reps = psd_fines.tailles_representatives()
    f_fin = [f if x <= coupe_mm else 0.0 for f, x in zip(fr, reps)]
    psd_fin = PSD.depuis_tranches(psd_fines.mailles, f_fin) if sum(f_fin) > 0 else psd_fines
    q_reste = q_fines_th - q_fin
    # le reste = feed − produit fin (mélange inverse)
    f_reste = [
        max(0.0, ft - (q_fin / q_fines_th) * ff / max(sum(f_fin), 1e-12))
        for ft, ff in zip(fr, f_fin)
    ] if q_fines_th > 0 else fr
    psd_reste = (
        PSD.depuis_tranches(psd_fines.mailles, f_reste) if sum(f_reste) > 0 else psd_fines
    )
    return {
        "q_produit_fin_th": q_fin,
        "q_reste_th": q_reste,
        "psd_produit_fin": psd_fin,
        "psd_reste": psd_reste,
        "Phi_coupe": phi,
        "certifie": certifie,
        "Q_air_m3h": q_air_m3h,
    }


def m8_cyclone_d50(calib: dict) -> float | None:
    """M8 — d50 cyclone (Lapple) : √(9·µ·b / (2π·N_e·v_in·(ρ_p−ρ_a))), en µm.
    Retourne None si la largeur d'entrée b n'est pas renseignée."""
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
