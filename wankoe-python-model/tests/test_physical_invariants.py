"""Physical monotonicities and limit laws (confidence program action 3,
2026-08-14).

The stress campaign (scripts/stress_test.py) proves the engine never
breaks conservation or produces non-physical numbers; THIS module proves
the engine moves in the RIGHT DIRECTION: every documented physical
monotonicity and limit behavior of zone 1.1, checked by engine runs.
"""

import pytest

from wankoe_model import load_parameters, run_scenario
from wankoe_model.grid import PSD
from wankoe_model import models
from wankoe_model.scenario import _flatten_calibration


def _yield_pct(overrides):
    return run_scenario(load_parameters(overrides=overrides))["indicators"]["kfs_yield_pct"]


def _kfs_in_cut(overrides):
    r = run_scenario(load_parameters(overrides=overrides))
    return r["products"]["KFS"]["compliance"]["in_cut_pct"]


def _rescaled_curve(k):
    """Shape-preserving size rescale of the measured feed curve (k > 1 =
    coarser), the same construction used for the quarry studies."""
    import math

    params = load_parameters()
    meas = {float(m): v for m, v in params["feed_product"]["cumulative_passing_curve"].items()}
    pts = sorted(meas.items())

    def passing_at(x):
        if x <= pts[0][0]:
            return pts[0][1] * x / pts[0][0]
        if x >= pts[-1][0]:
            return 100.0
        for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
            if x <= x1:
                t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
                return p0 + t * (p1 - p0)

    curve = {str(x): round(passing_at(x / k), 4) for x in meas}
    curve[str(pts[-1][0])] = 100.0
    return curve


# ------------------------------------------------------- flowsheet level
def test_coarser_feed_raises_kfs_yield():
    """Less sub-20 mm at the inlet -> more of the feed can become KFS.
    The central quarry-lever monotonicity."""
    finer = _yield_pct({"feed_product": {"cumulative_passing_curve": _rescaled_curve(0.8)}})
    base = _yield_pct({})
    coarser = _yield_pct({"feed_product": {"cumulative_passing_curve": _rescaled_curve(1.3)}})
    assert finer < base < coarser


def test_wider_roll_gap_raises_kfs_yield():
    """CR.5009 g wider -> coarser roll product -> less material broken
    below 20 mm (the 2026-08-13 optimization chose g at its max)."""
    assert _yield_pct(
        {"machines": {"CR.5009": {"parameters": {"g": {"default": 20}}}}}
    ) < _yield_pct({"machines": {"CR.5009": {"parameters": {"g": {"default": 60}}}}})


def test_wider_css_raises_kfs_yield():
    """CR.5011 CSS wider -> coarser impactor product -> more mass stays
    in the 20-35 cut instead of falling under 20."""
    assert _yield_pct(
        {"machines": {"CR.5011": {"parameters": {"x80": {"default": 15}}}}}
    ) < _yield_pct({"machines": {"CR.5011": {"parameters": {"x80": {"default": 30}}}}})


def test_slower_impactor_raises_kfs_yield():
    """Lower v -> lower Ecs -> lower t10 -> steeper product (JKMRC) ->
    fewer fines (the v = 30 adoption of 2026-08-14)."""
    assert _yield_pct(
        {"machines": {"CR.5011": {"parameters": {"v": {"default": 50}}}}}
    ) < _yield_pct({"machines": {"CR.5011": {"parameters": {"v": {"default": 30}}}}})


def test_sharper_screen_raises_kfs_in_cut():
    """Screen imperfection degrades the cut monotonically, and a
    near-perfect screen approaches a clean 20/35 window."""
    ic = [
        _kfs_in_cut({"machines": {"SR.5007": {"parameters": {"I": {"default": i}}}}})
        for i in (0.02, 0.10, 0.25, 0.40)
    ]
    assert ic[0] > ic[1] > ic[2] > ic[3]
    assert ic[0] > 96.0  # near-perfect screen limit


# ------------------------------------------------------------ model level
@pytest.fixture(scope="module")
def calib():
    return _flatten_calibration(load_parameters()["calibration"])


def test_m3_step_partition_limit(calib):
    """A nearly perfect screen (I -> 0) must send a mono-class far above
    the aperture almost entirely to oversize, and far below almost
    entirely to undersize."""
    coarse = PSD([70.0, 90.0, 200.0], [0.0, 1.0, 1.0])  # ~4x above a=20
    fine = PSD([4.0, 6.0, 200.0], [0.0, 1.0, 1.0])  # ~4x below
    over = models.m3_karra_partition(100.0, coarse, 20.0, 0.05, calib)
    under = models.m3_karra_partition(100.0, fine, 20.0, 0.05, calib)
    assert over["oversize_tph"] > 99.9
    assert under["undersize_tph"] > 99.9


def test_m1_all_fine_feed_bypasses_unchanged(calib):
    """M1 convention: the feed fraction already finer than x80 passes
    through unchanged — an all-fine feed leaves the crusher untouched."""
    meshes = [1.0, 2.0, 5.0, 10.0, 200.0]
    fine = PSD(meshes, [0.10, 0.35, 0.80, 1.0, 1.0])
    prod = models.m1_crusher_product(fine, 60.0, 1.35, calib)
    for m, before in zip(meshes, fine.passing):
        assert prod.passing_at(m) == pytest.approx(before, abs=1e-9)


def test_m6_no_drying_limit(calib):
    """Feed already at the target moisture: zero evaporation, zero duty."""
    out = models.m6_drying(30.0, 0.5, 0.5, calib)
    assert out["evaporated_water_tph"] == pytest.approx(0.0, abs=1e-12)


def test_m2_no_energy_when_product_not_finer(calib):
    """Bond law floor: a 'product' coarser than the feed costs zero
    comminution energy (never negative)."""
    out = models.m2_bond_power(100.0, 20.0, 25.0, calib)
    assert out["W_kWh_t"] == 0.0
