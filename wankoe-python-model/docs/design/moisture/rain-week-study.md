# Rain-week moisture study — porous stone, outdoor stockpiles

Client arbitration 2026-08-15. The stone is EXTREMELY POROUS: after one
week of continuous rain on the outdoor stockpiles the stock moistures
rise well above the 7 % reference (belt cut 2026-08-08), then drain
slowly back over 5-7 days. This study measures what the rain week costs
against a dry week, follows the drainage tail, and scales the impact to
an annual view with N rain weeks.

## 1. The arbitrated scenario (data-first, every value [H])

Encoded in `docs/design/moisture/rain-week-scenario.json` — engine
defaults unchanged.

| Item | Value | Status |
|---|---|---|
| Quarry feed moisture after the rain week | 7 → **12 %** | [H] client porous-stone estimate |
| Reclaimed 0/20 stock | 7 → **15 %** | [H] (finest outdoor pile absorbs the most) |
| FeedLime 6/20 stock | 7 → **11 %** | [H] (coarser pile drains better) |
| Drainage back to 7 % | 5-7 days, **6-day midpoint, linear** | [H] |
| Rain weeks per year N | **6** (parameterized) | [H] flagged study choice, pending site rainfall records |
| Operating policy | the line **CONTINUES everywhere** during the rain week | client |
| New external trigger | **ABSORPTION TEST on samples** — replaces every [H] moisture and the drainage profile | client |

**Physical rule (requalified in the register the same day):** wet
screening at **1.7 mm is IMPOSSIBLE** — rain forcing zone 1.2 into mode
2B is **physics, not policy** (zero AgLime during rain, full stop). The
zone-1.3 SC.B 2/1.5 product cuts sit **behind the dryer at 0.5 %** and
are unaffected; the 6 mm and 20/35 mm cuts remain feasible wet with the
`wet_capacity_factor` 0.75 [H] area derating. The data notes
(`rain_forces_mode_2B`, `I_rain`, `wet_capacity_factor`) now state this;
`I_rain` survives only in the audit branch (`rain_forces_mode_2B=false`,
directional result, never an operating case).

## 2. Method — composite photos (engine limitation, stated honestly)

The engine carries **one global moisture per photo**
(`feed_product.properties.moisture_pct`): in `scenario.py` the zone-1.2
reclaim and the zone-1.3 FeedLime streams inherit the FEED moisture. The
three simultaneous stock moistures (12/15/11 %) are therefore **not
expressible in a single photo**. The study reads a composite of per-zone
engine photos, each at its own stock moisture:

| Zone read | Photo | Why |
|---|---|---|
| 1.1 | 12 %, weather `rain` | quarry feed moisture; rain derates the SR.5007 areas |
| 1.2 | 15 %, weather `rain` | reclaimed 0/20 stock; mode 2B forced (physics) |
| 1.3 (G and F) | 11 %, weather `dry` **on purpose** | zone 1.3 is weather-independent (all cuts behind the dryer); the dry flag keeps the FeedLime stream on the **6/20 stock PSD** — a rain flag would swap it for the 2B bypass 0/20 PSD, which is not the stock the client scenario describes |

**Per-stream moisture overrides are a model-improvement item** (e.g.
`default_scenario.stream_moistures_pct.{reclaim,feedlime}`).

Weekly frame: the annual required-hours plan divided by 52 (effective
hours — the line continues at its planned regime in both weeks):
zone 1.1 mode 1A 26.3 h, zone 1.2 2A 33.7 h + 2C 13.1 h, zone 1.3
mode G 47.4 h + mode F 22.0 h.

## 3. (a) Dry week vs rain week — weekly balance

| Per week (same hours) | Dry week (7 %) | Rain week (12/15/11 %) | Delta |
|---|---|---|---|
| KFS (wet, as sold) | 1 634.6 t | 1 634.6 t | 0 (but 88 % dry solids vs 93 % — 5 pt more water sold) |
| AgLime | 2 596.2 t | **0 t** | **−2 596.2 t** (1.7 mm physics) |
| FeedLime grits | 769.2 t | 736.1 t | −33.1 t (−4.3 %) |
| FeedLime fines | 1 153.8 t | 1 104.2 t | −49.6 t (−4.3 %) |
| UltraFin | 5.5 t | 5.2 t | −0.3 t |
| FeedLime produced by z1.2 | 2 073.6 t (6/20, 2A) | 4 669.8 t (**2B bypass, unscreened 0/20**) | quality change, see § 7 |
| 0/20 reclaimed | 4 669.8 t | 4 669.8 t | 0 (wet belt-weighed rule) |
| Dryer outlet, mode G | 30.00 t/h | **28.71 t/h** | −1.29 t/h |
| Burner energy | 240.2 MWh | 337.7 MWh | +97.5 MWh |
| **Paraffin** | **25 080 L** | **35 265 L** | **+10 185 L (+40.6 %)** |

KFS wet tonnage is moisture-invariant because the 250 t/h pivot feed is
wet belt-weighed (total-flow rule) and the PSD split is
moisture-independent in the model — the rain week ships the same wet
tonnes carrying 5 pt more water.

### Dryer outlet vs the 30 t/h limit

At 11 % inlet moisture the 32.1 t/h wet-feed cap yields only
**28.71 t/h at the outlet** (32.1 × (1 − 0.11)/(1 − 0.005)) — the
30 t/h outlet limit **cannot be reached** during the rain week. This is
structural throughput loss, not an overload; the wet-feed cap is
respected. Mode F outlet drops 23.41 → 22.41 t/h. Burner: mode G
3 717.8 → 5 227.6 kW, mode F 2 901.3 → 4 079.5 kW.

### KFS envelope under rain

KFS envelope compliance is COMPLIANT and model-identical dry vs rain
(in-cut 82.75 %, below 8.69, above 8.56): the engine wires `I_rain` to
the 1.7 mm screens only (now moot — mode 2B is physics), so the 20/35
cut keeps its dry imperfection; rain enters zone 1.1 as the
`wet_capacity_factor` area derating — SR.5007 required areas grow
6.80/7.15 → 8.58/9.02 m² (top/bottom deck). A wet-screening
imperfection model for the coarse cuts is a candidate improvement,
pending site evidence.

## 4. (b) The 5-7 day drainage tail (6-day midpoint, linear [H])

Stock moistures interpolate linearly back to 7 %; daily hours = weekly
hours / 7. Engine photos per day (mode G shown; paraffin excess covers
G + F):

| Day after rain | Feed % | 0/20 % | 6/20 % | Dryer outlet G (t/h) | Burner G (kW) | Paraffin excess (L/day) | Grits deficit (t/day) | Fines deficit (t/day) |
|---|---|---|---|---|---|---|---|---|
| 1 | 11.2 | 13.7 | 10.3 | 28.93 | 4 976 | 1 213 | 3.9 | 5.9 |
| 2 | 10.3 | 12.3 | 9.7 | 29.14 | 4 724 | 970 | 3.2 | 4.7 |
| 3 | 9.5 | 11.0 | 9.0 | 29.36 | 4 473 | 728 | 2.4 | 3.5 |
| 4 | 8.7 | 9.7 | 8.3 | 29.57 | 4 221 | 485 | 1.6 | 2.4 |
| 5 | 7.8 | 8.3 | 7.7 | 29.79 | 3 969 | 243 | 0.8 | 1.2 |
| 6 | 7.0 | 7.0 | 7.0 | 30.00 | 3 718 | 0 | 0 | 0 |
| **Tail total** | | | | | | **3 638 L** | **11.8 t** | **17.7 t** |

Zone 1.2 returns to mode 2A when the rain stops (weather dry). The
engine has **no wet-stock screening degradation model** (I_rain and the
2B forcing key on the weather flag, not on stock moisture) — whether the
6 mm and 1.7 mm cuts really run cleanly on a 13-15 % stock in the first
tail days is exactly what the **absorption test** must answer
(limitation, § 8).

## 5. (c) Annual view — N = 6 rain weeks [H]

Weekly-scaled arithmetic on engine hourly rates (clearly labeled — not
a single engine photo), applied to the reference annual plan; each rain
week carries its drainage tail.

| Annual impact (N = 6) | Value | Basis |
|---|---|---|
| **Paraffin over-consumption** | **+82 938 L/y** (+6.4 % of the 1 304 155 L/y reference) | N × (week excess 10 185 + tail excess 3 638) L |
| AgLime | **no annual loss** — 15 577 t shifted from rain weeks to dry-week catch-up | zone-1.2 mode-mix identity below |
| Landfill | **unchanged, 13 816 t/y** | total reclaim invariant (every reclaimed tonne leaves as product in 2A, 2B and 2C alike — zero-waste structure) |
| Grits / fines hour deficits | 270 t / 404 t recovered by **+34.1 effective hours** in zone 1.3 | 3 644.6 h vs 6 000 h ceiling — feasible (60.7 % clock utilization vs 60.2) |
| KFS | annual wet tonnage unchanged; ~6 weeks ship 5 pt more water | wet-basis invariance |
| Markets | **all four served** | see identities below |

Zone-1.2 mode-mix identity (constant total hours 2 428.3 eff h):
rain weeks run 280.2 h in 2B (FeedLime bypass 28 020 t), displacing
454.7 h of 2A (1 749.7 → 1 295.1 h) and its AgLime co-production,
made up by 174.4 extra 2C campaign hours (678.6 → 853.0 h).
Utilization stays 40.5 %.

**Engine cross-check** — `run_required_hours` with season fractions
6/52: the planner schedules 0 rain-season hours (dry-season capacity
suffices) and the plan is N-invariant; production stays KFS 85 000 /
AgLime 135 000 / grits 40 000 / fines 60 000 / UltraFin 284 t. The 2B
rain-week running is the client's continue-everywhere policy, expressed
as the mode-mix shift above.

Scaling: every annual figure is linear in N (e.g. paraffin excess
≈ 13 823 L per rain week including its tail).

## 6. Sensitivity of the verdicts

- The AgLime "no annual loss" verdict holds while zone-1.2 headroom
  lasts: catch-up needs no extra hours at all (mode-mix identity), so
  it holds for any N up to the FeedLime-demand bound (~2 428 h of 2B
  ≈ 52 weeks) — AgLime timing, not volume, is the exposure
  (customer-delivery smoothing from stock).
- The zone-1.3 feasibility verdict holds up to N ≈ far beyond any
  plausible rainfall (34.1 extra hours per 6 weeks vs ~2 355 h of
  headroom).
- The paraffin figure scales linearly in N and in the [H] moistures —
  first thing the absorption test will sharpen.

## 7. Annex — what the rain-week 2B hours add to the FeedLime stock

The 2B bypass FeedLime is **unscreened 0/20** (the 0/6 fraction is not
removed). An annex photo (outside the arbitrated composite) feeds zone
1.3 with this bypass PSD at 12 %: grits 15.73 t/h, fines 12.45 t/h,
grits envelope still compliant (below-cut 13.69 % vs 8.69 on the 6/20
stock — margin shrinks). Six rain weeks add ~28 kt of this finer
material to the FeedLime yard: **stock-PSD watch item** for the D6
envelope on grits.

## 8. Limitations and model-improvement items

1. **One global moisture per photo** — reclaim and FeedLime streams
   inherit the feed moisture in `scenario.py`; distinct stock moistures
   required a composite of per-zone photos. Improvement: per-stream
   moisture overrides.
2. **No wet-stock screening model** — rain effects key on the weather
   flag, not on stock moisture; the drainage tail assumes 2A resumes at
   rain end. The absorption test decides.
3. **Coarse-cut imperfection weather-independent** — rain only derates
   screen areas (wet_capacity_factor 0.75 [H]); no wet imperfection for
   20/35 and 6 mm cuts.
4. **Every rain-week moisture, the drainage profile and N are [H]** —
   replaced by the absorption test on samples (new external trigger)
   and site rainfall records.
5. Weekly/daily frames are the annual plan divided by 52/7 —
   arithmetic, clearly labeled; the mode-mix and annual views are
   weekly-scaled arithmetic on engine rates, not one engine photo.
6. Stock wet tonnages are compared across moistures on the wet
   belt-weighed rule; the FeedLime yard balance across a rain year
   mixes 7-15 % material (second-order, absorbed by the drainage tail).

## 9. Provenance

- Engine run: commit `f31945d`, 2026-08-15, functions
  `wankoe_model.scenario.run_scenario` (composite per-zone photos:
  z1.1 @ 12 % rain, z1.2 @ 15 % rain, z1.3 @ 11 % dry-flag G/F,
  drainage-tail dailies, bypass-PSD annex) +
  `wankoe_model.planning.run_required_hours` (reference plan + N/52
  season cross-check).
- Data: `data/default_parameters.json` (defaults, 7 %) +
  `docs/design/moisture/rain-week-scenario.json` (overrides, [H]).
- Evidence: `docs/design/moisture/rain-week-engine-evidence.json`;
  replay without the assistant:
  `PYTHONPATH=src python scripts/rain_week_study.py`.
- All figures are engine executions except the weekly/daily hour
  scaling, the zone-1.2 mode-mix identity and the annual N-scaling,
  which are the labeled arithmetic of § 3/§ 5 on engine rates.
- Paraffin conversions use the data-first burner properties (LHV
  11.97 kWh/kg [H], density 0.80 kg/L [H]).

*Produced by NOEZYS.*
