"""Vérifie la règle d'or n° 3 : tout paramètre est modifiable SANS toucher au code.

Chaque test surcharge un paramètre via ``charger_parametres(overrides=...)``
et vérifie que le résultat change en conséquence — preuve que la valeur
n'est pas codée en dur.
"""

import pytest

from wankoe_model import charger_parametres, run_scenario


def test_maille_crible_modifiable():
    base = run_scenario(charger_parametres())
    modifie = run_scenario(
        charger_parametres(
            overrides={
                "machines": {"SR.5007": {"parametres": {"a1": {"defaut": 30}, "a2": {"defaut": 25}}}}
            }
        )
    )
    assert modifie["produits"]["KFS"]["t_h"] != base["produits"]["KFS"]["t_h"]


def test_indice_de_bond_modifiable():
    base = run_scenario(charger_parametres())
    modifie = run_scenario(
        charger_parametres(overrides={"calibration": {"Wi": {"defaut": 25.08}}})
    )
    # Wi doublé → énergie spécifique doublée (loi de Bond linéaire en Wi)
    assert modifie["machines"]["CR.5009"]["P_inst_kW"] == pytest.approx(
        2 * base["machines"]["CR.5009"]["P_inst_kW"], rel=1e-6
    )


def test_debit_scenario_modifiable():
    modifie = run_scenario(
        charger_parametres(
            overrides={"scenario_defaut": {"debits_th": {"alimentation_zone_1_1": 125}}}
        )
    )
    base = run_scenario(charger_parametres())
    assert modifie["produits"]["KFS"]["t_h"] == pytest.approx(
        base["produits"]["KFS"]["t_h"] / 2, rel=1e-6
    )


def test_mode_1b_supprime_le_kfs():
    modifie = run_scenario(
        charger_parametres(overrides={"scenario_defaut": {"mode_zone_1_1": "1B"}})
    )
    assert modifie["produits"]["KFS"]["t_h"] == 0.0


def test_pluie_force_mode_2b():
    modifie = run_scenario(
        charger_parametres(overrides={"scenario_defaut": {"meteo": "pluie"}})
    )
    assert modifie["produits"]["AgLime"]["t_h"] == 0.0
    assert modifie["scenario"]["mode_zone_1_2"] == "2B"
    assert any("2B" in a for a in modifie["alertes"])


def test_humidite_entree_modifiable():
    base = run_scenario(charger_parametres())
    modifie = run_scenario(
        charger_parametres(
            overrides={
                "produit_entree": {"proprietes": {"humidite_pct": {"defaut": 12, "statut": "test"}}}
            }
        )
    )
    assert (
        modifie["machines"]["DY.03"]["eau_evaporee_th"]
        > base["machines"]["DY.03"]["eau_evaporee_th"]
    )


def test_phi_100_mesure_supprime_l_alerte():
    modifie = run_scenario(
        charger_parametres(overrides={"calibration": {"Phi_100": {"defaut": 9.0}}})
    )
    assert not any("NON CERTIFIÉ" in a for a in modifie["alertes"])


def test_bilan_annuel_avec_heures():
    heures = {"heures_dispo": 5000, "disponibilite_pct": 80}
    modifie = run_scenario(
        charger_parametres(
            overrides={
                "scenario_defaut": {"zones": {"1.1": heures, "1.2": heures, "1.3": heures}}
            }
        )
    )
    bilan = modifie["bilan_annuel"]
    assert bilan is not None
    assert bilan["par_produit"]["KFS"]["tonnage_t"] == pytest.approx(
        modifie["produits"]["KFS"]["t_h"] * 4000, rel=1e-6
    )
