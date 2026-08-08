"""Wankoe Python Model — limestone processing line calculation model.

Static deterministic flowsheet of zones 1.1 / 1.2 / 1.3: each call to
``run_scenario`` computes the synchronized "photo" of the line for one
parameter set. Data lives in data/default_parameters.json, separated from
the code.
"""

from wankoe_model.fit import fit_parameters
from wankoe_model.grid import PSD, engine_grid
from wankoe_model.planning import run_required_hours
from wankoe_model.scenario import (
    DEFAULT_PARAMETERS_PATH,
    REFERENCE_FEED_CURVE_PATH,
    load_parameters,
    run_scenario,
    run_seasonal_balance,
)

__all__ = [
    "PSD",
    "engine_grid",
    "load_parameters",
    "run_scenario",
    "run_seasonal_balance",
    "run_required_hours",
    "fit_parameters",
    "DEFAULT_PARAMETERS_PATH",
    "REFERENCE_FEED_CURVE_PATH",
]
__version__ = "0.3.0"
