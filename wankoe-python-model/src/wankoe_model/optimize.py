"""Automatic scenario sweeps and optimum search (specification §7.3 / §8).

The engine itself never optimizes nor imposes an operating choice: this
module simply AUTOMATES what a user does by hand — define many scenarios,
run the photos, score them, rank them. Every scenario evaluation is a call
to the pure ``run_scenario`` / ``run_seasonal_balance`` functions.

A sweep is described by a JSON config (see data/sweep_example.json):

- ``variables``: parameters to explore. Each has a ``path`` (list of keys
  into the parameter dict — lists, because keys like "SR.5007" or "1.1"
  contain dots) and either explicit ``values`` or a ``min``/``max``/``step``
  range.
- ``method``: "grid" (full cartesian product) or "random" (uniform sampling,
  ``random_samples`` draws, reproducible via ``random_seed``).
- ``objective``: weights of the score (lower is better), aligned with the
  specification's arbitration rule — meet the FIRM targets first, then
  minimize the unsellable surplus, optionally minimize installed power.
- ``max_scenarios``: hard safety cap on the number of evaluations.

Scoring uses the period balance (t per period) when available hours are
provided; otherwise it falls back to hourly rates × 1 h, flagged in the
report — targets are yearly, so hours should be provided for real studies.
"""

from __future__ import annotations

import copy
import itertools
import random

from .paths import set_path
from .scenario import run_scenario, run_seasonal_balance


def _variable_values(var: dict) -> list:
    if "values" in var:
        return list(var["values"])
    lo, hi, step = var["min"], var["max"], var["step"]
    if step <= 0:
        raise ValueError(f"variable {var['path']}: step must be > 0")
    values, v = [], lo
    while v <= hi + 1e-9:
        values.append(round(v, 10))
        v += step
    return values


def _variable_label(var: dict) -> str:
    return var.get("label") or ".".join(str(k) for k in var["path"])


def _draw_random(var: dict, rng: random.Random):
    if "values" in var:
        return rng.choice(list(var["values"]))
    return round(rng.uniform(var["min"], var["max"]), 10)


def _kpis(params: dict, results: dict, per_product: dict | None) -> dict:
    """KPIs of one scenario: firm shortfall, unsellable surplus, power, alerts."""
    targets = params["production_targets"]
    firm_shortfall = 0.0
    surplus = 0.0
    fines_surplus = 0.0
    tonnages = {}
    for target in targets.values():
        product = target["product"]
        if per_product is not None:
            tonnage = per_product.get(product, {}).get("tonnage_t", 0.0)
        else:
            tonnage = results["products"].get(product, {}).get("tph", 0.0)
        tonnages[product] = tonnage
        if target["nature"] == "FIRM":
            firm_shortfall += max(0.0, target["target_t_per_year"] - tonnage)
        cap = target.get("market_cap_t_per_year")
        if cap is None and target["nature"] == "flexible":
            cap = target["target_t_per_year"]  # flexible: the target IS the market estimate
        if cap is not None:
            over = max(0.0, tonnage - cap)
            surplus += over
            # spec §7.3/§8: limestone fines are the PRIORITY surplus to avoid
            if product == "FeedLime fines":
                fines_surplus += over
    total_power = sum(
        m.get("P_installed_kW", 0.0)
        for m in results["machines"].values()
        if isinstance(m, dict)
    )
    # phantom-stockpile guard (expert review 2026-08-08): tonnages reclaimed
    # beyond what upstream produces over the period are not achievable
    pb = results.get("period_balance")
    stockpile_deficit = pb.get("stockpile_deficit_t", 0.0) if pb else 0.0
    return {
        "tonnages": tonnages,
        "firm_shortfall_t": round(firm_shortfall, 1),
        "unsellable_surplus_t": round(surplus, 1),
        "fines_surplus_t": round(fines_surplus, 1),
        "stockpile_deficit_t": round(stockpile_deficit, 1),
        "total_installed_power_kW": round(total_power, 1),
        "n_alerts": len(results["alerts"]),
    }


def _score(kpis: dict, objective: dict) -> float:
    # fines_surplus_weight > 1 encodes the spec's arbitration rule (§7.3/§8):
    # the limestone-fines surplus is the priority one to minimize
    fines_extra = max(0.0, objective.get("fines_surplus_weight", 2.0) - 1.0)
    return (
        objective.get("firm_shortfall_weight", 100.0) * kpis["firm_shortfall_t"]
        + objective.get("surplus_weight", 1.0) * kpis["unsellable_surplus_t"]
        + objective.get("surplus_weight", 1.0) * fines_extra * kpis["fines_surplus_t"]
        + objective.get("stockpile_deficit_weight", 100.0) * kpis["stockpile_deficit_t"]
        + objective.get("power_weight", 0.0) * kpis["total_installed_power_kW"]
        + objective.get("alert_weight", 0.0) * kpis["n_alerts"]
    )


def run_sweep(base_params: dict, config: dict) -> dict:
    """Runs a parameter sweep and returns the ranked scenarios (best first)."""
    variables = config["variables"]
    if not variables:
        raise ValueError("sweep config has no variables")
    method = config.get("method", "grid")
    max_scenarios = int(config.get("max_scenarios", 2000))
    labels = [_variable_label(v) for v in variables]

    if method == "grid":
        value_lists = [_variable_values(v) for v in variables]
        n_combos = 1
        for vl in value_lists:
            n_combos *= len(vl)
        if n_combos > max_scenarios:
            raise ValueError(
                f"grid sweep would evaluate {n_combos} scenarios > max_scenarios "
                f"{max_scenarios}: raise the cap or use method 'random'"
            )
        combos = itertools.product(*value_lists)
    elif method == "random":
        rng = random.Random(config.get("random_seed", 0))
        samples = int(config.get("random_samples", 100))
        if samples > max_scenarios:
            raise ValueError(f"random_samples {samples} > max_scenarios {max_scenarios}")
        combos = [tuple(_draw_random(v, rng) for v in variables) for _ in range(samples)]
    else:
        raise ValueError(f"unknown sweep method: {method}")

    use_seasonal = config.get("seasonal", True)
    hours_provided = all(
        z["available_hours"] is not None
        for z in base_params["default_scenario"]["zones"].values()
    )
    objective = config.get("objective", {})

    evaluated, failed, rows = 0, [], []
    for combo in combos:
        params = copy.deepcopy(base_params)
        for var, value in zip(variables, combo):
            set_path(params, var["path"], value)
        try:
            if hours_provided and use_seasonal:
                seasonal = run_seasonal_balance(params)
                results = seasonal["photos"]["dry"]  # machine KPIs from the dry photo
                per_product = seasonal["combined"]
            else:
                results = run_scenario(params)
                pb = results["period_balance"]
                per_product = pb["per_product"] if pb else None
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            failed.append({"values": dict(zip(labels, combo)), "error": str(exc)})
            continue
        # no steady state (a closed circuit did not converge) -> the photo's
        # tonnages are not physical: reject the scenario explicitly instead
        # of letting the sweep rank it (stress-test policy 2026-08-08)
        open_balances = [k for k, b in results["balances"].items() if not b["closed"]]
        if open_balances:
            failed.append({
                "values": dict(zip(labels, combo)),
                "error": f"no steady state: balance(s) {', '.join(open_balances)} not closed "
                         "(closed-circuit loop did not converge)",
            })
            continue
        kpis = _kpis(params, results, per_product)
        rows.append(
            {
                "values": dict(zip(labels, combo)),
                "score": round(_score(kpis, objective), 3),
                "kpis": kpis,
            }
        )
        evaluated += 1

    rows.sort(key=lambda r: r["score"])
    top_n = int(config.get("top_n", 10))
    return {
        "method": method,
        "evaluated": evaluated,
        "failed": failed,
        "tonnage_basis": (
            "per period (seasonal dry/rain mix)"
            if hours_provided and use_seasonal
            else "per period"
            if hours_provided
            else "PER HOUR PROXY - provide available hours for real target comparisons"
        ),
        "objective": {
            "firm_shortfall_weight": objective.get("firm_shortfall_weight", 100.0),
            "surplus_weight": objective.get("surplus_weight", 1.0),
            "stockpile_deficit_weight": objective.get("stockpile_deficit_weight", 100.0),
            "power_weight": objective.get("power_weight", 0.0),
            "alert_weight": objective.get("alert_weight", 0.0),
        },
        "best": rows[0] if rows else None,
        "top": rows[:top_n],
        "all_scores": [r["score"] for r in rows],
    }
