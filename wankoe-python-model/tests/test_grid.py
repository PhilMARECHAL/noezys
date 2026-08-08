"""Tests of the mesh grid and PSD curves."""

import pytest

from wankoe_model.grid import PSD, engine_grid

MESHES = [1.0, 2.0, 4.0, 8.0, 16.0]


def test_engine_grid_merged_and_sorted():
    g = engine_grid([1, 4, 2], [8, 4])
    assert g == [1.0, 2.0, 4.0, 8.0]


def test_psd_interpolation_and_bounds():
    psd = PSD(MESHES, [0.1, 0.3, 0.6, 0.9, 1.0])
    assert psd.passing_at(2.0) == pytest.approx(0.3)
    assert psd.passing_at(0.0) == 0.0
    assert psd.passing_at(100.0) == 1.0
    # log interpolation between 2 and 4 mm: halfway at the geometric mean
    assert psd.passing_at(2.0 * 2.0 ** 0.5) == pytest.approx(0.45)


def test_psd_p80():
    psd = PSD(MESHES, [0.1, 0.3, 0.6, 0.9, 1.0])
    p80 = psd.p80()
    assert 4.0 < p80 < 8.0
    assert psd.passing_at(p80) == pytest.approx(0.8, abs=1e-9)


def test_psd_incomplete_last_mesh_rejected():
    with pytest.raises(ValueError):
        PSD(MESHES, [0.1, 0.2, 0.3, 0.4, 0.5])


def test_intervals_round_trip():
    psd = PSD(MESHES, [0.1, 0.3, 0.6, 0.9, 1.0])
    fr = psd.interval_fractions()
    assert sum(fr) == pytest.approx(1.0)
    psd2 = PSD.from_intervals(MESHES, fr)
    assert psd2.passing == pytest.approx(psd.passing)


def test_bottom_interval_ratio_is_adjustable():
    psd = PSD(MESHES, [0.1, 0.3, 0.6, 0.9, 1.0])
    reps_default = psd.representative_sizes(2.0)
    reps_wide = psd.representative_sizes(4.0)
    assert reps_wide[0] < reps_default[0]
    assert reps_wide[1:] == reps_default[1:]


def test_blend_conserves_mass_and_curve():
    a = PSD(MESHES, [0.2, 0.4, 0.6, 0.8, 1.0])
    b = PSD(MESHES, [0.0, 0.2, 0.4, 0.8, 1.0])
    q, m = PSD.blend([(10.0, a), (30.0, b)])
    assert q == pytest.approx(40.0)
    assert m.passing[0] == pytest.approx((10 * 0.2 + 30 * 0.0) / 40)
