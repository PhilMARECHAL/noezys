"""Mesh grid and particle size distribution (PSD) curves.

Convention (specification §1.3): a size distribution curve is the cumulative
% passing at each mesh, meshes on a log scale. Internally proportions are
mass fractions 0-1; percentages are only used for reporting.

The engine grid = reference mesh series + extension meshes (parameter
``engine.extension_meshes_mm``) so it can carry crusher products coarser
than the last reference mesh.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def engine_grid(reference_series: Sequence[float], extension: Sequence[float]) -> list[float]:
    """Internal grid: reference series + extension meshes, sorted."""
    meshes = sorted(set(float(x) for x in reference_series) | set(float(x) for x in extension))
    if any(m <= 0 for m in meshes):
        raise ValueError("all meshes must be > 0 mm")
    return meshes


class PSD:
    """Particle size distribution: cumulative passing (fractions 0-1) on a grid.

    ``passing[i]`` = mass fraction finer than ``meshes[i]``. The last value
    must be 1 (the whole stream is finer than the last engine-grid mesh).
    """

    def __init__(self, meshes: Sequence[float], passing: Sequence[float]):
        if len(meshes) != len(passing):
            raise ValueError("meshes and passing must have the same length")
        self.meshes = [float(x) for x in meshes]
        p = [min(1.0, max(0.0, float(v))) for v in passing]
        # enforce monotonicity (noisy measurements are clipped)
        for i in range(1, len(p)):
            p[i] = max(p[i], p[i - 1])
        if p[-1] < 1.0 - 1e-9:
            raise ValueError(
                f"passing at the last mesh ({self.meshes[-1]} mm) = {p[-1]:.4f} < 1: "
                "extend the grid (parameter engine.extension_meshes_mm)"
            )
        p[-1] = 1.0
        self.passing = p

    # ---------------------------------------------------------------- access
    def passing_at(self, x: float) -> float:
        """Cumulative passing at size x (mm), interpolated linearly in log(x)."""
        m, p = self.meshes, self.passing
        if x <= 0:
            return 0.0
        if x <= m[0]:
            # below the first mesh: linear interpolation toward (0, 0)
            return p[0] * x / m[0]
        if x >= m[-1]:
            return 1.0
        for i in range(1, len(m)):
            if x <= m[i]:
                t = (math.log(x) - math.log(m[i - 1])) / (math.log(m[i]) - math.log(m[i - 1]))
                return p[i - 1] + t * (p[i] - p[i - 1])
        return 1.0

    def size_at_passing(self, target: float) -> float:
        """Size (mm) at which the cumulative passing equals ``target`` (e.g. 0.80 -> P80)."""
        if not 0.0 < target < 1.0:
            raise ValueError("target must be within ]0;1[")
        m, p = self.meshes, self.passing
        if p[0] >= target:
            return m[0] * target / max(p[0], 1e-12)
        for i in range(1, len(m)):
            if p[i] >= target:
                if p[i] == p[i - 1]:
                    return m[i]
                t = (target - p[i - 1]) / (p[i] - p[i - 1])
                return math.exp(math.log(m[i - 1]) + t * (math.log(m[i]) - math.log(m[i - 1])))
        return m[-1]

    def p80(self) -> float:
        # 0.80 is the definition of P80/F80 (Bond law), a mathematical identity
        return self.size_at_passing(0.80)

    def fraction_between(self, a: float, b: float) -> float:
        """Mass fraction within the ]a ; b] cut (mm)."""
        if b < a:
            a, b = b, a
        return max(0.0, self.passing_at(b) - self.passing_at(a))

    # ---------------------------------------------------------- per interval
    def interval_fractions(self) -> list[float]:
        """Mass fraction per interval; interval i = ]mesh[i-1] ; mesh[i]],
        interval 0 = ]0 ; mesh[0]]."""
        f = [self.passing[0]]
        for i in range(1, len(self.meshes)):
            f.append(self.passing[i] - self.passing[i - 1])
        return f

    def representative_sizes(self, bottom_interval_ratio: float = 2.0) -> list[float]:
        """Representative size of each interval (geometric mean of the bounds).

        For the bottom interval the conventional lower bound is
        mesh / bottom_interval_ratio (parameter ``calibration.bottom_interval_ratio``),
        giving rep. size = mesh / sqrt(ratio).
        """
        reps = [self.meshes[0] / math.sqrt(bottom_interval_ratio)]
        for i in range(1, len(self.meshes)):
            reps.append(math.sqrt(self.meshes[i - 1] * self.meshes[i]))
        return reps

    @classmethod
    def from_intervals(cls, meshes: Sequence[float], fractions: Sequence[float]) -> "PSD":
        """Builds a PSD from per-interval fractions (renormalized)."""
        total = sum(fractions)
        if total <= 0:
            raise ValueError("empty stream: all fractions are zero")
        cumulative, acc = [], 0.0
        for f in fractions:
            acc += f / total
            cumulative.append(min(1.0, acc))
        cumulative[-1] = 1.0
        return cls(meshes, cumulative)

    # ----------------------------------------------------------------- blend
    @staticmethod
    def blend(streams: Sequence[tuple[float, "PSD"]]) -> tuple[float, "PSD"]:
        """Mass blend of streams (q in t/h, PSD). Returns (total_q, PSD)."""
        streams = [(q, psd) for q, psd in streams if q > 0]
        if not streams:
            raise ValueError("blending streams that are all empty")
        meshes = streams[0][1].meshes
        total_q = sum(q for q, _ in streams)
        passing = [
            sum(q * psd.passing[i] for q, psd in streams) / total_q
            for i in range(len(meshes))
        ]
        return total_q, PSD(meshes, passing)

    def on_series(self, series: Sequence[float]) -> list[float]:
        """Cumulative passing (%) resampled on a mesh series (for reporting)."""
        return [round(100.0 * self.passing_at(x), 3) for x in series]
