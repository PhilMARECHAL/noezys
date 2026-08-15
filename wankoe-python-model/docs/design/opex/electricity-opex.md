# Electricity OPEX model — annual kWh + cascaded zone-exit EUR/t

**Date: 2026-08-15 — built on the client's 4 arbitrated choices of the same
day (see the decision-log row in `docs/spec-conformity-matrix.md`).**

1. **Perimeter** — process machines + materials handling + dryer
   ELECTRICAL auxiliaries. The dryer **burner BU.04 is fuel-fired**: it is
   excluded from every electricity figure and its thermal MWh is reported
   separately at the bottom.
2. **Power basis** — **ABSORBED power.** Engine-modeled machines (CR.5009,
   CR.5011, CR.5113, RC.1, RC.2; ML.26 belongs to the as-built variant
   only and is **skipped** at the c1 reference default) use the per-mode
   photo's `P_net_kW / eta_m`. All non-modeled drives use TYPICAL
   installed ratings **[H]** x the absorption factor **0.72 [H]** — every
   rating, its one-line justification and the factor live in
   `data/default_parameters.json` -> `electrical_loads` (data-first).
3. **Hours** — `run_required_hours` (hours follow the targets) for BOTH
   scenarios; consumers run only during their zone's mode-hour buckets
   (client 2026-08-15: SR.5105 and the loop machines SR.5111 / CR.5113 /
   SR.5115 run in BOTH the 2A and 2C hours).
4. **Output** — kWh only. **Partly superseded the same day**: the second
   2026-08-15 arbitration (cascaded zone-exit cost model, below) adds a
   EUR/t "prix de revient" at each zone exit, priced at 115 EUR/MWh [H].

Scenarios: **(a) defaults** = today's measured feed, AgLime market 135 kt;
**(b) quarry target** = quarry-works curve (40.1 % < 20 mm,
`quarry-target-curve-20pct-margin.json`) with the AgLime baseline 108 kt
(135 kt market − 20 % flex margin, client 2026-08-14).

Replay: `PYTHONPATH=src python scripts/opex_electricity.py`
(prints this table and writes `electricity-opex.json` alongside).

## Headline

| | (a) defaults | (b) quarry target |
|---|---:|---:|
| **Total electricity** | **1 276.9 MWh/y** | **1 192.8 MWh/y** |
| Line-level intensity (total sold product) | **3.99 kWh/t** (320 284 t) | **4.07 kWh/t** (293 285 t) |
| Excluded dryer burner FUEL (apart) | 12 488.6 MWh/y | 12 488.7 MWh/y |

The quarry curve saves ~84 MWh/y of electricity (shorter zone-1.1 and
zone-1.2 hours), but the smaller AgLime baseline (−27 kt sold) makes the
per-tonne intensity slightly higher.

## Effective hours by mode (from the planning)

| Mode bucket | (a) defaults h | (b) quarry h |
|---|---:|---:|
| Zone 1.1 — 1A | 1 366.6 | 1 203.3 |
| Zone 1.1 — 1B | 0.0 | 0.0 |
| Zone 1.2 — 2A (dry season) | 1 749.7 | 1 576.4 |
| Zone 1.2 — 2B (rain bypass) | 0.0 | 0.0 |
| Zone 1.2 — 2C (AgLime campaigns) | 678.6 | 581.9 |
| Zone 1.3 — G (grits) | 2 466.1 | 2 459.9 |
| Zone 1.3 — F (fines campaign) | 1 144.4 | 1 152.4 |

Mode 1B never runs (KFS-driven in both scenarios) — its photo is not
needed. Rain-season hours are 0 in both plans (dry-season capacity
suffices), so the 2B bucket carries no energy this year.

## Annual kWh by machine

Basis `engine` = absorbed power from the per-mode photo (P_net/eta_m,
shown per mode). Basis `typical [H]` = typical installed rating [H]
x 0.72 [H] (constant absorbed kW across its modes).

| Machine | Zone | Basis | Absorbed kW by mode (a) | kWh/y (a) | Absorbed kW by mode (b) | kWh/y (b) |
|---|---|---|---|---:|---|---:|
| CR.5009 | 1.1 | engine | 1A: 96.6 | 132 074 | 1A: 111.3 | 133 972 |
| CR.5011 | 1.1 | engine | 1A: 21.5 | 29 423 | 1A: 22.6 | 27 156 |
| SR.5007 | 1.1 | typical [H] 22 kW | 15.84 | 21 647 | 15.84 | 19 060 |
| BC.5004 | 1.1 | typical [H] 7.5 kW | 5.40 | 7 380 | 5.40 | 6 498 |
| BC.5007 | 1.1 | typical [H] 7.5 kW | 5.40 | 7 380 | 5.40 | 6 498 |
| BC.5010 | 1.1 | typical [H] 5.5 kW | 3.96 | 5 412 | 3.96 | 4 765 |
| BC.5012 | 1.1 | typical [H] 7.5 kW | 5.40 | 7 380 | 5.40 | 6 498 |
| BC.5013 (1A only) | 1.1 | typical [H] 5.5 kW | 3.96 | 5 412 | 3.96 | 4 765 |
| BF.5101+5102 | 1.2 | typical [H] 2x4 kW | 5.76 | 13 987 | 5.76 | 12 432 |
| BC.5103 | 1.2 | typical [H] 5.5 kW | 3.96 | 9 616 | 3.96 | 8 547 |
| SR.5105 (2A+2C) | 1.2 | typical [H] 15 kW | 10.80 | 26 226 | 10.80 | 23 310 |
| SR.5111 (2A+2C) | 1.2 | typical [H] 11 kW | 7.92 | 19 232 | 7.92 | 17 094 |
| **CR.5113 (2A+2C)** | 1.2 | engine | 2A: 87.4 / 2C: 348.1 | **389 141** | 2A: 74.2 / 2C: 359.4 | **326 088** |
| SR.5115 (2A+2C) | 1.2 | typical [H] 11 kW | 7.92 | 19 232 | 7.92 | 17 094 |
| BC.5107 (2A+2B) | 1.2 | typical [H] 4 kW | 2.88 | 5 039 | 2.88 | 4 540 |
| BC.5108 (2A+2B) | 1.2 | typical [H] 4 kW | 2.88 | 5 039 | 2.88 | 4 540 |
| BC.5110 (2A+2C) | 1.2 | typical [H] 4 kW | 2.88 | 6 994 | 2.88 | 6 216 |
| BC.5112 (2A+2C) | 1.2 | typical [H] 5.5 kW | 3.96 | 9 616 | 3.96 | 8 547 |
| BC.5114 (2A+2C) | 1.2 | typical [H] 4 kW | 2.88 | 6 994 | 2.88 | 6 216 |
| BC.5116 (2A+2C) | 1.2 | typical [H] 4 kW | 2.88 | 6 994 | 2.88 | 6 216 |
| BC.5117 (2A+2C) | 1.2 | typical [H] 4 kW | 2.88 | 6 994 | 2.88 | 6 216 |
| BC.02 | 1.3 | typical [H] 4 kW | 2.88 | 10 398 | 2.88 | 10 403 |
| DY.03 drum drive | 1.3 | typical [H] 37 kW | 26.64 | 96 184 | 26.64 | 96 232 |
| BU.04 combustion-air fan | 1.3 | typical [H] 18.5 kW | 13.32 | 48 092 | 13.32 | 48 116 |
| FI.05/FN.06 filter fan | 1.3 | typical [H] 30 kW | 21.60 | 77 987 | 21.60 | 78 026 |
| EM.09 metal detector | 1.3 | typical [H] 1 kW | 0.72 | 2 600 | 0.72 | 2 601 |
| SC.A | 1.3 | typical [H] 11 kW | 7.92 | 28 595 | 7.92 | 28 609 |
| SC.B | 1.3 | typical [H] 11 kW | 7.92 | 28 595 | 7.92 | 28 609 |
| RC.1 | 1.3 | engine | G: 17.4 / F: 13.6 | 58 615 | G: 18.2 / F: 14.2 | 61 296 |
| RC.2 (2 units) | 1.3 | engine | G: 37.9 / F: 48.5 | 148 943 | G: 37.3 / F: 47.9 | 146 897 |
| ML.26 | 1.3 | engine | SKIPPED (as-built variant only; c1 active) | 0 | — | 0 |
| BC.22 (G only) | 1.3 | typical [H] 4 kW | 2.88 | 7 102 | 2.88 | 7 085 |
| BE.40 | 1.3 | typical [H] 5.5 kW | 3.96 | 14 298 | 3.96 | 14 305 |
| SP.36 fan | 1.3 | typical [H] 5.5 kW | 3.96 | 14 298 | 3.96 | 14 305 |
| CL.38 | 1.3 | typical [H] 0 kW (negligible) | 0 | 0 | 0 | 0 |

**Top-3 consumers (both scenarios): CR.5113 (30/27 % of the total), RC.2,
CR.5009** — the three engine-modeled crushers dominate; the [H] typical
loads together make ~45 % of the total, so the absorbed-power hypotheses
matter and should be replaced by measured motor currents at commissioning.

**Finding worth an arbitration eye:** in mode 2C the model's absorbed power
for CR.5113 reaches **~350-360 kW** (the whole 100 t/h reclaim through the
loop, ~88 t/h through the crusher at equilibrium). That implies a much
larger motor than the 2A duty (~75-90 kW) — the CR.5113 installed-motor
sizing should be checked against the 2C campaign duty.

## Zone / mode rollup (kWh/y)

| Rollup | (a) defaults | (b) quarry target |
|---|---:|---:|
| Zone 1.1 | 216 107 | 209 212 |
| Zone 1.2 | 525 103 | 447 054 |
| Zone 1.3 | 535 706 | 536 484 |
| Mode 1A | 216 107 | 209 212 |
| Mode 2A | 253 674 | 207 763 |
| Mode 2C | 271 429 | 239 292 |
| Mode G | 362 867 | 362 394 |
| Mode F | 172 839 | 174 090 |
| **TOTAL** | **1 276 916** | **1 192 750** |

## kWh per tonne of sold product

Allocation rule (documented in the script header): each zone's energy is
spread over that zone's output mass (wet, as-stocked); the chain embeds
upstream energy pro rata of the mass pulled downstream — zone 1.2 embeds
the zone-1.1 rate on the reclaimed 0/20, zone 1.3 embeds the zone-1.2
rate on the FeedLime it consumes. Energy embedded in landfilled 0/20 is
NOT charged to sold products (it belongs to the landfill net loss,
client ruling 2026-08-13): 8 087 kWh/y at defaults, 0 at the quarry
target (zero landfill).

| Sold product | (a) kWh/t (sold t) | (b) kWh/t (sold t) |
|---|---:|---:|
| KFS | 0.633 (85 000) | 0.695 (85 000) |
| AgLime | 2.795 (135 000) | 2.767 (108 000) |
| FeedLime grits | 8.347 (40 000) | 8.325 (40 000) |
| FeedLime fines | 8.347 (60 000) | 8.325 (60 000) |
| UltraFin | 8.347 (284) | 8.325 (285) |
| **Line level (total sold)** | **3.987 (320 284)** | **4.067 (293 285)** |

The dry-products chain (zone 1.3) is ~13x more electricity-intensive per
tonne than KFS — three zones of embedded energy plus the dryer's
electrical auxiliaries over a small tonnage.

## Cascaded zone-exit costs ("prix de revient", client arbitration 2026-08-15)

**Client choices (second arbitration of 2026-08-15): MASS allocation
(option 1 — within each zone every outgoing tonne carries the same kWh/t
regardless of product) and electricity priced at the Western-Europe
industrial average, 115 EUR/MWh [H]** (2025, ex-recoverable taxes; encoded
data-first as `electrical_loads.electricity_price_eur_per_mwh` in
`data/default_parameters.json`, **to be replaced by the client's actual
supply contract price**).

The cascade:

- **Zone 1.1 exit** — kWh/t = zone-1.1 kWh / (KFS + 0/20 produced, wet).
  The SAME rate for 1 t of KFS and 1 t of 0/20.
- **Zone 1.2 exit** — each inlet 0/20 tonne carries the zone-1.1 rate;
  zone 1.2 conserves wet mass (reclaimed = AgLime + FeedLime produced),
  so exit kWh/t = zone-1.1 rate + zone-1.2 kWh / reclaimed tonnes —
  identical for AgLime and FeedLime 6/20.
- **Zone 1.3 exit** — inlet = the 6/20 stockpile cumulative kWh/t.
  **Mass-shrink convention (stated per the client's request)**: zone 1.3
  shrinks the mass (wet FeedLime in, dry products + vapor out); the
  evaporated water carries NO energy out — the whole energy (inherited
  inlet energy AND the zone-1.3 direct kWh) is divided by the **OUTGOING
  product tonnes**, so each product tonne carries the same added kWh/t.
  Exit rate identical for grits, fines and UltraFin.
- **EUR/t = kWh/t × 115 / 1000.** The cascade rates coincide numerically
  with the chained mass-allocation rates of the kWh section above (same
  rule, now priced).

### Zone-exit build-up (inherited + direct = cumulative kWh/t)

| Zone exit (products) | (a) inherited + direct = kWh/t | (a) EUR/t | (b) inherited + direct = kWh/t | (b) EUR/t |
|---|---:|---:|---:|---:|
| 1.1 — KFS = 0/20 stockpile | 0 + 0.633 = **0.633** | **0.073** | 0 + 0.695 = **0.695** | **0.080** |
| 1.2 — AgLime = FeedLime 6/20 | 0.633 + 2.162 = **2.795** | **0.321** | 0.695 + 2.071 = **2.767** | **0.318** |
| 1.3 — grits = fines = UltraFin | 3.005 + 5.342 = **8.347** | **0.960** | 2.975 + 5.350 = **8.325** | **0.957** |

(Zone-1.3 inherited > zone-1.2 cumulative because of the mass-shrink
convention: 107.8 kt wet FeedLime in, 100.3 kt dry product out.)

### EUR per tonne at each zone exit (headline)

| Product | (a) defaults kWh/t | (a) defaults EUR/t | (b) quarry kWh/t | (b) quarry EUR/t |
|---|---:|---:|---:|---:|
| KFS (zone-1.1 exit) | 0.633 | **0.073** | 0.695 | **0.080** |
| 0/20 to stockpile (zone-1.1 exit) | 0.633 | 0.073 | 0.695 | 0.080 |
| AgLime (zone-1.2 exit) | 2.795 | **0.321** | 2.767 | **0.318** |
| FeedLime 6/20 (zone-1.2 exit) | 2.795 | 0.321 | 2.767 | 0.318 |
| FeedLime grits (zone-1.3 exit) | 8.347 | **0.960** | 8.325 | **0.957** |
| FeedLime fines (zone-1.3 exit) | 8.347 | **0.960** | 8.325 | **0.957** |
| UltraFin (zone-1.3 exit) | 8.347 | 0.960 | 8.325 | 0.957 |
| **Line level (total sold product)** | 3.987 | **0.458** | 4.067 | **0.468** |

Total electricity cost at 115 EUR/MWh [H]: **146 845 EUR/y (defaults) /
137 166 EUR/y (quarry target)**. Even for the dry products the
electricity "prix de revient" stays below 1 EUR/t — the economic weight
of the line's energy is the dryer FUEL (~1 043 t/y of paraffin), not the
electricity.

Full detail (zone kWh, inlet/outgoing tonnages, per-product EUR/t) in
`electricity-opex.json` → `scenarios.*.cascaded_zone_exit_costs`.

## Excluded: dryer burner FUEL (reported apart, never added)

| | (a) defaults | (b) quarry target |
|---|---:|---:|
| Burner fuel input (M6, `burner_power_kW` x G/F hours) | 12 488.6 MWh/y | 12 488.7 MWh/y |
| of which useful thermal duty | 7 493.2 MWh/y | 7 493.2 MWh/y |

The burner fuel is ~10x the whole line's electricity — the dominant energy
cost of the line is thermal, not electrical.

## Dryer fuel (illuminating paraffin)

**The client specified the DY.03 burner fuel on 2026-08-15: ILLUMINATING
PARAFFIN (kerosene).** The burner therefore stays **EXCLUDED from every
electricity figure** (client choice 1 above, unchanged) — this section
converts its thermal MWh into fuel quantities, nothing moves into the
kWh totals.

Conversion (data-first, `electrical_loads.dryer_burner` in
`data/default_parameters.json`): LHV = **11.97 kWh/kg [H]** (typical
kerosene LHV ~43.1 MJ/kg; **supplier datasheet to confirm**), density =
**0.80 kg/L [H]**.

| | (a) defaults | (b) quarry target |
|---|---:|---:|
| Burner fuel input | 12 488.6 MWh/y | 12 488.7 MWh/y |
| **Illuminating paraffin** | **1 043.3 t/y** | **1 043.3 t/y** |
| **Volume at 0.80 kg/L [H]** | **1 304 155 L/y** | **1 304 172 L/y** |
| — of which dryer mode G (grits) | 765.9 t / 957 435 L | 764.0 t / 955 028 L |
| — of which dryer mode F (fines campaign) | 277.4 t / 346 720 L | 279.3 t / 349 144 L |

The fuel bill is essentially scenario-independent (~1 043 t/y ≈ 1.30 ML/y
in both): the dryer runs the same annual duty for the same dry-products
program; only the G/F split shifts marginally.

## Hypotheses register ([H] flags of this model)

- Absorption factor **0.72 [H]** on every typical rating (client
  arbitration 2026-08-15) — refine with measured motor currents.
- Every `typical_rating` installed kW is **[H]** — typical nameplate set
  by competent-electrical-engineer judgment, each with a one-line
  justification in `electrical_loads.consumers` (screens sized by deck
  area as dual-exciter 2x5.5-2x11 kW; belts/feeders 3-7.5 kW from the
  PFD tonnage ratings; dryer auxiliaries from the ~47 m3 drum / ~3.7 MW
  burner engine photo; SP.36 fan from the photo's Q_air).
- Engine absorbed powers inherit the model's [H] calibration (Wi 12.54,
  eta_m 0.75, A/b, n_comp / S_att pending the vendor gradation test).
- Mode-hour assignments (which consumer runs in which bucket) are encoded
  per consumer in the data; the 2A+2C rule for SR.5105 and the loop
  machines is the client's 2026-08-15 arbitration.
- Dryer fuel conversion: LHV **11.97 kWh/kg [H]** and density
  **0.80 kg/L [H]** of illuminating paraffin — both pending the supplier
  datasheet (the fuel CHOICE itself is the client's, 2026-08-15, not a
  hypothesis).
- Electricity price **115 EUR/MWh [H]** — Western-Europe industrial
  average 2025, ex-recoverable taxes; to be replaced by the client's
  actual supply contract price (the MASS-allocation cascade itself is the
  client's choice, 2026-08-15, not a hypothesis).

---
*Engine run: `wankoe_model.planning.run_required_hours` +
`wankoe_model.scenario.run_scenario` (per-mode photos), engine commit
5d16977 (cascaded zone-exit costs added the same day, in the commit that
carries this revision), data `default_parameters.json` (electrical_loads
incl. dryer_burner fuel + electricity_price_eur_per_mwh), run date
2026-08-15. Replay: `PYTHONPATH=src python scripts/opex_electricity.py`.
This software is created **by NOEZYS**.*
