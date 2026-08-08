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

from .scenario import _deep_merge, run_scenario


def run_required_hours(params: dict) -> dict:
    """Computes the operating hours each zone needs to meet the targets."""
    alerts: list[str] = []
    sc = params["default_scenario"]
    flow = sc["flow_rates_tph"]
    targets = {t["product"]: t for t in params["production_targets"].values()}

    photo_dry = run_scenario(_deep_merge(params, {"default_scenario": {"weather": "dry"}}))
    photo_rain = run_scenario(_deep_merge(params, {"default_scenario": {"weather": "rain"}}))

    # hourly product rates (t/h, as sold) from the photos
    kfs_tph = photo_dry["products"]["KFS"]["tph"]
    aglime_tph = photo_dry["products"]["AgLime"]["tph"]
    grits_tph = photo_dry["products"]["FeedLime grits"]["tph"]
    fines_tph = photo_dry["products"]["FeedLime fines"]["tph"]
    ultrafin_tph = photo_dry["products"]["UltraFin"]["tph"]
    moisture = params["feed_product"]["properties"]["moisture_pct"]["default"]
    q020_tph_wet = photo_dry["intermediate_flows"]["0/20_dry_tph"] / (1.0 - moisture / 100.0)
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
        raise ValueError("Zone 1.3 produces no grits: cannot plan hours from the grits target")
    h13_eff = targets["FeedLime grits"]["target_t_per_year"] / grits_tph
    zone13 = _zone_result("1.3", h13_eff)
    feedlime_demand_t = h13_eff * flow["zone_1_3_feedlime"]  # wet, consumed by the dryer

    # ---- 2. Zone 1.2: dry-season hours set by the AgLime market volume,
    #         rain-season hours added if FeedLime is still short
    aglime_target = targets["AgLime"].get("market_cap_t_per_year") or targets["AgLime"][
        "target_t_per_year"
    ]
    if aglime_tph <= 0:
        raise ValueError("Zone 1.2 produces no AgLime in dry weather: check the scenario")
    h2_dry_eff = aglime_target / aglime_tph
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
    zone12 = _zone_result("1.2", h2_dry_eff + h2_rain_eff)
    reclaimed_020_t = (h2_dry_eff + h2_rain_eff) * flow["zone_1_2_reclaim"]

    # ---- 3. Zone 1.1: hours set by the FIRM KFS target AND the 0/20 demand
    if kfs_tph <= 0:
        raise ValueError("Zone 1.1 produces no KFS (mode 1B?): cannot plan from the KFS target")
    h11_kfs_eff = targets["KFS"]["target_t_per_year"] / kfs_tph
    h11_020_eff = reclaimed_020_t / q020_tph_wet
    h11_eff = max(h11_kfs_eff, h11_020_eff)
    driver = "KFS target" if h11_kfs_eff >= h11_020_eff else "0/20 demand of zone 1.2"
    zone11 = {**_zone_result("1.1", h11_eff), "driven_by": driver}

    # ---- resulting yearly production and stockpile balance
    aglime_t = h2_dry_eff * aglime_tph
    production_t = {
        "KFS": round(h11_eff * kfs_tph, 0),
        "AgLime": round(aglime_t, 0),
        "FeedLime grits": round(h13_eff * grits_tph, 0),
        "FeedLime fines": round(h13_eff * fines_tph, 0),
        "UltraFin": round(h13_eff * ultrafin_tph, 0),
    }
    for product, tonnage in production_t.items():
        target = targets[product]
        cap = target.get("market_cap_t_per_year")
        if cap is None and target["nature"] == "flexible":
            cap = target["target_t_per_year"]
        if cap is not None and tonnage > cap + 0.5:
            alerts.append(
                f"{product}: {tonnage:.0f} t produced > market {cap} t — unsellable surplus "
                f"{tonnage - cap:.0f} t (inherent co-product at these settings)"
            )

    stockpiles_t = {
        "0/20 produced": round(h11_eff * q020_tph_wet, 0),
        "0/20 reclaimed": round(reclaimed_020_t, 0),
        "0/20 net to stock": round(h11_eff * q020_tph_wet - reclaimed_020_t, 0),
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
        },
        "production_t": production_t,
        "stockpiles_t": stockpiles_t,
        "alerts": alerts + photo_dry["alerts"],
    }
