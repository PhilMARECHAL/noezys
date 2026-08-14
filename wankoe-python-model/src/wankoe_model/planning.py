"""Operating-hours planning: hours are SET BY the production targets.

Client principle (2026-08-08): "Calez les heures de fonctionnement sur les
objectifs de production, jamais l'inverse" — operating hours follow the
production targets, never the other way around.

``run_required_hours(params)`` therefore treats the shift regimes
(``default_scenario.zones[*].available_hours``) as CAPACITY CEILINGS and
computes, from the line photos, the hours each zone must run:

1. Zone 1.3 runs long enough to make the FIRM grits target
   -> that fixes the FeedLime tonnage it consumes.
2. Zone 1.2 runs (in the dry season, mode 2A) long enough to make the
   AgLime market volume, plus rain-season hours (mode 2B) if more FeedLime
   is still needed -> that fixes the 0/20 tonnage it reclaims.
3. Zone 1.1 runs long enough to make the FIRM KFS target AND to feed the
   0/20 demand of zone 1.2 (whichever needs more hours).

Every step is checked against the zone's capacity ceiling; utilization and
infeasibilities are reported. All figures derive from the pure
``run_scenario`` photos — no hidden state.
"""

from __future__ import annotations

from .paths import deep_merge
from .scenario import run_scenario


def run_required_hours(params: dict) -> dict:
    """Computes the operating hours each zone needs to meet the targets.

    All rates derive from the DRY-weather photo; rain-season hours of zone
    1.2 run in mode 2B where FeedLime = the whole reclaim (a mass identity,
    not a model assumption). Zone 1.1 and 1.3 rates are weather-independent
    in the model, so a single photo suffices.
    """
    alerts: list[str] = []
    sc = params["default_scenario"]
    flow = sc["flow_rates_tph"]
    targets = {t["product"]: t for t in params["production_targets"].values()}

    photo_dry = run_scenario(deep_merge(params, {"default_scenario": {"weather": "dry"}}))

    # hourly product rates (t/h, as sold) from the photo
    products = photo_dry["products"]
    kfs_tph = products["KFS"]["tph"]
    aglime_tph = products["AgLime"]["tph"]
    grits_tph = products.get("FeedLime grits", {}).get("tph", 0.0)
    fines_tph = products.get("FeedLime fines", {}).get("tph", 0.0)
    ultrafin_tph = products.get("UltraFin", {}).get("tph", 0.0)
    moisture = params["feed_product"]["properties"]["moisture_pct"]["default"]
    q020_tph_wet = photo_dry["intermediate_flows"]["stream_0_20_dry_tph"] / (
        1.0 - moisture / 100.0
    )
    # FeedLime co-product of zone 1.2 (wet): reclaim - AgLime (2A) / all (2B)
    feedlime_dry_season_tph = flow["zone_1_2_reclaim"] - aglime_tph
    feedlime_rain_season_tph = flow["zone_1_2_reclaim"]

    ceilings = {
        name: {
            "clock_h": z["available_hours"],
            "effective_h": (
                z["available_hours"] * z["availability_pct"] / 100.0
                if z["available_hours"] is not None
                else None
            ),
            "availability_pct": z["availability_pct"],
        }
        for name, z in sc["zones"].items()
    }
    f_dry = sc["dry_season_fraction"]
    f_rain = sc["rain_season_fraction"]

    def _zone_result(name, required_eff):
        ceiling = ceilings[name]
        clock = required_eff / (ceiling["availability_pct"] / 100.0)
        result = {
            "required_hours_effective": round(required_eff, 1),
            "required_hours_clock": round(clock, 1),
            "ceiling_hours_clock": ceiling["clock_h"],
            "utilization_pct": (
                round(100.0 * clock / ceiling["clock_h"], 1)
                if ceiling["clock_h"]
                else None
            ),
            "feasible": None if ceiling["clock_h"] is None else bool(clock <= ceiling["clock_h"]),
        }
        if result["feasible"] is False:
            alerts.append(
                f"Zone {name}: {clock:.0f} h required > ceiling {ceiling['clock_h']} h "
                "— targets NOT reachable within the shift regime (raise hours or flow rate)"
            )
        return result

    # ---- 1. Zone 1.3: hours set by the FIRM grits target
    if grits_tph <= 0:
        raise ValueError(
            "Zone 1.3 produces no grits (zone 1.2 mode 2C, or no FeedLime): "
            "cannot plan hours from the grits target"
        )
    h13_eff = targets["FeedLime grits"]["target_t_per_year"] / grits_tph
    zone13 = _zone_result("1.3", h13_eff)
    feedlime_demand_t = h13_eff * flow["zone_1_3_feedlime"]  # wet, consumed by the dryer

    # ---- 2. Zone 1.2: client planning rules (c2 2026-08-12, amended by the
    #         ZERO-WASTE rule 2026-08-13): hours follow the FeedLime demand
    #         of zone 1.3. The fines surplus beyond its own market is
    #         REDIRECTED into the AgLime sales channel (fines 0/1.5 sit
    #         inside the AgLime 0/1.7 acceptance spec), so the AgLime LOOP
    #         only produces the complement up to the AgLime market cap.
    #         There is NO AgLime production objective. 2026-08-14 amendment
    #         (C1 adoption dried up the redirect): the residual market gap
    #         is served by DEDICATED 2C campaigns (see the campaign block).
    aglime_cap = targets["AgLime"].get("market_cap_t_per_year") or targets["AgLime"][
        "target_t_per_year"
    ]
    fines_spec = targets["FeedLime fines"]
    fines_cap = fines_spec.get("market_cap_t_per_year") or fines_spec["target_t_per_year"]
    fines_production_t = h13_eff * fines_tph
    fines_redirect_t = max(0.0, fines_production_t - fines_cap)
    if fines_redirect_t > aglime_cap:
        alerts.append(
            f"Zero-waste rule saturated: fines surplus {fines_redirect_t:.0f} t exceeds the "
            f"whole AgLime market {aglime_cap:.0f} t — {fines_redirect_t - aglime_cap:.0f} t "
            "remain UNSELLABLE"
        )
    aglime_loop_target = max(0.0, aglime_cap - fines_redirect_t)
    if aglime_tph <= 0:
        raise ValueError("Zone 1.2 produces no AgLime in dry weather: check the scenario")
    h2_aglime_cap_eff = aglime_loop_target / aglime_tph
    h2_feedlime_eff = (
        feedlime_demand_t / feedlime_dry_season_tph
        if feedlime_dry_season_tph > 0
        else float("inf")
    )
    h2_dry_eff = min(h2_aglime_cap_eff, h2_feedlime_eff)
    dry_capacity_eff = (
        ceilings["1.2"]["effective_h"] * f_dry if ceilings["1.2"]["effective_h"] else None
    )
    if dry_capacity_eff is not None and h2_dry_eff > dry_capacity_eff:
        alerts.append(
            f"Zone 1.2: {h2_dry_eff:.0f} effective dry-season hours needed for the AgLime "
            f"market volume > dry-season capacity {dry_capacity_eff:.0f} h — AgLime capped "
            "by the season, volume reduced"
        )
        h2_dry_eff = dry_capacity_eff
    feedlime_from_dry_t = h2_dry_eff * feedlime_dry_season_tph
    feedlime_short_t = max(0.0, feedlime_demand_t - feedlime_from_dry_t)
    h2_rain_eff = (
        feedlime_short_t / feedlime_rain_season_tph if feedlime_short_t > 0 else 0.0
    )
    rain_capacity_eff = (
        ceilings["1.2"]["effective_h"] * f_rain if ceilings["1.2"]["effective_h"] else None
    )
    if rain_capacity_eff is not None and h2_rain_eff > rain_capacity_eff:
        alerts.append(
            f"Zone 1.2: {h2_rain_eff:.0f} effective rain-season hours needed to complete "
            f"the FeedLime demand > rain-season capacity {rain_capacity_eff:.0f} h — "
            "grits target NOT reachable (raise reclaim rate or hours)"
        )
        # cap so the reported production/stockpiles reflect what is achievable
        h2_rain_eff = rain_capacity_eff
        achieved_feedlime = feedlime_from_dry_t + h2_rain_eff * feedlime_rain_season_tph
        h13_eff = achieved_feedlime / flow["zone_1_3_feedlime"]
        feedlime_demand_t = achieved_feedlime
        zone13 = _zone_result("1.3", h13_eff)
    # ---- 2C AgLime campaigns (client rule, wired 2026-08-14): when the 2A
    #      co-production + fines redirect leave the AgLime market unserved
    #      (the C1 adoption dried up the redirect), zone 1.2 runs DEDICATED
    #      mode-2C campaigns — everything reclaimed leaves as AgLime.
    rules = params.get("commercial_rules", {})
    aglime_2a_t = h2_dry_eff * aglime_tph
    aglime_2c_t = 0.0
    h2c_eff = 0.0
    aglime_gap_t = max(0.0, aglime_loop_target - aglime_2a_t)
    if rules.get("aglime_2c_campaigns", False) and aglime_gap_t > 0.5:
        photo_2c = run_scenario(
            deep_merge(
                params,
                {"default_scenario": {"weather": "dry", "zone_1_2_mode": "2C"}},
            )
        )
        aglime_2c_tph = photo_2c["products"]["AgLime"]["tph"]
        if aglime_2c_tph <= 0:
            raise ValueError("Mode 2C produces no AgLime: check the scenario")
        h2c_eff = aglime_gap_t / aglime_2c_tph
        ceiling_2_eff = ceilings["1.2"]["effective_h"]
        if ceiling_2_eff is not None and h2_dry_eff + h2_rain_eff + h2c_eff > ceiling_2_eff:
            h2c_eff = max(0.0, ceiling_2_eff - h2_dry_eff - h2_rain_eff)
            alerts.append(
                "Zone 1.2: 2C campaign hours capped by the zone ceiling — AgLime "
                "market not fully served"
            )
        aglime_2c_t = h2c_eff * aglime_2c_tph
        if aglime_2c_t > 0:
            alerts.append(
                f"AgLime 2C campaigns: {h2c_eff:.0f} effective hours produce "
                f"{aglime_2c_t:.0f} t to complete the market beyond the 2A "
                f"co-production ({aglime_2a_t:.0f} t) — consumes "
                f"{h2c_eff * flow['zone_1_2_reclaim']:.0f} t of 0/20"
            )
    zone12 = _zone_result("1.2", h2_dry_eff + h2_rain_eff + h2c_eff)
    reclaimed_020_t = (h2_dry_eff + h2_rain_eff + h2c_eff) * flow["zone_1_2_reclaim"]

    # ---- 3. Zone 1.1: hours set by the FIRM KFS target AND the 0/20 demand
    if kfs_tph <= 0:
        raise ValueError("Zone 1.1 produces no KFS (mode 1B?): cannot plan from the KFS target")
    h11_kfs_eff = targets["KFS"]["target_t_per_year"] / kfs_tph
    h11_020_eff = reclaimed_020_t / q020_tph_wet
    h11_eff = max(h11_kfs_eff, h11_020_eff)
    driver = "KFS target" if h11_kfs_eff >= h11_020_eff else "0/20 demand of zone 1.2"
    zone11 = {**_zone_result("1.1", h11_eff), "driven_by": driver}

    # ---- resulting yearly production and stockpile balance
    aglime_t = aglime_2a_t + aglime_2c_t
    production_t = {
        "KFS": round(h11_eff * kfs_tph, 0),
        "AgLime": round(aglime_t, 0),
        "FeedLime grits": round(h13_eff * grits_tph, 0),
        "FeedLime fines": round(h13_eff * fines_tph, 0),
        "UltraFin": round(h13_eff * ultrafin_tph, 0),
    }
    for product, tonnage in production_t.items():
        if product in ("FeedLime fines", "AgLime"):
            continue  # handled by the zero-waste redirect accounting below
        target = targets[product]
        cap = target.get("market_cap_t_per_year")
        if cap is None and target["nature"] == "flexible":
            cap = target["target_t_per_year"]
        if cap is not None and tonnage > cap + 0.5:
            alerts.append(
                f"{product}: {tonnage:.0f} t produced > market {cap} t — unsellable surplus "
                f"{tonnage - cap:.0f} t (inherent co-product at these settings)"
            )
    # ---- zero-waste sales accounting (client rule 2026-08-13)
    fines_sold_t = min(fines_production_t, fines_cap)
    aglime_sold_t = min(aglime_cap, aglime_t + fines_redirect_t)
    ultrafin_production_t = h13_eff * ultrafin_tph
    sales_t = {
        "UltraFin sold (market to develop)": round(ultrafin_production_t, 0),
        "FeedLime fines sold as fines": round(fines_sold_t, 0),
        # naming convention (client, 2026-08-14): the redirect is a SALES
        # routing at loadout — zone 1.3 never produces AgLime
        "Fines surplus redirected to the AgLime sales channel": round(fines_redirect_t, 0),
        "AgLime from loop (2A co-production)": round(aglime_2a_t, 0),
        "AgLime from dedicated 2C campaigns": round(aglime_2c_t, 0),
        "AgLime total sold (loop + campaigns + redirect)": round(aglime_sold_t, 0),
        "AgLime market cap": aglime_cap,
    }
    if fines_redirect_t > 0:
        alerts.append(
            f"Zero-waste rule: {fines_redirect_t:.0f} t of fines redirected to the AgLime "
            f"channel (loop production reduced to {aglime_t:.0f} t so total AgLime sales "
            f"stay at the {aglime_cap:.0f} t market cap)"
        )

    # ---- excess 0/20 disposal (client ruling 2026-08-13, final): there is
    # NO market for crude 0/20 — the excess beyond the downstream reclaim
    # goes to LANDFILL and is a NET FINANCIAL LOSS, alerted and minimized
    produced_020_t = h11_eff * q020_tph_wet
    excess_020_t = max(0.0, produced_020_t - reclaimed_020_t)
    if rules.get("crude_020_balancing_sales", False):
        # superseded historical rule kept toggleable for audit only
        sales_t["Crude 0/20 sold (balancing)"] = round(excess_020_t, 0)
        landfill_020_t = 0.0
    elif rules.get("excess_020_to_landfill", True):
        landfill_020_t = excess_020_t
        if landfill_020_t > 0:
            alerts.append(
                f"0/20 excess {landfill_020_t:.0f} t/y to LANDFILL — net financial "
                "loss (no crude market exists); reduce via grits sales, settings "
                "or KFS yield"
            )
    else:
        landfill_020_t = 0.0
    stockpiles_t = {
        "0/20 produced": round(produced_020_t, 0),
        "0/20 reclaimed": round(reclaimed_020_t, 0),
        "0/20 to LANDFILL (net loss)": round(landfill_020_t, 0),
        "0/20 net to stock": round(produced_020_t - reclaimed_020_t - excess_020_t, 0),
        "FeedLime produced": round(feedlime_from_dry_t + h2_rain_eff * feedlime_rain_season_tph, 0),
        "FeedLime consumed": round(feedlime_demand_t, 0),
    }
    stockpiles_t["FeedLime net to stock"] = round(
        stockpiles_t["FeedLime produced"] - stockpiles_t["FeedLime consumed"], 0
    )

    return {
        "principle": "hours follow the production targets (client rule 2026-08-08)",
        "flow_rates_tph": dict(flow),
        "zones": {"1.1": zone11, "1.2": zone12, "1.3": zone13},
        "zone_1_2_split": {
            "dry_season_hours_effective": round(h2_dry_eff, 1),
            "rain_season_hours_effective": round(h2_rain_eff, 1),
            "aglime_2c_campaign_hours_effective": round(h2c_eff, 1),
        },
        "production_t": production_t,
        "sales_t": sales_t,
        "stockpiles_t": stockpiles_t,
        # the photo's own period/stockpile alerts are computed AT CEILING
        # hours — planning solves the hours, so only process alerts carry over
        "alerts": alerts
        + [
            a
            for a in photo_dry["alerts"]
            if not a.startswith("Stockpile") and not a.startswith("Period balance")
        ],
    }
