"""Unit tests of models M1-M8 (hand-computed control values)."""

import pytest

from wankoe_model.grid import PSD
from wankoe_model import models

MESHES = [0.1, 0.5, 1, 2, 5, 10, 20, 35, 50, 80, 150, 320]
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
    "bottom_interval_ratio": 2.0,
}


def coarse_psd():
    return PSD(MESHES, [0.02, 0.05, 0.08, 0.12, 0.2, 0.3, 0.45, 0.6, 0.7, 0.8, 0.95, 1.0])


# ---------------------------------------------------------------------- M1
def test_m1_product_bounded_and_truncated():
    product = models.m1_crusher_product(coarse_psd(), 20.0, 1.2, CALIB)
    # the whole product is finer than 1.7*x80 = 34 mm -> passing = 1 at the
    # first grid mesh above the truncation (35 mm)
    assert product.passing_at(35.0) == pytest.approx(1.0, abs=1e-9)
    # the feed fraction already finer than x80 passes through unchanged
    assert product.passing_at(5.0) >= coarse_psd().passing_at(5.0) - 1e-9


def test_m1_x80_approximate():
    # all-coarse feed -> product is a pure truncated RR, P80 close to x80
    feed = PSD(MESHES, [0.0] * 11 + [1.0])
    product = models.m1_crusher_product(feed, 20.0, 1.2, CALIB)
    assert product.p80() == pytest.approx(20.0, rel=0.10)


# ---------------------------------------------------------------------- M2
def test_m2_bond_hand_value():
    # W = 10*12.54*(1/sqrt(40000) - 1/sqrt(200000)) = 0.34659 kWh/t
    res = models.m2_bond_power(250.0, 200.0, 40.0, CALIB)
    assert res["W_kWh_t"] == pytest.approx(0.34659, rel=1e-3)
    assert res["P_net_kW"] == pytest.approx(86.65, rel=1e-3)
    assert res["P_installed_kW"] == pytest.approx(115.53, rel=1e-3)


def test_m2_coarser_product_zero_energy():
    res = models.m2_bond_power(100.0, 10.0, 20.0, CALIB)
    assert res["W_kWh_t"] == 0.0


# ---------------------------------------------------------------------- M3
def test_m3_mass_conservation():
    part = models.m3_karra_partition(100.0, coarse_psd(), 20.0, 0.6, CALIB)
    assert part["oversize_tph"] + part["undersize_tph"] == pytest.approx(100.0)


def test_m3_cut_at_d50():
    # an interval exactly at d50c splits 50/50
    psd = PSD([10.0, 40.0], [0.0, 1.0])  # single interval 10-40, rep. size = 20
    part = models.m3_karra_partition(10.0, psd, 20.0, 0.6, CALIB)
    assert part["oversize_tph"] == pytest.approx(5.0, rel=1e-6)


# ---------------------------------------------------------------------- M4
def test_m4_area_hand_value():
    # Qb = 14*20^0.6 = 84.45 ; A = 100*1.2 / (84.45*0.347) = 4.095 m2
    res = models.m4_screen_area(100.0, 20.0, CALIB)
    assert res["required_area_m2"] == pytest.approx(4.095, rel=1e-3)


# ---------------------------------------------------------------------- M5
def test_m5_hand_value():
    # v = 45: Ecs = 0.28125 ; t10 = 60*(1-e^-0.225) = 12.098 ; n = (30/12.098)^0.3
    res = models.m5_impact_uniformity(45.0, CALIB)
    assert res["Ecs_kWh_t"] == pytest.approx(0.28125)
    assert res["t10_pct"] == pytest.approx(12.098, rel=1e-3)
    assert res["n"] == pytest.approx(1.313, rel=1e-3)


# ---------------------------------------------------------------------- M6
def test_m6_reference_case():
    # 30 t/h at 8 % -> 0.5 %: vapor ~2.26 t/h, burner ~3.83 MW (chapter 9.3)
    res = models.m6_drying(30.0, 8.0, 0.5, CALIB)
    assert res["dry_solids_tph"] == pytest.approx(27.6)
    assert res["evaporated_water_tph"] == pytest.approx(2.261, abs=0.01)
    assert res["burner_power_kW"] == pytest.approx(3827.0, rel=0.01)
    # water balance: input = products + vapor
    water_in = 30.0 * 0.08
    water_out = res["wet_output_tph"] * 0.005
    assert water_in == pytest.approx(water_out + res["evaporated_water_tph"], abs=1e-9)


# ---------------------------------------------------------------------- M7
def test_m7_conserves_and_grinds():
    feed = PSD(MESHES, [0.0, 0.0, 0.05, 0.1, 0.5, 1.0] + [1.0] * 6)
    product = models.m7_bed_mill_pass(feed, 4.0, CALIB)
    assert product.passing[-1] == pytest.approx(1.0)
    # the product is finer than the feed
    assert product.p80() < feed.p80()


def test_m7_strict_coefficient_access():
    # a missing coefficient must raise, never fall back silently (audit 1.4)
    feed = PSD(MESHES, [0.0, 0.0, 0.05, 0.1, 0.5, 1.0] + [1.0] * 6)
    incomplete = {k: v for k, v in CALIB.items() if k != "comp_lam"}
    with pytest.raises(KeyError):
        models.m7_bed_mill_pass(feed, 4.0, incomplete)


# ---------------------------------------------------------------------- M8
def test_m8_phi_measured_and_unmeasured():
    fines = PSD([0.05, 0.1, 0.5, 1.5], [0.1, 0.2, 0.7, 1.0])
    calib = {**CALIB, "v_in_cyclone": 15.0}
    measured = models.m8_air_classification(20.0, fines, 100.0, 10.0, calib)
    assert measured["certified"] is True
    assert measured["fine_product_tph"] == pytest.approx(20.0 * 0.10 * 0.75)
    unmeasured = models.m8_air_classification(20.0, fines, 100.0, None, calib)
    assert unmeasured["certified"] is False
    assert unmeasured["Phi_cut"] == pytest.approx(0.2)
    # conservation
    assert unmeasured["fine_product_tph"] + unmeasured["remainder_tph"] == pytest.approx(20.0)
