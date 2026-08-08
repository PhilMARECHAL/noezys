"""Scenario execution: the synchronized "photo" of the line.

run_scenario(params) is a PURE FUNCTION: a parameter dict goes in, a result
dict comes out (flows, size curves, powers, balances, compliance, alerts).
No global state — the function can be called massively for parameter sweeps
and optimum searches.

Default parameters live in data/default_parameters.json;
``load_parameters(overrides=...)`` applies deep-merged overrides without
ever modifying the file.

``run_seasonal_balance(params)`` runs the dry-weather and rain-weather
photos and mixes them with the season fractions (specification §7.2).
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from .grid import PSD, engine_grid
from . import flowsheet

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PARAMETERS_PATH = _ROOT / "data" / "default_parameters.json"
REFERENCE_FEED_CURVE_PATH = _ROOT / "data" / "reference_feed_curve.json"


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_parameters(path=None, overrides: dict | None = None) -> dict:
    """Loads the parameter set (JSON) and applies optional overrides."""
    with open(path or DEFAULT_PARAMETERS_PATH, encoding="utf-8") as f:
        params = json.load(f)
    if overrides:
        params = _deep_merge(params, overrides)
    return params


def _flatten_calibration(calibration: dict) -> dict:
    """{symbol: value} from the {name, unit, default, ...} records of the JSON."""
    return {
        key: (entry["default"] if isinstance(entry, dict) and "default" in entry else entry)
        for key, entry in calibration.items()
    }


def _validate_bounds(params: dict, alerts: list) -> None:
    """Warns when a machine setting sits outside its [min; max] range.

    The engine never blocks (it 'imposes no operating choice'), but automatic
    sweeps must not silently run out-of-range scenarios (audit finding §2).
    """
    for code, machine in params["machines"].items():
        for symbol, spec in machine.get("parameters", {}).items():
            value = spec.get("default")
            if value is None:
                continue
            lo, hi = spec.get("min"), spec.get("max")
            if (lo is not None and value < lo) or (hi is not None and value > hi):
                alerts.append(
                    f"{code}.{symbol} = {value} {spec.get('unit', '')} outside "
                    f"the allowed range [{lo}; {hi}]"
                )


def _build_feed(params: dict, alerts: list) -> tuple:
    """Builds the pivot feed stream from the parameters (curve + moisture).

    When no measured curve is provided, falls back to the CALIBRATED
    reference curve (working hypothesis) — reported as an alert.
    """
    fp = params["feed_product"]
    curve = fp["cumulative_passing_curve"]
    if not curve:
        if REFERENCE_FEED_CURVE_PATH.exists():
            with open(REFERENCE_FEED_CURVE_PATH, encoding="utf-8") as f:
                curve = json.load(f)["cumulative_passing_curve"]
            alerts.append(
                "Feed curve: no measurement provided — CALIBRATED reference curve "
                "used (hypothesis, to be replaced by a real measurement)"
            )
        else:
            raise ValueError(
                "Feed size curve missing (feed_product.cumulative_passing_curve) "
                "and no calibrated reference curve available."
            )
    grid = engine_grid(params["mesh_series_mm"], params["engine"]["extension_meshes_mm"])
    psd = PSD(grid, [interp_curve(curve, x) for x in grid])
    moisture = fp["properties"]["moisture_pct"]["default"]
    return psd, moisture


def interp_curve(curve: dict, x_mm: float) -> float:
    """Interpolates a {mesh: % passing} curve in log(x); returns a 0-1 fraction."""
    points = sorted((float(k), float(v) / 100.0) for k, v in curve.items())
    if x_mm <= points[0][0]:
        return points[0][1] * x_mm / points[0][0]
    if x_mm >= points[-1][0]:
        return 1.0 if points[-1][1] > 0.999 else points[-1][1]
    for (x0, p0), (x1, p1) in zip(points, points[1:]):
        if x_mm <= x1:
            t = (math.log(x_mm) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return p0 + t * (p1 - p0)
    return 1.0


def _wet_tonnage(stream) -> float:
    """WET tonnage of a stream (t/h) — wet products are sold wet."""
    if stream is None:
        return 0.0
    return stream["q"] / (1.0 - stream["moisture"] / 100.0)


def _product_compliance(stream, spec: dict) -> dict | None:
    if stream is None:
        return None
    out_of_cut = 1.0 - stream["psd"].fraction_between(spec["cut_min_mm"], spec["cut_max_mm"])
    tol = spec.get("max_out_of_cut_tol_pct")
    return {
        "out_of_cut_pct": round(100.0 * out_of_cut, 2),
        "tolerance_pct": tol,
        "compliant": None if tol is None else bool(100.0 * out_of_cut <= tol),
    }


def run_scenario(params: dict) -> dict:
    """Runs one full scenario and returns the line "photo"."""
    params = {**params, "calibration": _flatten_calibration(params["calibration"])}
    alerts: list[str] = []
    sc = params["default_scenario"]
    calib = params["calibration"]
    engine = params["engine"]
    weather = sc["weather"]

    # measured feed Bond index overrides the calibration value when provided
    feed_wi = params["feed_product"]["properties"]["Wi_kWht"]["default"]
    if feed_wi is not None:
        calib["Wi"] = feed_wi

    _validate_bounds(params, alerts)
    feed_psd, moisture = _build_feed(params, alerts)

    # ---------------- Zone 1.1
    q_feed = sc["flow_rates_tph"]["zone_1_1_feed"]
    feed = {"q": q_feed * (1.0 - moisture / 100.0), "psd": feed_psd, "moisture": moisture}
    z11 = flowsheet.zone_1_1(feed, params, sc["zone_1_1_mode"], alerts)

    # ---------------- Zone 1.2 (reclaim from the 0/20 stockpile)
    q_reclaim = sc["flow_rates_tph"]["zone_1_2_reclaim"]
    stream_0_20 = z11["products"]["0/20"]
    if stream_0_20 is None:
        raise ValueError("Zone 1.1 produces no 0/20: inconsistent scenario")
    reclaim = {
        "q": q_reclaim * (1.0 - moisture / 100.0),
        "psd": stream_0_20["psd"],
        "moisture": moisture,
    }
    z12 = flowsheet.zone_1_2(reclaim, params, sc["zone_1_2_mode"], weather, alerts)

    # ---------------- Zone 1.3 (reclaim from the FeedLime stockpile)
    q_feedlime = sc["flow_rates_tph"]["zone_1_3_feedlime"]
    stream_fl = z12["products"]["FeedLime"]
    if stream_fl is not None and q_feedlime > 0:
        feedlime = {
            "q": q_feedlime * (1.0 - moisture / 100.0),
            "psd": stream_fl["psd"],
            "moisture": moisture,
        }
        z13 = flowsheet.zone_1_3(feedlime, params, calib["Phi_100"], alerts)
    else:
        z13 = None
        if q_feedlime > 0:
            alerts.append("Zone 1.3: no FeedLime produced in zone 1.2 (mode 2C?)")

    # ---------------- Closure balances (dry solids, per processed zone)
    balance_tol = engine["balance_relative_tolerance"]
    balances = {}

    def _balance(name, input_tph, outputs):
        total_out = sum(s["q"] for s in outputs if s)
        gap = abs(input_tph - total_out) / max(input_tph, 1e-9)
        balances[name] = {
            "dry_input_tph": round(input_tph, 4),
            "dry_outputs_tph": round(total_out, 4),
            "relative_gap": gap,
            "closed": bool(gap <= balance_tol),
        }
        if gap > balance_tol:
            alerts.append(f"Balance {name} NOT closed: relative gap {gap:.2e}")

    _balance("zone_1_1", feed["q"], [z11["products"]["KFS"], z11["products"]["0/20"]])
    _balance("zone_1_2", reclaim["q"], list(z12["products"].values()))
    if z13:
        _balance("zone_1_3", feedlime["q"], list(z13["products"].values()))
        # WATER balance zone 1.3: water in = water in products + vapor
        water_in = feedlime["q"] / (1.0 - moisture / 100.0) * moisture / 100.0
        m_out = params["machines"]["DY.03"]["parameters"]["m_out"]["default"]
        water_products = sum(
            s["q"] / (1.0 - m_out / 100.0) * m_out / 100.0
            for s in z13["products"].values()
            if s
        )
        water_gap = abs(water_in - (water_products + z13["vapor_tph"])) / max(water_in, 1e-9)
        balances["water_zone_1_3"] = {
            "water_input_tph": round(water_in, 4),
            "water_in_products_tph": round(water_products, 4),
            "vapor_tph": round(z13["vapor_tph"], 4),
            "relative_gap": water_gap,
            "closed": bool(water_gap <= balance_tol),
        }
        if water_gap > balance_tol:
            alerts.append(f"WATER balance zone 1.3 NOT closed: relative gap {water_gap:.2e}")

    # ---------------- Products: "as sold" tonnages + compliance
    specs = params["output_products"]
    products = {}

    def _product(name, stream):
        if stream is None:
            products[name] = {"tph": 0.0, "state": "absent (mode/scenario)"}
            return
        # wet/dry state comes from the data (audit finding 1.2)
        wet = specs[name]["state"] == "wet"
        tph = _wet_tonnage(stream) if wet else stream["q"]
        products[name] = {
            "tph": round(tph, 3),
            "state": specs[name]["state"],
            "P80_mm": round(stream["psd"].p80(), 4),
            "passing_curve_pct": dict(
                zip(
                    [str(m) for m in params["mesh_series_mm"]],
                    stream["psd"].on_series(params["mesh_series_mm"]),
                )
            ),
            "compliance": _product_compliance(stream, specs[name]),
        }

    _product("KFS", z11["products"]["KFS"])
    _product("AgLime", z12["products"]["AgLime"])
    if z13:
        _product("FeedLime grits", z13["products"]["FeedLime grits"])
        _product("FeedLime fines", z13["products"]["FeedLime fines"])
        _product("UltraFin", z13["products"]["UltraFin"])

    machines = {**z11["machines"], **z12["machines"], **(z13["machines"] if z13 else {})}

    results = {
        "scenario": {
            "zone_1_1_mode": sc["zone_1_1_mode"],
            "zone_1_2_mode": (
                "2B"
                if weather == "rain" and sc.get("rain_forces_mode_2B", True)
                else sc["zone_1_2_mode"]
            ),
            "weather": weather,
            "time_basis": sc["time_basis"],
            "flow_rates_tph": sc["flow_rates_tph"],
        },
        "products": products,
        "intermediate_flows": {
            "0/20_dry_tph": round(z11["products"]["0/20"]["q"], 3),
            "zone_1_1_recirculation_tph": round(z11["recirculation_tph"], 3),
            "zone_1_2_recirculation_tph": round(z12["recirculation_tph"], 3),
            "zone_1_3_recirculation_tph": round(z13["recirculation_tph"], 3) if z13 else None,
        },
        "machines": machines,
        "balances": balances,
        "alerts": alerts,
    }
    results["period_balance"] = _period_balance(params, results, alerts)
    return results


def _period_balance(params: dict, results: dict, alerts: list) -> dict | None:
    """Tonnages over the chosen time basis when hours are provided."""
    sc = params["default_scenario"]
    zones = sc["zones"]
    if any(z["available_hours"] is None for z in zones.values()):
        alerts.append(
            "Period balance not computed: available hours not provided (parameter)"
        )
        return None
    effective_hours = {
        name: z["available_hours"] * z["availability_pct"] / 100.0 for name, z in zones.items()
    }
    product_zone = {
        "KFS": "1.1",
        "AgLime": "1.2",
        "FeedLime grits": "1.3",
        "FeedLime fines": "1.3",
        "UltraFin": "1.3",
    }
    p = results["products"]
    tonnages = {
        name: p.get(name, {}).get("tph", 0.0) * effective_hours[zone]
        for name, zone in product_zone.items()
    }
    # product -> target mapping comes from the data (audit finding §4)
    per_product = {}
    for target_key, target in params["production_targets"].items():
        product = target["product"]
        tonnage = tonnages.get(product, 0.0)
        cap = target.get("market_cap_t_per_year")
        per_product[product] = {
            "target_key": target_key,
            "tonnage_t": round(tonnage, 0),
            "target_t": target["target_t_per_year"],
            "gap_t": round(tonnage - target["target_t_per_year"], 0),
            "nature": target["nature"],
            "surplus_beyond_market_t": round(max(0.0, tonnage - cap), 0) if cap else None,
        }
    return {
        "time_basis": sc["time_basis"],
        "effective_hours": effective_hours,
        "per_product": per_product,
    }


def run_seasonal_balance(params: dict) -> dict:
    """Season-weighted balance: dry photo × dry fraction + rain photo × rain fraction.

    Wires the ``dry_season_fraction`` / ``rain_season_fraction`` parameters
    (specification §7.2); hours are split between the two weathers.
    """
    sc = params["default_scenario"]
    f_dry = sc["dry_season_fraction"]
    f_rain = sc["rain_season_fraction"]
    total = f_dry + f_rain
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"season fractions must sum to 1 (got {total})")

    photos = {}
    for weather, fraction in (("dry", f_dry), ("rain", f_rain)):
        season_params = _deep_merge(params, {"default_scenario": {"weather": weather}})
        season_zones = {
            name: {
                "available_hours": (
                    z["available_hours"] * fraction if z["available_hours"] is not None else None
                ),
                "availability_pct": z["availability_pct"],
            }
            for name, z in sc["zones"].items()
        }
        season_params = _deep_merge(season_params, {"default_scenario": {"zones": season_zones}})
        photos[weather] = run_scenario(season_params)

    combined = None
    for weather in ("dry", "rain"):
        pb = photos[weather]["period_balance"]
        if pb is None:
            return {"photos": photos, "combined": None}
        if combined is None:
            combined = copy.deepcopy(pb["per_product"])
        else:
            for product, row in pb["per_product"].items():
                combined[product]["tonnage_t"] += row["tonnage_t"]
    for product, row in combined.items():
        row["gap_t"] = round(row["tonnage_t"] - row["target_t"], 0)
        cap = None
        for target in params["production_targets"].values():
            if target["product"] == product:
                cap = target.get("market_cap_t_per_year")
        row["surplus_beyond_market_t"] = (
            round(max(0.0, row["tonnage_t"] - cap), 0) if cap else None
        )
    return {"photos": photos, "combined": combined, "season_fractions": {"dry": f_dry, "rain": f_rain}}
