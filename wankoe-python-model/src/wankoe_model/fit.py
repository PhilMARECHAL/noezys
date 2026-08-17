"""Auto-calibration on plant measurements (specification preamble).

Fits any set of free parameters (the [H] coefficients, or anything else in
the parameter dict) so that the model reproduces measured quantities. Both
sides are described by paths, no code change needed:

- an OBSERVATION targets a value in the ``run_scenario`` result dict:
  {"result_path": ["machines", "CR.5006", "P_installed_kW"],
   "measured": 141.0, "weight": 1.0}
- a FREE PARAMETER points into the parameter dict, with its allowed range:
  {"path": ["calibration", "Wi", "default"], "min": 8, "max": 20}

The cost is the weighted sum of squared RELATIVE errors. The search is a
derivative-free pattern search (coordinate descent with shrinking steps) —
robust for the smooth, low-dimensional fits this model needs, with no
extra dependency.
"""

from __future__ import annotations

import copy

from .paths import get_path as _get_path, set_path as _set_path
from .scenario import run_scenario


def _label(entry: dict) -> str:
    return entry.get("label") or ".".join(str(k) for k in entry["path"])


def _evaluate(params: dict, observations: list) -> tuple[float, dict]:
    results = run_scenario(params)
    cost, achieved = 0.0, {}
    for obs in observations:
        value = _get_path(results, obs["result_path"])
        if value is None:
            raise ValueError(f"observation {obs['result_path']}: result is None")
        scale = abs(obs["measured"]) if obs["measured"] else 1.0
        cost += obs.get("weight", 1.0) * ((value - obs["measured"]) / scale) ** 2
        achieved[".".join(str(k) for k in obs["result_path"])] = value
    return cost, achieved


def fit_parameters(
    base_params: dict,
    observations: list,
    free_parameters: list,
    max_rounds: int = 80,
    tolerance: float = 1e-4,
) -> dict:
    """Fits the free parameters to the observations. Returns a fit report."""
    if not observations or not free_parameters:
        raise ValueError("fit needs at least one observation and one free parameter")
    params = copy.deepcopy(base_params)

    values = []
    for fp in free_parameters:
        current = _get_path(params, fp["path"])
        start = fp.get("start", current if current is not None else (fp["min"] + fp["max"]) / 2)
        start = min(fp["max"], max(fp["min"], start))
        _set_path(params, fp["path"], start)
        values.append(start)

    initial_cost, _ = _evaluate(params, observations)
    cost = initial_cost
    steps = [(fp["max"] - fp["min"]) / 4.0 for fp in free_parameters]
    achieved = {}

    for _ in range(max_rounds):
        improved = False
        for i, fp in enumerate(free_parameters):
            for sign in (+1, -1):
                candidate = min(fp["max"], max(fp["min"], values[i] + sign * steps[i]))
                if candidate == values[i]:
                    continue
                _set_path(params, fp["path"], candidate)
                try:
                    c, a = _evaluate(params, observations)
                except (ValueError, ZeroDivisionError, OverflowError):
                    _set_path(params, fp["path"], values[i])
                    continue
                if c < cost:
                    cost, achieved, values[i] = c, a, candidate
                    improved = True
                else:
                    _set_path(params, fp["path"], values[i])
        if not improved:
            if max(s / (fp["max"] - fp["min"]) for s, fp in zip(steps, free_parameters)) < tolerance:
                break
            steps = [s / 2.0 for s in steps]

    if not achieved:
        _, achieved = _evaluate(params, observations)
    return {
        "fitted": {
            _label(fp): round(v, 6) for fp, v in zip(free_parameters, values)
        },
        "fitted_paths": [
            {"path": fp["path"], "value": round(v, 6)}
            for fp, v in zip(free_parameters, values)
        ],
        "initial_cost": round(initial_cost, 8),
        "final_cost": round(cost, 8),
        "observations": [
            {
                "target": ".".join(str(k) for k in obs["result_path"]),
                "measured": obs["measured"],
                "achieved": round(
                    achieved[".".join(str(k) for k in obs["result_path"])], 4
                ),
            }
            for obs in observations
        ],
    }
