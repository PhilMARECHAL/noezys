"""Calibration de la courbe granulométrique d'entrée de référence.

Aucune mesure réelle n'existe à ce jour (CdC §5.1). Ce script construit une
courbe-pivot PLAUSIBLE et la CALE pour reproduire le cas de référence du
chapitre 9 (validé par l'utilisateur le 2026-08-08) :

  - zone 1.1, mode 1A, 250 t/h : KFS = 23,7 % de l'alimentation
  - puissance CR.5009 ≈ 116 kW
  - zone 1.2, mode 2A : FeedLime (5-15) = 45 % de la reprise

Modèle de courbe (3 degrés de liberté) — mélange physique cohérent avec le
CdC §5.1 (« passant grizzly <80 non concassé + produit mâchoires ») :
  pivot = w · RR(x80=150, n=1,15, tronqué)  +  (1−w) · RRtronquée_à_80(x80_g, n_g)

Sortie : data/courbe_entree_reference.json (courbe + rapport de calage).
La courbe est une HYPOTHÈSE DE TRAVAIL, à remplacer par la première mesure.

Usage : python scripts/calibrer_courbe_reference.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

from wankoe_model.grid import PSD, grille_moteur  # noqa: E402
from wankoe_model.scenario import charger_parametres, run_scenario  # noqa: E402

CIBLES = {"kfs_pct": 23.7, "p_cr5009_kw": 116.0, "feedlime_pct": 45.0, "p_cr5011_kw": 37.0}
POIDS = {"kfs_pct": 4.0, "p_cr5009_kw": 0.02, "feedlime_pct": 2.0, "p_cr5011_kw": 0.05}


def courbe_pivot(params: dict, w: float, x80_g: float, n_g: float) -> dict:
    """Construit la courbe pivot (dict maille → % passant) sur la série de référence."""
    calib = {
        "trunc_factor": params["calibration"]["trunc_factor"]["defaut"],
        "m1_ln_arg": params["calibration"]["m1_ln_arg"]["defaut"],
    }
    p_jaw = params["machines"]["CR.5003"]["parametres"]
    x80_j, n_j = p_jaw["x80"]["defaut"], p_jaw["n"]["defaut"]
    ln_arg, trunc = calib["m1_ln_arg"], calib["trunc_factor"]

    def rr_tronquee(x: float, x80: float, n: float, x_max: float) -> float:
        xc = x80 / (math.log(ln_arg) ** (1.0 / n))
        p = 1.0 - math.exp(-((x / xc) ** n))
        p_max = 1.0 - math.exp(-((x_max / xc) ** n))
        return min(1.0, p / p_max)

    # grille étendue : le produit mâchoires porte une queue jusqu'à 1,7·x80 (> 200 mm)
    serie = sorted(
        set(params["serie_mailles_mm"]) | set(params["moteur"]["mailles_extension_mm"])
    )
    courbe = {}
    for x in serie:
        p_machoires = rr_tronquee(x, x80_j, n_j, trunc * x80_j)  # produit CR.5003
        p_grizzly = rr_tronquee(x, x80_g, n_g, 80.0)  # passant grizzly <80, naturel
        courbe[str(x)] = round(100.0 * (w * p_machoires + (1.0 - w) * p_grizzly), 4)
    return courbe


def evaluer(params_base: dict, w: float, x80_g: float, n_g: float) -> tuple[float, dict]:
    courbe = courbe_pivot(params_base, w, x80_g, n_g)
    params = charger_parametres(
        overrides={"produit_entree": {"courbe_passant_cumule": courbe}}
    )
    try:
        res = run_scenario(params)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        return 1e9, {"erreur": str(exc)}
    q_alim = res["scenario"]["debits_th"]["alimentation_zone_1_1"]
    kfs_pct = 100.0 * res["produits"]["KFS"]["t_h"] / q_alim
    p9 = res["machines"]["CR.5009"]["P_inst_kW"]
    # part FeedLime = reprise − AgLime (boucle fermée), en base humide cohérente
    q_rep = res["scenario"]["debits_th"]["reprise_zone_1_2"]
    aglime_th = res["produits"]["AgLime"]["t_h"]
    feedlime_pct = 100.0 * (q_rep - aglime_th) / q_rep
    p11 = res["machines"]["CR.5011"].get("P_inst_kW", 0.0)
    obtenu = {
        "kfs_pct": kfs_pct,
        "p_cr5009_kw": p9,
        "feedlime_pct": feedlime_pct,
        "p_cr5011_kw": p11,
    }
    cout = sum(POIDS[k] * (obtenu[k] - CIBLES[k]) ** 2 for k in CIBLES)
    return cout, obtenu


def calibrer() -> dict:
    params_base = charger_parametres()

    # 1) balayage grossier
    meilleur = None
    for w in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        for x80_g in [15, 25, 35, 45, 60]:
            for n_g in [0.7, 0.9, 1.1, 1.3]:
                cout, obtenu = evaluer(params_base, w, x80_g, n_g)
                if meilleur is None or cout < meilleur[0]:
                    meilleur = (cout, (w, x80_g, n_g), obtenu)
    print(f"Balayage grossier : coût {meilleur[0]:.2f} pour {meilleur[1]} → {meilleur[2]}")

    # 2) raffinement par recherche locale (pattern search)
    (cout, (w, x80_g, n_g), obtenu) = meilleur
    pas = [0.05, 5.0, 0.1]
    for _ in range(60):
        ameliore = False
        for i, (delta, borne_min, borne_max) in enumerate(
            zip(pas, [0.05, 5.0, 0.5], [0.95, 79.0, 2.0])
        ):
            for signe in (+1, -1):
                candidat = [w, x80_g, n_g]
                candidat[i] = min(borne_max, max(borne_min, candidat[i] + signe * delta))
                c, o = evaluer(params_base, *candidat)
                if c < cout:
                    cout, (w, x80_g, n_g), obtenu = c, tuple(candidat), o
                    ameliore = True
        if not ameliore:
            if max(pas) < 1e-3:
                break
            pas = [p / 2 for p in pas]
    print(f"Raffinement : coût {cout:.3f} pour w={w:.3f}, x80_g={x80_g:.2f}, n_g={n_g:.3f}")
    print(f"Obtenu : {obtenu}  |  Cibles : {CIBLES}")

    courbe = courbe_pivot(params_base, w, x80_g, n_g)
    rapport = {
        "_statut": "COURBE CALIBRÉE — hypothèse de travail, à remplacer par la première mesure réelle",
        "date_calibration": "2026-08-08",
        "modele": "pivot = w·RR(150; 1,15) + (1−w)·RR_tronquée_80(x80_g; n_g)",
        "parametres_calibres": {"w": round(w, 4), "x80_g_mm": round(x80_g, 3), "n_g": round(n_g, 4)},
        "cibles_chapitre_9": CIBLES,
        "valeurs_obtenues": {k: round(v, 2) for k, v in obtenu.items()},
        "courbe_passant_cumule": courbe,
    }
    return rapport


if __name__ == "__main__":
    rapport = calibrer()
    sortie = RACINE / "data" / "courbe_entree_reference.json"
    sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Écrit : {sortie}")
