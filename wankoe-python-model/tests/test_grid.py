"""Tests de la grille de mailles et des courbes PSD."""

import pytest

from wankoe_model.grid import PSD, grille_moteur

MAILLES = [1.0, 2.0, 4.0, 8.0, 16.0]


def test_grille_moteur_fusion_triee():
    g = grille_moteur([1, 4, 2], [8, 4])
    assert g == [1.0, 2.0, 4.0, 8.0]


def test_psd_interpolation_et_bornes():
    psd = PSD(MAILLES, [0.1, 0.3, 0.6, 0.9, 1.0])
    assert psd.passant_a(2.0) == pytest.approx(0.3)
    assert psd.passant_a(0.0) == 0.0
    assert psd.passant_a(100.0) == 1.0
    # interpolation log entre 2 et 4 mm : à la moyenne géométrique, mi-chemin
    assert psd.passant_a(2.0 * 2.0 ** 0.5) == pytest.approx(0.45)


def test_psd_p80():
    psd = PSD(MAILLES, [0.1, 0.3, 0.6, 0.9, 1.0])
    p80 = psd.p80()
    assert 4.0 < p80 < 8.0
    assert psd.passant_a(p80) == pytest.approx(0.8, abs=1e-9)


def test_psd_derniere_maille_incomplete_refusee():
    with pytest.raises(ValueError):
        PSD(MAILLES, [0.1, 0.2, 0.3, 0.4, 0.5])


def test_tranches_aller_retour():
    psd = PSD(MAILLES, [0.1, 0.3, 0.6, 0.9, 1.0])
    fr = psd.fractions_tranches()
    assert sum(fr) == pytest.approx(1.0)
    psd2 = PSD.depuis_tranches(MAILLES, fr)
    assert psd2.passant == pytest.approx(psd.passant)


def test_melange_conserve_masse_et_courbe():
    a = PSD(MAILLES, [0.2, 0.4, 0.6, 0.8, 1.0])
    b = PSD(MAILLES, [0.0, 0.2, 0.4, 0.8, 1.0])
    q, m = PSD.melange([(10.0, a), (30.0, b)])
    assert q == pytest.approx(40.0)
    assert m.passant[0] == pytest.approx((10 * 0.2 + 30 * 0.0) / 40)
