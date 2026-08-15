# SOFT-ROCK SENSITIVITY STUDY — robustness of the adopted decisions

**Date:** 2026-08-15 — **Client arbitrations (3 choices of the same day):**

1. **Rock class** = *very soft limestone, rippable, no blasting* — UCS
   reference **20 MPa**, envelope **15–30 MPa**. Encoded data-first in
   `data/default_parameters.json` → `feed_product.properties.UCS_MPa`
   (case discriminator only, never a formula input — rule 2026-08-11).
   **No model coefficient default was changed.**
2. **Soft-rock coefficient scenario** built from soft-limestone
   literature, every value **[H]** — stored as overrides files
   `soft-rock-scenario.json` (central, UCS 20) +
   `soft-rock-scenario-soft15.json` / `soft-rock-scenario-soft30.json`
   (UCS-envelope variants).
3. **Engine sensitivity run** (`run_scenario` modes G/F + forced 1B/2C,
   `run_required_hours`) soft-rock vs current defaults — this document;
   evidence `soft-rock-engine-evidence.json`, replay
   `scripts/soft_rock_sensitivity.py`.

The question answered: **which adopted decisions HOLD and which FLIP if
the rock really is as soft as the client's class says** — i.e. if the
drop-weight / Bond / vendor-gradation tests come back at the soft end
instead of the current mid-hard reference set.

---

## 1. ROBUSTNESS VERDICT TABLE

Central soft-rock case (UCS 20) vs current defaults; envelope soft15 /
soft30 in § 4. All figures are engine output (provenance § 7).

| # | Adopted decision | Verdict | Engine proof (defaults → soft20) |
|---|---|---|---|
| 1 | **C1 circuit + two-mode G/F operation** (client 2026-08-14) | **HOLDS** | All four markets still served exactly (KFS 85 000 / grits 40 000 / fines 60 000 / AgLime 135 000 t); every zone feasible; mode split self-adjusts: G 2 466 → 2 818 h, F 1 144 → 700 h (soft rock co-produces more fines in mode G: fines/grits ratio 0.836 → 1.095) |
| 2 | **RC.1 purchase spec 32 t/h** (client 2026-08-14) | **HOLDS** | Mode-G loop load 29.21 → **28.31 t/h** vs 32 (soft15 worst case 27.95): margin widens from 8.7 % to 11.5 % |
| 3 | **RC.2 = 2 × 22 t/h + minimum gap 1.5 mm** (client 2026-08-14) | **HOLDS** | Mode-F total load 43.99 → **38.74 t/h** vs 44 (was at 100 % of capacity, now 88 %); mode F still converges (recirculation 66.8 → 60.8 t/h); the 1.5 mm gap requirement is topological (nipping the diverted 2/3.75 band) and remains |
| 4 | **CR.5113 2C motor finding** (348 kW absorbed → 450 kW rec. [H] or capped rate; FMECA RPN 224) | **HOLDS in kind, number drops** | 2C absorbed duty 348.1 → **211.0 kW** — still 3.7× the 2A duty (57.2 kW), so the sizing branch (big motor OR capped campaign rate) still must be decided with the vendor; but the recommended motor drops **450 → 250 kW** (211.0 × 1.15 → next IEC). Biggest purchase-spec revision if softness is confirmed |
| 5 | **Quarry works target 40.1 % < 20 mm** (client 2026-08-14) | **FLIPS** | At 40.1 % the soft-rock line leaves **36 034 t/y landfill** (yield realized 25.22 % < 28.24 % required — the crushers themselves make the fines the quarry was asked to deliver). Zero landfill at the AgLime 108 kt baseline re-bisects to **35.13 % < 20 mm** (rescale k 1.8504 vs 1.4263): the quarry control value must be RENEGOTIATED COARSER |
| 6 | **Two-mode annual plan, all four markets** (client 2026-08-14) | **HOLDS (costlier)** | Plan feasible in every soft case; zone 1.1 rises 71.2 → 80.3 % (soft15: 83.8 %) of the Saturday regime, zones 1.2/1.3 ≈ unchanged; but landfill grows **13 816 → 57 597 t/y** (KFS yield realized 24.88 → 22.04 % vs required 25.92 %) — the zero-waste economics degrade, quarry-spec renegotiation (#5) is the counter-lever |
| 7 | **FMECA priorities** (top-3 RPN: SC.B panels 252, BE.40 245, CR.5113 motor 224) | **PARTIAL FLIP** | CR.5113 motor-overload mode DE-ESCALATES (2C duty −39 %: 348 → 211 kW — occurrence cote falls, drops below the 200 critical line once the motor is sized per #4); SC.B panel wear ESCALATES (grits D6 below-2 mm margin 0.82 → **0.59 pt**, soft15 0.41 pt — even less room for aperture wear); BE.40/BC.22 handling overloads persist (zone-1.3 mass flows change < 5 %) |

Cross-cutting compliance (all soft cases): **KFS 30/55/15 envelope
HOLDS** (in-cut 82.2 % vs ≥ 55; below 9.1 ≤ 30; above 8.7 ≤ 15);
**grits D6 HOLDS** (below-2 mm 14.4 ≤ 15, above-4 mm 3.4 ≤ 5) though the
below-cut margin thins; **fines < 1.7 mm redirect eligibility HOLDS and
improves** (mode G 96.61 → 97.39 %, mode F 98.88 → 99.07 % vs ≥ 95);
**CR.5011 90 t/h wet HOLDS** (1A 74.5 → 68.6; forced 1B 90.0 → 83.5 —
the mode-1B feed 186.1 t/h gains headroom); zone-1.2 loop 2C overload
**unchanged at 155 %** (93 t/h vs 60 — a screening load, not a
hardness-driven one: the SR.5111 resize finding stands).

## 2. Soft-rock coefficient scenario (choice 2) — values and rationale

Current defaults are UNCHANGED in the data; the scenario lives as
overrides. Every value **[H]**, one-line rationale (full text in the
JSON files):

| Coefficient (model) | Default | soft15 | **soft20 (central)** | soft30 | Rationale (direction & magnitude) |
|---|---|---|---|---|---|
| Wi kWh/t (M2, power only) | 12.54 [ref.] | 6.0 | **7.5** | 9.0 | Bond tabulations, soft/weathered limestone ~6–9 kWh/t vs the competent-limestone 12.54 |
| A_j % (M5) | 60 [H] | 67 | **65** | 62 | JKMRC soft calcite A 62–69 (expert book Q12 note) |
| b_j (M5) | 0.80 [H] | 2.0 | **1.5** | 1.3 | JKMRC soft calcite b 1.3–3.0; A·b rises 48 → 97.5 — t10 at CR.5011 v30: 5.7 → 11.1 %, impact-product RR n 1.65 → 1.35 (finer, broader) |
| CR.5009 n (M1) | 1.35 | 1.10 | **1.15** | 1.25 | Friable rock breaks broader: RR slopes ~1.0–1.2 on soft limestone vs 1.3–1.5 competent; x80 = gap unchanged, the shift is all extra fines |
| RC.1/RC.2 n_comp (M7) | 1.8 [H] | 1.5 | **1.6** | 1.7 | Same direction for the smooth-roll compression component; inside the declared 1.5–2.2 range |
| RC.1/RC.2 S_att (M7) | 0.06 [H] | 0.10 | **0.09** | 0.075 | Weak rock abrades more per pass (Thiere 2020 trend); upper half of the declared 0.03–0.10 range |
| ML.26 S_att (M7, as-built only) | 0.171 [H] | 0.25 | **0.22** | 0.19 | Same direction; passes the book's Houben 0.206, inside 0.15–0.25 |

**UCS scaling assumption [H]:** each coefficient is mapped
piecewise-linearly in UCS across the 15–30 MPa envelope, anchored at the
20 MPa central value; endpoints = the soft/hard edges of the literature
range, clipped to the machines' declared parameter ranges. No measured
UCS-coefficient law exists for this deposit — the map is a documented
monotone interpolation, to be replaced by the test campaign.

## 3. Sensitivity — line photo (modes G/F, defaults vs soft cases)

| Quantity | defaults | soft15 | **soft20** | soft30 |
|---|---|---|---|---|
| KFS t/h wet (mode 1A) | 62.20 | 52.82 | **55.11** | 57.79 |
| KFS Yield realized % | 24.88 | 21.13 | **22.04** | 23.12 |
| KFS Yield required % (zero landfill) | 25.93 | 25.91 | **25.92** | 25.92 |
| Yield gap (pt) | 1.05 | 4.78 | **3.88** | 2.80 |
| KFS envelope (in/below/above %) | 82.8/8.7/8.6 ✓ | 82.1/9.2/8.8 ✓ | **82.2/9.1/8.7 ✓** | 82.4/8.9/8.7 ✓ |
| Grits t/h dry (mode G) | 16.22 | 13.35 | **14.20** | 15.19 |
| Grits D6: < 2 mm % (limit 15) | 14.18 | 14.59 | **14.41** | 14.29 |
| Grits D6 below-cut margin (pt) | 0.82 | 0.41 | **0.59** | 0.71 |
| Grits D6: > 4 mm % (limit 5) | 3.37 | 3.40 | **3.40** | 3.39 |
| Fines t/h (G / F) | 13.57 / 23.19 | 16.36 / 23.09 | **15.55 / 23.13** | 14.57 / 23.17 |
| Fines < 1.7 mm % (G / F, spec ≥ 95) | 96.6 / 98.9 | 97.7 / 99.2 | **97.4 / 99.1** | 97.0 / 99.0 |
| Zone-1.3 fines/grits ratio (mode G) | 0.836 | 1.225 | **1.095** | 0.959 |
| Zone-1.3 recirculation t/h (G / F) | 62.4 / 66.8 | 57.2 / 58.2 | **58.7 / 60.8** | 60.5 / 63.8 |

### Machine loads vs the client-decided capacities

| Load (basis) | Capacity | defaults | soft15 | **soft20** | soft30 |
|---|---|---|---|---|---|
| RC.1 mode G (dry) | 32 | 29.21 | 27.95 | **28.31** | 28.70 |
| RC.2 mode F total (dry) | 2 × 22 = 44 | 43.99 | 36.39 | **38.74** | 41.37 |
| CR.5011 mode 1A (wet) | 90 | 74.48 | 66.88 | **68.58** | 71.54 |
| CR.5011 forced 1B (wet) | 90 | 90.02 | 81.52 | **83.51** | 86.74 |
| SR.5111 loop feed 2C (dry) | 60 | 93.0 (155 %) | 93.0 | **93.0** | 93.0 |

### Absorbed powers (P_net/η_m, kW) and engine-modeled electricity

| Machine [mode] | defaults | soft15 | **soft20** | soft30 |
|---|---|---|---|---|
| CR.5009 [1A] | 96.6 | 48.6 | **60.1** | 70.6 |
| CR.5011 [1A / 1B] | 21.5 / 46.0 | 10.0 / 21.0 | **12.5 / 26.4** | 15.4 / 32.6 |
| CR.5113 [2A / 2C] | 87.4 / 348.1 | 47.5 / 170.2 | **57.2 / 211.0** | 66.6 / 252.8 |
| RC.1 [G] | 17.4 | 8.2 | **10.2** | 12.3 |
| RC.2 [F, total] | 48.5 | 20.2 | **26.3** | 33.2 |
| **Modeled drives MWh/y** (kW × plan hours) | 758.2 | 368.8 | **458.4** | 549.2 |
| **Electricity OPEX delta** at 115 EUR/MWh [H] | — (87.2 kEUR/y) | −44.8 kEUR/y | **−34.5 kEUR/y** | −24.0 kEUR/y |

(Method identical to the 2026-08-15 OPEX study for the engine-modeled
drives; non-modeled drives keep their typical ratings [H] and move only
through the small hour changes.)

### Two-mode annual plan (hours follow the targets)

| Quantity | defaults | soft15 | **soft20** | soft30 |
|---|---|---|---|---|
| Zone 1.1 h clock / util % / feasible | 1 708 / 71.2 / ✓ | 2 012 / 83.8 / ✓ | **1 928 / 80.3 / ✓** | 1 839 / 76.6 / ✓ |
| Zone 1.2 h clock / util % | 3 035 / 40.5 | 3 039 / 40.5 | **3 037 / 40.5** | 3 036 / 40.5 |
| Zone 1.3 h clock / util % | 4 513 / 60.2 | 4 339 / 57.9 | **4 397 / 58.6** | 4 458 / 59.4 |
| Zone-1.3 split G / F (eff. h) | 2 466 / 1 144 | 2 996 / 476 | **2 818 / 700** | 2 633 / 934 |
| Zone-1.2 split 2A / 2C (eff. h) | 1 750 / 679 | 1 869 / 562 | **1 831 / 599** | 1 798 / 631 |
| Mode-1B hours (auto rule) | 0 | 0 | **0** | 0 |
| All four markets served | ✓ | ✓ | **✓** | ✓ |
| **0/20 to LANDFILL t/y** | 13 816 | 74 259 | **57 597** | 39 796 |

## 4. Quarry-target check (decision #5)

| Case | < 20 mm at zone-1 inlet | Landfill t/y | Yield realized / required % |
|---|---|---|---|
| defaults + 40.1 % curve + AgLime 108 kt | 40.10 | **0** | 28.26 / 28.26 (self-consistent) |
| soft20 + 40.1 % curve + AgLime 108 kt | 40.10 | **36 034** | 25.22 / 28.24 |
| soft20, re-bisected zero-landfill curve | **35.13** (k 1.8504) | ~0 | 28.24 / 28.24 |

Reading: soft rock makes the crushing block itself produce more sub-20 mm
— so the quarry must deliver a **coarser** run-of-mine for the 0/20
balance to close. The 40.1 % acceptance band (40.1/45.5) of
`docs/design/zone13-redesign/quarry-works-specification.md` no longer
buys zero landfill; the control value moves to **≈ 35.1 %** at the soft20
central case (and lower still toward soft15). With rippable rock and no
blasting the achievable ROM gradation is itself different — the quarry
spec must be re-issued together with the test campaign below.

## 5. Decisions to REVISIT if the drop-weight / gradation tests confirm softness

Priority order:

1. **Quarry works specification** (the one outright FLIP): re-bisect the
   control value (≈ 35.1 % < 20 mm at soft20) and the acceptance band on
   the MEASURED coefficient set; re-check the 20 % AgLime flex buffer.
2. **CR.5113 motor purchase branch**: 450 kW rec. is over-sized in every
   soft case (needed ≈ 250 kW at soft20, ≈ 200 at soft15) — hold the
   motor order until the tests land; the branch decision (big motor vs
   capped campaign rate) itself remains.
3. **Landfill economics / KFS-yield program**: the yield gap widens to
   3.9 pt (57.6 kt/y landfill) — the quarry renegotiation (#1) is the
   lever; zone-1 settings (g/CSS/v) could also be re-optimized on the
   soft coefficient set (the 2026-08-13 settings campaign assumed the
   mid-hard set).
4. **FMECA re-scoring**: SC.B panel-wear criticality up (D6 margin
   0.59 → 0.41 pt across the envelope), CR.5113 motor overload down —
   re-run `scripts/fmeca_engine_evidence.py` with the confirmed set.
5. **Purchase datasheet duty tables** (`docs/purchase/`): all absorbed
   powers drop 25–50 % — motors sized on the mid-hard set become the
   conservative bound; keep them as maxima, restate expected duty.
6. **Zone-1.1 hours watch**: utilization 80.3 % (soft15 83.8 %) of the
   Saturday regime — still feasible but the Q7 headroom shrinks.

What does NOT need revisiting: RC.1 32 t/h, RC.2 2 × 22 + gap 1.5,
C1 topology and the two-mode plan, KFS envelope compliance, fines
redirect eligibility, SR.5111 loop resize (hardness-independent),
dryer/fuel sizing (M6 unchanged by hardness).

## 6. Limits of this study

- Every soft-rock coefficient is **[H]** literature-based; the UCS map of
  § 2 is an assumed monotone interpolation. The study ranks decisions by
  robustness — it does not predict the soft-rock line photo better than
  the tests will.
- The imperfection-convention question (Q3 family) and the vendor
  gradation test interact with n_comp/S_att; the RC.1/RC.2 vendor test
  required by the purchase datasheets closes both.
- Wi affects power only (M2); PSD shifts come from b_j (M5) and the
  n/n_comp/S_att slopes (M1/M7). A soft Bond result without a soft
  drop-weight result would change OPEX but not the mass balance.

## 7. Provenance

- Engine run: commit `8a7ee50`, 2026-08-15, functions
  `wankoe_model.scenario.run_scenario` (per-mode photos G / F / forced
  1B / 2C, weather dry, X2 converged grid) +
  `wankoe_model.planning.run_required_hours`.
- Data: `data/default_parameters.json` (defaults) +
  `docs/design/soft-rock/soft-rock-scenario*.json` (overrides, [H]).
- Evidence: `docs/design/soft-rock/soft-rock-engine-evidence.json`;
  replay without the assistant:
  `PYTHONPATH=src python scripts/soft_rock_sensitivity.py`.
- All figures in this document are engine executions (no
  assistant-computed figures) except the IEC motor roundings of § 1/#4
  and § 5/#2, which apply the purchase-datasheet rule (worst absorbed
  × 1.15 [H] → next IEC rating) to engine outputs.

*Produced by NOEZYS.*
