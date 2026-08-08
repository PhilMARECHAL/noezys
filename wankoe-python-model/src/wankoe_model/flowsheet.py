"""Flowsheet statique des zones 1.1 / 1.2 / 1.3 (cahier des charges §4).

Structure FIXE, fidèle aux schémas de principe en blocs. Les boucles fermées
sont résolues par itération de point fixe sur le flux de recirculation
(critères dans la section "moteur" des paramètres). Chaque machine est
désignée par son code exact (§2 — codification).

Un « flux » est un dict : {"q": t/h de solide SEC, "psd": PSD, "hum": % base
humide}. L'eau est portée par l'humidité et n'est retirée qu'au séchoir
(§1.4) ; les bilans sont bouclés sur le solide sec et sur l'eau.
"""

from __future__ import annotations

from .grid import PSD
from . import models


def _flux(q: float, psd: PSD, hum: float) -> dict:
    return {"q": q, "psd": psd, "hum": hum}


def _melange(flux_list: list[dict]) -> dict:
    actifs = [f for f in flux_list if f["q"] > 1e-12]
    if not actifs:
        raise ValueError("mélange de flux vides")
    q, psd = PSD.melange([(f["q"], f["psd"]) for f in actifs])
    hum = sum(f["q"] / (1.0 - f["hum"] / 100.0) * f["hum"] / 100.0 for f in actifs)
    eau = hum  # t/h d'eau
    humide = sum(f["q"] / (1.0 - f["hum"] / 100.0) for f in actifs)
    return _flux(q, psd, 100.0 * eau / humide if humide > 0 else 0.0)


def _crible_karra(flux: dict, a_mm: float, imperfection: float, calib: dict):
    """Un étage de crible : retourne (flux_refus, flux_passant) — même humidité."""
    part = models.m3_partition_karra(flux["q"], flux["psd"], a_mm, imperfection, calib)
    refus = (
        _flux(part["q_refus_th"], part["psd_refus"], flux["hum"])
        if part["psd_refus"] is not None
        else None
    )
    passant = (
        _flux(part["q_passant_th"], part["psd_passant"], flux["hum"])
        if part["psd_passant"] is not None
        else None
    )
    return refus, passant


def _percuteur(flux: dict, v_ms: float, x80_mm: float, calib: dict):
    """Concasseur à percussion (M5 → n, M1 → produit, M2 → puissance)."""
    m5 = models.m5_uniformite_impact(v_ms, calib)
    psd_out = models.m1_produit_concassage(flux["psd"], x80_mm, m5["n"], calib)
    bond = models.m2_puissance_bond(flux["q"], flux["psd"].p80(), psd_out.p80(), calib)
    return _flux(flux["q"], psd_out, flux["hum"]), {**m5, **bond, "q_traite_th": flux["q"]}


def _boucle_point_fixe(iterer, moteur: dict, alertes: list, nom_boucle: str):
    """Itère ``iterer(recycle) -> (recycle', sorties)`` jusqu'à convergence.

    Convergence sur le débit ET la courbe du flux recyclé. Alarme si la
    charge circulante dépasse ``ratio_circulant_max``.
    """
    max_iter = int(moteur["boucle_max_iterations"])
    tol = float(moteur["boucle_tolerance_relative"])
    recycle = None
    for _ in range(max_iter):
        nouveau, sorties = iterer(recycle)
        if recycle is None and nouveau is None:
            return None, sorties
        if recycle is not None and nouveau is not None:
            dq = abs(nouveau["q"] - recycle["q"]) / max(recycle["q"], 1e-9)
            dpsd = max(
                abs(a - b) for a, b in zip(nouveau["psd"].passant, recycle["psd"].passant)
            )
            if dq < tol and dpsd < tol:
                return nouveau, sorties
        recycle = nouveau
    alertes.append(f"{nom_boucle} : boucle non convergée après {max_iter} itérations")
    return recycle, sorties


# ===================================================================== 1.1
def zone_1_1(alimentation: dict, params: dict, mode: str, alertes: list) -> dict:
    """Zone 1.1 — concassage / criblage (entrée-pivot → KFS + 0/20).

    Pivot (§5) : la courbe d'entrée est MESURÉE en sortie de station primaire
    (grizzly + CR.5003 déjà confondus dans la courbe). Enchaînement modélisé :
    pivot → CR.5009 → SR.5007 (35/20) avec boucle CR.5011 sur le refus +35.
    Mode 1A : coupe 20-35 → KFS ; mode 1B : coupe 20-35 → CR.5011 (pas de KFS).
    """
    mp = params["machines"]
    calib = params["calibration"]
    moteur = params["moteur"]

    # CR.5009 — rouleaux dentés : x80 = gap (validé), n paramétré
    p9 = mp["CR.5009"]["parametres"]
    gap9 = p9["g"]["defaut"]
    psd9 = models.m1_produit_concassage(alimentation["psd"], gap9, p9["n"]["defaut"], calib)
    bond9 = models.m2_puissance_bond(
        alimentation["q"], alimentation["psd"].p80(), psd9.p80(), calib
    )
    sortie_cr5009 = _flux(alimentation["q"], psd9, alimentation["hum"])

    p7 = mp["SR.5007"]["parametres"]
    p11 = mp["CR.5011"]["parametres"]
    a1, a2, imp = p7["a1"]["defaut"], p7["a2"]["defaut"], p7["I"]["defaut"]
    resultat_cr5011 = {}

    def iterer(recycle):
        feed = _melange([sortie_cr5009, recycle]) if recycle else sortie_cr5009
        refus35, sous35 = _crible_karra(feed, a1, imp, calib)
        mid, passant20 = (
            _crible_karra(sous35, a2, imp, calib) if sous35 else (None, None)
        )
        # flux repris par le percuteur selon le mode
        vers_percuteur = [f for f in [refus35] + ([mid] if mode == "1B" else []) if f]
        if vers_percuteur:
            feed11 = _melange(vers_percuteur)
            out11, info11 = _percuteur(
                feed11, p11["v"]["defaut"], p11["x80"]["defaut"], calib
            )
            resultat_cr5011.update(info11)
            nouveau_recycle = out11
        else:
            nouveau_recycle = None
        sorties = {
            "kfs": mid if mode == "1A" else None,
            "passant_0_20": passant20,
            "feed_crible": feed,
            "u_etage_haut": sous35["q"] if sous35 else 0.0,
            "u_etage_bas": passant20["q"] if passant20 else 0.0,
        }
        return nouveau_recycle, sorties

    recycle, sorties = _boucle_point_fixe(iterer, moteur, alertes, "Zone 1.1 / CR.5011")

    cap11 = mp["CR.5011"].get("capacite_max_th")
    if recycle and cap11 and recycle["q"] > cap11:
        alertes.append(
            f"CR.5011 : goulot — charge {recycle['q']:.1f} t/h > capacité {cap11} t/h"
        )
    if recycle and recycle["q"] > moteur["ratio_circulant_max"] * alimentation["q"]:
        alertes.append("Zone 1.1 : charge circulante excessive (ratio_circulant_max dépassé)")

    surfaces = {
        "etage_haut": models.m4_surface_crible(sorties["u_etage_haut"], a1, calib),
        "etage_bas": models.m4_surface_crible(sorties["u_etage_bas"], a2, calib),
    }
    return {
        "produits": {"KFS": sorties["kfs"], "0/20": sorties["passant_0_20"]},
        "machines": {
            "CR.5009": {**bond9, "q_traite_th": alimentation["q"], "x80_mm": gap9},
            "CR.5011": resultat_cr5011,
            "SR.5007": {
                "q_alimentation_th": sorties["feed_crible"]["q"],
                "surfaces_m2": surfaces,
            },
        },
        "recirculation_th": recycle["q"] if recycle else 0.0,
    }


# ===================================================================== 1.2
def zone_1_2(reprise: dict, params: dict, mode: str, meteo: str, alertes: list) -> dict:
    """Zone 1.2 — reprise / AgLime.

    Stock 0/20 → BF.5101 → SR.5105 (15/5) : +15, 5-15 (mid), 0-5.
    Mode 2A : mid → FeedLime, reste → boucle ; 2B (pluie) : tout → FeedLime ;
    2C : tout → boucle. Boucle : SR.5115 (1,7) ; refus → CR.5107 → retour ;
    passant 0-1,7 = AgLime. Sous la pluie le mode 2B est FORCÉ.
    """
    mp = params["machines"]
    calib = params["calibration"]
    moteur = params["moteur"]

    if meteo == "pluie" and mode != "2B":
        alertes.append(
            f"Zone 1.2 : météo pluie → coupe 1,7 mm impossible, mode {mode} remplacé par 2B"
        )
        mode = "2B"

    p05 = mp["SR.5105"]["parametres"]
    refus15, sous15 = _crible_karra(
        reprise, p05["a1"]["defaut"], calib["I_sec"], calib
    )
    mid, passant5 = (
        _crible_karra(sous15, p05["a2"]["defaut"], calib["I_sec"], calib)
        if sous15
        else (None, None)
    )

    resultat = {
        "machines": {
            "SR.5105": {"q_alimentation_th": reprise["q"]},
            "SR.5115": {},
            "CR.5107": {},
        }
    }

    if mode == "2B":
        resultat["produits"] = {"AgLime": None, "FeedLime": reprise}
        resultat["recirculation_th"] = 0.0
        return resultat

    feedlime = mid if mode == "2A" else None
    vers_boucle = [f for f in [refus15, passant5] + ([mid] if mode == "2C" else []) if f]
    if not vers_boucle:
        resultat["produits"] = {"AgLime": None, "FeedLime": feedlime}
        resultat["recirculation_th"] = 0.0
        return resultat
    entree_boucle = _melange(vers_boucle)

    p15 = mp["SR.5115"]["parametres"]
    p07 = mp["CR.5107"]["parametres"]
    imp_1_7 = p15["I"]["defaut"] if meteo == "sec" else calib["I_pluie"]
    info_cr5107 = {}

    def iterer(recycle):
        feed = _melange([entree_boucle, recycle]) if recycle else entree_boucle
        refus, aglime = _crible_karra(feed, p15["a"]["defaut"], imp_1_7, calib)
        if refus:
            out, info = _percuteur(refus, p07["v"]["defaut"], p07["x80"]["defaut"], calib)
            info_cr5107.update(info)
            nouveau = out
        else:
            nouveau = None
        return nouveau, {"aglime": aglime, "feed_sr5115": feed}

    recycle, sorties = _boucle_point_fixe(iterer, moteur, alertes, "Zone 1.2 / CR.5107")
    if recycle and recycle["q"] > moteur["ratio_circulant_max"] * entree_boucle["q"]:
        alertes.append(
            "CR.5107 : charge circulante explose (CSS trop grand ?) — alarme cahier des charges"
        )

    resultat["machines"]["SR.5115"] = {
        "q_alimentation_th": sorties["feed_sr5115"]["q"],
        "surface_m2": models.m4_surface_crible(
            sorties["aglime"]["q"] if sorties["aglime"] else 0.0,
            p15["a"]["defaut"],
            calib,
        ),
        "imperfection_utilisee": imp_1_7,
    }
    resultat["machines"]["CR.5107"] = info_cr5107
    resultat["produits"] = {"AgLime": sorties["aglime"], "FeedLime": feedlime}
    resultat["recirculation_th"] = recycle["q"] if recycle else 0.0
    return resultat


# ===================================================================== 1.3
def zone_1_3(feedlime: dict, params: dict, phi_100_pct, alertes: list) -> dict:
    """Zone 1.3 — séchage / grits / UltraFin.

    FeedLime → DY.03 (séchoir, → m_out) → SN.21 (4/2/1,5) : 2-4 = grits ;
    refus +4 et sliver 1,5-2 → ML.26 → retour SN.21 (boucle fermée) ;
    passant 0-1,5 = fines → SP.36 (+ CL.38) → UltraFin ; reste = FeedLime fines.
    """
    mp = params["machines"]
    calib = params["calibration"]
    moteur = params["moteur"]

    # DY.03 — séchoir : bilan M6 sur le débit HUMIDE
    m_out = mp["DY.03"]["parametres"]["m_out"]["defaut"]
    q_humide = feedlime["q"] / (1.0 - feedlime["hum"] / 100.0)
    m6 = models.m6_sechage(q_humide, feedlime["hum"], m_out, calib)
    seche = _flux(m6["q_sec_th"], feedlime["psd"], m_out)

    p21 = mp["SN.21"]["parametres"]
    a1, a2, a3 = (p21[k]["defaut"] for k in ("a1", "a2", "a3"))
    p26 = mp["ML.26"]["parametres"]
    gap26 = p26["g"]["defaut"]
    # la fiche machine ML.26 a priorité sur la section calibration pour ses coefficients
    calib_ml26 = {**calib, "comp_lam": p26["comp_lam"]["defaut"], "S_att": p26["S_att"]["defaut"]}
    info_ml26 = {}

    def iterer(recycle):
        feed = _melange([seche, recycle]) if recycle else seche
        refus4, sous4 = _crible_karra(feed, a1, calib["I_sec"], calib)
        grits, sous2 = _crible_karra(sous4, a2, calib["I_sec"], calib) if sous4 else (None, None)
        sliver, fines = _crible_karra(sous2, a3, calib["I_sec"], calib) if sous2 else (None, None)
        vers_ml26 = [f for f in [refus4, sliver] if f]
        if vers_ml26:
            feed26 = _melange(vers_ml26)
            psd26 = models.m7_passe_broyeur_lit(feed26["psd"], gap26, calib_ml26)
            bond26 = models.m2_puissance_bond(feed26["q"], feed26["psd"].p80(), psd26.p80(), calib)
            info_ml26.update({**bond26, "q_traite_th": feed26["q"]})
            nouveau = _flux(feed26["q"], psd26, feed26["hum"])
        else:
            nouveau = None
        return nouveau, {
            "grits": grits,
            "fines": fines,
            "feed_sn21": feed,
            "u1": sous4["q"] if sous4 else 0.0,
        }

    recycle, sorties = _boucle_point_fixe(iterer, moteur, alertes, "Zone 1.3 / ML.26")

    # SP.36 + CL.38 — UltraFin par classification à air
    fines = sorties["fines"]
    p36 = mp["SP.36"]["parametres"]
    # la fiche machine SP.36 / CL.38 a priorité pour ses propres réglages
    calib_cl = {
        **calib,
        "eta_cl": p36["eta_cl"]["defaut"],
        "v_in_cyclone": mp["CL.38"]["parametres"]["v_in"]["defaut"],
    }
    if fines:
        m8 = models.m8_classification_air(
            fines["q"], fines["psd"], p36["coupe"]["defaut"], phi_100_pct, calib_cl
        )
        if not m8["certifie"]:
            alertes.append(
                "SP.36 : Φ(<coupe) non mesuré — UltraFin calculé sur courbe modèle, "
                "drapeau NON CERTIFIÉ (à mesurer au tamis/laser)"
            )
        ultrafin = _flux(m8["q_produit_fin_th"], m8["psd_produit_fin"], fines["hum"])
        fines_restantes = _flux(m8["q_reste_th"], m8["psd_reste"], fines["hum"])
    else:
        m8 = None
        ultrafin = None
        fines_restantes = None

    d50_cyclone = models.m8_cyclone_d50(calib_cl)

    return {
        "produits": {
            "FeedLime grits": sorties["grits"],
            "FeedLime fines": fines_restantes,
            "UltraFin": ultrafin,
        },
        "machines": {
            "DY.03": m6,
            "SN.21": {
                "q_alimentation_th": sorties["feed_sn21"]["q"],
                "surfaces_m2": {
                    "maille_1": models.m4_surface_crible(sorties["u1"], a1, calib),
                },
            },
            "ML.26": info_ml26,
            "SP.36": {
                "Q_air_m3h": m8["Q_air_m3h"] if m8 else None,
                "Phi_coupe": m8["Phi_coupe"] if m8 else None,
                "certifie": m8["certifie"] if m8 else None,
            },
            "CL.38": {"d50_um": d50_cyclone},
        },
        "recirculation_th": recycle["q"] if recycle else 0.0,
        "vapeur_th": m6["eau_evaporee_th"],
    }
