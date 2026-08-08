"""Grille de mailles et courbes granulométriques (PSD).

Convention (cahier des charges §1.3) : courbe granulométrique = % passant
cumulé à chaque maille, mailles en échelle log. En interne les proportions
sont des fractions massiques 0–1 ; l'affichage en % se fait en sortie.

La grille moteur = série de mailles de référence + mailles d'extension
(paramètre ``mailles_extension``) pour porter les produits de concassage
plus grossiers que la dernière maille de référence.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def grille_moteur(serie_reference: Sequence[float], extension: Sequence[float]) -> list[float]:
    """Grille interne : série de référence + mailles d'extension, triées."""
    mailles = sorted(set(float(x) for x in serie_reference) | set(float(x) for x in extension))
    if any(m <= 0 for m in mailles):
        raise ValueError("toutes les mailles doivent être > 0 mm")
    return mailles


class PSD:
    """Courbe granulométrique : passant cumulé (fractions 0–1) sur une grille.

    ``passant[i]`` = fraction massique plus fine que ``mailles[i]``.
    La dernière valeur doit valoir 1 (tout le flux est plus fin que la
    dernière maille de la grille moteur).
    """

    def __init__(self, mailles: Sequence[float], passant: Sequence[float]):
        if len(mailles) != len(passant):
            raise ValueError("mailles et passant doivent avoir la même longueur")
        self.mailles = [float(x) for x in mailles]
        p = [min(1.0, max(0.0, float(v))) for v in passant]
        # monotonie croissante imposée (les mesures bruitées sont écrêtées)
        for i in range(1, len(p)):
            p[i] = max(p[i], p[i - 1])
        if p[-1] < 1.0 - 1e-9:
            raise ValueError(
                f"passant à la dernière maille ({self.mailles[-1]} mm) = {p[-1]:.4f} < 1 : "
                "étendre la grille (paramètre mailles_extension)"
            )
        p[-1] = 1.0
        self.passant = p

    # ------------------------------------------------------------------ accès
    def passant_a(self, x: float) -> float:
        """Passant cumulé à la taille x (mm), interpolé linéairement en log(x)."""
        m, p = self.mailles, self.passant
        if x <= 0:
            return 0.0
        if x <= m[0]:
            # sous la première maille : interpolation linéaire vers (0, 0)
            return p[0] * x / m[0]
        if x >= m[-1]:
            return 1.0
        for i in range(1, len(m)):
            if x <= m[i]:
                t = (math.log(x) - math.log(m[i - 1])) / (math.log(m[i]) - math.log(m[i - 1]))
                return p[i - 1] + t * (p[i] - p[i - 1])
        return 1.0

    def taille_a_passant(self, cible: float) -> float:
        """Taille (mm) où le passant cumulé vaut ``cible`` (ex. 0,80 → P80)."""
        if not 0.0 < cible < 1.0:
            raise ValueError("cible doit être dans ]0;1[")
        m, p = self.mailles, self.passant
        if p[0] >= cible:
            return m[0] * cible / max(p[0], 1e-12)
        for i in range(1, len(m)):
            if p[i] >= cible:
                if p[i] == p[i - 1]:
                    return m[i]
                t = (cible - p[i - 1]) / (p[i] - p[i - 1])
                return math.exp(math.log(m[i - 1]) + t * (math.log(m[i]) - math.log(m[i - 1])))
        return m[-1]

    def p80(self) -> float:
        return self.taille_a_passant(0.80)

    def fraction_entre(self, a: float, b: float) -> float:
        """Fraction massique dans la coupure ]a ; b] (mm)."""
        if b < a:
            a, b = b, a
        return max(0.0, self.passant_a(b) - self.passant_a(a))

    # ------------------------------------------------------------- par tranche
    def fractions_tranches(self) -> list[float]:
        """Fraction massique par tranche ; tranche i = ]maille[i-1] ; maille[i]],
        tranche 0 = ]0 ; maille[0]]."""
        f = [self.passant[0]]
        for i in range(1, len(self.mailles)):
            f.append(self.passant[i] - self.passant[i - 1])
        return f

    def tailles_representatives(self) -> list[float]:
        """Taille représentative de chaque tranche (moyenne géométrique des bornes ;
        pour la tranche du bas, borne basse conventionnelle = maille/2)."""
        reps = [self.mailles[0] / math.sqrt(2.0)]
        for i in range(1, len(self.mailles)):
            reps.append(math.sqrt(self.mailles[i - 1] * self.mailles[i]))
        return reps

    @classmethod
    def depuis_tranches(cls, mailles: Sequence[float], fractions: Sequence[float]) -> "PSD":
        """Construit une PSD depuis des fractions par tranche (renormalisées)."""
        total = sum(fractions)
        if total <= 0:
            raise ValueError("flux vide : fractions nulles")
        cumul, acc = [], 0.0
        for f in fractions:
            acc += f / total
            cumul.append(min(1.0, acc))
        cumul[-1] = 1.0
        return cls(mailles, cumul)

    # ---------------------------------------------------------------- mélange
    @staticmethod
    def melange(flux: Sequence[tuple[float, "PSD"]]) -> tuple[float, "PSD"]:
        """Mélange massique de flux (q en t/h, PSD). Retourne (q_total, PSD)."""
        flux = [(q, psd) for q, psd in flux if q > 0]
        if not flux:
            raise ValueError("mélange de flux tous nuls")
        mailles = flux[0][1].mailles
        q_total = sum(q for q, _ in flux)
        passant = [
            sum(q * psd.passant[i] for q, psd in flux) / q_total
            for i in range(len(mailles))
        ]
        return q_total, PSD(mailles, passant)

    def sur_serie(self, serie: Sequence[float]) -> list[float]:
        """Passant cumulé (%) ré-échantillonné sur une série de mailles (rapport)."""
        return [round(100.0 * self.passant_a(x), 3) for x in serie]
