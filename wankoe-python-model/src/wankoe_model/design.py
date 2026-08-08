"""Design confirmation: computed machine duties vs installed equipment.

THE ultimate goal of the project (client, 2026-08-08): a NEW line is being
built — the model's job is to CONFIRM the line design and the machine
selection, fed only by belt-cut PSD measurements at the primary crusher
outlet.

``run_design_check(params)`` runs the line photo and compares, machine by
machine, every computed duty against the installed limit declared in the
data (nameplate capacity, screen area, motor power, dryer burner/drum,
classifier airflow). Verdicts:

- ``OK``        duty within the limit (margin reported)
- ``EXCEEDED``  duty beyond the limit — the design does not hold there
- ``NO LIMIT``  no installed value provided yet (data key null): the row
                lists what the vendor/design data must supply

``run_design_check_all_measurements(params)`` repeats the check for every
stored feed measurement and keeps the WORST margin per check — the
governing case for design confirmation across rock variability.
"""

from __future__ import annotations

from .feed import apply_measurement, list_measurements
from .planning import run_required_hours
from .scenario import run_scenario


def _row(code, check, duty, unit, limit):
    if duty is None:
        return None
    if limit is None:
        verdict, margin = "NO LIMIT", None
    else:
        margin = round(100.0 * (limit - duty) / limit, 1)
        verdict = "OK" if duty <= limit else "EXCEEDED"
    return {
        "machine": code,
        "check": check,
        "computed": round(duty, 2),
        "installed_limit": limit,
        "unit": unit,
        "margin_pct": margin,
        "verdict": verdict,
    }


def _max_area(machine_result):
    areas = machine_result.get("areas_m2")
    if not areas:
        return None
    return max(a["required_area_m2"] for a in areas.values())


def run_design_check(params: dict) -> dict:
    """One design check: photo + planning + duty-vs-installed table."""
    photo = run_scenario(params)
    machines_data = params["machines"]
    m = photo["machines"]
    rows = []

    def add(code, check, duty, unit, limit_key, holder=None):
        holder = machines_data[code] if holder is None else holder
        row = _row(code, check, duty, unit, holder.get(limit_key))
        if row:
            rows.append(row)

    # CR.5009 — toothed roll crusher
    if m["CR.5009"].get("active"):
        add("CR.5009", "feed F80 vs nip", m["CR.5009"]["F80_mm"], "mm", "max_feed_size_mm")
        add("CR.5009", "installed power", m["CR.5009"]["P_installed_kW"], "kW", "installed_power_kW")
    # CR.5011 — impact crusher (loop)
    if m["CR.5011"].get("active"):
        add("CR.5011", "circulating load", m["CR.5011"].get("throughput_tph"), "t/h", "max_capacity_tph")
        add("CR.5011", "installed power", m["CR.5011"].get("P_installed_kW"), "kW", "installed_power_kW")
    # CR.5107 — impact crusher (AgLime loop)
    if m["CR.5107"].get("active"):
        add("CR.5107", "installed power", m["CR.5107"].get("P_installed_kW"), "kW", "installed_power_kW")
    # screens — required vs installed area
    for code in ("SR.5007", "SR.5105", "SR.5115", "SN.21"):
        if m.get(code, {}).get("active"):
            add(code, "screen area", _max_area(m[code]), "m2", "installed_area_m2")
    # DY.03 — dryer
    if m["DY.03"].get("active"):
        wet_feed = photo["scenario"]["flow_rates_tph"]["zone_1_3_feedlime"]
        add("DY.03", "wet feed vs capacity", wet_feed, "t/h", "max_capacity_tph")
        add("DY.03", "burner power", m["DY.03"]["burner_power_kW"], "kW", "installed_burner_kW")
        add("DY.03", "drum volume", m["DY.03"]["drum_volume_m3"], "m3", "installed_drum_volume_m3")
    # ML.26 — roller mill
    if m["ML.26"].get("active"):
        add("ML.26", "circulating load", m["ML.26"].get("throughput_tph"), "t/h", "max_capacity_tph")
        add("ML.26", "installed power", m["ML.26"].get("P_installed_kW"), "kW", "installed_power_kW")
    # SP.36 — air classifier
    if m["SP.36"].get("active") and m["SP.36"].get("Q_air_m3h") is not None:
        add("SP.36", "airflow", m["SP.36"]["Q_air_m3h"], "m3/h", "max_airflow_m3h")

    exceeded = [r for r in rows if r["verdict"] == "EXCEEDED"]
    missing = sorted({f"{r['machine']}.{r['check']}" for r in rows if r["verdict"] == "NO LIMIT"})

    # target attainability completes the design view (hours follow targets)
    try:
        planning = run_required_hours(params)
        targets_feasible = all(
            z["feasible"] is not False for z in planning["zones"].values()
        )
        planning_summary = {
            "targets_feasible_within_ceilings": targets_feasible,
            "zones": {
                name: {
                    "required_hours_clock": z["required_hours_clock"],
                    "ceiling_hours_clock": z["ceiling_hours_clock"],
                    "utilization_pct": z["utilization_pct"],
                }
                for name, z in planning["zones"].items()
            },
        }
    except ValueError as exc:
        planning_summary = {"targets_feasible_within_ceilings": None, "error": str(exc)}

    return {
        "purpose": "design confirmation: computed duties vs installed equipment",
        "checks": rows,
        "design_holds": len(exceeded) == 0,
        "exceeded": exceeded,
        "limits_to_provide": missing,
        "planning": planning_summary,
        "alerts": photo["alerts"],
    }


def run_design_check_all_measurements(params: dict) -> dict:
    """Design check across every stored feed measurement; worst case governs."""
    measurements = list_measurements()
    if not measurements:
        raise ValueError(
            "no feed measurement stored in data/feed_measurements/ — "
            "add belt-cut analyses to run the multi-measurement design check"
        )
    per_measurement = {}
    worst: dict = {}
    for name in measurements:
        report = run_design_check(apply_measurement(params, name))
        per_measurement[name] = report
        for row in report["checks"]:
            key = f"{row['machine']} / {row['check']}"
            current = worst.get(key)
            if (
                current is None
                or (row["margin_pct"] is not None
                    and (current["margin_pct"] is None or row["margin_pct"] < current["margin_pct"]))
            ):
                worst[key] = {**row, "governing_measurement": name}
    return {
        "measurements": list(measurements),
        "per_measurement": per_measurement,
        "worst_case": worst,
        "design_holds": all(r["design_holds"] for r in per_measurement.values()),
    }
