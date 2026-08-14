"""Literature anchors (internal confidence program, action 2, 2026-08-14).

Each model function is confronted with its SOURCE-literature formula
evaluated independently: every expected value below is hand arithmetic
written into the test (source cited), never read back from the engine.
A pass proves the transcription engine == published formula; a deviation
is a transcription finding.
"""

import math

import pytest

from wankoe_model import load_parameters
from wankoe_model.grid import PSD
from wankoe_model import models
from wankoe_model.scenario import _flatten_calibration


@pytest.fixture(scope="module")
def calib():
    return _flatten_calibration(load_parameters()["calibration"])


# ------------------------------------------------------------------ M2 Bond
def test_m2_reproduces_bond_worked_example(calib):
    """Bond's third law (Bond 1952/1961; Wills, Mineral Processing
    Technology): W = 10·Wi·(1/sqrt(P80) − 1/sqrt(F80)), sizes in µm.
    Worked case Wi = 12.74 kWh/t, F80 = 25 mm, P80 = 3 mm.
    Hand arithmetic: 1/sqrt(3000) = 0.01825742, 1/sqrt(25000) = 0.00632456,
    difference 0.01193286, x 127.4 = 1.520246 kWh/t."""
    c = {**calib, "Wi": 12.74, "bond_coef": 10.0, "eta_m": 0.75}
    out = models.m2_bond_power(100.0, 25.0, 3.0, c)
    assert out["W_kWh_t"] == pytest.approx(1.520246, abs=1e-5)
    assert out["P_net_kW"] == pytest.approx(152.0246, abs=1e-3)
    # installed = net / eta_m (documented motor efficiency convention)
    assert out["P_installed_kW"] == pytest.approx(152.0246 / 0.75, abs=1e-3)


# ------------------------------------------------------- M5 JKMRC breakage
def test_m5_kinetic_energy_identity_is_exact(calib):
    """Ecs = v²/7200 is EXACT physics, not a fit: kinetic energy per unit
    mass v²/2 [J/kg] = v²/2/3.6e6 [kWh/kg] = v²/7200 [kWh/t].
    At v = 30 m/s: Ecs = 900/7200 = 0.125 kWh/t exactly."""
    assert float(calib["ecs_div"]) == 7200.0
    out = models.m5_impact_uniformity(30.0, calib)
    assert out["Ecs_kWh_t"] == pytest.approx(0.125, abs=1e-12)


def test_m5_reproduces_jkmrc_t10_form(calib):
    """JKMRC breakage model (Napier-Munn et al., Mineral Comminution
    Circuits, 1996): t10 = A·(1 − e^(−b·Ecs)).
    With the project values A = 60, b = 0.80 [H] at Ecs = 0.125:
    hand arithmetic e^(−0.1) = 0.90483742 -> t10 = 60 x 0.09516258
    = 5.709755 %."""
    c = {**calib, "A_j": 60.0, "b_j": 0.80}
    out = models.m5_impact_uniformity(30.0, c)
    assert out["t10_pct"] == pytest.approx(5.709755, abs=1e-5)


# --------------------------------------------------------- M3 screen curve
def test_m3_logistic_quartiles_match_the_analytic_form(calib):
    """The implemented partition is the logistic reduced-efficiency curve
    ro(x) = 1/(1 + (d50c/x)^s) (Reid/Plitt family; King, Modeling and
    Simulation of Mineral Processing Systems, Table 7.1). Its quartiles
    are analytic: ro = 0.75 at x75 = d50c·3^(1/s), ro = 0.25 at
    x25 = d50c·3^(−1/s). The engine partition must reproduce them."""
    a = 20.0
    imperfection = 0.15
    d50c = a * float(calib["k_d"])
    s = math.log(9.0) / math.log(1.0 / (1.0 - imperfection))
    # hand check of the sharpness value itself: ln9/ln(1/0.85)
    assert s == pytest.approx(2.1972246 / 0.1625189, abs=2e-4)  # 13.5198

    # probe the engine's partition with two one-interval feeds whose
    # representative (geometric-mean) size lands exactly on x75 / x25
    for target_ro, xq in ((0.75, d50c * 3 ** (1 / s)), (0.25, d50c * 3 ** (-1 / s))):
        lo, hi = xq / 1.001, xq * 1.001  # geometric mean == xq
        psd = PSD([lo, hi, hi * 4], [0.0, 1.0, 1.0])
        part = models.m3_karra_partition(100.0, psd, a, imperfection, calib)
        assert part["oversize_tph"] == pytest.approx(100.0 * target_ro, rel=2e-3)


def test_m3_attribution_note_classic_imperfection_equivalent(calib):
    """DISCLOSED FINDING (attribution, not a failure): with the SPEC's
    prescribed sharpness s = ln9/ln(1/(1−I)), the curve's CLASSIC
    imperfection (d75−d25)/(2·d50) equals sinh(ln(1/(1−I))/2), i.e.
    ~0.0813 when I = 0.15 is input — the implemented screens are about
    twice as sharp as a classic I = 0.15 screen (and close to Karra 1979's
    fixed ~0.13-equivalent sharpness family). Spec convention arbitrated
    2026-08-08; quantified here so a reviewer sees it stated, not hidden."""
    imperfection = 0.15
    s = math.log(9.0) / math.log(1.0 / (1.0 - imperfection))
    classic = math.sinh(math.log(3.0) / s)
    assert classic == pytest.approx(0.08135, abs=2e-4)


# --------------------------------------------------------------- M4 VSMA
def test_m4_effective_capacity_matches_published_vsma_within_5pct(calib):
    """VSMA basic-capacity anchor (VSMA handbook Factor-A table, via the
    2026-08-08 literature review): published effective capacities are
    ~30.8 t/h/m² at 20 mm and ~39.5 t/h/m² at 35 mm. The engine's
    Qb·f0 = 14·a^0.6 × 0.347 must land within 5 %.
    Hand arithmetic: 20^0.6 = 6.03418 -> 14×6.03418×0.347 = 29.314 ;
    35^0.6 = 8.44412 -> 14×8.44412×0.347 = 41.021."""
    for a_mm, published in ((20.0, 30.8), (35.0, 39.5)):
        out = models.m4_screen_area(100.0, a_mm, calib)
        effective = out["Qb_tph_m2"] * float(calib["f0"])
        assert abs(effective - published) / published < 0.05
    # and the documented area identity A = U·f_p/(Qb·f0)
    out = models.m4_screen_area(175.325, 20.0, calib)
    assert out["required_area_m2"] == pytest.approx(
        175.325 * float(calib["f_p"]) / (14.0 * 20.0**0.6 * 0.347), rel=1e-9
    )


# ------------------------------------------------------- M1 Rosin-Rammler
def test_m1_rosin_rammler_anchor_at_x80(calib):
    """Rosin-Rammler (1933) with the x80 anchor: P(x) = 1−exp(−(x/xc)^n),
    xc = x80/ln(5)^(1/n) so that P(x80) = 0.8 exactly. With the project
    truncation at 1.7·x80 (mass renormalized), the product of an
    all-coarse feed passes P(x80) = 0.8/P_RR(1.7·x80).
    Hand arithmetic at n = 1.35: 1.7^1.35 = e^(1.35×0.5306283) = 2.0469440;
    exp(−ln5 × 2.0469440) = exp(−3.2944271) = 0.0370893;
    P_t(x80) = 0.8/0.9629107 = 0.830814. (A first hand evaluation with
    4-digit exponentials gave 0.830783 — the 3e-5 gap was the TEST's
    arithmetic, verified and corrected 2026-08-14; the engine value stood.)"""
    assert float(calib["m1_ln_arg"]) == 5.0
    assert float(calib["trunc_factor"]) == 1.7
    x80, n = 20.0, 1.35
    meshes = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 34.0, 100.0, 200.0]
    all_coarse = PSD(meshes, [0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1.0])
    prod = models.m1_crusher_product(all_coarse, x80, n, calib)
    assert prod.passing_at(20.0) == pytest.approx(0.830814, abs=1e-5)
    # truncation: nothing of the crushed mass survives above 1.7·x80 = 34
    assert prod.passing_at(34.0) == pytest.approx(1.0, abs=1e-9)
