"""Tests of the feed-measurement ingestion and the design check
(the project's ultimate goal: confirm the line design and machine choice)."""

import pytest

from wankoe_model import (
    apply_measurement,
    list_measurements,
    load_parameters,
    run_design_check,
    run_design_check_all_measurements,
)
from wankoe_model.feed import build_curve_from_measurement, load_measurement


# ------------------------------------------------------------ ingestion
def test_measurement_library_has_the_belt_cut():
    measurements = list_measurements()
    assert "2026-08-08-belt-cut" in measurements


def test_unknown_measurement_actionable_error():
    with pytest.raises(ValueError, match="known:"):
        load_measurement("no-such-campaign")


def test_apply_measurement_sets_curve_and_moisture():
    params = apply_measurement(load_parameters(), "2026-08-08-belt-cut")
    assert params["feed_product"]["properties"]["moisture_pct"]["default"] == 7
    curve = params["feed_product"]["cumulative_passing_curve"]
    assert curve["320"] == 100.0
    # measured points respected (average of the two tests at 80 mm = 65 %)
    assert curve["80.0"] == pytest.approx(65.0, abs=0.1)


def test_plain_value_measurement_format_accepted():
    meas = {
        "_meta": {"moisture_pct_wet_basis": 6},
        "cumulative_passing_pct": {"19": 45.0, "80": 65.0, "200": 81.0},
    }
    curve = build_curve_from_measurement(meas, load_parameters())
    assert curve["320"] == 100.0
    assert curve["80.0"] == pytest.approx(65.0, abs=0.1)


# ------------------------------------------------------------ design check
@pytest.fixture(scope="module")
def report():
    return run_design_check(load_parameters())


def test_known_limit_violation_is_caught(report):
    # the measured feed F80 (181 mm) exceeds CR.5009's 150 mm nip limit
    nip = [r for r in report["checks"] if r["machine"] == "CR.5009" and "nip" in r["check"]]
    assert nip and nip[0]["verdict"] == "EXCEEDED"
    assert report["design_holds"] is False


def test_missing_limits_are_listed_not_ignored(report):
    assert any("SR.5007" in item for item in report["limits_to_provide"])
    assert any(r["verdict"] == "NO LIMIT" for r in report["checks"])


def test_provided_limit_flips_the_verdict():
    ok = run_design_check(
        load_parameters(overrides={"machines": {"SR.5007": {"installed_area_m2": 50}}})
    )
    row = [r for r in ok["checks"] if r["machine"] == "SR.5007"][0]
    assert row["verdict"] == "OK" and row["margin_pct"] > 0
    bad = run_design_check(
        load_parameters(overrides={"machines": {"SR.5007": {"installed_area_m2": 0.5}}})
    )
    row = [r for r in bad["checks"] if r["machine"] == "SR.5007"][0]
    assert row["verdict"] == "EXCEEDED"


def test_planning_summary_included(report):
    assert report["planning"]["targets_feasible_within_ceilings"] is True
    assert set(report["planning"]["zones"]) == {"1.1", "1.2", "1.3"}


def test_all_measurements_check_aggregates_worst_case():
    result = run_design_check_all_measurements(load_parameters())
    assert result["measurements"] == list(list_measurements())
    key = "CR.5009 / feed F80 vs nip"
    assert key in result["worst_case"]
    assert result["worst_case"][key]["governing_measurement"] == "2026-08-08-belt-cut"
    assert result["design_holds"] is False
