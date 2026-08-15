# PURCHASE TECHNICAL DATASHEET — RC.2

**Smooth double-roll crusher, stage 2 — TWO PARALLEL UNITS — zone 1.3**
Issued 2026-08-15 (client order of the same day: purchase datasheets for the 13 major process machines) — produced by NOEZYS.

## 1. Identification and role

| Item | Value |
|---|---|
| Tag | RC.2 (2 units) |
| Type | Smooth double-roll crusher, stage 2; **TWO units installed** (client 2026-08-14, fines-objective configuration option 1) |
| Zone / duty | 1.3 — fine crushing loop (SC.A deck-2 recycle + mode-F regrind of the 2/3.75 diverted band and the 1.5/2 sliver) |
| Operating modes | G (grits), F (fines campaign — needs BOTH units at capacity) |
| Annual running hours (defaults) | 3 610.5 h effective |
| Criticality | Redundant in mode G; **NO redundancy in mode F** (both at 100 %) |

## 2. Process duty (engine runs, 2026-08-15)

Dry basis (zone 1.3). Engine power is the TOTAL over both units.

| Quantity | Mode G | Mode F |
|---|---|---|
| Throughput (total, 2 units) | 33.2 t/h (66 % of 2 x 25) | **44.0 t/h = 88 % of 2 x 25** (x2-grid figure; converged ~44.4 — client decision 2026-08-15, error-hunt PD-4: capacity raised from 2 x 22, where this point sat at exactly 100 %) |
| Operating gap | 3.4 mm | **1.5 mm** (mode-F gap) |
| Feed F80 | 7.0 mm | 6.0 mm |
| Product P80 | 2.8 mm | 2.6 mm |
| Circulating context | — | **sliver + 2/3.75 regrind loop; at gap 1.5 the loop stabilizes at 44.0 t/h through RC.2 (2 units, engine-proven; 88 % of the 2 x 25 purchase capacity); at gap 2.8 the loop RUNS AWAY — 172.8 t/h at the current mode-F feed (error-hunt fix 2026-08-15: a previous revision attributed the runaway figure to gap 1.5 — inverted)** |
| Absorbed power, total (P_net / eta_m 0.75) | 37.9 kW | 48.5 kW |
| Absorbed power, per unit | 19.0 kW | 24.2 kW |

## 3. Settings and required adjustability

| Parameter | Unit | Range required | Reference setting |
|---|---|---|---|
| Gap g | mm | **1.5 - 4.5** operating (data range 2.8 - 4.5 default 3.4, PLUS the mode-F point 1.5) | 3.4 (G) / **1.5 (F)** |
| Compression lambda | - | 1.8 - 2.8 | 2.2 **[H]** |
| RR slope n_comp | - | 1.5 - 2.2 | 1.8 **[H]** |
| Attrition S_att | - | 0.03 - 0.10 | 0.06 **[H]** |

Gap changeover 3.4 <-> 1.5 mm is a ROUTINE mode-change operation (pattern `mode_F_gap_mm`), not a workshop setting.

## 4. Capacity and sizing requirements (client-decided)

- **Capacity 2 x 25 t/h dry — CLIENT PURCHASE SPEC (2026-08-15, error-hunt PD-4; supersedes the 2 x 22 of 2026-08-14)**. 25 t/h per unit at gap 1.5 mm is a GUARANTEE point, not a nominal. Rationale: the mode-F duty is 44.0 t/h on the production grid and ~44.4 t/h converged, the first 0.1 mm of gap drift adds ~1 t/h, and the comp_lam hypothesis [H] swings the load +/-7.5 % per +/-10 % until the vendor gradation test lands — 2 x 22 left ZERO margin against all three; 2 x 25 gives ~12 %.
- **Minimum gap capability 1.5 mm — VENDOR TO CONFIRM** (open purchase item, FMECA RC.2-FM2): the fines objective (60 kt/y) is infeasible above ~2.8 mm (runaway circulating load: 172.8 t/h at the current 25.05 t/h wet mode-F feed; the historic 147 t/h figure was computed at the old 21.3 t/h design feed). An offer whose smooth rolls cannot close and HOLD 1.5 mm under load does not meet this specification.
- **Motor**: worst per-unit absorbed 24.2 kW; recommended minimum installed **30 kW per unit** (x1.15 allowance [H], next IEC size; vendor to confirm). `installed_power_kW` null — vendor value closes it.
- Two identical units, fully interchangeable (rolls, bearings, drives, spares).

## 5. FMECA-derived purchase requirements

| FM (RPN) | Failure mode | Purchase requirement |
|---|---|---|
| RC.2-FM1 (168) | Roll surface wear / corrugation at gap 1.5 | **Roll surface wear specification**: shell hardness/material for fine abrasive dry duty, guaranteed wear life or regrind interval AT GAP 1.5 mm under the 44 t/h (2 units) circulating regrind duty (error-hunt fix 2026-08-15: 147 t/h is the gap-2.8 runaway, not the gap-1.5 duty); rolls regrindable on site or cartridge-exchangeable so campaigns can be staggered (FMECA: one unit always fresh) |
| RC.2-FM2 (144) | Gap drift at the min-gap operating point | **Gap-drift instrumentation on BOTH units**: position feedback, drift alarm, setting repeatable to 0.1 mm — operating AT the vendor minimum leaves no drift allowance; weekly verification without dismantling |
| RC.2-FM3 (100) | Roll bearing failure (one unit) | **Bearing temperature + vibration monitoring per unit** (comparative trending between the twin units is the detection method); grease per vendor; single-unit overhaul possible while the twin runs |
| RC.2-FM4 (60) | Drive / coupling failure | Yearly gearbox service per unit, staggered; spare coupling element shared |
| (EM.09 chain) | Tramp metal on smooth rolls | Same requirement as RC.1: max tolerable tramp size stated for the EM.09 threshold; overload release on each unit |

## 6. Open [H] items the vendor must close — VENDOR GRADATION TEST (REQUIREMENT)

- **The vendor gradation test is a PURCHASE REQUIREMENT** (golden rule 2; `product_curve_table` null): product PSD value tables at gaps 1.5 - 4.5 mm on WANKOE material, declared interpolation mode. It **fixes n_comp and S_att [H]** (the D6 grits margin is only **0.8 pt**), **confirms the 25 t/h per-unit capacity at gap 3.4** (open note in the data) and **proves the 1.5 mm gap capability** — the three open items of this purchase in one witnessed test.
- **[H] lambda / n_comp / S_att** — replaced by the test.
- Installed power, roll dimensions (data slots null); motor allowance x1.15 [H].

## 7. Acceptance tests and QC criteria

1. **Mode-F guarantee test**: 25 t/h per unit sustained 2 h at gap 1.5 mm on WANKOE material — gap held within 0.1 mm, no overload release, product P80 consistent with 2.6 mm.
2. **Gradation acceptance** = the section-6 test, witnessed; model coefficients re-fitted data-first and the two-mode plan replayed by the engine before acceptance.
3. **Gap changeover demonstration**: 3.4 -> 1.5 -> 3.4 within the vendor-stated time, both units.
4. **Downstream QC tie-in**: fines 0/1.5 product spec + redirect eligibility (>= 95 % < 1.7 mm) and grits D6 envelope at SC.B; loop stability (no runaway circulating load) over a 4 h mode-F run.
5. Per-unit bearing/vibration baselines; twin-unit comparative trend configured.

---
*Engine provenance: commit 5dc5b53, run 2026-08-15, `wankoe_model.scenario.run_scenario` (per-mode photos G / F, weather dry), data `data/default_parameters.json`. Replay: `PYTHONPATH=src python scripts/purchase_datasheet_evidence.py` -> `docs/purchase/purchase-engine-evidence.json`. Produced by NOEZYS.*
