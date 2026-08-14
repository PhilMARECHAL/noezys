"""Static flowsheet of zones 1.1 / 1.2 / 1.3 (specification §4).

FIXED structure, faithful to the block diagrams. Closed circuits are solved
by fixed-point iteration on the recirculating stream (criteria in the
"engine" section of the parameters). Every machine is referenced by its
exact code (§2 — machine codification).

A "stream" is a dict: {"q": t/h of DRY solids, "psd": PSD, "moisture": %
wet basis}. Water travels with the moisture value and is only removed at
the dryer (§1.4); balances close on dry solids and on water.
"""

from __future__ import annotations

from .grid import PSD
from . import models


def _stream(q: float, psd: PSD, moisture: float) -> dict:
    return {"q": q, "psd": psd, "moisture": moisture}


def _blend(streams: list[dict]) -> dict:
    active = [s for s in streams if s["q"] > 1e-12]
    if not active:
        raise ValueError("blending empty streams")
    q, psd = PSD.blend([(s["q"], s["psd"]) for s in active])
    water = sum(s["q"] / (1.0 - s["moisture"] / 100.0) * s["moisture"] / 100.0 for s in active)
    wet = sum(s["q"] / (1.0 - s["moisture"] / 100.0) for s in active)
    return _stream(q, psd, 100.0 * water / wet if wet > 0 else 0.0)


def _karra_screen(stream: dict, aperture_mm: float, imperfection: float, calib: dict):
    """One screen deck: returns (oversize_stream, undersize_stream) — same moisture."""
    part = models.m3_karra_partition(stream["q"], stream["psd"], aperture_mm, imperfection, calib)
    oversize = (
        _stream(part["oversize_tph"], part["oversize_psd"], stream["moisture"])
        if part["oversize_psd"] is not None
        else None
    )
    undersize = (
        _stream(part["undersize_tph"], part["undersize_psd"], stream["moisture"])
        if part["undersize_psd"] is not None
        else None
    )
    return oversize, undersize


def _impactor(stream: dict, v_ms: float, x80_mm: float, calib: dict):
    """Impact crusher (M5 -> n, M1 -> product, M2 -> power)."""
    m5 = models.m5_impact_uniformity(v_ms, calib)
    out_psd = models.m1_crusher_product(stream["psd"], x80_mm, m5["n"], calib)
    bond = models.m2_bond_power(stream["q"], stream["psd"].p80(), out_psd.p80(), calib)
    return _stream(stream["q"], out_psd, stream["moisture"]), {**m5, **bond, "throughput_tph": stream["q"]}


def _check_installed_area(code: str, areas: dict, installed_m2, alerts: list) -> None:
    """Spec sheets: 'alert when required area > installed area' (when provided)."""
    if installed_m2 is None:
        return
    required = max(a["required_area_m2"] for a in areas.values())
    if required > installed_m2:
        alerts.append(
            f"{code}: required screen area {required:.1f} m2 > installed {installed_m2} m2"
        )


def _psd_from_table(table: dict, meshes: list) -> PSD:
    """PSD from a vendor curve table {curve_pct: {mesh: %}, interpolation:
    'log'|'linear'} — the declared interpolation mode is honored (golden
    rule 2)."""
    import math

    mode = table.get("interpolation", "log")
    points = sorted((float(k), float(v) / 100.0) for k, v in table["curve_pct"].items())

    def interp(x):
        if x <= points[0][0]:
            return points[0][1] * x / points[0][0]
        if x >= points[-1][0]:
            return 1.0
        for (x0, p0), (x1, p1) in zip(points, points[1:]):
            if x <= x1:
                if mode == "linear":
                    t = (x - x0) / (x1 - x0)
                else:
                    t = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
                return p0 + t * (p1 - p0)
        return 1.0

    passing = [interp(x) for x in meshes]
    passing[-1] = 1.0
    return PSD(meshes, passing)


def _fixed_point_loop(iterate, engine: dict, alerts: list, loop_name: str):
    """Iterates ``iterate(recycle) -> (recycle', outputs)`` until convergence.

    Convergence on both the flow rate AND the curve of the recycled stream.
    Alarm when the circulating load exceeds ``max_circulating_ratio``.
    """
    max_iter = int(engine["loop_max_iterations"])
    tol = float(engine["loop_relative_tolerance"])
    recycle = None
    for _ in range(max_iter):
        new, outputs = iterate(recycle)
        if recycle is None and new is None:
            return None, outputs
        if recycle is not None and new is not None:
            dq = abs(new["q"] - recycle["q"]) / max(recycle["q"], 1e-9)
            dpsd = max(abs(a - b) for a, b in zip(new["psd"].passing, recycle["psd"].passing))
            if dq < tol and dpsd < tol:
                return new, outputs
        recycle = new
    alerts.append(f"{loop_name}: loop did not converge after {max_iter} iterations")
    return recycle, outputs


# ===================================================================== 1.1
def zone_1_1(feed: dict, params: dict, mode: str, alerts: list, weather: str | None = None) -> dict:
    """Zone 1.1 — crushing / primary screening (pivot feed -> KFS + 0/20).

    Pivot (§5): the feed curve is MEASURED at the primary station outlet
    (grizzly + CR.5003 already blended into the curve). Modelled chain:
    pivot -> CR.5009 -> SR.5007 (35/20) with the CR.5011 loop on the +35
    oversize. Mode 1A: 20-35 cut -> KFS; mode 1B: 20-35 cut -> CR.5011
    (no KFS).
    """
    if mode not in ("1A", "1B"):
        raise ValueError(f"zone 1.1: unknown mode {mode!r} (expected '1A' or '1B')")
    mp = params["machines"]
    calib = params["calibration"]
    engine = params["engine"]

    # CR.5009 — toothed roll crusher: x80 = explicit parameter, or gap when null
    # (x80 = g validated by the client on 2026-08-08; audit finding 1.1)
    p9 = mp["CR.5009"]["parameters"]
    gap9 = p9["g"]["default"]
    x80_9 = p9["x80"]["default"] if p9["x80"]["default"] is not None else gap9
    max_feed = mp["CR.5009"].get("max_feed_size_mm")
    feed_f80 = feed["psd"].p80()
    if max_feed is not None and feed_f80 > max_feed:
        alerts.append(
            f"CR.5009: feed F80 {feed_f80:.0f} mm > max nip size {max_feed} mm — saturation"
        )
    psd9 = models.m1_crusher_product(feed["psd"], x80_9, p9["n"]["default"], calib)
    bond9 = models.m2_bond_power(feed["q"], feed_f80, psd9.p80(), calib)
    cr5009_out = _stream(feed["q"], psd9, feed["moisture"])

    p7 = mp["SR.5007"]["parameters"]
    p11 = mp["CR.5011"]["parameters"]
    a1, a2, imp = p7["a1"]["default"], p7["a2"]["default"], p7["I"]["default"]
    cr5011_info = {}

    def iterate(recycle):
        screen_feed = _blend([cr5009_out, recycle]) if recycle else cr5009_out
        over35, under35 = _karra_screen(screen_feed, a1, imp, calib)
        mid, under20 = _karra_screen(under35, a2, imp, calib) if under35 else (None, None)
        # streams sent to the impactor depend on the mode
        to_impactor = [s for s in [over35] + ([mid] if mode == "1B" else []) if s]
        if to_impactor:
            feed11 = _blend(to_impactor)
            out11, info11 = _impactor(feed11, p11["v"]["default"], p11["x80"]["default"], calib)
            cr5011_info.update(info11)
            new_recycle = out11
        else:
            new_recycle = None
        outputs = {
            "kfs": mid if mode == "1A" else None,
            "undersize_0_20": under20,
            "screen_feed": screen_feed,
            "u_top_deck": under35["q"] if under35 else 0.0,
            "u_bottom_deck": under20["q"] if under20 else 0.0,
        }
        return new_recycle, outputs

    recycle, outputs = _fixed_point_loop(iterate, engine, alerts, "Zone 1.1 / CR.5011")

    cap11 = mp["CR.5011"].get("max_capacity_tph")
    # capacity-basis fix (adversarial audit 2026-08-14): the 90 t/h is a
    # VENDOR rating — vendor tonnages are as-fed (wet); the loop stream is
    # dry solids, so compare in the capacity's own declared basis
    if recycle and cap11:
        load = recycle["q"]
        if mp["CR.5011"].get("capacity_basis", "dry") == "wet":
            load = recycle["q"] / (1.0 - recycle["moisture"] / 100.0)
        if load > cap11:
            alerts.append(
                f"CR.5011: bottleneck — load {load:.1f} t/h "
                f"({mp['CR.5011'].get('capacity_basis', 'dry')} basis) > capacity {cap11} t/h"
            )
    if cr5011_info and cap11:
        # the spec's reference power (~37 kW) evaluates the impactor AT its
        # nameplate capacity, not at the loop equilibrium — report both
        cr5011_info["P_net_at_capacity_kW"] = cr5011_info["W_kWh_t"] * cap11
        cr5011_info["P_installed_at_capacity_kW"] = (
            cr5011_info["P_net_at_capacity_kW"] / calib["eta_m"]
        )
    if recycle and recycle["q"] > engine["max_circulating_ratio"] * feed["q"]:
        alerts.append("Zone 1.1: excessive circulating load (max_circulating_ratio exceeded)")

    # spec: wet screening loses capacity — derate outdoor screens under rain
    # weather comes as an argument like zone_1_2 (audit 2026-08-14: the
    # old default_scenario read could silently diverge from the caller's)
    if weather is None:
        weather = params["default_scenario"]["weather"]
    wet_factor = calib["wet_capacity_factor"] if weather == "rain" else 1.0
    areas = {
        "top_deck": models.m4_screen_area(outputs["u_top_deck"], a1, calib, wet_factor),
        "bottom_deck": models.m4_screen_area(outputs["u_bottom_deck"], a2, calib, wet_factor),
    }
    _check_installed_area("SR.5007", areas, mp["SR.5007"].get("installed_area_m2"), alerts)
    return {
        "products": {"KFS": outputs["kfs"], "0/20": outputs["undersize_0_20"]},
        "machines": {
            "CR.5009": {**bond9, "throughput_tph": feed["q"], "x80_mm": x80_9},
            "CR.5011": cr5011_info,
            "SR.5007": {
                "feed_tph": outputs["screen_feed"]["q"],
                "areas_m2": areas,
            },
        },
        "recirculation_tph": recycle["q"] if recycle else 0.0,
    }


# ===================================================================== 1.2
def zone_1_2(reclaim: dict, params: dict, mode: str, weather: str, alerts: list) -> dict:
    """Zone 1.2 — reclaim / AgLime (PFD REV18 topology, client ruling 2026-08-12).

    KFS-fines 0/20 stockpile -> BF.5101/5102 -> DV.5104:
    mode 2A -> SR.5105 (single deck, 6 mm): oversize 6/20 = FeedLime,
    undersize 0/6 -> AgLime loop; mode 2B -> whole reclaim = FeedLime
    (bypass, exact mass identity); mode 2C -> whole reclaim -> loop.

    AgLime loop (two-stage closing, PFD REV18): the loop feed passes the
    OPEN first screen SR.5111 (1.7 mm) — its undersize is AgLime; its
    oversize goes to CR.5113 whose product passes the second screen
    SR.5115 (1.7 mm): undersize joins AgLime, oversize recycles to
    CR.5113 (the closed loop involves the second screen only).

    Under rain the spec forces mode 2B (scenario parameter
    ``rain_forces_mode_2B``, default true). When that forcing is disabled,
    the AgLime loop is computed with the degraded imperfection ``I_rain``
    and flagged as directional (audit finding on I_rain reachability).
    """
    if mode not in ("2A", "2B", "2C"):
        raise ValueError(f"zone 1.2: unknown mode {mode!r} (expected '2A', '2B' or '2C')")
    mp = params["machines"]
    calib = params["calibration"]
    engine = params["engine"]
    force_2b = params["default_scenario"].get("rain_forces_mode_2B", True)

    if weather == "rain" and mode != "2B" and force_2b:
        alerts.append(
            f"Zone 1.2: rain -> 1.7 mm cut impossible, mode {mode} replaced by 2B"
        )
        mode = "2B"
    elif weather == "rain" and mode != "2B":
        alerts.append(
            "Zone 1.2: rain with 2B forcing disabled — AgLime computed with degraded "
            "imperfection I_rain, DIRECTIONAL result"
        )

    wet_factor = calib["wet_capacity_factor"] if weather == "rain" else 1.0
    result = {
        "machines": {
            "SR.5105": {},
            "SR.5111": {},
            "SR.5115": {},
            "CR.5113": {},
        }
    }

    if mode == "2B":
        # DV.5104 bypass: the whole reclaim goes to the Feed stockpile
        result["products"] = {"AgLime": None, "FeedLime": reclaim}
        result["recirculation_tph"] = 0.0
        return result

    if mode == "2A":
        p05 = mp["SR.5105"]["parameters"]
        feedlime, under6 = _karra_screen(reclaim, p05["a"]["default"], calib["I_dry"], calib)
        sr5105_areas = {
            "deck": models.m4_screen_area(
                under6["q"] if under6 else 0.0, p05["a"]["default"], calib, wet_factor
            )
        }
        _check_installed_area("SR.5105", sr5105_areas, mp["SR.5105"].get("installed_area_m2"), alerts)
        result["machines"]["SR.5105"] = {"feed_tph": reclaim["q"], "areas_m2": sr5105_areas}
        loop_feed = under6
    else:  # 2C: DV.5106 sends the whole reclaim to the loop, no FeedLime
        feedlime = None
        loop_feed = reclaim

    if loop_feed is None or loop_feed["q"] <= 1e-12:
        result["products"] = {"AgLime": None, "FeedLime": feedlime}
        result["recirculation_tph"] = 0.0
        return result

    loop_rating = mp["SR.5111"].get("loop_rating_tph")
    loop_feed_wet = loop_feed["q"] / (1.0 - loop_feed["moisture"] / 100.0)
    if loop_rating is not None and loop_feed_wet > loop_rating:
        alerts.append(
            f"AgLime loop: feed {loop_feed_wet:.1f} t/h wet > conveyor rating "
            f"{loop_rating} t/h (BC.5110/BC.5116, PFD REV18)"
        )

    p11 = mp["SR.5111"]["parameters"]
    p15 = mp["SR.5115"]["parameters"]
    p13 = mp["CR.5113"]["parameters"]
    imp_1_7_first = p11["I"]["default"] if weather == "dry" else calib["I_rain"]
    imp_1_7_second = p15["I"]["default"] if weather == "dry" else calib["I_rain"]

    # ---- first screen SR.5111: OPEN circuit, single pass of the loop feed
    over1, aglime1 = _karra_screen(loop_feed, p11["a"]["default"], imp_1_7_first, calib)
    sr5111_areas = {
        "deck": models.m4_screen_area(
            aglime1["q"] if aglime1 else 0.0, p11["a"]["default"], calib, wet_factor
        )
    }
    _check_installed_area("SR.5111", sr5111_areas, mp["SR.5111"].get("installed_area_m2"), alerts)
    result["machines"]["SR.5111"] = {
        "feed_tph": loop_feed["q"],
        "areas_m2": sr5111_areas,
        "imperfection_used": imp_1_7_first,
    }

    if over1 is None or over1["q"] <= 1e-12:
        # nothing coarse: AgLime = the whole loop feed, crusher idle
        result["products"] = {"AgLime": aglime1, "FeedLime": feedlime}
        result["recirculation_tph"] = 0.0
        return result

    # ---- CR.5113 + second screen SR.5115: closed loop on the recycle
    cr5113_info = {}

    def iterate(recycle):
        crusher_feed = _blend([over1, recycle]) if recycle else over1
        out, info = _impactor(crusher_feed, p13["v"]["default"], p13["x80"]["default"], calib)
        cr5113_info.update(info)
        oversize2, aglime2 = _karra_screen(out, p15["a"]["default"], imp_1_7_second, calib)
        return oversize2, {"aglime2": aglime2, "sr5115_feed": out}

    recycle, outputs = _fixed_point_loop(iterate, engine, alerts, "Zone 1.2 / CR.5113")
    if recycle and recycle["q"] > engine["max_circulating_ratio"] * over1["q"]:
        alerts.append(
            "CR.5113: circulating load explodes (CSS too large?) — specification alarm"
        )

    sr5115_areas = {
        "deck": models.m4_screen_area(
            outputs["aglime2"]["q"] if outputs["aglime2"] else 0.0,
            p15["a"]["default"],
            calib,
            wet_factor,
        )
    }
    _check_installed_area("SR.5115", sr5115_areas, mp["SR.5115"].get("installed_area_m2"), alerts)
    result["machines"]["SR.5115"] = {
        "feed_tph": outputs["sr5115_feed"]["q"],
        "areas_m2": sr5115_areas,
        "imperfection_used": imp_1_7_second,
    }
    result["machines"]["CR.5113"] = cr5113_info

    aglime_parts = [s for s in (aglime1, outputs["aglime2"]) if s]
    aglime = _blend(aglime_parts) if aglime_parts else None
    result["products"] = {"AgLime": aglime, "FeedLime": feedlime}
    result["recirculation_tph"] = recycle["q"] if recycle else 0.0
    return result


# ===================================================================== 1.3
def _dy03_dryer(feedlime: dict, mp: dict, calib: dict, alerts: list):
    """DY.03 — dryer: M6 balance on the WET flow rate. Shared by every
    zone-1.3 variant (D2: the dryer is acquired, identical in all designs)."""
    m_out = mp["DY.03"]["parameters"]["m_out"]["default"]
    wet_feed = feedlime["q"] / (1.0 - feedlime["moisture"] / 100.0)
    cap_dryer = mp["DY.03"].get("max_capacity_tph")
    if cap_dryer is not None and wet_feed > cap_dryer:
        alerts.append(
            f"DY.03: bottleneck — wet feed {wet_feed:.1f} t/h > dryer capacity {cap_dryer} t/h"
        )
    m6 = models.m6_drying(wet_feed, feedlime["moisture"], m_out, calib)
    if m6["no_drying"]:
        alerts.append(
            f"DY.03: feed already drier ({feedlime['moisture']}%) than the target "
            f"m_out ({m_out}%) — no drying, outlet keeps the feed moisture"
        )
    dried = _stream(m6["dry_solids_tph"], feedlime["psd"], m6["m_out_effective_pct"])
    return m6, dried


def _sp36_ultrafin(fines, mp: dict, calib: dict, phi_100_pct, alerts: list):
    """SP.36 + CL.38 — UltraFin by air classification on the 0-1.5 fines.
    Shared by every zone-1.3 variant. Returns (m8, ultrafin, remaining_fines,
    d50_cyclone_um)."""
    sp36_enabled = mp["SP.36"].get("enabled", True)
    if not sp36_enabled:
        alerts.append("SP.36/CL.38 block disabled by parameter — no UltraFin extraction, fines kept whole")
    p36 = mp["SP.36"]["parameters"]
    # the SP.36 / CL.38 machine sheets take precedence for their own settings
    calib_cl = {
        **calib,
        "eta_cl": p36["eta_cl"]["default"],
        "v_in_cyclone": mp["CL.38"]["parameters"]["v_in"]["default"],
    }
    if fines and sp36_enabled:
        m8 = models.m8_air_classification(
            fines["q"], fines["psd"], p36["coupe"]["default"], phi_100_pct, calib_cl
        )
        if not m8["certified"]:
            alerts.append(
                "SP.36: Phi(<cut) not measured — UltraFin computed from the modelled "
                "curve, flagged NOT CERTIFIED (to be measured by sieve/laser)"
            )
        if m8["warning"]:
            alerts.append(f"SP.36: {m8['warning']}")
        ultrafin = _stream(m8["fine_product_tph"], m8["fine_product_psd"], fines["moisture"])
        remaining_fines = _stream(m8["remainder_tph"], m8["remainder_psd"], fines["moisture"])
    else:
        m8 = None
        ultrafin = None
        # block disabled (or no fines): the 0-1.5 stream stays whole
        remaining_fines = fines
    return m8, ultrafin, remaining_fines, models.m8_cyclone_d50(calib_cl)


def zone_1_3(feedlime: dict, params: dict, phi_100_pct, alerts: list) -> dict:
    """Zone 1.3 AS-BUILT — drying / grits / UltraFin.

    FeedLime -> DY.03 (dryer, -> m_out) -> SN.21 (4/2/1.5): 2-4 = grits;
    +4 oversize and 1.5-2 sliver -> ML.26 -> back to SN.21 (closed circuit);
    0-1.5 undersize = fines -> SP.36 (+ CL.38) -> UltraFin; remainder =
    FeedLime fines.
    """
    mp = params["machines"]
    calib = params["calibration"]
    engine = params["engine"]

    m6, dried = _dy03_dryer(feedlime, mp, calib, alerts)

    p21 = mp["SN.21"]["parameters"]
    a1, a2, a3 = (p21[k]["default"] for k in ("a1", "a2", "a3"))
    p26 = mp["ML.26"]["parameters"]
    gap26 = p26["g"]["default"]
    vendor_table = mp["ML.26"].get("product_curve_table")
    vendor_psd = _psd_from_table(vendor_table, dried["psd"].meshes) if vendor_table else None
    if vendor_psd is not None:
        alerts.append("ML.26: vendor product curve table in use (replaces hypotheses H-M7-1/2)")
    # the ML.26 machine sheet is the single source for its own coefficients
    # (removed from the calibration section — audit finding on shadowing)
    calib_ml26 = {**calib, "comp_lam": p26["comp_lam"]["default"], "S_att": p26["S_att"]["default"]}
    cap_ml26 = mp["ML.26"].get("max_capacity_tph")
    ml26_info = {}

    def iterate(recycle):
        screen_feed = _blend([dried, recycle]) if recycle else dried
        over4, under4 = _karra_screen(screen_feed, a1, calib["I_dry"], calib)
        grits, under2 = _karra_screen(under4, a2, calib["I_dry"], calib) if under4 else (None, None)
        sliver, fines = _karra_screen(under2, a3, calib["I_dry"], calib) if under2 else (None, None)
        to_mill = [s for s in [over4, sliver] if s]
        if to_mill:
            mill_feed = _blend(to_mill)
            mill_psd = (
                vendor_psd
                if vendor_psd is not None
                else models.m7_bed_mill_pass(mill_feed["psd"], gap26, calib_ml26)
            )
            bond26 = models.m2_bond_power(mill_feed["q"], mill_feed["psd"].p80(), mill_psd.p80(), calib)
            ml26_info.update({**bond26, "throughput_tph": mill_feed["q"]})
            new = _stream(mill_feed["q"], mill_psd, mill_feed["moisture"])
        else:
            new = None
        return new, {
            "grits": grits,
            "fines": fines,
            "sn21_feed": screen_feed,
            "u1": under4["q"] if under4 else 0.0,
            "u2": under2["q"] if under2 else 0.0,
            "u3": fines["q"] if fines else 0.0,
        }

    recycle, outputs = _fixed_point_loop(iterate, engine, alerts, "Zone 1.3 / ML.26")
    if cap_ml26 is not None and ml26_info.get("throughput_tph", 0.0) > cap_ml26:
        alerts.append(
            f"ML.26: bottleneck — load {ml26_info['throughput_tph']:.1f} t/h > "
            f"roller capacity {cap_ml26} t/h"
        )

    # SP.36 + CL.38 — UltraFin by air classification
    fines = outputs["fines"]
    m8, ultrafin, remaining_fines, d50_cyclone = _sp36_ultrafin(
        fines, mp, calib, phi_100_pct, alerts
    )

    sn21_areas = {
        "deck_1": models.m4_screen_area(outputs["u1"], a1, calib),
        "deck_2": models.m4_screen_area(outputs["u2"], a2, calib),
        "deck_3": models.m4_screen_area(outputs["u3"], a3, calib),
    }
    _check_installed_area("SN.21", sn21_areas, mp["SN.21"].get("installed_area_m2"), alerts)

    return {
        "products": {
            "FeedLime grits": outputs["grits"],
            "FeedLime fines": remaining_fines,
            "UltraFin": ultrafin,
        },
        "machines": {
            "DY.03": m6,
            "SN.21": {
                "feed_tph": outputs["sn21_feed"]["q"],
                "areas_m2": sn21_areas,
            },
            "ML.26": ml26_info,
            "SP.36": {
                "Q_air_m3h": m8["Q_air_m3h"] if m8 else None,
                "Phi_cut": m8["Phi_cut"] if m8 else None,
                "certified": m8["certified"] if m8 else None,
            },
            "CL.38": {"d50_um": d50_cyclone},
        },
        "recirculation_tph": recycle["q"] if recycle else 0.0,
        "vapor_tph": m6["evaporated_water_tph"],
    }


# ================================================================ 1.3 / C1
def zone_1_3_c1(feedlime: dict, params: dict, phi_100_pct, alerts: list) -> dict:
    """Zone 1.3 — C1 STUDY VARIANT (zone-1.3 redesign, panel round 1,
    client-validated lead candidate 2026-08-14; as-built stays the default).

    FeedLime -> DY.03 (unchanged, D2) -> two double-deck screens (client
    arbitration 2026-08-14, "2+2" arrangement): SC.A 8/3.75 carries the
    RECYCLE cuts (+8 -> RC.1 smooth rolls stage 1; 3.75-8 -> RC.2 smooth
    rolls stage 2, 2 parallel units; both roll products return to SC.A —
    closed circuit); the SC.A undersize 0/3.75 feeds SC.B 2/1.5 carrying
    the PRODUCT cuts (2-3.75 = grits leave IMMEDIATELY, no regrind of
    in-spec material; 0-1.5 = fines -> SP.36 (+ CL.38) -> UltraFin;
    remainder = FeedLime fines). The 1.5-2 sliver (SC.B deck-2 oversize)
    follows SC.B's sliver_routing (client arbitration 2026-08-14,
    two-position diverter in the design): "regrind" (default) sends it to
    RC.2 with the 3.75-8 midsize; "extract" keeps it as the separate
    Sliver 1.5/2 product.
    """
    mp = params["machines"]
    calib = params["calibration"]
    engine = params["engine"]

    m6, dried = _dy03_dryer(feedlime, mp, calib, alerts)

    pa = mp["SC.A"]["parameters"]
    a1, a2 = (pa[k]["default"] for k in ("a1", "a2"))
    pb = mp["SC.B"]["parameters"]
    b1, b2 = (pb[k]["default"] for k in ("a1", "a2"))
    sliver_regrind = mp["SC.B"].get("sliver_routing", "regrind") == "regrind"

    def _roll_calib(code):
        p = mp[code]["parameters"]
        return p["g"]["default"], {
            **calib,
            "comp_lam": p["comp_lam"]["default"],
            "S_att": p["S_att"]["default"],
            "m7_n_comp": p["n_comp"]["default"],
        }

    g1, calib_rc1 = _roll_calib("RC.1")
    g2, calib_rc2 = _roll_calib("RC.2")
    rc1_info, rc2_info = {}, {}

    def _roll_pass(stream, gap, calib_rc, info):
        out_psd = models.m7_bed_mill_pass(stream["psd"], gap, calib_rc)
        bond = models.m2_bond_power(stream["q"], stream["psd"].p80(), out_psd.p80(), calib)
        info.update({**bond, "throughput_tph": stream["q"]})
        return _stream(stream["q"], out_psd, stream["moisture"])

    def iterate(recycle):
        screen_feed = _blend([dried, recycle]) if recycle else dried
        over8, under8 = _karra_screen(screen_feed, a1, calib["I_dry"], calib)
        mid, under375 = _karra_screen(under8, a2, calib["I_dry"], calib) if under8 else (None, None)
        # SC.A undersize 0/3.75 travels on the linking conveyor to SC.B
        grits, under2 = _karra_screen(under375, b1, calib["I_dry"], calib) if under375 else (None, None)
        sliver, fines = _karra_screen(under2, b2, calib["I_dry"], calib) if under2 else (None, None)
        if sliver_regrind and sliver:
            rc2_feed = _blend([s for s in (mid, sliver) if s])
            sliver = None
        else:
            rc2_feed = mid
        crushed = [s for s in (
            _roll_pass(over8, g1, calib_rc1, rc1_info) if over8 else None,
            _roll_pass(rc2_feed, g2, calib_rc2, rc2_info) if rc2_feed else None,
        ) if s]
        new = _blend(crushed) if crushed else None
        return new, {
            "grits": grits,
            "sliver": sliver,
            "fines": fines,
            "sca_feed": screen_feed,
            "scb_feed": under375,
            "ua1": under8["q"] if under8 else 0.0,
            "ua2": under375["q"] if under375 else 0.0,
            "ub1": under2["q"] if under2 else 0.0,
            "ub2": fines["q"] if fines else 0.0,
        }

    recycle, outputs = _fixed_point_loop(iterate, engine, alerts, "Zone 1.3 C1 / RC.1+RC.2")

    # capacity checks: RC.1 single unit; RC.2 capacity is PER UNIT with
    # n_units in parallel (phase 1 runs 1 of 2 — turndown, per D1)
    cap_rc1 = mp["RC.1"].get("max_capacity_tph")
    if cap_rc1 is not None and rc1_info.get("throughput_tph", 0.0) > cap_rc1 * mp["RC.1"].get("n_units", 1):
        alerts.append(
            f"RC.1: bottleneck — load {rc1_info['throughput_tph']:.1f} t/h > "
            f"{mp['RC.1'].get('n_units', 1)} x {cap_rc1} t/h installed"
        )
    cap_rc2 = mp["RC.2"].get("max_capacity_tph")
    n_rc2 = mp["RC.2"].get("n_units", 1)
    load_rc2 = rc2_info.get("throughput_tph", 0.0)
    if cap_rc2 is not None:
        units_needed = max(1, -(-load_rc2 // cap_rc2)) if load_rc2 > 0 else 0
        rc2_info["units_in_service"] = int(min(units_needed, n_rc2))
        if load_rc2 > cap_rc2 * n_rc2:
            alerts.append(
                f"RC.2: bottleneck — load {load_rc2:.1f} t/h > "
                f"{n_rc2} x {cap_rc2} t/h installed"
            )

    # SP.36 + CL.38 — identical UltraFin block (D2 scope)
    fines = outputs["fines"]
    m8, ultrafin, remaining_fines, d50_cyclone = _sp36_ultrafin(
        fines, mp, calib, phi_100_pct, alerts
    )

    sca_areas = {
        "deck_1": models.m4_screen_area(outputs["ua1"], a1, calib),
        "deck_2": models.m4_screen_area(outputs["ua2"], a2, calib),
    }
    _check_installed_area("SC.A", sca_areas, mp["SC.A"].get("installed_area_m2"), alerts)
    scb_areas = {
        "deck_1": models.m4_screen_area(outputs["ub1"], b1, calib),
        "deck_2": models.m4_screen_area(outputs["ub2"], b2, calib),
    }
    _check_installed_area("SC.B", scb_areas, mp["SC.B"].get("installed_area_m2"), alerts)

    return {
        "products": {
            "FeedLime grits": outputs["grits"],
            "FeedLime fines": remaining_fines,
            "UltraFin": ultrafin,
            "Sliver 1.5/2": outputs["sliver"],
        },
        "machines": {
            "DY.03": m6,
            "SC.A": {
                "feed_tph": outputs["sca_feed"]["q"],
                "areas_m2": sca_areas,
            },
            "SC.B": {
                "feed_tph": outputs["scb_feed"]["q"] if outputs["scb_feed"] else 0.0,
                "areas_m2": scb_areas,
            },
            "RC.1": rc1_info,
            "RC.2": rc2_info,
            "SP.36": {
                "Q_air_m3h": m8["Q_air_m3h"] if m8 else None,
                "Phi_cut": m8["Phi_cut"] if m8 else None,
                "certified": m8["certified"] if m8 else None,
            },
            "CL.38": {"d50_um": d50_cyclone},
        },
        "recirculation_tph": recycle["q"] if recycle else 0.0,
        "vapor_tph": m6["evaporated_water_tph"],
    }
