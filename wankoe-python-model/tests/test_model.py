"""Tests unitaires du modèle Wankoe."""

import pytest

from wankoe_model import WankoeModel


def test_predict_returns_mean():
    model = WankoeModel()
    assert model.predict([1.0, 2.0, 3.0]) == pytest.approx(2.0)


def test_predict_empty_raises():
    model = WankoeModel()
    with pytest.raises(ValueError):
        model.predict([])


def test_fit_returns_self():
    model = WankoeModel()
    assert model.fit([1.0]) is model


def test_fit_empty_raises():
    model = WankoeModel()
    with pytest.raises(ValueError):
        model.fit([])
