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
def zone_1_1(feed: dict, params: dict, mode: str, alerts: list) -> dict:
    """Zone 1.1 — crushing / primary screening (pivot feed -> KFS + 0/20).

    Pivot (§5): the feed curve is MEASURED at the primary station outlet
    (grizzly + CR.5003 already blended into the curve). Modelled chain:
    pivot -> CR.5009 -> SR.5007 (35/20) with the CR.5011 loop on the +35
    oversize. Mode 1A: 20-35 cut -> KFS; mode 1B: 20-35 cut -> CR.5011
    (no KFS).
    """
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
    if recycle and cap11 and recycle["q"] > cap11:
        alerts.append(
            f"CR.5011: bottleneck — load {recycle['q']:.1f} t/h > capacity {cap11} t/h"
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

    areas = {
        "top_deck": models.m4_screen_area(outputs["u_top_deck"], a1, calib),
        "bottom_deck": models.m4_screen_area(outputs["u_bottom_deck"], a2, calib),
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
    """Zone 1.2 — reclaim / AgLime.

    0/20 stockpile -> BF.5101 -> SR.5105 (15/5): +15, 5-15 (mid), 0-5.
    Mode 2A: mid -> FeedLime, rest -> loop; 2B (rain): everything ->
    FeedLime; 2C: everything -> loop. Loop: SR.5115 (1.7); oversize ->
    CR.5107 -> return; undersize 0-1.7 = AgLime.

    Under rain the spec forces mode 2B (scenario parameter
    ``rain_forces_mode_2B``, default true). When that forcing is disabled,
    the AgLime loop is computed with the degraded imperfection ``I_rain``
    and flagged as directional (audit finding on I_rain reachability).
    """
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

    p05 = mp["SR.5105"]["parameters"]
    over15, under15 = _karra_screen(reclaim, p05["a1"]["default"], calib["I_dry"], calib)
    mid, under5 = (
        _karra_screen(under15, p05["a2"]["default"], calib["I_dry"], calib)
        if under15
        else (None, None)
    )
    sr5105_areas = {
        "top_deck": models.m4_screen_area(under15["q"] if under15 else 0.0, p05["a1"]["default"], calib),
        "bottom_deck": models.m4_screen_area(under5["q"] if under5 else 0.0, p05["a2"]["default"], calib),
    }
    _check_installed_area("SR.5105", sr5105_areas, mp["SR.5105"].get("installed_area_m2"), alerts)

    result = {
        "machines": {
            "SR.5105": {"feed_tph": reclaim["q"], "areas_m2": sr5105_areas},
            "SR.5115": {},
            "CR.5107": {},
        }
    }

    if mode == "2B":
        result["products"] = {"AgLime": None, "FeedLime": reclaim}
        result["recirculation_tph"] = 0.0
        return result

    feedlime = mid if mode == "2A" else None
    to_loop = [s for s in [over15, under5] + ([mid] if mode == "2C" else []) if s]
    if not to_loop:
        result["products"] = {"AgLime": None, "FeedLime": feedlime}
        result["recirculation_tph"] = 0.0
        return result
    loop_feed = _blend(to_loop)

    p15 = mp["SR.5115"]["parameters"]
    p07 = mp["CR.5107"]["parameters"]
    imp_1_7 = p15["I"]["default"] if weather == "dry" else calib["I_rain"]
    cr5107_info = {}

    def iterate(recycle):
        screen_feed = _blend([loop_feed, recycle]) if recycle else loop_feed
        oversize, aglime = _karra_screen(screen_feed, p15["a"]["default"], imp_1_7, calib)
        if oversize:
            out, info = _impactor(oversize, p07["v"]["default"], p07["x80"]["default"], calib)
            cr5107_info.update(info)
            new = out
        else:
            new = None
        return new, {"aglime": aglime, "sr5115_feed": screen_feed}

    recycle, outputs = _fixed_point_loop(iterate, engine, alerts, "Zone 1.2 / CR.5107")
    if recycle and recycle["q"] > engine["max_circulating_ratio"] * loop_feed["q"]:
        alerts.append(
            "CR.5107: circulating load explodes (CSS too large?) — specification alarm"
        )

    sr5115_areas = {
        "deck": models.m4_screen_area(
            outputs["aglime"]["q"] if outputs["aglime"] else 0.0, p15["a"]["default"], calib
        )
    }
    _check_installed_area("SR.5115", sr5115_areas, mp["SR.5115"].get("installed_area_m2"), alerts)
    result["machines"]["SR.5115"] = {
        "feed_tph": outputs["sr5115_feed"]["q"],
        "areas_m2": sr5115_areas,
        "imperfection_used": imp_1_7,
    }
    result["machines"]["CR.5107"] = cr5107_info
    result["products"] = {"AgLime": outputs["aglime"], "FeedLime": feedlime}
    result["recirculation_tph"] = recycle["q"] if recycle else 0.0
    return result


# ===================================================================== 1.3
def zone_1_3(feedlime: dict, params: dict, phi_100_pct, alerts: list) -> dict:
    """Zone 1.3 — drying / grits / UltraFin.

    FeedLime -> DY.03 (dryer, -> m_out) -> SN.21 (4/2/1.5): 2-4 = grits;
    +4 oversize and 1.5-2 sliver -> ML.26 -> back to SN.21 (closed circuit);
    0-1.5 undersize = fines -> SP.36 (+ CL.38) -> UltraFin; remainder =
    FeedLime fines.
    """
    mp = params["machines"]
    calib = params["calibration"]
    engine = params["engine"]

    # DY.03 — dryer: M6 balance on the WET flow rate
    m_out = mp["DY.03"]["parameters"]["m_out"]["default"]
    wet_feed = feedlime["q"] / (1.0 - feedlime["moisture"] / 100.0)
    cap_dryer = mp["DY.03"].get("max_capacity_tph")
    if cap_dryer is not None and wet_feed > cap_dryer:
        alerts.append(
            f"DY.03: bottleneck — wet feed {wet_feed:.1f} t/h > dryer capacity {cap_dryer} t/h"
        )
    m6 = models.m6_drying(wet_feed, feedlime["moisture"], m_out, calib)
    dried = _stream(m6["dry_solids_tph"], feedlime["psd"], m_out)

    p21 = mp["SN.21"]["parameters"]
    a1, a2, a3 = (p21[k]["default"] for k in ("a1", "a2", "a3"))
    p26 = mp["ML.26"]["parameters"]
    gap26 = p26["g"]["default"]
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
            mill_psd = models.m7_bed_mill_pass(mill_feed["psd"], gap26, calib_ml26)
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
    p36 = mp["SP.36"]["parameters"]
    # the SP.36 / CL.38 machine sheets take precedence for their own settings
    calib_cl = {
        **calib,
        "eta_cl": p36["eta_cl"]["default"],
        "v_in_cyclone": mp["CL.38"]["parameters"]["v_in"]["default"],
    }
    if fines:
        m8 = models.m8_air_classification(
            fines["q"], fines["psd"], p36["coupe"]["default"], phi_100_pct, calib_cl
        )
        if not m8["certified"]:
            alerts.append(
                "SP.36: Phi(<cut) not measured — UltraFin computed from the modelled "
                "curve, flagged NOT CERTIFIED (to be measured by sieve/laser)"
            )
        ultrafin = _stream(m8["fine_product_tph"], m8["fine_product_psd"], fines["moisture"])
        remaining_fines = _stream(m8["remainder_tph"], m8["remainder_psd"], fines["moisture"])
    else:
        m8 = None
        ultrafin = None
        remaining_fines = None

    d50_cyclone = models.m8_cyclone_d50(calib_cl)

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
