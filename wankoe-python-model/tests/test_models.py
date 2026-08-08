"""Tests unitaires des modèles M1–M8 (valeurs de contrôle calculées à la main)."""

import pytest

from wankoe_model.grid import PSD
from wankoe_model import models

MAILLES = [0.1, 0.5, 1, 2, 5, 10, 20, 35, 50, 80, 150, 320]
CALIB = {
    "trunc_factor": 1.7,
    "m1_ln_arg": 5.0,
    "Wi": 12.54,
    "bond_coef": 10.0,
    "eta_m": 0.75,
    "k_d": 1.0,
    "m3_ln_arg": 9.0,
    "f_p": 1.2,
    "f0": 0.347,
    "qb_coef": 14.0,
    "qb_exp": 0.6,
    "A_j": 60.0,
    "b_j": 0.8,
    "ecs_div": 7200.0,
    "m5_t10_ref": 30.0,
    "m5_n_exp": 0.30,
    "m5_n_min": 0.65,
    "L_v": 2257.0,
    "c_e": 4.18,
    "c_s": 0.9,
    "dT_e": 85.0,
    "dT_s": 95.0,
    "eta_th": 0.6,
    "I_ev": 45.0,
    "comp_lam": 4.11,
    "S_att": 0.206,
    "m7_n_comp": 1.0,
    "m7_x80_att": 0.8,
    "m7_n_att": 1.3,
    "eta_cl": 0.75,
    "lambda": 0.5,
}


def psd_grossiere():
    return PSD(MAILLES, [0.02, 0.05, 0.08, 0.12, 0.2, 0.3, 0.45, 0.6, 0.7, 0.8, 0.95, 1.0])


# ---------------------------------------------------------------------- M1
def test_m1_produit_borne_et_tronque():
    produit = models.m1_produit_concassage(psd_grossiere(), 20.0, 1.2, CALIB)
    # tout le produit est plus fin que 1,7·x80 = 34 mm → passant = 1 à la
    # première maille de la grille au-dessus de la troncature (35 mm)
    assert produit.passant_a(35.0) == pytest.approx(1.0, abs=1e-9)
    # la fraction déjà plus fine que x80 passe inchangée
    assert produit.passant_a(5.0) >= psd_grossiere().passant_a(5.0) - 1e-9


def test_m1_x80_approximatif():
    # alimentation intégralement grossière → produit pur RR tronqué, P80 ≈ x80
    alim = PSD(MAILLES, [0.0] * 11 + [1.0])
    produit = models.m1_produit_concassage(alim, 20.0, 1.2, CALIB)
    assert produit.p80() == pytest.approx(20.0, rel=0.10)


# ---------------------------------------------------------------------- M2
def test_m2_bond_valeur_manuelle():
    # W = 10·12,54·(1/√40000 − 1/√200000) = 0,34659 kWh/t
    res = models.m2_puissance_bond(250.0, 200.0, 40.0, CALIB)
    assert res["W_kWh_t"] == pytest.approx(0.34659, rel=1e-3)
    assert res["P_net_kW"] == pytest.approx(86.65, rel=1e-3)
    assert res["P_inst_kW"] == pytest.approx(115.53, rel=1e-3)


def test_m2_produit_plus_grossier_energie_nulle():
    res = models.m2_puissance_bond(100.0, 10.0, 20.0, CALIB)
    assert res["W_kWh_t"] == 0.0


# ---------------------------------------------------------------------- M3
def test_m3_conservation_masse():
    part = models.m3_partition_karra(100.0, psd_grossiere(), 20.0, 0.6, CALIB)
    assert part["q_refus_th"] + part["q_passant_th"] == pytest.approx(100.0)


def test_m3_coupure_au_d50():
    # une tranche pile à d50c se partage 50/50
    psd = PSD([10.0, 40.0], [0.0, 1.0])  # tranche unique 10-40, taille rep = 20
    part = models.m3_partition_karra(10.0, psd, 20.0, 0.6, CALIB)
    assert part["q_refus_th"] == pytest.approx(5.0, rel=1e-6)


# ---------------------------------------------------------------------- M4
def test_m4_surface_valeur_manuelle():
    # Qb = 14·20^0,6 = 84,45 ; A = 100·1,2 / (84,45·0,347) = 4,095 m²
    res = models.m4_surface_crible(100.0, 20.0, CALIB)
    assert res["A_requise_m2"] == pytest.approx(4.095, rel=1e-3)


# ---------------------------------------------------------------------- M5
def test_m5_valeur_manuelle():
    # v = 45 : Ecs = 0,28125 ; t10 = 60·(1−e^−0,225) = 12,098 ; n = (30/12,098)^0,3
    res = models.m5_uniformite_impact(45.0, CALIB)
    assert res["Ecs_kWh_t"] == pytest.approx(0.28125)
    assert res["t10_pct"] == pytest.approx(12.098, rel=1e-3)
    assert res["n"] == pytest.approx(1.313, rel=1e-3)


# ---------------------------------------------------------------------- M6
def test_m6_cas_de_reference():
    # 30 t/h à 8 % → 0,5 % : vapeur ≈ 2,26 t/h, brûleur ≈ 3,83 MW (chap. 9.3)
    res = models.m6_sechage(30.0, 8.0, 0.5, CALIB)
    assert res["q_sec_th"] == pytest.approx(27.6)
    assert res["eau_evaporee_th"] == pytest.approx(2.261, abs=0.01)
    assert res["P_bruleur_kW"] == pytest.approx(3827.0, rel=0.01)
    # bilan eau : entrée = produits + vapeur
    eau_in = 30.0 * 0.08
    eau_out = res["q_sortie_humide_th"] * 0.005
    assert eau_in == pytest.approx(eau_out + res["eau_evaporee_th"], abs=1e-9)


# ---------------------------------------------------------------------- M7
def test_m7_conserve_et_broie():
    alim = PSD(MAILLES, [0.0, 0.0, 0.05, 0.1, 0.5, 1.0] + [1.0] * 6)
    produit = models.m7_passe_broyeur_lit(alim, 4.0, CALIB)
    assert produit.passant[-1] == pytest.approx(1.0)
    # le produit est plus fin que l'alimentation
    assert produit.p80() < alim.p80()


# ---------------------------------------------------------------------- M8
def test_m8_phi_mesure_et_non_mesure():
    fines = PSD([0.05, 0.1, 0.5, 1.5], [0.1, 0.2, 0.7, 1.0])
    calib = {**CALIB, "v_in_cyclone": 15.0}
    avec_mesure = models.m8_classification_air(20.0, fines, 100.0, 10.0, calib)
    assert avec_mesure["certifie"] is True
    assert avec_mesure["q_produit_fin_th"] == pytest.approx(20.0 * 0.10 * 0.75)
    sans_mesure = models.m8_classification_air(20.0, fines, 100.0, None, calib)
    assert sans_mesure["certifie"] is False
    assert sans_mesure["Phi_coupe"] == pytest.approx(0.2)
    # conservation
    assert sans_mesure["q_produit_fin_th"] + sans_mesure["q_reste_th"] == pytest.approx(20.0)
