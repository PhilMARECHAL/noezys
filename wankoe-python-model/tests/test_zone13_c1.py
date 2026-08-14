"""Zone-1.3 C1 STUDY VARIANT (redesign panel round 1, client-validated lead
candidate 2026-08-14): 2-stage smooth rolls RC.1/RC.2 + SC.A triple deck
8/3.75/2 + SC.B sliver screen 1.5. The as-built circuit stays the DEFAULT
until the client adopts the redesign — these tests select the variant
explicitly and also pin that the default is untouched."""

import pytest

from wankoe_model import load_parameters, run_scenario


@pytest.fixture(scope="module")
def c1():
    return run_scenario(
        load_parameters(overrides={"default_scenario": {"zone_1_3_variant": "c1"}})
    )


def test_default_variant_is_as_built():
    params = load_parameters()
    assert params["default_scenario"]["zone_1_3_variant"] == "as-built"
    results = run_scenario(params)
    assert results["products"]["Sliver 1.5/2"]["present"] is False
    assert "ML.26" in results["machines"] and results["machines"]["ML.26"]["active"]
    assert "RC.1" not in results["machines"]


def test_c1_machines_replace_as_built(c1):
    for code in ("RC.1", "RC.2", "SC.A", "SC.B"):
        assert c1["machines"][code]["active"] is True
    for code in ("ML.26", "SN.21"):
        assert code not in c1["machines"]
    # dryer + UltraFin block unchanged (design basis D2)
    assert c1["machines"]["DY.03"]["active"] is True
    assert c1["machines"]["SP.36"]["active"] is True


def test_c1_meets_the_machine_spec(c1):
    """The redesign objective (design basis D3 + machine spec from the
    diagnosis): >=40 % of the zone-1.3 feed leaves as 2-4 grits, and the
    total-fines-to-grits ratio comes down from the as-built 2.83 to <=1.25
    FIRM. Client arbitration 2026-08-14 (option B): the 1.5/2 sliver is
    REGROUND through RC.2 — the ratio drops to 0.79, also meeting the
    <=1.0 D3 objective."""
    p = c1["products"]
    grits = p["FeedLime grits"]["tph"]
    total_fines = p["FeedLime fines"]["tph"] + p["UltraFin"]["tph"]
    dryer_out = c1["machines"]["DY.03"]["dry_solids_tph"] / (
        1.0 - c1["machines"]["DY.03"]["m_out_effective_pct"] / 100.0
    )
    assert grits / dryer_out >= 0.40  # engine 2026-08-14 (regrind): 55.5 %
    assert total_fines / grits <= 1.0  # engine 2026-08-14 (regrind): 0.79


def test_c1_grits_quality(c1):
    # D6 envelope encoded 2026-08-14: <2 mm <= 15 %, >4 mm <= 5 %.
    # Regrind narrows the below-cut margin (13.6 % vs 5.2 % in extract
    # mode) — the client accepted this against the vendor gradation test.
    comp = c1["products"]["FeedLime grits"]["compliance"]
    assert comp["compliant"] is True
    assert comp["below_cut_pct"] <= 15  # engine 2026-08-14 (regrind): 13.6
    assert comp["above_cut_pct"] <= 5  # engine 2026-08-14 (regrind): 2.6


def test_c1_capacities_hold_at_reference_feed(c1):
    """RC.1 single unit; regrind raises the stage-2 load to 31.7 t/h so
    BOTH RC.2 units are in service (2 x 22 = 44 t/h installed) — no
    bottleneck alert at the reference dryer-outlet flow."""
    assert c1["machines"]["RC.1"]["throughput_tph"] <= 29
    assert c1["machines"]["RC.2"]["throughput_tph"] <= 2 * 22
    assert c1["machines"]["RC.2"]["units_in_service"] == 2
    assert not any(a.startswith(("RC.1:", "RC.2:")) for a in c1["alerts"])


def test_c1_balances_close(c1):
    assert c1["balances"]["zone_1_3"]["closed"]
    assert c1["balances"]["water_zone_1_3"]["closed"]


def test_c1_sliver_regrind_is_the_default(c1):
    # Client arbitration 2026-08-14 (option B): SC.B oversize_routing =
    # "regrind" — the sliver returns to RC.2 and the product is absent
    assert c1["products"]["Sliver 1.5/2"]["present"] is False


def test_c1_extract_routing_stays_selectable():
    # the two-position diverter of the design: "extract" keeps the sliver
    # as a separate product (reversible in operation)
    r = run_scenario(
        load_parameters(
            overrides={
                "default_scenario": {"zone_1_3_variant": "c1"},
                "machines": {"SC.B": {"sliver_routing": "extract"}},
            }
        )
    )
    sliver = r["products"]["Sliver 1.5/2"]
    assert sliver["present"] is True
    assert 0 < sliver["tph"] < r["products"]["FeedLime grits"]["tph"]
    assert r["machines"]["RC.2"]["units_in_service"] == 1
