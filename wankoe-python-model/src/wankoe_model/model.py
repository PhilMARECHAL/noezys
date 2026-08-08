"""Modèle principal du projet Wankoe.

Squelette de départ : la classe WankoeModel expose une interface
classique (fit / predict) à compléter avec la logique métier réelle.
"""

from __future__ import annotations

from collections.abc import Sequence


class WankoeModel:
    """Modèle Wankoe.

    Implémentation de départ : `predict` renvoie la moyenne des valeurs
    d'entrée, en attendant la définition du modèle définitif.
    """

    def __init__(self, name: str = "wankoe") -> None:
        self.name = name
        self._fitted = False

    def fit(self, data: Sequence[float]) -> "WankoeModel":
        """Entraîne le modèle sur les données fournies."""
        if not data:
            raise ValueError("data ne doit pas être vide")
        self._fitted = True
        return self

    def predict(self, values: Sequence[float]) -> float:
        """Calcule une prédiction à partir des valeurs d'entrée."""
        if not values:
            raise ValueError("values ne doit pas être vide")
        return sum(values) / len(values)
