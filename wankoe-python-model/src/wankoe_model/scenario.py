"""Exécution d'un scénario : la « photo » synchronisée de la ligne.

run_scenario(params) est une FONCTION PURE : un dict de paramètres entre,
un dict de résultats sort (flux, granulos, puissances, bilans, conformité,
alertes). Aucun état global — la fonction peut donc être appelée en masse
pour des balayages de paramètres / recherches d'optimum.

Les paramètres par défaut vivent dans data/parametres_defaut.json ;
``charger_parametres(overrides=...)`` applique des surcharges par fusion
profonde, sans jamais modifier le fichier.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from .grid import PSD, grille_moteur
from . import flowsheet

_RACINE = Path(__file__).resolve().parent.parent.parent
CHEMIN_PARAMETRES_DEFAUT = _RACINE / "data" / "parametres_defaut.json"
CHEMIN_COURBE_REFERENCE = _RACINE / "data" / "courbe_entree_reference.json"


def _fusion_profonde(base: dict, surcharge: dict) -> dict:
    resultat = copy.deepcopy(base)
    for cle, valeur in surcharge.items():
        if isinstance(valeur, dict) and isinstance(resultat.get(cle), dict):
            resultat[cle] = _fusion_profonde(resultat[cle], valeur)
        else:
            resultat[cle] = copy.deepcopy(valeur)
    return resultat


def charger_parametres(chemin=None, overrides: dict | None = None) -> dict:
    """Charge le jeu de paramètres (JSON) et applique les surcharges éventuelles."""
    with open(chemin or CHEMIN_PARAMETRES_DEFAUT, encoding="utf-8") as f:
        params = json.load(f)
    if overrides:
        params = _fusion_profonde(params, overrides)
    return params


def _construire_alimentation(params: dict, alertes: list) -> tuple:
    """Construit le flux d'entrée-pivot depuis les paramètres (courbe + humidité).

    Si aucune courbe mesurée n'est renseignée, repli sur la courbe de
    référence CALIBRÉE (hypothèse de travail) — signalé en alerte.
    """
    pe = params["produit_entree"]
    courbe = pe["courbe_passant_cumule"]
    if not courbe:
        if CHEMIN_COURBE_REFERENCE.exists():
            with open(CHEMIN_COURBE_REFERENCE, encoding="utf-8") as f:
                courbe = json.load(f)["courbe_passant_cumule"]
            alertes.append(
                "Courbe d'entrée : aucune mesure renseignée — courbe de référence "
                "CALIBRÉE utilisée (hypothèse, à remplacer par une mesure réelle)"
            )
        else:
            raise ValueError(
                "Courbe granulométrique d'entrée absente (produit_entree.courbe_passant_cumule) "
                "et pas de courbe de référence calibrée disponible."
            )
    grille = grille_moteur(params["serie_mailles_mm"], params["moteur"]["mailles_extension_mm"])
    psd = PSD(grille, [courbe_interp(courbe, x) for x in grille])
    hum = pe["proprietes"]["humidite_pct"]["defaut"]
    return psd, hum


def courbe_interp(courbe: dict, x_mm: float) -> float:
    """Interpole une courbe {maille: % passant} en log(x), retourne une fraction 0–1."""
    import math

    points = sorted((float(k), float(v) / 100.0) for k, v in courbe.items())
    if x_mm <= points[0][0]:
        return points[0][1] * x_mm / points[0][0]
    if x_mm >= points[-1][0]:
        return 1.0 if points[-1][1] > 0.999 else points[-1][1]
    for (x0, p0), (x1, p1) in zip(points, points[1:]):
        if x_mm <= x1:
            t = (math.log(x_mm) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return p0 + t * (p1 - p0)
    return 1.0


def _tonnage_humide(flux, ref_hum_pct: float | None = None) -> float:
    """Tonnage HUMIDE d'un flux (t/h) — les produits humides se vendent humides."""
    if flux is None:
        return 0.0
    hum = flux["hum"] if ref_hum_pct is None else ref_hum_pct
    return flux["q"] / (1.0 - hum / 100.0)


def _conformite_produit(flux, spec: dict) -> dict | None:
    if flux is None:
        return None
    hors = 1.0 - flux["psd"].fraction_entre(spec["coupure_min_mm"], spec["coupure_max_mm"])
    tol = spec.get("tol_max_hors_coupure_pct")
    return {
        "hors_coupure_pct": round(100.0 * hors, 2),
        "tolerance_pct": tol,
        "conforme": None if tol is None else bool(100.0 * hors <= tol),
    }


def _aplatir_calibration(calibration: dict) -> dict:
    """{symbole: valeur} depuis les fiches {nom, unite, defaut, ...} du JSON."""
    return {
        cle: (entree["defaut"] if isinstance(entree, dict) and "defaut" in entree else entree)
        for cle, entree in calibration.items()
    }


def run_scenario(params: dict) -> dict:
    """Exécute un scénario complet et retourne la « photo » de la ligne."""
    params = {**params, "calibration": _aplatir_calibration(params["calibration"])}
    alertes: list[str] = []
    sc = params["scenario_defaut"]
    calib = params["calibration"]
    moteur = params["moteur"]
    meteo = sc["meteo"]

    psd_pivot, hum = _construire_alimentation(params, alertes)

    # ---------------- Zone 1.1
    q_alim = sc["debits_th"]["alimentation_zone_1_1"]
    alim = {"q": q_alim * (1.0 - hum / 100.0), "psd": psd_pivot, "hum": hum}
    z11 = flowsheet.zone_1_1(alim, params, sc["mode_zone_1_1"], alertes)

    # ---------------- Zone 1.2 (reprise du stock 0/20)
    q_reprise = sc["debits_th"]["reprise_zone_1_2"]
    flux_0_20 = z11["produits"]["0/20"]
    if flux_0_20 is None:
        raise ValueError("Zone 1.1 ne produit pas de 0/20 : scénario incohérent")
    reprise = {"q": q_reprise * (1.0 - hum / 100.0), "psd": flux_0_20["psd"], "hum": hum}
    z12 = flowsheet.zone_1_2(reprise, params, sc["mode_zone_1_2"], meteo, alertes)

    # ---------------- Zone 1.3 (reprise du stock FeedLime)
    q_feedlime = sc["debits_th"]["feedlime_zone_1_3"]
    flux_fl = z12["produits"]["FeedLime"]
    if flux_fl is not None and q_feedlime > 0:
        feedlime = {
            "q": q_feedlime * (1.0 - hum / 100.0),
            "psd": flux_fl["psd"],
            "hum": hum,
        }
        z13 = flowsheet.zone_1_3(feedlime, params, calib["Phi_100"], alertes)
    else:
        z13 = None
        if q_feedlime > 0:
            alertes.append("Zone 1.3 : pas de FeedLime produit en zone 1.2 (mode 2C ?)")

    # ---------------- Bilans de bouclage (solide sec, par zone traitée)
    tol_bilan = moteur["tolerance_bilan_relative"]
    bilans = {}

    def _bilan(nom, entree, sorties):
        total_sorties = sum(f["q"] for f in sorties if f)
        ecart = abs(entree - total_sorties) / max(entree, 1e-9)
        bilans[nom] = {
            "entree_sec_th": round(entree, 4),
            "sorties_sec_th": round(total_sorties, 4),
            "ecart_relatif": ecart,
            "boucle": bool(ecart <= tol_bilan),
        }
        if ecart > tol_bilan:
            alertes.append(f"Bilan {nom} NON bouclé : écart relatif {ecart:.2e}")

    _bilan("zone_1_1", alim["q"], [z11["produits"]["KFS"], z11["produits"]["0/20"]])
    _bilan("zone_1_2", reprise["q"], list(z12["produits"].values()))
    if z13:
        _bilan("zone_1_3", feedlime["q"], list(z13["produits"].values()))
        # bilan EAU zone 1.3 : eau entrée = eau produits + vapeur
        eau_in = feedlime["q"] / (1.0 - hum / 100.0) * hum / 100.0
        m_out = params["machines"]["DY.03"]["parametres"]["m_out"]["defaut"]
        eau_produits = sum(
            f["q"] / (1.0 - m_out / 100.0) * m_out / 100.0
            for f in z13["produits"].values()
            if f
        )
        ecart_eau = abs(eau_in - (eau_produits + z13["vapeur_th"])) / max(eau_in, 1e-9)
        bilans["eau_zone_1_3"] = {
            "eau_entree_th": round(eau_in, 4),
            "eau_produits_th": round(eau_produits, 4),
            "vapeur_th": round(z13["vapeur_th"], 4),
            "ecart_relatif": ecart_eau,
            "boucle": bool(ecart_eau <= tol_bilan),
        }
        if ecart_eau > tol_bilan:
            alertes.append(f"Bilan EAU zone 1.3 NON bouclé : écart relatif {ecart_eau:.2e}")

    # ---------------- Produits : tonnages « tels que vendus » + conformité
    specs = params["produits_sortie"]
    produits = {}

    def _produit(nom, flux, humide: bool):
        if flux is None:
            produits[nom] = {"t_h": 0.0, "etat": "absent (mode/scénario)"}
            return
        t_h = _tonnage_humide(flux) if humide else flux["q"]
        produits[nom] = {
            "t_h": round(t_h, 3),
            "etat": "humide" if humide else "sec",
            "P80_mm": round(flux["psd"].p80(), 4),
            "courbe_pct_passant": dict(
                zip(
                    [str(m) for m in params["serie_mailles_mm"]],
                    flux["psd"].sur_serie(params["serie_mailles_mm"]),
                )
            ),
            "conformite": _conformite_produit(flux, specs[nom]),
        }

    _produit("KFS", z11["produits"]["KFS"], humide=True)
    _produit("AgLime", z12["produits"]["AgLime"], humide=True)
    if z13:
        _produit("FeedLime grits", z13["produits"]["FeedLime grits"], humide=False)
        _produit("FeedLime fines", z13["produits"]["FeedLime fines"], humide=False)
        _produit("UltraFin", z13["produits"]["UltraFin"], humide=False)

    machines = {**z11["machines"], **z12["machines"], **(z13["machines"] if z13 else {})}

    resultats = {
        "scenario": {
            "mode_zone_1_1": sc["mode_zone_1_1"],
            "mode_zone_1_2": "2B" if meteo == "pluie" else sc["mode_zone_1_2"],
            "meteo": meteo,
            "debits_th": sc["debits_th"],
        },
        "produits": produits,
        "flux_intermediaires": {
            "0/20_th_sec": round(z11["produits"]["0/20"]["q"], 3),
            "recirculation_zone_1_1_th": round(z11["recirculation_th"], 3),
            "recirculation_zone_1_2_th": round(z12["recirculation_th"], 3),
            "recirculation_zone_1_3_th": round(z13["recirculation_th"], 3) if z13 else None,
        },
        "machines": machines,
        "bilans": bilans,
        "alertes": alertes,
    }
    resultats["bilan_annuel"] = _bilan_annuel(params, resultats, alertes)
    return resultats


def _bilan_annuel(params: dict, resultats: dict, alertes: list) -> dict | None:
    """Tonnages par période si les heures sont renseignées ; sinon alerte."""
    sc = params["scenario_defaut"]
    zones = sc["zones"]
    if any(z["heures_dispo"] is None for z in zones.values()):
        alertes.append(
            "Bilan par période non calculé : heures disponibles non renseignées (paramètre)"
        )
        return None
    heures_eff = {
        nom: z["heures_dispo"] * z["disponibilite_pct"] / 100.0 for nom, z in zones.items()
    }
    p = resultats["produits"]
    tonnages = {
        "KFS": p["KFS"]["t_h"] * heures_eff["1.1"],
        "AgLime": p.get("AgLime", {}).get("t_h", 0.0) * heures_eff["1.2"],
        "FeedLime grits": p.get("FeedLime grits", {}).get("t_h", 0.0) * heures_eff["1.3"],
        "FeedLime fines": p.get("FeedLime fines", {}).get("t_h", 0.0) * heures_eff["1.3"],
        "UltraFin": p.get("UltraFin", {}).get("t_h", 0.0) * heures_eff["1.3"],
    }
    objectifs = params["objectifs"]
    correspondance = {
        "KFS": "KFS 20/35",
        "AgLime": "AgLime 0/1,7",
        "FeedLime grits": "FeedLime grits 2-4",
        "FeedLime fines": "FeedLime fines 0/1,5",
        "UltraFin": "UltraFin <100um",
    }
    ecarts = {}
    for produit, tonnage in tonnages.items():
        obj = objectifs[correspondance[produit]]
        plafond = obj.get("plafond_marche_t_an")
        ecarts[produit] = {
            "tonnage_t": round(tonnage, 0),
            "cible_t": obj["cible_t_an"],
            "ecart_t": round(tonnage - obj["cible_t_an"], 0),
            "nature": obj["nature"],
            "excedent_hors_marche_t": round(max(0.0, tonnage - plafond), 0) if plafond else None,
        }
    return {"heures_effectives": heures_eff, "par_produit": ecarts}
